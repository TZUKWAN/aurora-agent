"""Tests for SwarmBus and SwarmOrchestrator enhancements."""

import asyncio

import pytest

from aurora.swarm.bus import BusMessage, PriorityBusMessage, SwarmBus
from aurora.swarm.orchestrator import SwarmOrchestrator
from aurora.swarm.roles import RoleTemplate, RoleTemplateBank


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_message(sender="agent_a", recipient="agent_b", content="hello",
                  message_type="informational"):
    return BusMessage(
        sender=sender,
        recipient=recipient,
        content=content,
        message_type=message_type,
    )


class FakeToolRegistry:
    """Minimal tool registry stub for orchestrator tests."""

    def get_schemas(self):
        return []

    def dispatch(self, name, args):
        return f"dispatched {name}"


def _make_orchestrator():
    """Create a SwarmOrchestrator with fake dependencies."""

    async def fake_llm_call(messages, tools=None, tool_dispatch=None):
        return "LLM response"

    return SwarmOrchestrator(
        run_fn=lambda *a, **k: "ok",
        llm_call_fn=fake_llm_call,
        tools_registry=FakeToolRegistry(),
    )


# ===================================================================
# SwarmBus tests
# ===================================================================

class TestSwarmBusExisting:
    """Ensure existing bus functionality still works."""

    def test_send_and_get_messages(self):
        async def _test():
            bus = SwarmBus()
            msg = _make_message()
            await bus.send(msg)
            messages = await bus.get_messages("agent_b")
            assert len(messages) == 1
            assert messages[0].content == "hello"

        asyncio.run(_test())

    def test_broadcast(self):
        async def _test():
            bus = SwarmBus()
            await bus.broadcast("agent_a", "announcement")
            messages = await bus.get_messages("anyone")
            assert len(messages) == 1
            assert messages[0].recipient == "*"

        asyncio.run(_test())

    def test_subscribe_and_receive(self):
        async def _test():
            bus = SwarmBus()
            queue = bus.subscribe("agent_b")
            msg = _make_message()
            await bus.send(msg)
            received = await queue.get()
            assert received.content == "hello"

        asyncio.run(_test())

    def test_get_history(self):
        async def _test():
            bus = SwarmBus()
            await bus.send(_make_message(content="a"))
            await bus.send(_make_message(content="b"))
            history = bus.get_history()
            assert len(history) == 2

        asyncio.run(_test())

    def test_clear_history(self):
        async def _test():
            bus = SwarmBus()
            await bus.send(_make_message())
            bus.clear_history()
            assert len(bus.get_history()) == 0

        asyncio.run(_test())


class TestPriorityBusMessage:
    """Test PriorityBusMessage dataclass."""

    def test_is_bus_message_subclass(self):
        msg = PriorityBusMessage(
            sender="a", recipient="b", content="hi", priority=5
        )
        assert isinstance(msg, BusMessage)
        assert msg.priority == 5

    def test_default_priority_is_zero(self):
        msg = PriorityBusMessage(sender="a", recipient="b", content="hi")
        assert msg.priority == 0


class TestSwarmBusSendPriority:
    """Test SwarmBus.send_priority."""

    def test_send_priority_creates_priority_message(self):
        async def _test():
            bus = SwarmBus()
            msg = _make_message(content="urgent")
            await bus.send_priority(msg, priority=10)
            history = bus.get_history()
            assert len(history) == 1
            assert isinstance(history[0], PriorityBusMessage)
            assert history[0].priority == 10
            assert history[0].content == "urgent"

        asyncio.run(_test())

    def test_send_priority_default_priority(self):
        async def _test():
            bus = SwarmBus()
            msg = _make_message()
            await bus.send_priority(msg)
            history = bus.get_history()
            assert history[0].priority == 0

        asyncio.run(_test())

    def test_send_priority_delivers_to_subscriber(self):
        async def _test():
            bus = SwarmBus()
            queue = bus.subscribe("agent_b")
            msg = _make_message(content="priority test")
            await bus.send_priority(msg, priority=5)
            received = await queue.get()
            assert isinstance(received, PriorityBusMessage)
            assert received.priority == 5

        asyncio.run(_test())


class TestSwarmBusRequestResponse:
    """Test SwarmBus.request_response."""

    def test_request_gets_response(self):
        async def _test():
            bus = SwarmBus()
            queue = bus.subscribe("responder")

            async def respond():
                msg = await asyncio.wait_for(queue.get(), timeout=2.0)
                response = BusMessage(
                    sender="responder",
                    recipient=msg.sender,
                    content="response_data",
                )
                await bus.send(response)

            responder_task = asyncio.create_task(respond())
            result = await bus.request_response(
                sender="requester",
                recipient="responder",
                content="ping",
                timeout=2.0,
            )
            await responder_task
            assert result == "response_data"

        asyncio.run(_test())

    def test_request_response_timeout(self):
        async def _test():
            bus = SwarmBus()
            try:
                await bus.request_response(
                    sender="requester",
                    recipient="nobody",
                    content="ping",
                    timeout=0.2,
                )
                pytest.fail("Should have raised TimeoutError")
            except TimeoutError:
                pass  # expected

        asyncio.run(_test())

    def test_request_response_cleans_up_subscription(self):
        async def _test():
            bus = SwarmBus()
            queue = bus.subscribe("responder")

            async def respond():
                msg = await asyncio.wait_for(queue.get(), timeout=2.0)
                response = BusMessage(
                    sender="responder",
                    recipient=msg.sender,
                    content="ok",
                )
                await bus.send(response)

            responder_task = asyncio.create_task(respond())
            await bus.request_response(
                sender="requester",
                recipient="responder",
                content="ping",
                timeout=2.0,
            )
            await responder_task
            # Temporary subscription should be cleaned up
            listeners_count = sum(len(qs) for qs in bus._listeners.values())
            assert listeners_count == 1  # Only the original responder queue

        asyncio.run(_test())


class TestSwarmBusGetStats:
    """Test SwarmBus.get_stats."""

    def test_empty_stats(self):
        bus = SwarmBus()
        stats = bus.get_stats()
        assert stats["total_messages"] == 0
        assert stats["active_listeners"] == 0
        assert stats["message_types"] == {}

    def test_stats_with_messages(self):
        async def _test():
            bus = SwarmBus()
            await bus.send(_make_message(message_type="request"))
            await bus.send(_make_message(message_type="request"))
            await bus.send(_make_message(message_type="informational"))

            stats = bus.get_stats()
            assert stats["total_messages"] == 3
            assert stats["message_types"]["request"] == 2
            assert stats["message_types"]["informational"] == 1

        asyncio.run(_test())

    def test_stats_with_listeners(self):
        bus = SwarmBus()
        bus.subscribe("agent_a")
        bus.subscribe("agent_a")
        bus.subscribe("agent_b")

        stats = bus.get_stats()
        assert stats["active_listeners"] == 3


class TestSwarmBusGetRecent:
    """Test SwarmBus.get_recent."""

    def test_get_recent_default(self):
        async def _test():
            bus = SwarmBus()
            for i in range(15):
                await bus.send(_make_message(content=f"msg_{i}"))

            recent = await bus.get_recent()
            assert len(recent) == 10
            assert recent[0].content == "msg_5"
            assert recent[-1].content == "msg_14"

        asyncio.run(_test())

    def test_get_recent_custom_count(self):
        async def _test():
            bus = SwarmBus()
            for i in range(5):
                await bus.send(_make_message(content=f"msg_{i}"))

            recent = await bus.get_recent(count=3)
            assert len(recent) == 3
            assert recent[0].content == "msg_2"

        asyncio.run(_test())

    def test_get_recent_empty(self):
        async def _test():
            bus = SwarmBus()
            recent = await bus.get_recent()
            assert recent == []

        asyncio.run(_test())

    def test_get_recent_zero_count(self):
        async def _test():
            bus = SwarmBus()
            await bus.send(_make_message())
            recent = await bus.get_recent(count=0)
            assert recent == []

        asyncio.run(_test())

    def test_get_recent_fewer_than_count(self):
        async def _test():
            bus = SwarmBus()
            await bus.send(_make_message(content="only"))
            recent = await bus.get_recent(count=10)
            assert len(recent) == 1

        asyncio.run(_test())


# ===================================================================
# SwarmOrchestrator tests
# ===================================================================

class TestSwarmOrchestratorGetProgress:
    """Test SwarmOrchestrator.get_progress."""

    def test_initial_progress(self):
        orch = _make_orchestrator()
        progress = orch.get_progress()
        assert progress["completed_tasks"] == 0
        assert progress["total_tasks"] == 0
        assert progress["current_phase"] == "idle"


class TestSwarmOrchestratorGetRoleRecommendations:
    """Test SwarmOrchestrator.get_role_recommendations."""

    def test_recommendations_for_business_plan(self):
        orch = _make_orchestrator()
        recs = orch.get_role_recommendations("撰写商业计划书和商业模式分析")
        assert len(recs) > 0
        for rec in recs:
            assert "role_id" in rec
            assert "name" in rec
            assert "relevance_score" in rec
            assert "reason" in rec
            assert 0 < rec["relevance_score"] <= 1.0

    def test_recommendations_sorted_by_score(self):
        orch = _make_orchestrator()
        recs = orch.get_role_recommendations("商业计划书和PPT路演")
        scores = [r["relevance_score"] for r in recs]
        assert scores == sorted(scores, reverse=True)

    def test_recommendations_empty_for_unknown(self):
        orch = _make_orchestrator()
        recs = orch.get_role_recommendations("xyz nothing matches")
        assert recs == []

    def test_recommendations_includes_expected_roles(self):
        orch = _make_orchestrator()
        recs = orch.get_role_recommendations("商业计划书BP金奖框架")
        role_ids = [r["role_id"] for r in recs]
        assert "writing_expert" in role_ids


class TestSwarmOrchestratorRunWithProgress:
    """Test SwarmOrchestrator.run_with_progress."""

    def test_run_with_progress_calls_callback(self):
        async def _test():
            orch = _make_orchestrator()
            progress_calls = []

            def callback(progress):
                progress_calls.append(progress.copy())

            await orch.run_with_progress("分析项目", callback=callback)

            assert len(progress_calls) >= 2
            # First call should be planning phase
            assert progress_calls[0]["current_phase"] == "planning"
            # Last call should be complete
            assert progress_calls[-1]["current_phase"] == "complete"

        asyncio.run(_test())

    def test_run_with_progress_updates_completed(self):
        async def _test():
            orch = _make_orchestrator()
            progress_snapshots = []

            def callback(progress):
                progress_snapshots.append(progress.copy())

            await orch.run_with_progress("分析项目", callback=callback)

            # At least some snapshots should show progress during execution
            executing_phases = [
                p for p in progress_snapshots if p["current_phase"] == "executing"
            ]
            if executing_phases:
                # completed_tasks should increase over executing phase snapshots
                completed_values = [p["completed_tasks"] for p in executing_phases]
                # Values should be non-decreasing
                for i in range(1, len(completed_values)):
                    assert completed_values[i] >= completed_values[i - 1]

        asyncio.run(_test())


class TestSwarmOrchestratorShouldTrigger:
    """Test SwarmOrchestrator.should_trigger still works."""

    def test_complex_triggers(self):
        orch = _make_orchestrator()
        assert orch.should_trigger("帮我写一个完整的商业计划书") is True

    def test_simple_does_not_trigger(self):
        orch = _make_orchestrator()
        assert orch.should_trigger("你好") is False
