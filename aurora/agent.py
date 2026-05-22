"""Core agent for AuroraAgent."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from aurora.config import Config, load_config
from aurora.prompts.system import SYSTEM_PROMPT
from aurora.swarm.orchestrator import SwarmOrchestrator
from aurora.tools.business_plan_tools import _register_tools as bp_register_tools
from aurora.tools.competition_tools import _register_tools as comp_register_tools
from aurora.tools.evaluation_tools import _register_tools as eval_register_tools
from aurora.tools.presentation_tools import _register_tools as pres_register_tools
from aurora.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class AuroraAgent:
    """Core AuroraAgent implementation."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or load_config()
        self.tools = ToolRegistry()
        self._register_all_tools()
        
        self.messages: List[Dict[str, str]] = []
        self._setup_provider()
        
        self.swarm_orchestrator = SwarmOrchestrator(
            run_fn=self.run,
            llm_call_fn=self._call_llm,
            tools_registry=self.tools,
            hooks=None,
            max_workers=3
        )

    def _register_all_tools(self):
        """Register all tools."""
        comp_register_tools(self.tools)
        bp_register_tools(self.tools)
        eval_register_tools(self.tools)
        pres_register_tools(self.tools)
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

    async def run(self, user_input: str) -> str:
        """Main entry point for the agent."""
        self.messages.append({"role": "user", "content": user_input})
        
        if self.swarm_orchestrator.should_trigger(user_input):
            logger.info("Triggering Swarm for complex task")
            result = await self.swarm_orchestrator.run(user_input)
        else:
            result = await self._process_message(user_input)
        
        self.messages.append({"role": "assistant", "content": result})
        
        return result

    async def _process_message(self, user_input: str) -> str:
        """Process a single message."""
        messages = self._build_messages()
        
        tool_schemas = self.tools.get_schemas()
        
        if tool_schemas:
            response = await self._call_llm_with_tools(messages, tool_schemas)
        else:
            response = await self._call_llm(messages)
        
        return response

    def _build_messages(self) -> List[Dict[str, str]]:
        """Build message history for LLM call."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        recent_messages = self.messages[-self.config.context.keep_recent:]
        messages.extend(recent_messages)
        
        return messages

    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        tool_dispatch=None
    ) -> str:
        """Call LLM with optional tool support."""
        try:
            # If tools are provided, use tool-enabled call
            if tools:
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    max_tokens=4096,
                    temperature=0.7
                )
                
                message = response.choices[0].message
                
                if message.tool_calls:
                    # If custom tool_dispatch is provided (from Swarm), use it
                    if tool_dispatch:
                        return await self._handle_tool_call_with_dispatch(message, tool_dispatch)
                    else:
                        return await self._handle_tool_call(message)
                else:
                    return message.content or ""
            else:
                # Simple call without tools
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=4096,
                    temperature=0.7
                )
                return response.choices[0].message.content or ""
        except Exception as e:
            logger.exception("LLM call failed")
            return f"很抱歉，处理您的请求时出现错误：{str(e)}"

    async def _handle_tool_call_with_dispatch(self, message, tool_dispatch) -> str:
        """Handle tool calls with custom dispatch function."""
        results = []
        
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args = {}
            
            # Use the custom dispatch function (from FilteredToolRegistry)
            result = tool_dispatch(tool_name, args)
            results.append(result)
        
        if len(results) == 1:
            try:
                result_data = json.loads(results[0])
                if "error" in result_data:
                    return f"工具调用失败：{result_data['error']}"
                return self._format_tool_result(result_data)
            except json.JSONDecodeError:
                return results[0]
        else:
            return "\n\n".join(results)

    async def _call_llm_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> str:
        """Call LLM with tool support."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=4096,
                temperature=0.7
            )
            
            message = response.choices[0].message
            
            if message.tool_calls:
                return await self._handle_tool_call(message)
            else:
                return message.content or ""
        except Exception as e:
            logger.exception("LLM call with tools failed")
            return f"很抱歉，处理您的请求时出现错误：{str(e)}"

    async def _handle_tool_call(self, message) -> str:
        """Handle tool calls from LLM."""
        results = []
        
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args = {}
            
            result = self.tools.dispatch(tool_name, args)
            results.append(result)
        
        if len(results) == 1:
            try:
                result_data = json.loads(results[0])
                if "error" in result_data:
                    return f"工具调用失败：{result_data['error']}"
                
                return self._format_tool_result(result_data)
            except json.JSONDecodeError:
                return results[0]
        else:
            return "\n\n".join(results)

    def _format_tool_result(self, result: Dict) -> str:
        """Format tool result for user."""
        if "result" in result:
            output = result["result"]
            
            if "data" in result:
                data = result["data"]
                if isinstance(data, list):
                    output += "\n\n匹配结果：\n"
                    for i, item in enumerate(data, 1):
                        if isinstance(item, dict):
                            name = item.get("name", item.get("id", f"项目{i}"))
                            desc = item.get("description", item.get("full_name", ""))
                            output += f"{i}. {name}\n"
                            if desc:
                                output += f"   {desc}\n"
                        else:
                            output += f"{i}. {item}\n"
            
            if "matches" in result:
                matches = result["matches"]
                output += "\n\n推荐赛道：\n"
                for i, match in enumerate(matches, 1):
                    confidence = match.get("confidence", 0)
                    output += f"{i}. {match.get('track_name', '')} (匹配度: {confidence*100:.0f}%)\n"
                    if "reasons" in match:
                        for reason in match["reasons"]:
                            output += f"   - {reason}\n"
            
            if "suggestions" in result:
                suggestions = result["suggestions"]
                output += "\n\n优化建议：\n"
                for i, suggestion in enumerate(suggestions, 1):
                    output += f"{i}. {suggestion}\n"
            
            return output
        
        return json.dumps(result, ensure_ascii=False, indent=2)

    def clear_history(self):
        """Clear message history."""
        self.messages = []

    def get_tool_list(self) -> List[str]:
        """Get list of registered tools."""
        return self.tools.list_tools()
