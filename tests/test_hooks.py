"""Tests for Hook system."""

from aurora.hooks import HookEvent, HookManager


class TestHookEvent:
    def test_event_constants_exist(self):
        assert HookEvent.AGENT_START == "agent.start"
        assert HookEvent.AGENT_MESSAGE == "agent.message"
        assert HookEvent.AGENT_RESPONSE == "agent.response"
        assert HookEvent.AGENT_ERROR == "agent.error"
        assert HookEvent.TOOL_PRE_DISPATCH == "tool.pre_dispatch"
        assert HookEvent.TOOL_POST_DISPATCH == "tool.post_dispatch"
        assert HookEvent.TOOL_ERROR == "tool.error"
        assert HookEvent.SWARM_START == "swarm.start"
        assert HookEvent.LOOP_TICK == "loop.tick"
        assert HookEvent.MEMORY_STORE == "memory.store"
        assert HookEvent.CONTEXT_COMPRESS == "context.compress"


class TestHookManager:
    def test_register_and_emit(self):
        hooks = HookManager()
        received = []
        hooks.register("test.event", lambda ctx: received.append(ctx))
        hooks.emit("test.event", {"key": "value"})
        assert len(received) == 1
        assert received[0]["key"] == "value"

    def test_multiple_handlers(self):
        hooks = HookManager()
        order = []
        hooks.register("test.event", lambda ctx: order.append("first"), priority=10)
        hooks.register("test.event", lambda ctx: order.append("second"), priority=50)
        hooks.register("test.event", lambda ctx: order.append("third"), priority=100)
        hooks.emit("test.event")
        assert order == ["first", "second", "third"]

    def test_blocking(self):
        hooks = HookManager()
        calls = []

        def blocker(ctx):
            ctx["blocked"] = True
            ctx["block_reason"] = "test block"
            return ctx

        def should_not_run(ctx):
            calls.append("should_not_run")

        hooks.register("test.event", blocker, priority=10)
        hooks.register("test.event", should_not_run, priority=50)
        result = hooks.emit("test.event")
        assert result["blocked"] is True
        assert result["block_reason"] == "test block"
        assert len(calls) == 0

    def test_handler_modifies_context(self):
        hooks = HookManager()

        def add_field(ctx):
            ctx["added"] = "yes"
            return ctx

        hooks.register("test.event", add_field)
        result = hooks.emit("test.event", {"original": 1})
        assert result["original"] == 1
        assert result["added"] == "yes"

    def test_handler_returns_none(self):
        hooks = HookManager()

        def noop(ctx):
            return None

        hooks.register("test.event", noop)
        result = hooks.emit("test.event", {"key": "value"})
        assert result["key"] == "value"

    def test_handler_exception_does_not_break_chain(self):
        hooks = HookManager()
        calls = []

        def failing(ctx):
            raise ValueError("test error")

        def after_fail(ctx):
            calls.append("after")

        hooks.register("test.event", failing, priority=10)
        hooks.register("test.event", after_fail, priority=50)
        hooks.emit("test.event")
        assert len(calls) == 1

    def test_emit_no_handlers(self):
        hooks = HookManager()
        result = hooks.emit("nonexistent.event", {"key": "value"})
        assert result["key"] == "value"

    def test_emit_no_context(self):
        hooks = HookManager()
        result = hooks.emit("nonexistent.event")
        assert result == {}

    def test_remove_by_name(self):
        hooks = HookManager()
        hooks.register("test.event", lambda ctx: ctx, name="my_handler")
        assert hooks.has_hooks("test.event")
        removed = hooks.remove("test.event", name="my_handler")
        assert removed is True
        assert not hooks.has_hooks("test.event")

    def test_remove_by_handler(self):
        hooks = HookManager()
        handler = lambda ctx: ctx
        hooks.register("test.event", handler)
        removed = hooks.remove("test.event", handler=handler)
        assert removed is True
        assert not hooks.has_hooks("test.event")

    def test_remove_nonexistent(self):
        hooks = HookManager()
        removed = hooks.remove("test.event", name="nope")
        assert removed is False

    def test_remove_all_event(self):
        hooks = HookManager()
        hooks.register("test.event", lambda ctx: ctx)
        hooks.register("test.event", lambda ctx: ctx)
        hooks.remove_all("test.event")
        assert not hooks.has_hooks("test.event")

    def test_remove_all(self):
        hooks = HookManager()
        hooks.register("a", lambda ctx: ctx)
        hooks.register("b", lambda ctx: ctx)
        hooks.remove_all()
        assert not hooks.has_hooks("a")
        assert not hooks.has_hooks("b")

    def test_list_hooks(self):
        hooks = HookManager()
        hooks.register("a", lambda ctx: ctx, name="h1", priority=10)
        hooks.register("a", lambda ctx: ctx, name="h2", priority=50)
        hooks.register("b", lambda ctx: ctx, name="h3")
        listing = hooks.list_hooks()
        assert "a" in listing
        assert "b" in listing
        assert len(listing["a"]) == 2
        assert listing["a"][0]["name"] == "h1"
        assert listing["a"][0]["priority"] == 10

    def test_list_hooks_filtered(self):
        hooks = HookManager()
        hooks.register("a", lambda ctx: ctx, name="h1")
        hooks.register("b", lambda ctx: ctx, name="h2")
        listing = hooks.list_hooks("a")
        assert "a" in listing
        assert "b" not in listing

    def test_has_hooks(self):
        hooks = HookManager()
        assert not hooks.has_hooks("test.event")
        hooks.register("test.event", lambda ctx: ctx)
        assert hooks.has_hooks("test.event")


class TestToolRegistryHookIntegration:
    def test_pre_dispatch_hook_called(self):
        from aurora.tools.registry import ToolRegistry

        hooks = HookManager()
        received = []
        hooks.register(HookEvent.TOOL_PRE_DISPATCH, lambda ctx: received.append(ctx.get("tool")))
        registry = ToolRegistry(hooks=hooks)
        registry.register("test_tool", "A test tool", {"type": "object", "properties": {}}, lambda args: '{"ok": true}')
        registry.dispatch("test_tool", {})
        assert received == ["test_tool"]

    def test_post_dispatch_hook_called(self):
        from aurora.tools.registry import ToolRegistry

        hooks = HookManager()
        received = []
        hooks.register(HookEvent.TOOL_POST_DISPATCH, lambda ctx: received.append(ctx.get("tool")))
        registry = ToolRegistry(hooks=hooks)
        registry.register("test_tool", "A test tool", {"type": "object", "properties": {}}, lambda args: '{"ok": true}')
        registry.dispatch("test_tool", {})
        assert received == ["test_tool"]

    def test_blocked_tool_returns_error(self):
        from aurora.tools.registry import ToolRegistry

        hooks = HookManager()

        def blocker(ctx):
            ctx["blocked"] = True
            ctx["block_reason"] = "rate limited"
            return ctx

        hooks.register(HookEvent.TOOL_PRE_DISPATCH, blocker)
        registry = ToolRegistry(hooks=hooks)
        registry.register("test_tool", "A test tool", {"type": "object", "properties": {}}, lambda args: '{"ok": true}')
        result = registry.dispatch("test_tool", {})
        assert "rate limited" in result

    def test_error_hook_called_on_exception(self):
        import json
        from aurora.tools.registry import ToolRegistry

        hooks = HookManager()
        errors = []
        hooks.register(HookEvent.TOOL_ERROR, lambda ctx: errors.append(ctx.get("tool")))
        registry = ToolRegistry(hooks=hooks)
        registry.register("bad_tool", "A bad tool", {"type": "object", "properties": {}}, lambda args: 1 / 0)
        result = json.loads(registry.dispatch("bad_tool", {}))
        assert "error" in result
        assert errors == ["bad_tool"]
