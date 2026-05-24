"""Tests for autonomous loop system."""

import json
import time
import threading

from aurora.loop import LoopManager


class TestLoopManager:
    def test_start_and_list(self):
        lm = LoopManager()
        loop_id = lm.start("test prompt", interval_seconds=10, max_iterations=1)
        assert loop_id
        loops = lm.list_loops()
        assert len(loops) == 1
        assert loops[0]["loop_id"] == loop_id
        assert loops[0]["status"] == "running"
        lm.stop(loop_id)

    def test_stop(self):
        lm = LoopManager()
        loop_id = lm.start("test", interval_seconds=60)
        assert lm.stop(loop_id) is True
        loops = lm.list_loops()
        assert loops[0]["status"] == "stopped"

    def test_stop_nonexistent(self):
        lm = LoopManager()
        assert lm.stop("nonexistent") is False

    def test_pause_and_resume(self):
        lm = LoopManager()
        loop_id = lm.start("test", interval_seconds=60)
        assert lm.pause(loop_id) is True
        loops = lm.list_loops()
        assert loops[0]["status"] == "paused"
        assert lm.resume(loop_id) is True
        loops = lm.list_loops()
        assert loops[0]["status"] == "running"
        lm.stop(loop_id)

    def test_pause_nonexistent(self):
        lm = LoopManager()
        assert lm.pause("nonexistent") is False

    def test_resume_nonexistent(self):
        lm = LoopManager()
        assert lm.resume("nonexistent") is False

    def test_custom_loop_id(self):
        lm = LoopManager()
        loop_id = lm.start("test", interval_seconds=60, loop_id="my-loop")
        assert loop_id == "my-loop"
        lm.stop(loop_id)

    def test_min_interval(self):
        lm = LoopManager()
        loop_id = lm.start("test", interval_seconds=1)
        loops = lm.list_loops()
        # Should be clamped to minimum of 10
        assert loops[0]["interval_seconds"] >= 10
        lm.stop(loop_id)

    def test_max_iterations_completion(self):
        lm = LoopManager()
        loop_id = lm.start("test", interval_seconds=10, max_iterations=1)
        # Wait for the loop to complete (should finish after ~10 seconds)
        time.sleep(12)
        loops = lm.list_loops()
        assert loops[0]["iterations"] >= 1
        assert loops[0]["status"] == "stopped"

    def test_list_multiple_loops(self):
        lm = LoopManager()
        id1 = lm.start("prompt 1", interval_seconds=60)
        id2 = lm.start("prompt 2", interval_seconds=60)
        loops = lm.list_loops()
        assert len(loops) == 2
        lm.stop(id1)
        lm.stop(id2)

    def test_hooks_emit_on_tick(self):
        from aurora.hooks import HookManager, HookEvent
        hooks = HookManager()
        received = []
        hooks.register("loop.tick", lambda ctx: received.append(ctx.get("loop_id")))

        lm = LoopManager(hooks=hooks)
        loop_id = lm.start("test", interval_seconds=10, max_iterations=1)
        time.sleep(12)

        assert loop_id in received
        lm.stop(loop_id)

    def test_tools_registered(self):
        from aurora.tools.registry import ToolRegistry
        from aurora.tools.loop_tools import _register_tools
        registry = ToolRegistry()
        _register_tools(registry)
        tools = registry.list_tools()
        assert "loop_start" in tools
        assert "loop_stop" in tools
        assert "loop_pause" in tools
        assert "loop_resume" in tools
        assert "loop_list" in tools
