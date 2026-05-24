"""Tests for the sandbox security system."""

import json
import time

import pytest

from aurora.sandbox.guard import SandboxGuard, SimpleHooks
from aurora.sandbox.policy import SecurityPolicy
from aurora.tools.registry import ToolRegistry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _echo_handler(args):
    """A trivial tool handler that echoes its arguments."""
    return {"echo": args}


def _register_echo(registry: ToolRegistry, name: str = "echo") -> None:
    """Register a simple echo tool."""
    registry.register(
        name=name,
        description="Echo tool",
        parameters={"type": "object", "properties": {"text": {"type": "string"}}},
        handler=_echo_handler,
    )


# ===========================================================================
# SecurityPolicy tests
# ===========================================================================


class TestSecurityPolicy:
    """Tests for SecurityPolicy creation and built-in rules."""

    def test_create_policy(self):
        """Policy should initialize with four built-in rules."""
        policy = SecurityPolicy()
        rules = policy.list_rules()
        assert len(rules) == 4
        names = [r["name"] for r in rules]
        assert "check_input_size" in names
        assert "check_dangerous_patterns" in names
        assert "check_required_params" in names
        assert "check_rate_limit" in names

    def test_add_custom_rule(self):
        """Custom rules can be added and are included in list_rules."""
        policy = SecurityPolicy()
        policy.add_rule("custom_check", lambda t, a: None, severity="warn")
        rules = policy.list_rules()
        assert any(r["name"] == "custom_check" for r in rules)

    def test_list_rules_returns_name_and_severity(self):
        """list_rules should return dicts with name and severity."""
        policy = SecurityPolicy()
        rules = policy.list_rules()
        for rule in rules:
            assert "name" in rule
            assert "severity" in rule
            assert rule["severity"] in ("block", "warn")

    # -- check_input_size ---------------------------------------------------

    def test_input_size_allows_normal_text(self):
        """Normal-sized inputs should pass the size check."""
        policy = SecurityPolicy()
        result = policy.check("echo", {"text": "hello world"})
        assert result["allowed"] is True

    def test_input_size_blocks_oversized_string(self):
        """Strings exceeding 100000 characters should be blocked."""
        policy = SecurityPolicy()
        big_text = "x" * 100_001
        result = policy.check("echo", {"text": big_text})
        assert result["allowed"] is False
        violations = [v for v in result["violations"] if v["rule"] == "check_input_size"]
        assert len(violations) == 1
        assert "exceeds maximum" in violations[0]["reason"]

    def test_input_size_blocks_oversized_list_item(self):
        """List items exceeding the limit should be blocked."""
        policy = SecurityPolicy()
        big_item = "y" * 100_001
        result = policy.check("echo", {"items": [big_item]})
        assert result["allowed"] is False

    def test_input_size_blocks_oversized_nested_dict(self):
        """Nested dict values exceeding the limit should be blocked."""
        policy = SecurityPolicy()
        big_text = "z" * 100_001
        result = policy.check("echo", {"data": {"nested": big_text}})
        assert result["allowed"] is False

    # -- check_dangerous_patterns -------------------------------------------

    def test_dangerous_patterns_blocks_script_tag(self):
        """XSS-style script tags should be blocked."""
        policy = SecurityPolicy()
        result = policy.check("echo", {"text": "<script>alert('xss')</script>"})
        assert result["allowed"] is False
        violations = [v for v in result["violations"] if v["rule"] == "check_dangerous_patterns"]
        assert len(violations) == 1

    def test_dangerous_patterns_blocks_import(self):
        """__import__ should be blocked."""
        policy = SecurityPolicy()
        result = policy.check("echo", {"code": "__import__('os').system('ls')"})
        assert result["allowed"] is False

    def test_dangerous_patterns_blocks_subprocess(self):
        """subprocess should be blocked."""
        policy = SecurityPolicy()
        result = policy.check("echo", {"cmd": "import subprocess; subprocess.run(['rm'])"})
        assert result["allowed"] is False

    def test_dangerous_patterns_blocks_eval(self):
        """eval( should be blocked."""
        policy = SecurityPolicy()
        result = policy.check("echo", {"expr": "eval('1+1')"})
        assert result["allowed"] is False

    def test_dangerous_patterns_blocks_exec(self):
        """exec( should be blocked."""
        policy = SecurityPolicy()
        result = policy.check("echo", {"expr": "exec('print(1)')"})
        assert result["allowed"] is False

    def test_dangerous_patterns_allows_safe_text(self):
        """Normal text without dangerous patterns should pass."""
        policy = SecurityPolicy()
        result = policy.check("echo", {"text": "Hello, this is a safe input."})
        assert result["allowed"] is True

    def test_dangerous_patterns_case_insensitive_script(self):
        """Script tag detection should be case-insensitive."""
        policy = SecurityPolicy()
        result = policy.check("echo", {"text": "<SCRIPT>alert(1)</SCRIPT>"})
        assert result["allowed"] is False

    # -- check_required_params ----------------------------------------------

    def test_required_params_allows_dict_args(self):
        """Dict args should pass the required params check."""
        policy = SecurityPolicy()
        result = policy.check("echo", {"key": "value"})
        param_violations = [
            v for v in result["violations"] if v["rule"] == "check_required_params"
        ]
        assert len(param_violations) == 0

    # -- check_rate_limit ---------------------------------------------------

    def test_rate_limit_allows_normal_usage(self):
        """Calls within the rate limit should be allowed."""
        policy = SecurityPolicy()
        for _ in range(10):
            result = policy.check("echo", {"text": "ok"})
        assert result["allowed"] is True

    def test_rate_limit_blocks_excessive_calls(self):
        """Exceeding 60 calls per minute per tool should be blocked."""
        policy = SecurityPolicy()
        for _ in range(60):
            policy.check("burst_tool", {"text": "ok"})

        result = policy.check("burst_tool", {"text": "one more"})
        assert result["allowed"] is False
        violations = [v for v in result["violations"] if v["rule"] == "check_rate_limit"]
        assert len(violations) == 1
        assert "Rate limit exceeded" in violations[0]["reason"]

    def test_rate_limit_per_tool_isolation(self):
        """Rate limits should be independent per tool."""
        policy = SecurityPolicy()
        for _ in range(60):
            policy.check("tool_a", {"text": "ok"})

        result_a = policy.check("tool_a", {"text": "ok"})
        result_b = policy.check("tool_b", {"text": "ok"})
        assert result_a["allowed"] is False
        assert result_b["allowed"] is True

    # -- combined policy check ----------------------------------------------

    def test_policy_allows_valid_call(self):
        """A valid tool call should be allowed with no violations."""
        policy = SecurityPolicy()
        result = policy.check("echo", {"text": "Hello world"})
        assert result["allowed"] is True
        assert len(result["violations"]) == 0

    def test_policy_blocks_with_all_violations_reported(self):
        """All violated rules should be reported even when blocked."""
        policy = SecurityPolicy()
        big_dangerous = "x" * 100_001 + "<script>"
        result = policy.check("echo", {"text": big_dangerous})
        assert result["allowed"] is False
        assert len(result["violations"]) >= 2


# ===========================================================================
# SimpleHooks tests
# ===========================================================================


class TestSimpleHooks:
    """Tests for SimpleHooks event system."""

    def test_emit_no_handlers(self):
        """Emitting with no handlers should return the data dict unchanged."""
        hooks = SimpleHooks()
        result = hooks.emit("test.event", {"key": "value"})
        assert result == {"key": "value"}

    def test_on_and_emit(self):
        """Handlers should receive and can mutate the data dict."""
        hooks = SimpleHooks()
        received = []

        def handler(data):
            received.append(dict(data))
            data["modified"] = True

        hooks.on("test.event", handler)
        result = hooks.emit("test.event", {"key": "value"})

        assert len(received) == 1
        assert received[0] == {"key": "value"}
        assert result["modified"] is True

    def test_multiple_handlers(self):
        """Multiple handlers run in registration order."""
        hooks = SimpleHooks()
        order = []

        def handler_a(data):
            order.append("a")

        def handler_b(data):
            order.append("b")

        hooks.on("test.event", handler_a)
        hooks.on("test.event", handler_b)
        hooks.emit("test.event", {})

        assert order == ["a", "b"]

    def test_emit_returns_copy(self):
        """emit should return a copy, not the original data."""
        hooks = SimpleHooks()
        original = {"key": "value"}
        result = hooks.emit("test.event", original)
        assert result is not original
        assert result == original


# ===========================================================================
# SandboxGuard tests
# ===========================================================================


class TestSandboxGuard:
    """Tests for SandboxGuard integration."""

    def test_guard_creates_default_policy(self):
        """Guard should create a default SecurityPolicy if none is provided."""
        guard = SandboxGuard()
        assert guard.policy is not None
        assert isinstance(guard.policy, SecurityPolicy)

    def test_guard_uses_custom_policy(self):
        """Guard should use a provided SecurityPolicy."""
        policy = SecurityPolicy()
        guard = SandboxGuard(policy=policy)
        assert guard.policy is policy

    def test_get_hooks_returns_simple_hooks(self):
        """get_hooks should return a SimpleHooks instance."""
        guard = SandboxGuard()
        hooks = guard.get_hooks()
        assert isinstance(hooks, SimpleHooks)

    # -- integration with ToolRegistry --------------------------------------

    def test_guard_allows_safe_call_through_registry(self):
        """Safe tool calls should execute normally through the registry."""
        registry = ToolRegistry()
        guard = SandboxGuard()
        registry.set_hooks(guard.get_hooks())
        _register_echo(registry)

        result = json.loads(registry.dispatch("echo", {"text": "hello"}))
        assert "echo" in result
        assert result["echo"]["text"] == "hello"

    def test_guard_blocks_dangerous_call_through_registry(self):
        """Dangerous tool calls should be blocked through the registry."""
        registry = ToolRegistry()
        guard = SandboxGuard()
        registry.set_hooks(guard.get_hooks())
        _register_echo(registry)

        result = json.loads(
            registry.dispatch("echo", {"text": "<script>alert('xss')</script>"})
        )
        assert "error" in result
        assert "dangerous pattern" in result["error"]

    def test_guard_blocks_unknown_tool_normally(self):
        """Unknown tools should still return the normal error message."""
        registry = ToolRegistry()
        guard = SandboxGuard()
        registry.set_hooks(guard.get_hooks())

        result = json.loads(registry.dispatch("nonexistent", {}))
        assert "error" in result
        assert "Unknown tool" in result["error"]

    def test_guard_prevents_execution_on_block(self):
        """When blocked, the tool handler should never be called."""
        call_count = 0

        def counting_handler(args):
            nonlocal call_count
            call_count += 1
            return {"count": call_count}

        registry = ToolRegistry()
        guard = SandboxGuard()
        registry.set_hooks(guard.get_hooks())
        registry.register(
            name="counter",
            description="Counting tool",
            parameters={"type": "object", "properties": {}},
            handler=counting_handler,
        )

        # Safe call
        registry.dispatch("counter", {"text": "safe"})
        assert call_count == 1

        # Blocked call - handler should not run
        registry.dispatch("counter", {"text": "<script>bad</script>"})
        assert call_count == 1

    def test_guard_blocks_eval_injection(self):
        """eval() injection attempts should be blocked."""
        registry = ToolRegistry()
        guard = SandboxGuard()
        registry.set_hooks(guard.get_hooks())
        _register_echo(registry)

        result = json.loads(
            registry.dispatch("echo", {"text": "eval('malicious')"})
        )
        assert "error" in result

    def test_guard_blocks_exec_injection(self):
        """exec() injection attempts should be blocked."""
        registry = ToolRegistry()
        guard = SandboxGuard()
        registry.set_hooks(guard.get_hooks())
        _register_echo(registry)

        result = json.loads(
            registry.dispatch("echo", {"text": "exec('malicious')"})
        )
        assert "error" in result

    def test_guard_blocks_oversized_input_through_registry(self):
        """Oversized inputs should be blocked through the registry."""
        registry = ToolRegistry()
        guard = SandboxGuard()
        registry.set_hooks(guard.get_hooks())
        _register_echo(registry)

        big_text = "A" * 100_001
        result = json.loads(registry.dispatch("echo", {"text": big_text}))
        assert "error" in result
        assert "exceeds maximum" in result["error"]

    def test_guard_without_hooks(self):
        """Registry without hooks should work normally (no guard)."""
        registry = ToolRegistry()
        _register_echo(registry)

        result = json.loads(
            registry.dispatch("echo", {"text": "<script>anything</script>"})
        )
        # No guard, so it goes through
        assert "echo" in result

    def test_multiple_safe_calls_through_guard(self):
        """Multiple safe calls should all succeed."""
        registry = ToolRegistry()
        guard = SandboxGuard()
        registry.set_hooks(guard.get_hooks())
        _register_echo(registry)

        for i in range(5):
            result = json.loads(
                registry.dispatch("echo", {"text": f"safe call {i}"})
            )
            assert result["echo"]["text"] == f"safe call {i}"
