"""MCP Server for AuroraAgent.

Exposes Aurora tools via stdio-based JSON-RPC MCP protocol.
Allows external tools (Claude Code, Codex) to call Aurora capabilities.
"""

import json
import logging
import sys
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AuroraMCPServer:
    """Lightweight MCP server exposing Aurora tools via stdio JSON-RPC."""

    def __init__(self, agent=None):
        self.agent = agent
        self._tools_cache = None

    def _get_tools(self) -> List[Dict[str, Any]]:
        """Get tool schemas from agent registry."""
        if self._tools_cache is not None:
            return self._tools_cache
        if self.agent:
            self._tools_cache = self.agent.tools.get_schemas()
        return self._tools_cache or []

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle a single JSON-RPC request."""
        method = request.get("method", "")
        req_id = request.get("id")
        params = request.get("params", {})

        handler = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "ping": self._handle_ping,
        }.get(method)

        if handler:
            try:
                result = handler(params)
                if req_id is not None:
                    return {"jsonrpc": "2.0", "id": req_id, "result": result}
            except Exception as e:
                logger.error("MCP handler error for %s: %s", method, e)
                if req_id is not None:
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32000, "message": str(e)},
                    }
        elif method == "notifications/initialized":
            return None
        else:
            if req_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
        return None

    def _handle_initialize(self, params: Dict) -> Dict:
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": False},
            },
            "serverInfo": {
                "name": "aurora-agent",
                "version": "1.0.0",
            },
        }

    def _handle_tools_list(self, params: Dict) -> Dict:
        tools = self._get_tools()
        mcp_tools = []
        for t in tools:
            func = t.get("function", {})
            mcp_tools.append({
                "name": func.get("name", ""),
                "description": func.get("description", ""),
                "inputSchema": func.get("parameters", {"type": "object", "properties": {}}),
            })
        return {"tools": mcp_tools}

    def _handle_tools_call(self, params: Dict) -> Dict:
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if not self.agent:
            return {
                "content": [{"type": "text", "text": json.dumps({"error": "Agent not initialized"})}],
                "isError": True,
            }

        result_str = self.agent.tools.dispatch(tool_name, arguments)

        return {
            "content": [{"type": "text", "text": result_str}],
            "isError": False,
        }

    def _handle_ping(self, params: Dict) -> Dict:
        return {}

    def run(self):
        """Run the MCP server, reading from stdin and writing to stdout."""
        logger.info("Aurora MCP server starting on stdio")

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                continue

            response = self.handle_request(request)
            if response:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()


def create_mcp_server(config=None):
    """Factory to create an MCP server with an initialized agent."""
    from aurora.agent import AuroraAgent
    agent = AuroraAgent(config=config)
    return AuroraMCPServer(agent=agent)
