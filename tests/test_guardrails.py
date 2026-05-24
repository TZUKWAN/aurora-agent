"""Tests for tool guardrails."""

from aurora.guardrails import ToolGuardrails


class TestToolGuardrails:
    def test_allow_normal_call(self):
        g = ToolGuardrails()
        allowed, reason = g.check("bp_generate")
        assert allowed is True
        assert reason == ""

    def test_block_consecutive_limit(self):
        g = ToolGuardrails(consecutive_limits={"my_tool": 3}, default_consecutive=10)
        for _ in range(3):
            g.record("my_tool")
        allowed, reason = g.check("my_tool")
        assert allowed is False
        assert "连续调用超过3次" in reason

    def test_different_tool_resets_consecutive(self):
        g = ToolGuardrails(consecutive_limits={"a": 2, "b": 2})
        g.record("a")
        g.record("a")
        # Switch to different tool
        allowed, reason = g.check("b")
        assert allowed is True

    def test_default_consecutive_limit(self):
        g = ToolGuardrails(default_consecutive=3)
        for _ in range(3):
            g.record("tool_x")
        allowed, reason = g.check("tool_x")
        assert allowed is False

    def test_rate_limit(self):
        g = ToolGuardrails(rate_limits={"fast_tool": 3}, default_rate=100)
        for _ in range(3):
            g.record("fast_tool")
        allowed, reason = g.check("fast_tool")
        assert allowed is False
        assert "每分钟调用超过3次" in reason

    def test_check_hook_allows(self):
        g = ToolGuardrails()
        ctx = {"tool": "bp_generate", "args": {}}
        result = g.check_hook(ctx)
        assert not result.get("blocked")

    def test_check_hook_blocks(self):
        g = ToolGuardrails(consecutive_limits={"limited": 1})
        g.record("limited")
        ctx = {"tool": "limited", "args": {}}
        result = g.check_hook(ctx)
        assert result["blocked"] is True

    def test_reset(self):
        g = ToolGuardrails(consecutive_limits={"x": 1})
        g.record("x")
        g.reset()
        allowed, _ = g.check("x")
        assert allowed is True
