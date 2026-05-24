"""MCP (Model Context Protocol) server wrapping AuroraAgent's tool registry.

Implements a basic JSON-RPC 2.0 server that exposes registered tools
through the MCP protocol, supporting initialize, ping, tools/list, and
tools/call methods.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from aurora.mcp.config import MCPServerConfig, load_mcp_config
from aurora.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class MCPServer:
    """Simple MCP protocol server wrapping AuroraAgent's tool registry."""

    def __init__(
        self,
        tools_registry: Optional[ToolRegistry] = None,
        config: Optional[MCPServerConfig] = None,
    ):
        self._registry = tools_registry
        self._config = config or load_mcp_config()

    def handle_request(self, request: dict) -> dict:
        """Handle an MCP JSON-RPC request.

        Args:
            request: A JSON-RPC 2.0 request dict with method, params, and id.

        Returns:
            A JSON-RPC 2.0 response dict.
        """
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            return self._initialize(request_id)
        elif method == "ping":
            return self._make_result(request_id, {"status": "ok"})
        elif method == "tools/list":
            return self._list_tools(request_id)
        elif method == "tools/call":
            return self._call_tool(request_id, params)
        else:
            return self._make_error(
                request_id, -32601, f"Method not found: {method}"
            )

    def _initialize(self, request_id) -> dict:
        """Handle initialize request."""
        return self._make_result(
            request_id,
            {
                "protocolVersion": self._config.protocol_version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {
                    "name": self._config.name,
                    "version": self._config.version,
                },
            },
        )

    def _list_tools(self, request_id) -> dict:
        """List available tools in MCP format."""
        if not self._registry:
            return self._make_result(request_id, {"tools": []})

        schemas = self._registry.get_schemas()
        tools = []
        for schema in schemas:
            func = schema.get("function", {})
            tool_name = func.get("name", "")

            if self._is_tool_disabled(tool_name):
                continue

            tools.append(
                {
                    "name": tool_name,
                    "description": func.get("description", ""),
                    "inputSchema": func.get("parameters", {}),
                }
            )
        return self._make_result(request_id, {"tools": tools})

    def _call_tool(self, request_id, params) -> dict:
        """Call a tool via MCP."""
        if not self._registry:
            return self._make_error(request_id, -32000, "No registry configured")

        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if self._is_tool_disabled(tool_name):
            return self._make_error(request_id, -32603, f"Tool disabled: {tool_name}")

        result_str = self._registry.dispatch(tool_name, arguments)
        try:
            result_data = json.loads(result_str)
        except (json.JSONDecodeError, TypeError):
            result_data = {"result": result_str}

        return self._make_result(
            request_id,
            {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result_data, ensure_ascii=False),
                    }
                ]
            },
        )

    def _is_tool_disabled(self, tool_name: str) -> bool:
        """Check if a tool is disabled by configuration."""
        if self._config.disabled_tools and tool_name in self._config.disabled_tools:
            return True
        if self._config.enabled_tools and tool_name not in self._config.enabled_tools:
            return True
        return False

    @staticmethod
    def _make_result(request_id, result) -> dict:
        """Build a JSON-RPC 2.0 success response."""
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    @staticmethod
    def _make_error(request_id, code: int, message: str) -> dict:
        """Build a JSON-RPC 2.0 error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }
