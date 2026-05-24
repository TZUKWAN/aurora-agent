"""Core agent for AuroraAgent."""

import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from aurora.config import Config, load_config
from aurora.context import ContextCompressor
from aurora.guardrails import ToolGuardrails
from aurora.hooks import HookEvent, HookManager
from aurora.history import ConversationHistory
from aurora.memory.session_db import MemoryManager
from aurora.prompts.system import SYSTEM_PROMPT
from aurora.recovery import RecoveryManager
from aurora.security import SecurityManager
from aurora.swarm.orchestrator import SwarmOrchestrator
from aurora.tools.business_plan_tools import _register_tools as bp_register_tools
from aurora.tools.competition_tools import _register_tools as comp_register_tools
from aurora.tools.evaluation_tools import _register_tools as eval_register_tools
from aurora.tools.presentation_tools import _register_tools as pres_register_tools
from aurora.tools.web_search_tools import _register_tools as web_register_tools
from aurora.tools.registry import ToolRegistry
from aurora.tools.quality_tools import _register_tools as quality_register_tools
from aurora.tools.competitor_tools import _register_tools as competitor_register_tools
from aurora.instructions.loader import InstructionLoader
from aurora.tools.editor_tools import _register_tools as editor_register_tools
from aurora.tools.defense_tools import _register_tools as defense_register_tools
from aurora.tools.image_tools import _register_tools as image_register_tools
from aurora.tools.visual_tools import _register_tools as visual_register_tools
from aurora.tools.team_tools import _register_tools as team_register_tools
from aurora.tools.export_tools import _register_tools as export_register_tools
from aurora.tools.dachuang_tools import _register_tools as dachuang_register_tools
from aurora.tools.loop_tools import _register_tools as loop_register_tools
from aurora.loop import LoopManager

logger = logging.getLogger(__name__)


class AuroraAgent:
    """Core AuroraAgent implementation."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or load_config()
        self.hooks = HookManager()
        self.tools = ToolRegistry(hooks=self.hooks)
        self.loop_manager = LoopManager(hooks=self.hooks)
        self._register_all_tools()

        self.history = ConversationHistory()
        self.memory = MemoryManager()
        self.session_id: Optional[str] = None

        self._setup_provider()

        self.context_compressor = ContextCompressor(
            compress_threshold=self.config.context.compress_threshold,
            keep_recent=self.config.context.keep_recent,
        )

        # Security and recovery subsystems
        self.guardrails = ToolGuardrails()
        self.security = SecurityManager()
        self.recovery = RecoveryManager()
        self.hooks.register(HookEvent.TOOL_PRE_DISPATCH, self.guardrails.check_hook, priority=10)
        self.hooks.register(HookEvent.TOOL_PRE_DISPATCH, self.security.check_hook, priority=20)
        self.hooks.register(HookEvent.TOOL_ERROR, self.recovery.handle_error_hook, priority=50)

        # Connect LLM client to context compressor for intelligent summarization
        self.context_compressor.llm_client = self.client
        self.context_compressor.model_name = self.model_name

        self.swarm_orchestrator = SwarmOrchestrator(
            run_fn=self.run,
            llm_call_fn=self._call_llm,
            tools_registry=self.tools,
            hooks=self.hooks,
            max_workers=3
        )

    @property
    def messages(self) -> List[Dict[str, str]]:
        """Backward-compatible access to message list."""
        return self.history.get_messages()

    def _register_all_tools(self):
        """Register all tools."""
        comp_register_tools(self.tools)
        bp_register_tools(self.tools)
        eval_register_tools(self.tools)
        pres_register_tools(self.tools)
        web_register_tools(self.tools)
        quality_register_tools(self.tools)
        editor_register_tools(self.tools)
        competitor_register_tools(self.tools)
        defense_register_tools(self.tools)
        image_register_tools(self.tools)
        visual_register_tools(self.tools)
        team_register_tools(self.tools)
        export_register_tools(self.tools)
        dachuang_register_tools(self.tools)
        loop_register_tools(self.tools, loop_manager=self.loop_manager)
        logger.info(f"Registered {len(self.tools.list_tools())} tools")

    def _setup_provider(self):
        """Setup LLM provider."""
        provider_name = self.config.model.provider

        if provider_name == "openai-compat":
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                api_key=self.config.model.api_key,
                base_url=self.config.model.base_url
            )
            self.model_name = self.config.model.name
        elif provider_name == "anthropic":
            try:
                from anthropic import AsyncAnthropic
                self.client = AsyncAnthropic(api_key=self.config.model.api_key)
                self.model_name = "claude-3-sonnet-20240229"
            except ImportError:
                logger.warning("anthropic package not installed, falling back to openai-compat")
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(
                    api_key=self.config.model.api_key,
                    base_url=self.config.model.base_url
                )
                self.model_name = self.config.model.name
        else:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                api_key=self.config.model.api_key,
                base_url=self.config.model.base_url
            )
            self.model_name = self.config.model.name

    def start_session(self, project_info: Dict = None) -> str:
        """Start a new session or auto-generate ID."""
        self.session_id = uuid.uuid4().hex[:12]
        if project_info:
            self.memory.create_or_update_session(self.session_id, project_info)
        else:
            self.memory.create_or_update_session(self.session_id, {})
        return self.session_id

    def load_session(self, session_id: str) -> bool:
        """Load a previous session."""
        data = self.memory.load_session(session_id)
        if not data:
            return False
        self.session_id = session_id
        self.history.clear()

        msgs = self.memory.load_messages(session_id)
        for m in msgs:
            self.history.add(m["role"], m["content"])
        return True

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions."""
        return self.memory.list_sessions()

    async def run(self, user_input: str) -> str:
        """Main entry point for the agent."""
        # Auto-start session if none active
        if not self.session_id:
            self.start_session({"input": user_input})

        self.hooks.emit(HookEvent.AGENT_MESSAGE, {"input": user_input})
        self.history.add("user", user_input)
        self.memory.save_message(self.session_id, "user", user_input)

        if self.swarm_orchestrator.should_trigger(user_input):
            logger.info("Triggering Swarm for complex task")
            result = await self.swarm_orchestrator.run(user_input)
        else:
            result = await self._process_message(user_input)

        self.hooks.emit(HookEvent.AGENT_RESPONSE, {"response": result})
        self.history.add("assistant", result)
        self.memory.save_message(self.session_id, "assistant", result)

        return result

    def edit_message(self, index: int, new_content: str) -> bool:
        """Edit a message and truncate subsequent history."""
        return self.history.edit(index, new_content)

    def undo(self) -> bool:
        """Undo last edit operation."""
        return self.history.undo()

    async def _process_message(self, user_input: str) -> str:
        """Process a single message."""
        messages = self._build_messages()

        tool_schemas = self.tools.get_schemas()

        if tool_schemas:
            response = await self._call_llm(messages, tools=tool_schemas)
        else:
            response = await self._call_llm(messages)

        return response

    def _build_messages(self) -> List[Dict[str, str]]:
        """Build message history for LLM call."""
        system_content = SYSTEM_PROMPT

        # Inject hierarchical instructions
        loader = InstructionLoader()
        instruction_addition = loader.get_system_prompt_addition()
        if instruction_addition:
            system_content += "\n\n" + instruction_addition

        messages = [{"role": "system", "content": system_content}]

        recent = self.history.get_messages()[-self.config.context.keep_recent:]
        messages.extend(recent)

        # Apply context compression
        messages = self.context_compressor.compress(messages, system_content)

        return messages

    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        tool_dispatch=None,
        max_rounds: int = 10,
    ) -> str:
        """Call LLM with multi-round ReAct tool calling support."""
        dispatch_fn = tool_dispatch or self.tools.dispatch
        try:
            for round_idx in range(max_rounds):
                if tools:
                    response = await self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                        max_tokens=4096,
                        temperature=0.7,
                    )
                else:
                    response = await self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        max_tokens=4096,
                        temperature=0.7,
                    )

                message = response.choices[0].message

                if not tools or not message.tool_calls:
                    return self._extract_content(message)

                tool_results = self._execute_tool_calls(message, dispatch_fn)

                messages.append({
                    "role": "assistant",
                    "content": self._extract_content(message) or None,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in message.tool_calls
                    ],
                })
                for tr in tool_results:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tr["tool_call_id"],
                        "content": tr["result"],
                    })

            return self._extract_content(message)
        except Exception as e:
            logger.exception("LLM call failed")
            return f"Error processing request: {str(e)}"

    @staticmethod
    def _extract_content(message) -> str:
        """Extract content from LLM message, handling reasoning_content."""
        content = message.content or ""
        if content.strip():
            return content
        rc = getattr(message, 'reasoning_content', None)
        if rc and rc.strip():
            return rc
        return ""

    async def _handle_tool_call_with_dispatch(self, message, tool_dispatch, original_messages=None) -> str:
        """Compat: handle tool calls with custom dispatch via single synthesis round."""
        tool_results = self._execute_tool_calls(message, tool_dispatch)
        return await self._synthesize_tool_response(message, tool_results, original_messages)

    async def _handle_tool_call(self, message, original_messages=None) -> str:
        """Compat: handle tool calls via single synthesis round."""
        tool_results = self._execute_tool_calls(message, self.tools.dispatch)
        return await self._synthesize_tool_response(message, tool_results, original_messages)

    def _execute_tool_calls(self, message, dispatch_fn) -> List[Dict]:
        """Execute all tool calls and collect results."""
        results = []
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args = {}

            result_str = dispatch_fn(tool_name, args)
            results.append({
                "tool_call_id": tool_call.id,
                "tool_name": tool_name,
                "result": result_str,
            })
        return results

    async def _synthesize_tool_response(self, message, tool_results, original_messages=None) -> str:
        """Send tool results back to LLM for natural language synthesis."""
        try:
            assistant_msg = {"role": "assistant", "content": self._extract_content(message) or None}
            if message.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]

            tool_messages = []
            for tr in tool_results:
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tr["tool_call_id"],
                    "content": tr["result"],
                })

            base_messages = original_messages or self._build_messages()
            synthesis_messages = base_messages + [assistant_msg] + tool_messages

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=synthesis_messages,
                max_tokens=4096,
                temperature=0.7,
            )
            return self._extract_content(response.choices[0].message)

        except Exception as e:
            logger.exception("Tool result synthesis failed")
            return self._fallback_format_results(tool_results)

    def _fallback_format_results(self, tool_results: List[Dict]) -> str:
        """Fallback: format tool results directly if LLM synthesis fails."""
        parts = []
        for tr in tool_results:
            try:
                result_data = json.loads(tr["result"])
                if "error" in result_data:
                    parts.append(f"[{tr['tool_name']}] Error: {result_data['error']}")
                else:
                    parts.append(self._format_tool_result(result_data))
            except json.JSONDecodeError:
                parts.append(tr["result"])
        return "\n\n".join(parts)

    def _format_tool_result(self, result: Dict) -> str:
        """Format tool result for user."""
        if "result" in result:
            output = result["result"]

            if "data" in result:
                data = result["data"]
                if isinstance(data, list):
                    output += "\n\nResults:\n"
                    for i, item in enumerate(data, 1):
                        if isinstance(item, dict):
                            name = item.get("name", item.get("id", f"Item {i}"))
                            desc = item.get("description", item.get("full_name", ""))
                            output += f"{i}. {name}\n"
                            if desc:
                                output += f"   {desc}\n"
                        else:
                            output += f"{i}. {item}\n"

            if "matches" in result:
                matches = result["matches"]
                output += "\n\nRecommended tracks:\n"
                for i, match in enumerate(matches, 1):
                    confidence = match.get("confidence", 0)
                    output += f"{i}. {match.get('track_name', '')} (confidence: {confidence*100:.0f}%)\n"
                    if "reasons" in match:
                        for reason in match["reasons"]:
                            output += f"   - {reason}\n"

            if "suggestions" in result:
                suggestions = result["suggestions"]
                output += "\n\nSuggestions:\n"
                for i, suggestion in enumerate(suggestions, 1):
                    output += f"{i}. {suggestion}\n"

            return output

        return json.dumps(result, ensure_ascii=False, indent=2)

    def clear_history(self):
        """Clear message history."""
        self.history.clear()

    def get_tool_list(self) -> List[str]:
        """Get list of registered tools."""
        return self.tools.list_tools()
