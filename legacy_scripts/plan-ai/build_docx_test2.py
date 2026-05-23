import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, r'C:\Users\lauze\.claude\skills\business-plan-writer\scripts')
from build_docx import build_batch_commands, run_officecli

print("Script started")

parser = argparse.ArgumentParser()
parser.add_argument("--content", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

print("Args parsed")
content = json.loads(Path(args.content).read_text(encoding="utf-8"))
commands = build_batch_commands(content)
print("Commands:", len(commands))

run_officecli(["create", args.output])
print("Created")
run_officecli(["open", args.output])
print("Opened")

chunk_size = 100
for i in range(0, len(commands), chunk_size):
    chunk = commands[i:i+chunk_size]
    print(f"Chunk {i//chunk_size+1} size {len(chunk)}")
    proc = subprocess.run(
        ["officecli", "batch", args.output, "--json"],
        input=json.dumps(chunk, ensure_ascii=False),
        capture_output=True, text=True, encoding="utf-8",
        timeout=30
    )
    print(f"Chunk result {proc.returncode}")

run_officecli(["close", args.output])
print("Closed")
