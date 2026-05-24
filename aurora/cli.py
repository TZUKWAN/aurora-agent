"""CLI interface for AuroraAgent."""

import asyncio
import json
import os
import sys
from argparse import ArgumentParser

import aurora
from aurora.agent import AuroraAgent
from aurora.config import MODEL_PROFILES, load_config, validate_config
from aurora.logging_config import setup_logging


async def chat(config):
    """Run interactive chat mode."""
    setup_logging()
    agent = AuroraAgent(config)

    model_name = config.model.name
    version = aurora.__version__
    session_id = agent.session_id or "new"

    print("=" * 60)
    print(f"  AuroraAgent v{version} - Competition AI Assistant")
    print("=" * 60)
    print(f"  Model: {model_name}")
    print(f"  Session: {session_id}")
    print("  Commands:")
    print("    /tools   - List registered tools")
    print("    /history - Show message history")
    print("    /edit N  - Edit message at index N")
    print("    /undo    - Undo last edit")
    print("    quit     - Exit")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nYou: ")

            if user_input.lower() in ["quit", "exit", "q"]:
                break

            stripped = user_input.strip()

            if stripped == "/tools":
                tools = agent.get_tool_list()
                print(f"\nRegistered tools ({len(tools)}):")
                for t in tools:
                    print(f"  - {t}")
                continue

            if stripped == "/history":
                msgs = agent.history.get_messages()
                if not msgs:
                    print("  (empty)")
                for i, m in enumerate(msgs):
                    role = m["role"].upper()
                    content = m["content"][:80].replace("\n", " ")
                    print(f"  [{i}] {role}: {content}")
                continue

            if stripped.startswith("/edit "):
                try:
                    idx = int(stripped.split()[1])
                    msgs = agent.history.get_messages()
                    if 0 <= idx < len(msgs):
                        old = msgs[idx]
                        print(f"  Editing [{idx}] {old['role']}: {old['content'][:60]}...")
                        new_content = input("  New content: ")
                        if new_content.strip():
                            agent.edit_message(idx, new_content.strip())
                            print("  Edited. Messages after that index truncated.")
                    else:
                        print(f"  Invalid index. Valid: 0-{len(msgs)-1}")
                except (ValueError, IndexError):
                    print("  Usage: /edit <index>")
                continue

            if stripped == "/undo":
                if agent.undo():
                    print("  Undo successful.")
                else:
                    print("  Nothing to undo.")
                continue

            if not stripped:
                continue

            print("Thinking...")
            response = await agent.run(user_input)
            print(f"\nAurora: {response}")

        except KeyboardInterrupt:
            print()
            break
        except Exception as e:
            print(f"Error: {e}")


def cmd_sessions(config):
    """List all sessions."""
    from aurora.memory.session_db import MemoryManager
    mm = MemoryManager()
    sessions = mm.list_sessions()
    if not sessions:
        print("No sessions found.")
        return
    print(f"{'ID':<15} {'Project':<20} {'Updated':<22}")
    print("-" * 60)
    for s in sessions:
        print(f"{s['session_id']:<15} {s['project_name'][:20]:<20} {s['last_updated'][:19]:<22}")


def cmd_resume(config, session_id):
    """Resume a session."""
    setup_logging()
    agent = AuroraAgent(config)
    if agent.load_session(session_id):
        print(f"Resumed session {session_id} ({len(agent.history)} messages)")
        asyncio.run(chat(config))
    else:
        print(f"Session {session_id} not found.")


def cmd_delete(config, session_id):
    """Delete a session."""
    from aurora.memory.session_db import MemoryManager
    mm = MemoryManager()
    if mm.delete_session(session_id):
        print(f"Session {session_id} deleted.")
    else:
        print(f"Session {session_id} not found.")


async def _cmd_generate(config, args):
    """Generate a business plan directly."""
    setup_logging()
    agent = AuroraAgent(config)

    project_info = {
        "project_name": args.name or "",
        "technology": args.tech or "",
        "target_market": args.market or "",
        "problem": getattr(args, "problem", "") or "",
        "solution": getattr(args, "solution", "") or "",
        "product": getattr(args, "product", "") or "",
        "business_model": getattr(args, "business_model", "") or "",
        "team_background": getattr(args, "team", "") or "",
    }

    competition = getattr(args, "competition", "internet_plus") or "internet_plus"
    output = getattr(args, "output", None)
    fmt = getattr(args, "format", "text") or "text"

    prompt = (
        f"Generate a complete business plan for: "
        f"Project={project_info['project_name']}, "
        f"Tech={project_info['technology']}, "
        f"Market={project_info['target_market']}, "
        f"Competition={competition}"
    )

    result = await agent.run(prompt)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Output saved to {output}")
    else:
        print(result)


async def _cmd_evaluate(config, args):
    """Evaluate a project directly."""
    setup_logging()
    agent = AuroraAgent(config)

    prompt = (
        f"Evaluate my project: "
        f"Technology={args.tech}, "
        f"Innovation={getattr(args, 'innovation', '')}, "
        f"Team={getattr(args, 'team', '')}, "
        f"Competition={getattr(args, 'competition', 'internet_plus')}"
    )

    result = await agent.run(prompt)
    print(result)


async def _cmd_match(config, args):
    """Match competition tracks."""
    setup_logging()
    agent = AuroraAgent(config)

    prompt = f"Match competition tracks for: Tech={args.tech}, Market={getattr(args, 'market', '')}"
    result = await agent.run(prompt)
    print(result)


async def _cmd_exec(config, args):
    """Execute a prompt in headless mode."""
    setup_logging()
    agent = AuroraAgent(config)

    prompt = args.prompt
    output = getattr(args, "output", None)
    timeout = getattr(args, "timeout", 120)

    try:
        result = await asyncio.wait_for(agent.run(prompt), timeout=timeout)
    except asyncio.TimeoutError:
        print(f"Timeout after {timeout}s", file=sys.stderr)
        sys.exit(1)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        if not getattr(args, "quiet", False):
            print(f"Output saved to {output}")
    else:
        fmt = getattr(args, "format", "text")
        if fmt == "json":
            print(json.dumps({"result": result}, ensure_ascii=False))
        else:
            print(result)


def cmd_batch(config, args):
    """Process batch tasks from a file."""
    import time

    filepath = args.tasks_file
    parallel = getattr(args, "parallel", 1)
    retry_count = getattr(args, "retry", 0)
    output_dir = getattr(args, "output_dir", ".")

    os.makedirs(output_dir, exist_ok=True)

    with open(filepath, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    if not isinstance(tasks, list):
        print("Error: tasks file must contain a JSON array of prompt strings")
        sys.exit(1)

    results = []

    for i, task_prompt in enumerate(tasks):
        attempt = 0
        success = False
        result_text = ""

        while attempt <= retry_count and not success:
            attempt += 1
            try:
                agent = AuroraAgent(config)
                result_text = asyncio.run(asyncio.wait_for(
                    agent.run(str(task_prompt)), timeout=120
                ))
                success = True
            except Exception as e:
                result_text = f"Error: {e}"

        results.append({"prompt": task_prompt, "result": result_text, "success": success})

        # Save individual result
        out_path = os.path.join(output_dir, f"task_{i:03d}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(result_text)

        status = "OK" if success else "FAIL"
        print(f"[{i+1}/{len(tasks)}] {status}: {str(task_prompt)[:60]}")

    # Save summary
    summary_path = os.path.join(output_dir, "batch_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    ok_count = sum(1 for r in results if r["success"])
    print(f"\nDone: {ok_count}/{len(results)} succeeded. Summary: {summary_path}")


def main():
    """Main entry point."""
    parser = ArgumentParser(prog="aurora", description="AuroraAgent CLI")
    parser.add_argument("--version", "-v", action="version",
                        version=f"aurora {aurora.__version__}")
    parser.add_argument("--model", "-m", dest="model",
                        choices=list(MODEL_PROFILES.keys()),
                        help="Model profile to use")
    parser.add_argument("--config", "-c", dest="config",
                        help="Config file path")

    subparsers = parser.add_subparsers(dest="command")

    # chat
    chat_p = subparsers.add_parser("chat", help="Start interactive chat")
    chat_p.add_argument("--model", "-m", dest="model",
                        choices=list(MODEL_PROFILES.keys()), help="Model profile")

    # sessions
    subparsers.add_parser("sessions", help="List all sessions")

    # resume
    resume_p = subparsers.add_parser("resume", help="Resume a session")
    resume_p.add_argument("session_id", help="Session ID")

    # delete
    delete_p = subparsers.add_parser("delete", help="Delete a session")
    delete_p.add_argument("session_id", help="Session ID")

    # generate
    gen_p = subparsers.add_parser("generate", help="Generate a business plan")
    gen_p.add_argument("--name", "-n", help="Project name")
    gen_p.add_argument("--tech", "-t", help="Technology")
    gen_p.add_argument("--market", "-m", dest="market", help="Target market")
    gen_p.add_argument("--problem", help="Problem to solve")
    gen_p.add_argument("--solution", help="Solution")
    gen_p.add_argument("--product", help="Product name")
    gen_p.add_argument("--business-model", dest="business_model", help="Business model")
    gen_p.add_argument("--team", help="Team background")
    gen_p.add_argument("--competition", default="internet_plus", help="Competition ID")
    gen_p.add_argument("--output", "-o", help="Output file path")
    gen_p.add_argument("--format", "-f", default="text", choices=["text", "md", "json"])

    # evaluate
    eval_p = subparsers.add_parser("evaluate", help="Evaluate a project")
    eval_p.add_argument("--tech", "-t", required=True, help="Technology")
    eval_p.add_argument("--innovation", help="Innovation description")
    eval_p.add_argument("--team", help="Team background")
    eval_p.add_argument("--competition", default="internet_plus")

    # match
    match_p = subparsers.add_parser("match", help="Match competition tracks")
    match_p.add_argument("--tech", "-t", required=True, help="Technology")
    match_p.add_argument("--market", "-m", help="Target market")

    # exec
    exec_p = subparsers.add_parser("exec", help="Execute a prompt (headless mode)")
    exec_p.add_argument("prompt", help="Prompt to execute")
    exec_p.add_argument("--output", "-o", help="Output file")
    exec_p.add_argument("--format", "-f", default="text", choices=["text", "json"])
    exec_p.add_argument("--timeout", type=int, default=120, help="Timeout in seconds")
    exec_p.add_argument("--quiet", "-q", action="store_true")

    # batch
    batch_p = subparsers.add_parser("batch", help="Batch process tasks from file")
    batch_p.add_argument("tasks_file", help="JSON file with task prompts")
    batch_p.add_argument("--parallel", "-j", type=int, default=1)
    batch_p.add_argument("--retry", type=int, default=0)
    batch_p.add_argument("--output-dir", default="./output")

    args = parser.parse_args()

    # Apply model profile
    if hasattr(args, "model") and args.model:
        os.environ["AURORA_PROFILE"] = args.model

    config = load_config(getattr(args, "config", None))

    # Commands that don't need API validation
    if args.command in ("sessions",):
        cmd_sessions(config)
        return
    if args.command == "delete":
        cmd_delete(config, args.session_id)
        return
    if args.command is None:
        parser.print_help()
        return
    if args.command == "batch":
        if not os.path.exists(args.tasks_file):
            print(f"File not found: {args.tasks_file}", file=sys.stderr)
            sys.exit(1)
        cmd_batch(config, args)
        return

    try:
        validate_config(config)
    except ValueError as e:
        print(f"Config error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.command == "chat":
        asyncio.run(chat(config))
    elif args.command == "resume":
        cmd_resume(config, args.session_id)
    elif args.command == "generate":
        asyncio.run(_cmd_generate(config, args))
    elif args.command == "evaluate":
        asyncio.run(_cmd_evaluate(config, args))
    elif args.command == "match":
        asyncio.run(_cmd_match(config, args))
    elif args.command == "exec":
        asyncio.run(_cmd_exec(config, args))
    elif args.command == "batch":
        cmd_batch(config, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
