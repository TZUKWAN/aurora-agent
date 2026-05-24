"""Tests for MCP server."""

import json

from aurora.mcp_server import AuroraMCPServer


class TestMCPServer:
    def test_initialize(self):
        server = AuroraMCPServer()
        resp = server.handle_request({
            "jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {},
        })
        assert resp["id"] == 1
        assert resp["result"]["protocolVersion"] == "2024-11-05"
        assert resp["result"]["serverInfo"]["name"] == "aurora-agent"

    def test_ping(self):
        server = AuroraMCPServer()
        resp = server.handle_request({
            "jsonrpc": "2.0", "id": 2, "method": "ping", "params": {},
        })
        assert resp["result"] == {}

    def test_tools_list_no_agent(self):
        server = AuroraMCPServer()
        resp = server.handle_request({
            "jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {},
        })
        assert resp["result"]["tools"] == []

    def test_tools_list_with_agent(self):
        from aurora.agent import AuroraAgent
        agent = AuroraAgent()
        server = AuroraMCPServer(agent=agent)
        resp = server.handle_request({
            "jsonrpc": "2.0", "id": 4, "method": "tools/list", "params": {},
        })
        tools = resp["result"]["tools"]
        assert len(tools) > 0
        tool_names = [t["name"] for t in tools]
        assert "bp_generate" in tool_names

    def test_tools_call_no_agent(self):
        server = AuroraMCPServer()
        resp = server.handle_request({
            "jsonrpc": "2.0", "id": 5, "method": "tools/call",
            "params": {"name": "bp_generate", "arguments": {}},
        })
        assert resp["result"]["isError"] is True

    def test_tools_call_with_agent(self):
        from aurora.agent import AuroraAgent
        agent = AuroraAgent()
        server = AuroraMCPServer(agent=agent)
        resp = server.handle_request({
            "jsonrpc": "2.0", "id": 6, "method": "tools/call",
            "params": {"name": "dachuang_generate_budget", "arguments": {"total_amount": 10000, "project_type": "innovation"}},
        })
        content = resp["result"]["content"][0]["text"]
        data = json.loads(content)
        assert "items" in data

    def test_method_not_found(self):
        server = AuroraMCPServer()
        resp = server.handle_request({
            "jsonrpc": "2.0", "id": 7, "method": "nonexistent", "params": {},
        })
        assert "error" in resp
        assert resp["error"]["code"] == -32601

    def test_notification_no_response(self):
        server = AuroraMCPServer()
        resp = server.handle_request({
            "jsonrpc": "2.0", "method": "notifications/initialized", "params": {},
        })
        assert resp is None
