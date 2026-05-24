"""Tests for learning manager."""

from aurora.learning import LearningManager


class TestLearningManager:
    def test_record_execution(self):
        lm = LearningManager()
        lm.record_execution("bp_generate", {"type": "innovation"}, '{"result": "ok"}', 0.8)
        assert len(lm._logs) == 1
        assert lm._logs[0]["tool_name"] == "bp_generate"

    def test_analyze_patterns_empty(self):
        lm = LearningManager()
        patterns = lm.analyze_patterns()
        assert patterns["tool_frequency"] == {}
        assert patterns.get("total_executions", 0) == 0

    def test_analyze_tool_frequency(self):
        lm = LearningManager()
        for _ in range(5):
            lm.record_execution("bp_generate", score=0.8)
        for _ in range(2):
            lm.record_execution("evaluate", score=0.6)

        patterns = lm.analyze_patterns()
        assert patterns["tool_frequency"]["bp_generate"] == 5
        assert patterns["tool_frequency"]["evaluate"] == 2

    def test_detect_error_tools(self):
        lm = LearningManager()
        lm.record_execution("broken_tool", score=0.1)
        lm.record_execution("broken_tool", score=0.1)

        patterns = lm.analyze_patterns()
        assert "broken_tool" in patterns["error_tools"]

    def test_detect_workflow_sequences(self):
        lm = LearningManager()
        for _ in range(3):
            lm.record_execution("bp_generate", score=0.8)
            lm.record_execution("evaluate", score=0.7)

        patterns = lm.analyze_patterns()
        assert len(patterns["workflow_sequences"]) > 0
        assert patterns["workflow_sequences"][0]["count"] >= 2

    def test_suggest_improvements(self):
        lm = LearningManager()
        for _ in range(3):
            lm.record_execution("bp_generate", score=0.8)
            lm.record_execution("evaluate", score=0.7)

        suggestions = lm.suggest_improvements()
        assert len(suggestions) > 0
        assert any("频繁工作流" in s for s in suggestions)

    def test_post_dispatch_hook(self):
        lm = LearningManager()
        ctx = {"tool": "bp_generate", "args": {}, "result": '{"result": "success", "data": "...long content..."}'}
        lm.post_dispatch_hook(ctx)
        assert len(lm._logs) == 1
        assert lm._logs[0]["score"] == 0.8

    def test_post_dispatch_hook_error(self):
        lm = LearningManager()
        ctx = {"tool": "broken", "args": {}, "result": '{"error": "failed"}'}
        lm.post_dispatch_hook(ctx)
        assert lm._logs[0]["score"] == 0.1
