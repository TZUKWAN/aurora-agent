"""Tests for defense simulation system."""

import json

import pytest

from aurora.defense.simulator import DefenseSimulator
from aurora.tools.registry import ToolRegistry
from aurora.tools.defense_tools import _register_tools


def _make_plan():
    """Create a sample business plan for testing."""
    return {
        "metadata": {"competition": "internet_plus"},
        "sections": {
            "executive_summary": {
                "title": "Executive Summary",
                "content": "An innovative AI-powered platform targeting a 500 billion market with unique technology.",
            },
            "project_overview": {
                "title": "Project Overview",
                "content": "Core innovation: patent-pending algorithm with significant technical barrier. Market-leading AI solution.",
            },
            "market_analysis": {
                "title": "Market Analysis",
                "content": "Target market size is 500 billion, growing at 20% annually. Key competitors lack our innovation.",
            },
            "business_model": {
                "title": "Business Model",
                "content": "Revenue from subscription and licensing. Gross margin 75%. Strong profitability model.",
            },
            "financial_analysis": {
                "title": "Financial Analysis",
                "content": "Year 1 revenue 5 million, Year 2 revenue 20 million, Year 3 revenue 80 million. ROI 300%.",
            },
            "team_introduction": {
                "title": "Team",
                "content": "Experienced founding team with complementary skills. Professional background in AI and business.",
            },
            "risk_management": {
                "title": "Risk Management",
                "content": "Key risks identified with mitigation strategies. Contingency plans for market and technology risks.",
            },
        },
    }


class TestDefenseSimulator:
    """Test the core DefenseSimulator class."""

    def setup_method(self):
        self.simulator = DefenseSimulator()
        self.plan = _make_plan()

    def test_generate_questions_basic(self):
        result = self.simulator.generate_questions(self.plan)
        assert "questions" in result
        assert "total_questions" in result
        assert result["total_questions"] == len(result["questions"])
        assert result["total_questions"] == 10

    def test_generate_questions_custom_count(self):
        result = self.simulator.generate_questions(self.plan, num_questions=5)
        assert result["total_questions"] == 5

    def test_generate_questions_has_categories(self):
        result = self.simulator.generate_questions(self.plan)
        categories = {q["category"] for q in result["questions"]}
        # Should have multiple categories represented
        assert len(categories) >= 3

    def test_generate_questions_structure(self):
        result = self.simulator.generate_questions(self.plan)
        for q in result["questions"]:
            assert "id" in q
            assert "category" in q
            assert "question" in q
            assert "difficulty" in q
            assert q["difficulty"] in ("easy", "medium", "hard")

    def test_generate_questions_with_competition_id(self):
        result = self.simulator.generate_questions(self.plan, competition_id="internet_plus")
        assert result["competition_id"] == "internet_plus"

    def test_simulate_defense_basic(self):
        result = self.simulator.simulate_defense(self.plan)
        assert "questions" in result
        assert "rubric" in result
        assert "tips" in result
        assert "total_questions" in result

    def test_simulate_defense_question_detail(self):
        result = self.simulator.simulate_defense(self.plan)
        for q in result["questions"]:
            assert "expected_keywords" in q
            assert "scoring_criteria" in q
            assert "time_limit_seconds" in q
            assert q["time_limit_seconds"] == 180

    def test_simulate_defense_rubric(self):
        result = self.simulator.simulate_defense(self.plan)
        rubric = result["rubric"]
        assert "clarity" in rubric
        assert "accuracy" in rubric
        assert "depth" in rubric
        assert "persuasiveness" in rubric
        assert "completeness" in rubric
        for criterion, info in rubric.items():
            assert "weight" in info
            assert "description" in info
            assert "levels" in info

    def test_score_answer_good_answer(self):
        question = "请阐述你们项目的核心创新点是什么?与现有解决方案相比有哪些实质性突破?"
        answer = (
            "首先，我们的核心创新在于专利算法，具有显著的技术壁垒。"
            "其次，通过独特的AI技术，我们实现了市场上首创的解决方案。"
            "我们的创新经过实验验证，数据显示效果提升了50%。"
            "最后，我们已经申请了3项专利，确保了知识产权保护。"
        )
        result = self.simulator.score_answer(question, answer, self.plan)
        assert "score" in result
        assert "feedback" in result
        assert "suggestions" in result
        assert "dimension_scores" in result
        assert result["score"] > 50

    def test_score_answer_bad_answer(self):
        question = "请阐述你们项目的核心创新点是什么?"
        answer = "我们的项目很好。"
        result = self.simulator.score_answer(question, answer, self.plan)
        assert result["score"] < 70

    def test_score_answer_empty_answer(self):
        question = "请阐述你们项目的核心创新点是什么?"
        result = self.simulator.score_answer(question, "", self.plan)
        assert result["score"] == 0
        assert "未提供回答内容" in result["feedback"]

    def test_score_answer_dimension_ranges(self):
        question = "请介绍你们的目标市场?"
        answer = (
            "首先，我们的目标市场规模达到500亿，年增长率20%。"
            "其次，通过市场调研我们发现用户痛点非常明显。"
            "因此，我们基于数据分析和行业报告确定了市场定位。"
            "综合来看，市场前景广阔，份额增长潜力巨大。"
        )
        result = self.simulator.score_answer(question, answer, self.plan)
        for dim, score in result["dimension_scores"].items():
            assert 0 <= score <= 100, f"{dim} score {score} out of range"

    def test_get_defense_tips_default(self):
        tips = self.simulator.get_defense_tips()
        assert isinstance(tips, list)
        assert len(tips) > 0

    def test_get_defense_tips_competition_specific(self):
        tips = self.simulator.get_defense_tips("internet_plus")
        assert isinstance(tips, list)
        assert len(tips) > 0
        # Competition-specific tips should be at the beginning
        has_internet = any("互联网" in tip for tip in tips)
        assert has_internet

    def test_get_defense_tips_unknown_competition(self):
        tips = self.simulator.get_defense_tips("unknown_comp")
        assert isinstance(tips, list)
        assert len(tips) > 0


class TestDefenseTools:
    """Test defense tool registration and dispatch."""

    def setup_method(self):
        self.registry = ToolRegistry()
        _register_tools(self.registry)

    def test_tools_registered(self):
        tool_names = self.registry.list_tools()
        assert "defense_generate_questions" in tool_names
        assert "defense_simulate" in tool_names
        assert "defense_score_answer" in tool_names
        assert "defense_tips" in tool_names

    def test_generate_questions_tool(self):
        result = json.loads(
            self.registry.dispatch(
                "defense_generate_questions",
                {"plan": _make_plan(), "num_questions": 5},
            )
        )
        assert "data" in result
        assert result["data"]["total_questions"] == 5

    def test_simulate_tool(self):
        result = json.loads(
            self.registry.dispatch(
                "defense_simulate",
                {"plan": _make_plan()},
            )
        )
        assert "data" in result
        assert "rubric" in result["data"]
        assert "questions" in result["data"]

    def test_score_answer_tool(self):
        result = json.loads(
            self.registry.dispatch(
                "defense_score_answer",
                {
                    "question": "你们的核心创新是什么?",
                    "answer": "我们的核心创新是专利算法，具有技术壁垒和创新性。",
                    "plan": _make_plan(),
                },
            )
        )
        assert "data" in result
        assert "score" in result["data"]

    def test_tips_tool(self):
        result = json.loads(
            self.registry.dispatch("defense_tips", {"competition_id": "internet_plus"})
        )
        assert "tips" in result
        assert isinstance(result["tips"], list)
        assert len(result["tips"]) > 0

    def test_tips_tool_no_args(self):
        result = json.loads(self.registry.dispatch("defense_tips", {}))
        assert "tips" in result
        assert len(result["tips"]) > 0

    def test_unknown_tool_returns_error(self):
        result = json.loads(self.registry.dispatch("nonexistent_tool", {}))
        assert "error" in result

    def test_score_empty_answer_tool(self):
        result = json.loads(
            self.registry.dispatch(
                "defense_score_answer",
                {
                    "question": "你们的核心创新是什么?",
                    "answer": "",
                    "plan": _make_plan(),
                },
            )
        )
        assert "data" in result
        assert result["data"]["score"] == 0
