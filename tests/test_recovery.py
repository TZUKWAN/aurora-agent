"""Tests for error recovery manager."""

from aurora.recovery import RecoveryManager


class TestErrorClassification:
    def test_transient_timeout(self):
        r = RecoveryManager()
        assert r.classify_error("Connection timeout occurred") == "transient"

    def test_transient_network(self):
        r = RecoveryManager()
        assert r.classify_error("Network error: connection refused") == "transient"

    def test_rate_limit(self):
        r = RecoveryManager()
        assert r.classify_error("Rate limit exceeded: 429 too many requests") == "rate_limit"

    def test_auth_error(self):
        r = RecoveryManager()
        assert r.classify_error("Unauthorized: invalid API key") == "auth"

    def test_permanent_error(self):
        r = RecoveryManager()
        assert r.classify_error("FileNotFoundError: no such file") == "permanent"

    def test_error_type_param(self):
        r = RecoveryManager()
        assert r.classify_error("failed", error_type="TimeoutError") == "transient"


class TestRetryLogic:
    def test_should_retry_transient(self):
        r = RecoveryManager(max_retries=3)
        assert r.should_retry("tool_a", "transient") is True

    def test_should_not_retry_permanent(self):
        r = RecoveryManager()
        assert r.should_retry("tool_a", "permanent") is False

    def test_should_not_retry_auth(self):
        r = RecoveryManager()
        assert r.should_retry("tool_a", "auth") is False

    def test_should_retry_rate_limit(self):
        r = RecoveryManager()
        assert r.should_retry("tool_a", "rate_limit") is True

    def test_max_retries_exceeded(self):
        r = RecoveryManager(max_retries=2)
        r.record_retry("tool_a")
        r.record_retry("tool_a")
        assert r.should_retry("tool_a", "transient") is False

    def test_delay_increases(self):
        r = RecoveryManager(base_delay=1.0)
        d0 = r.get_delay(0, "transient")
        d1 = r.get_delay(1, "transient")
        d2 = r.get_delay(2, "transient")
        assert d0 < d1 < d2

    def test_rate_limit_delay_doubled(self):
        r = RecoveryManager(base_delay=1.0)
        d_transient = r.get_delay(1, "transient")
        d_rate = r.get_delay(1, "rate_limit")
        assert d_rate > d_transient

    def test_permanent_no_delay(self):
        r = RecoveryManager()
        assert r.get_delay(0, "permanent") == 0


class TestRecoveryHook:
    def test_hook_sets_retry_for_transient(self):
        r = RecoveryManager()
        ctx = {"tool": "my_tool", "error": "connection timeout", "error_type": "TimeoutError"}
        result = r.handle_error_hook(ctx)
        assert result["error_category"] == "transient"
        assert result["retry_recommended"] is True
        assert result["retry_delay"] > 0

    def test_hook_no_retry_for_permanent(self):
        r = RecoveryManager()
        ctx = {"tool": "my_tool", "error": "FileNotFoundError", "error_type": "FileNotFoundError"}
        result = r.handle_error_hook(ctx)
        assert result["retry_recommended"] is False

    def test_reset_clears_counts(self):
        r = RecoveryManager()
        r.record_retry("tool_a")
        r.record_retry("tool_a")
        r.reset()
        assert r.should_retry("tool_a", "transient") is True
