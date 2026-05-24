"""End-to-end tests for AuroraAgent conversation flow.

These tests mock the LLM to verify the complete pipeline:
user input -> agent -> tool call -> synthesis -> response.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aurora.agent import AuroraAgent
from aurora.config import Config, ModelConfig, ContextConfig


def _make_config():
    return Config(
        model=ModelConfig(
            provider="openai-compat",
            api_key="test-key",
            base_url="https://test.api",
            name="test-model",
        ),
        context=ContextConfig(keep_recent=20),
    )


def _mock_tool_call_response(tool_name, tool_args):
    """Create a mock LLM response that triggers a tool call."""
    mock_msg = MagicMock()
    mock_msg.content = None
    mock_msg.tool_calls = [
        MagicMock(
            id="call_123",
            function=MagicMock(
                name=tool_name,
                arguments=json.dumps(tool_args),
            ),
        )
    ]
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=mock_msg)]
    return mock_resp


def _mock_text_response(text):
    """Create a mock LLM response that returns plain text."""
    mock_msg = MagicMock()
    mock_msg.content = text
    mock_msg.tool_calls = None
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=mock_msg)]
    return mock_resp


class TestE2ESimpleConversation:
    """Test simple conversation without tool calls."""

    @pytest.mark.asyncio
    async def test_simple_message(self):
        """Agent should return LLM response for a simple message."""
        config = _make_config()
        agent = AuroraAgent(config)
        agent.session_id = "test-session"

        with patch.object(agent.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = _mock_text_response("这是测试回复")

            result = await agent.run("你好")
            assert result == "这是测试回复"
            assert len(agent.history.get_messages()) == 2


class TestE2EToolCallFlow:
    """Test complete tool call -> synthesis flow."""

    @pytest.mark.asyncio
    async def test_tool_call_with_synthesis(self):
        """Tool call should be executed and result sent back to LLM for synthesis."""
        config = _make_config()
        agent = AuroraAgent(config)
        agent.session_id = "test-session"

        # First call: LLM decides to call competition_search
        tool_resp = _mock_tool_call_response("competition_search", {"keyword": "互联网+"})
        # Second call: LLM synthesizes the tool result into natural language
        synthesis_resp = _mock_text_response("我为你找到了互联网+大赛的信息，这是一个国家级A类赛事...")

        with patch.object(agent.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = [tool_resp, synthesis_resp]

            result = await agent.run("帮我搜索互联网+大赛")

            # Should have called LLM twice: once for tool call, once for synthesis
            assert mock_create.call_count == 2
            assert "互联网+" in result or "大赛" in result

    @pytest.mark.asyncio
    async def test_track_matcher_tool_call(self):
        """Test track matcher tool call flow."""
        config = _make_config()
        agent = AuroraAgent(config)
        agent.session_id = "test-session"

        tool_resp = _mock_tool_call_response("track_matcher", {
            "technology": "AI",
            "target_market": "教育",
        })
        synthesis_resp = _mock_text_response("根据你的AI教育项目，推荐以下赛道...")

        with patch.object(agent.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = [tool_resp, synthesis_resp]

            result = await agent.run("匹配赛道")
            assert mock_create.call_count == 2

    @pytest.mark.asyncio
    async def test_multiple_tool_calls(self):
        """Test multiple tool calls in a single response."""
        config = _make_config()
        agent = AuroraAgent(config)
        agent.session_id = "test-session"

        mock_msg = MagicMock()
        mock_msg.content = None
        mock_msg.tool_calls = [
            MagicMock(
                id="call_1",
                function=MagicMock(
                    name="list_competitions",
                    arguments="{}",
                ),
            ),
            MagicMock(
                id="call_2",
                function=MagicMock(
                    name="competition_search",
                    arguments='{"keyword": "互联网+"}',
                ),
            ),
        ]
        tool_resp = MagicMock()
        tool_resp.choices = [MagicMock(message=mock_msg)]

        synthesis_resp = _mock_text_response("为你找到了多个竞赛信息...")

        with patch.object(agent.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = [tool_resp, synthesis_resp]

            result = await agent.run("列出所有竞赛并搜索互联网+")
            assert mock_create.call_count == 2
            assert result  # Should return synthesized result


class TestE2ESessionManagement:
    """Test session persistence across conversations."""

    @pytest.mark.asyncio
    async def test_session_auto_created(self):
        """Session should be auto-created on first message."""
        config = _make_config()
        agent = AuroraAgent(config)
        assert agent.session_id is None

        with patch.object(agent.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = _mock_text_response("好的")

            await agent.run("你好")
            assert agent.session_id is not None

    @pytest.mark.asyncio
    async def test_history_persists(self):
        """Message history should persist across calls."""
        config = _make_config()
        agent = AuroraAgent(config)
        agent.session_id = "test-session"

        with patch.object(agent.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = _mock_text_response("回复")

            await agent.run("第一条")
            await agent.run("第二条")

            messages = agent.history.get_messages()
            assert len(messages) == 4  # 2 user + 2 assistant


class TestE2EToolCallFallback:
    """Test fallback behavior when synthesis fails."""

    @pytest.mark.asyncio
    async def test_synthesis_failure_fallback(self):
        """If synthesis LLM call fails, should fallback to formatted tool result."""
        config = _make_config()
        agent = AuroraAgent(config)
        agent.session_id = "test-session"

        tool_resp = _mock_tool_call_response("list_competitions", {})
        synthesis_error = Exception("Synthesis failed")

        with patch.object(agent.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = [tool_resp, synthesis_error]

            result = await agent.run("列出竞赛")
            assert result  # Should still return something via fallback


class TestE2ESwarmTrigger:
    """Test swarm orchestration trigger."""

    def test_complex_message_triggers_swarm(self):
        """Complex messages should trigger swarm."""
        config = _make_config()
        agent = AuroraAgent(config)
        assert agent.swarm_orchestrator.should_trigger("帮我写一份完整的商业计划书")

    def test_simple_message_no_swarm(self):
        """Simple messages should not trigger swarm."""
        config = _make_config()
        agent = AuroraAgent(config)
        assert not agent.swarm_orchestrator.should_trigger("你好")
