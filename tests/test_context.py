"""Tests for context compression."""

from aurora.context import ContextCompressor


def _make_messages(count, chars_per_msg=100):
    """Generate test messages with specified content length."""
    messages = [{"role": "system", "content": "System prompt"}]
    for i in range(count):
        messages.append({"role": "user", "content": "x" * chars_per_msg + f" message {i}"})
        messages.append({"role": "assistant", "content": "y" * chars_per_msg + f" reply {i}"})
    return messages


class TestContextCompressor:
    def test_estimate_tokens_empty(self):
        comp = ContextCompressor()
        assert comp.estimate_tokens([]) == 0

    def test_estimate_tokens_ascii(self):
        comp = ContextCompressor()
        msgs = [{"role": "user", "content": "Hello world"}]
        tokens = comp.estimate_tokens(msgs)
        assert tokens > 0
        assert tokens < 20

    def test_estimate_tokens_chinese(self):
        comp = ContextCompressor()
        msgs = [{"role": "user", "content": "你好世界测试"}]
        tokens = comp.estimate_tokens(msgs)
        assert tokens > 0
        # 5 Chinese chars * 1.5 = ~7-8 tokens
        assert tokens >= 7

    def test_no_compression_below_threshold(self):
        comp = ContextCompressor(context_window=100000, compress_threshold=0.65)
        msgs = _make_messages(5, chars_per_msg=50)
        result = comp.compress(msgs)
        assert result == msgs

    def test_compression_reduces_message_count(self):
        # Small context window to trigger compression easily
        comp = ContextCompressor(
            context_window=500,
            compress_threshold=0.5,
            keep_recent=3,
        )
        msgs = _make_messages(20, chars_per_msg=100)
        result = comp.compress(msgs)
        assert len(result) < len(msgs)
        # Should keep at least system msg + keep_recent
        assert len(result) >= 1 + 3

    def test_compression_preserves_system_msg(self):
        comp = ContextCompressor(
            context_window=500,
            compress_threshold=0.5,
            keep_recent=3,
        )
        msgs = _make_messages(20, chars_per_msg=100)
        result = comp.compress(msgs)
        assert result[0]["role"] == "system"
        assert "System prompt" in result[0]["content"]

    def test_compression_adds_summary(self):
        comp = ContextCompressor(
            context_window=500,
            compress_threshold=0.5,
            keep_recent=3,
        )
        msgs = _make_messages(20, chars_per_msg=100)
        result = comp.compress(msgs)
        system_content = result[0]["content"]
        # Should have summary marker since old messages were compressed
        assert "摘要" in system_content

    def test_no_compression_when_few_messages(self):
        comp = ContextCompressor(
            context_window=500,
            compress_threshold=0.5,
            keep_recent=20,
        )
        msgs = _make_messages(3, chars_per_msg=50)
        result = comp.compress(msgs)
        # All messages kept since keep_recent > conversation length
        assert len(result) == len(msgs)

    def test_extractive_summarize(self):
        comp = ContextCompressor()
        msgs = [
            {"role": "user", "content": "Test message one"},
            {"role": "assistant", "content": "Test reply two"},
        ]
        summary = comp._extractive_summarize(msgs)
        assert "user" in summary
        assert "assistant" in summary

    def test_extractive_summarize_empty(self):
        comp = ContextCompressor()
        assert comp._extractive_summarize([]) == ""

    def test_extractive_summarize_long_content(self):
        comp = ContextCompressor()
        msgs = [
            {"role": "user", "content": "x" * 500},
        ]
        summary = comp._extractive_summarize(msgs)
        # Should truncate long content
        assert len(summary) < 600
