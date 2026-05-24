"""Tests for MCP (Model Context Protocol) support."""

import json
import os

import pytest

from aurora.mcp.client import MCPServer
from aurora.mcp.config import MCPServerConfig, load_mcp_config
from aurora.tools.registry import ToolRegistry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_registry_with_tools() -> ToolRegistry:
    """Create a ToolRegistry with sample tools for testing."""
    registry = ToolRegistry()
    registry.register(
        name="add_numbers",
        description="Add two numbers together",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"},
            },
            "required": ["a", "b"],
        },
        handler=lambda args: {"result": args["a"] + args["b"]},
    )
    registry.register(
        name="echo",
        description="Echo back the input text",
        parameters={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to echo"},
            },
            "required": ["text"],
        },
        handler=lambda args: {"echo": args["text"]},
    )
    registry.register(
        name="fail_tool",
        description="A tool that always raises an exception",
        parameters={"type": "object", "properties": {}},
        handler=lambda args: (_ for _ in ()).throw(RuntimeError("deliberate failure")),
    )
    return registry


# ---------------------------------------------------------------------------
# MCPServerConfig tests
# ---------------------------------------------------------------------------


class TestMCPServerConfig:
    """Tests for MCPServerConfig dataclass."""

    def test_default_config(self):
        config = MCPServerConfig()
        assert config.name == "aurora-agent"
        assert config.version == "1.0.0"
        assert config.protocol_version == "2024-11-05"
        assert config.enabled_tools == []
        assert config.disabled_tools == []

    def test_custom_config(self):
        config = MCPServerConfig(
            name="custom-server",
            version="2.0.0",
            protocol_version="2025-01-01",
            enabled_tools=["tool_a"],
            disabled_tools=["tool_b"],
        )
        assert config.name == "custom-server"
        assert config.version == "2.0.0"
        assert config.protocol_version == "2025-01-01"
        assert config.enabled_tools == ["tool_a"]
        assert config.disabled_tools == ["tool_b"]


class TestLoadMCPConfig:
    """Tests for load_mcp_config function."""

    def test_load_defaults(self):
        config = load_mcp_config()
        assert isinstance(config, MCPServerConfig)
        assert config.name == "aurora-agent"

    def test_load_with_disabled_tools_env(self, monkeypatch):
        monkeypatch.setenv("AURORA_MCP_DISABLED_TOOLS", "tool_x, tool_y, tool_z")
        config = load_mcp_config()
        assert config.disabled_tools == ["tool_x", "tool_y", "tool_z"]

    def test_load_with_empty_disabled_tools_env(self, monkeypatch):
        monkeypatch.setenv("AURORA_MCP_DISABLED_TOOLS", "")
        config = load_mcp_config()
        assert config.disabled_tools == []

    def test_load_with_whitespace_only_env(self, monkeypatch):
        monkeypatch.setenv("AURORA_MCP_DISABLED_TOOLS", "  ,  ,  ")
        config = load_mcp_config()
        assert config.disabled_tools == []


# ---------------------------------------------------------------------------
# MCPServer tests -- no registry
# ---------------------------------------------------------------------------


class TestMCPServerNoRegistry:
    """Tests for MCPServer when no registry is provided."""

    def setup_method(self):
        self.server = MCPServer()

    def test_initialize(self):
        request = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
        response = self.server.handle_request(request)
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        result = response["result"]
        assert result["protocolVersion"] == "2024-11-05"
        assert result["serverInfo"]["name"] == "aurora-agent"
        assert result["capabilities"]["tools"]["listChanged"] is False

    def test_ping(self):
        request = {"jsonrpc": "2.0", "id": 2, "method": "ping"}
        response = self.server.handle_request(request)
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        assert response["result"] == {"status": "ok"}

    def test_list_tools_empty(self):
        request = {"jsonrpc": "2.0", "id": 3, "method": "tools/list"}
        response = self.server.handle_request(request)
        assert response["result"]["tools"] == []

    def test_call_tool_no_registry_error(self):
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "whatever", "arguments": {}},
        }
        response = self.server.handle_request(request)
        assert "error" in response
        assert response["error"]["code"] == -32000
        assert "No registry" in response["error"]["message"]

    def test_unknown_method(self):
        request = {"jsonrpc": "2.0", "id": 5, "method": "nonexistent/method"}
        response = self.server.handle_request(request)
        assert "error" in response
        assert response["error"]["code"] == -32601
        assert "Method not found" in response["error"]["message"]

    def test_missing_method_defaults_to_error(self):
        request = {"jsonrpc": "2.0", "id": 6}
        response = self.server.handle_request(request)
        assert "error" in response
        assert response["error"]["code"] == -32601

    def test_null_request_id(self):
        request = {"jsonrpc": "2.0", "id": None, "method": "ping"}
        response = self.server.handle_request(request)
        assert response["id"] is None
        assert response["result"] == {"status": "ok"}


# ---------------------------------------------------------------------------
# MCPServer tests -- with registry
# ---------------------------------------------------------------------------


class TestMCPServerWithRegistry:
    """Tests for MCPServer with a real ToolRegistry."""

    def setup_method(self):
        self.registry = _make_registry_with_tools()
        self.server = MCPServer(tools_registry=self.registry)

    def test_list_tools_returns_registered_tools(self):
        request = {"jsonrpc": "2.0", "id": 10, "method": "tools/list"}
        response = self.server.handle_request(request)
        tools = response["result"]["tools"]
        assert len(tools) == 3
        names = [t["name"] for t in tools]
        assert "add_numbers" in names
        assert "echo" in names
        assert "fail_tool" in names

    def test_tool_schema_format(self):
        request = {"jsonrpc": "2.0", "id": 11, "method": "tools/list"}
        response = self.server.handle_request(request)
        tools = response["result"]["tools"]
        add_tool = next(t for t in tools if t["name"] == "add_numbers")
        assert add_tool["description"] == "Add two numbers together"
        assert add_tool["inputSchema"]["type"] == "object"
        assert "a" in add_tool["inputSchema"]["properties"]
        assert "b" in add_tool["inputSchema"]["properties"]
        assert add_tool["inputSchema"]["required"] == ["a", "b"]

    def test_call_tool_add_numbers(self):
        request = {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {
                "name": "add_numbers",
                "arguments": {"a": 3, "b": 7},
            },
        }
        response = self.server.handle_request(request)
        assert "result" in response
        content = response["result"]["content"]
        assert len(content) == 1
        assert content[0]["type"] == "text"
        parsed = json.loads(content[0]["text"])
        assert parsed["result"] == 10

    def test_call_tool_echo(self):
        request = {
            "jsonrpc": "2.0",
            "id": 13,
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {"text": "hello world"},
            },
        }
        response = self.server.handle_request(request)
        content = response["result"]["content"]
        parsed = json.loads(content[0]["text"])
        assert parsed["echo"] == "hello world"

    def test_call_unknown_tool(self):
        request = {
            "jsonrpc": "2.0",
            "id": 14,
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {},
            },
        }
        response = self.server.handle_request(request)
        # Registry returns error JSON, MCP wraps it as content
        content = response["result"]["content"]
        parsed = json.loads(content[0]["text"])
        assert "error" in parsed
        assert "Unknown tool" in parsed["error"]

    def test_call_failing_tool(self):
        request = {
            "jsonrpc": "2.0",
            "id": 15,
            "method": "tools/call",
            "params": {
                "name": "fail_tool",
                "arguments": {},
            },
        }
        response = self.server.handle_request(request)
        content = response["result"]["content"]
        parsed = json.loads(content[0]["text"])
        assert "error" in parsed

    def test_call_tool_with_empty_arguments(self):
        request = {
            "jsonrpc": "2.0",
            "id": 16,
            "method": "tools/call",
            "params": {"name": "echo"},  # no arguments key
        }
        response = self.server.handle_request(request)
        content = response["result"]["content"]
        parsed = json.loads(content[0]["text"])
        assert "error" in parsed  # missing required 'text' param

    def test_response_has_jsonrpc_version(self):
        request = {"jsonrpc": "2.0", "id": 17, "method": "initialize"}
        response = self.server.handle_request(request)
        assert response["jsonrpc"] == "2.0"


# ---------------------------------------------------------------------------
# MCPServer tests -- config-based filtering
# ---------------------------------------------------------------------------


class TestMCPServerConfigFiltering:
    """Tests for tool filtering via MCPServerConfig."""

    def test_disabled_tools_excluded_from_list(self):
        registry = _make_registry_with_tools()
        config = MCPServerConfig(disabled_tools=["fail_tool"])
        server = MCPServer(tools_registry=registry, config=config)

        request = {"jsonrpc": "2.0", "id": 20, "method": "tools/list"}
        response = server.handle_request(request)
        tools = response["result"]["tools"]
        names = [t["name"] for t in tools]
        assert "fail_tool" not in names
        assert "add_numbers" in names
        assert "echo" in names

    def test_disabled_tools_blocked_on_call(self):
        registry = _make_registry_with_tools()
        config = MCPServerConfig(disabled_tools=["echo"])
        server = MCPServer(tools_registry=registry, config=config)

        request = {
            "jsonrpc": "2.0",
            "id": 21,
            "method": "tools/call",
            "params": {"name": "echo", "arguments": {"text": "hi"}},
        }
        response = server.handle_request(request)
        assert "error" in response
        assert "disabled" in response["error"]["message"].lower()

    def test_enabled_tools_whitelist(self):
        registry = _make_registry_with_tools()
        config = MCPServerConfig(enabled_tools=["add_numbers"])
        server = MCPServer(tools_registry=registry, config=config)

        request = {"jsonrpc": "2.0", "id": 22, "method": "tools/list"}
        response = server.handle_request(request)
        tools = response["result"]["tools"]
        assert len(tools) == 1
        assert tools[0]["name"] == "add_numbers"

    def test_enabled_and_disabled_both_set(self):
        """When both enabled and disabled lists are set, disabled takes
        precedence for listing, and enabled acts as whitelist."""
        registry = _make_registry_with_tools()
        config = MCPServerConfig(enabled_tools=["add_numbers", "echo"], disabled_tools=["echo"])
        server = MCPServer(tools_registry=registry, config=config)

        request = {"jsonrpc": "2.0", "id": 23, "method": "tools/list"}
        response = server.handle_request(request)
        tools = response["result"]["tools"]
        names = [t["name"] for t in tools]
        assert "add_numbers" in names
        assert "echo" not in names


# ---------------------------------------------------------------------------
# Integration: full round-trip with ToolRegistry
# ---------------------------------------------------------------------------


class TestMCPIntegration:
    """Integration tests verifying MCP wrapping a real ToolRegistry end-to-end."""

    def test_full_workflow(self):
        """Register tools, list them, call one, verify the result."""
        registry = ToolRegistry()
        registry.register(
            name="multiply",
            description="Multiply two numbers",
            parameters={
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                },
                "required": ["x", "y"],
            },
            handler=lambda args: {"product": args["x"] * args["y"]},
        )

        server = MCPServer(tools_registry=registry)

        # Step 1: initialize
        init_resp = server.handle_request(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
        )
        assert init_resp["result"]["serverInfo"]["name"] == "aurora-agent"

        # Step 2: list tools
        list_resp = server.handle_request(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
        )
        tools = list_resp["result"]["tools"]
        assert len(tools) == 1
        assert tools[0]["name"] == "multiply"

        # Step 3: call tool
        call_resp = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "multiply", "arguments": {"x": 6, "y": 7}},
            }
        )
        content = call_resp["result"]["content"]
        parsed = json.loads(content[0]["text"])
        assert parsed["product"] == 42

    def test_tool_returning_string(self):
        """Verify a tool that returns a plain string (not JSON) is handled."""
        registry = ToolRegistry()
        registry.register(
            name="greet",
            description="Return a greeting",
            parameters={"type": "object", "properties": {}},
            handler=lambda args: "Hello!",
        )

        server = MCPServer(tools_registry=registry)
        resp = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "greet", "arguments": {}},
            }
        )
        content = resp["result"]["content"]
        parsed = json.loads(content[0]["text"])
        # Non-JSON string from handler gets wrapped in {"result": ...} by MCP layer
        assert parsed == {"result": "Hello!"}

    def test_unicode_handling(self):
        """Verify unicode content passes through correctly."""
        registry = ToolRegistry()
        registry.register(
            name="unicode_echo",
            description="Echo unicode text",
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
            handler=lambda args: {"text": args["text"]},
        )

        server = MCPServer(tools_registry=registry)
        resp = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "unicode_echo", "arguments": {"text": "中文测试"}},
            }
        )
        content = resp["result"]["content"]
        text = content[0]["text"]
        assert "中文测试" in text
