"""Tests for TaskDecomposer LLM upgrade and keyword fallback."""

import pytest

from aurora.swarm.decomposer import TaskDecomposer


class TestKeywordDecomposition:
    """Test keyword-based decomposition (original logic preserved)."""

    def test_business_plan_decomposition(self):
        """Test decomposition of business plan task."""
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose("帮我写一份商业计划书")

        assert len(tasks) >= 5
        assert tasks[0]["id"] == "1"
        assert "背景" in tasks[0]["description"] or "市场" in tasks[0]["description"]
        assert all("id" in t and "description" in t for t in tasks)

    def test_business_plan_with_internet_plus(self):
        """Test business plan with internet+ competition keyword."""
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose("写一份互联网+商业计划书")

        assert len(tasks) == 6
        last = tasks[-1]
        assert "互联网+" in last["description"]

    def test_business_plan_with_challenge_cup(self):
        """Test business plan with challenge cup keyword."""
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose("写一份挑战杯商业计划书")

        assert len(tasks) == 6
        last = tasks[-1]
        assert "挑战杯" in last["description"]

    def test_bp_keyword_decomposition(self):
        """Test BP keyword triggers business plan decomposition."""
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose("帮我准备BP")

        assert len(tasks) >= 5
        assert tasks[0]["id"] == "1"

    def test_ppt_decomposition(self):
        """Test decomposition of PPT task."""
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose("帮我制作PPT")

        assert len(tasks) == 3
        assert any("PPT" in t["description"] for t in tasks)

    def test_presentation_with_video(self):
        """Test PPT task with video keyword adds video subtask."""
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose("制作路演PPT和视频")

        assert len(tasks) == 4
        assert any("视频" in t["description"] for t in tasks)

    def test_defense_keyword_triggers_presentation(self):
        """Test that the 'defense' keyword triggers presentation decomposition."""
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose("准备答辩材料")

        assert len(tasks) == 3
        assert any("答辩" in t["description"] for t in tasks)

    def test_analysis_decomposition(self):
        """Test decomposition of analysis task."""
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose("分析项目可行性")

        assert len(tasks) == 4
        assert any("创新" in t["description"] for t in tasks)

    def test_evaluation_decomposition(self):
        """Test evaluation keyword triggers analysis decomposition."""
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose("评估商业模式")

        assert len(tasks) == 4
        assert any("优化" in t["description"] for t in tasks)

    def test_project_decomposition(self):
        """Test decomposition of project task."""
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose("帮我规划项目方案")

        assert len(tasks) == 4
        assert any("创意" in t["description"] for t in tasks)

    def test_unknown_task_default(self):
        """Test default decomposition for unrecognized task."""
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose("随便聊聊天气")

        assert len(tasks) == 1
        assert tasks[0]["description"] == "随便聊聊天气"


class TestEstimateTaskCount:
    """Test the estimate_task_count method."""

    def test_full_business_plan_count(self):
        """Test estimation for full business plan."""
        decomposer = TaskDecomposer()
        count = decomposer.estimate_task_count("写完整的商业计划书")
        assert count == 7

    def test_comprehensive_task_count(self):
        """Test estimation with 'all' keyword."""
        decomposer = TaskDecomposer()
        count = decomposer.estimate_task_count("完成全部内容")
        assert count == 7

    def test_ppt_task_count(self):
        """Test estimation for PPT task."""
        decomposer = TaskDecomposer()
        count = decomposer.estimate_task_count("制作PPT")
        assert count == 4

    def test_roadshow_task_count(self):
        """Test estimation for roadshow task."""
        decomposer = TaskDecomposer()
        count = decomposer.estimate_task_count("准备路演材料")
        assert count == 4

    def test_analysis_task_count(self):
        """Test estimation for analysis task."""
        decomposer = TaskDecomposer()
        count = decomposer.estimate_task_count("分析项目可行性")
        assert count == 4

    def test_evaluation_task_count(self):
        """Test estimation for evaluation task."""
        decomposer = TaskDecomposer()
        count = decomposer.estimate_task_count("评估团队实力")
        assert count == 4

    def test_default_task_count(self):
        """Test default estimation for unknown task."""
        decomposer = TaskDecomposer()
        count = decomposer.estimate_task_count("随便写点东西")
        assert count == 2


class TestConfigHandling:
    """Test TaskDecomposer initialization and config handling."""

    def test_create_without_config(self):
        """Test creating decomposer without config uses keyword path."""
        decomposer = TaskDecomposer()
        assert decomposer._client is None
        assert decomposer._config is None

        # Should still decompose via keywords
        tasks = decomposer.decompose("写一份商业计划书")
        assert len(tasks) >= 5

    def test_create_with_none_config(self):
        """Test creating decomposer with explicit None config."""
        decomposer = TaskDecomposer(config=None)
        assert decomposer._client is None

        tasks = decomposer.decompose("制作PPT")
        assert len(tasks) == 3

    def test_config_without_api_key_falls_back(self):
        """Test that config without API key falls back gracefully."""

        class MockConfig:
            class model:
                api_key = None
                base_url = None
                name = None

        decomposer = TaskDecomposer(config=MockConfig)
        assert decomposer._client is None

        # Keyword fallback works
        tasks = decomposer.decompose("帮我分析项目")
        assert len(tasks) == 4

    def test_config_with_empty_api_key_falls_back(self):
        """Test that config with empty string API key falls back."""

        class MockConfig:
            class model:
                api_key = ""
                base_url = ""
                name = ""

        decomposer = TaskDecomposer(config=MockConfig)
        assert decomposer._client is None

        tasks = decomposer.decompose("评估方案")
        assert len(tasks) == 4

    def test_invalid_config_does_not_crash(self):
        """Test that invalid config objects don't crash initialization."""
        # Config without model attribute
        decomposer = TaskDecomposer(config="not_a_real_config")
        assert decomposer._client is None

        # Should still work via keywords
        tasks = decomposer.decompose("写商业计划书")
        assert len(tasks) >= 5


class TestExtractKeywords:
    """Test the _extract_keywords helper method."""

    def test_extract_multiple_keywords(self):
        """Test extracting multiple matching keywords."""
        decomposer = TaskDecomposer()
        keywords = decomposer._extract_keywords("帮我写互联网+竞赛的PPT")
        assert "互联网+" in keywords
        assert "竞赛" in keywords
        assert "PPT" in keywords

    def test_extract_no_keywords(self):
        """Test extracting from text with no matching keywords."""
        decomposer = TaskDecomposer()
        keywords = decomposer._extract_keywords("今天天气怎么样")
        assert keywords == []

    def test_extract_single_keyword(self):
        """Test extracting a single matching keyword."""
        decomposer = TaskDecomposer()
        keywords = decomposer._extract_keywords("做市场分析")
        assert keywords == ["分析"]
