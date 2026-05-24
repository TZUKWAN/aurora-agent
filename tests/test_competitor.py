"""Tests for competitor analysis module."""

import json

import pytest

from aurora.competition.competitor_analyzer import CompetitorAnalyzer
from aurora.tools.registry import ToolRegistry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_project():
    """Create a sample project info dict for tests."""
    return {
        "technology": "AI",
        "business_model": "SaaS",
        "target_market": "教育",
        "team_background": "计算机专业",
        "project_stage": "初创",
        "innovation": "基于大模型的智能辅导",
        "social_impact": "教育公平",
    }


def _make_competitors():
    """Create a sample competitor list for tests."""
    return [
        {
            "name": "竞品A",
            "strengths": ["品牌知名度高", "用户基数大"],
            "weaknesses": ["产品老旧", "技术落后"],
            "market_share": 35,
        },
        {
            "name": "竞品B",
            "strengths": ["技术先进"],
            "weaknesses": ["市场覆盖不足", "团队规模小"],
            "market_share": 10,
        },
    ]


@pytest.fixture
def analyzer():
    return CompetitorAnalyzer()


@pytest.fixture
def project():
    return _make_project()


@pytest.fixture
def competitors():
    return _make_competitors()


# ---------------------------------------------------------------------------
# CompetitorAnalyzer - SWOT Analysis
# ---------------------------------------------------------------------------

class TestSWOTAnalysis:
    """Test the analyze_swot method."""

    def test_returns_all_swot_keys(self, analyzer, project):
        result = analyzer.analyze_swot(project)
        assert "strengths" in result
        assert "weaknesses" in result
        assert "opportunities" in result
        assert "threats" in result
        assert "overall_assessment" in result

    def test_strengths_detected(self, analyzer, project):
        result = analyzer.analyze_swot(project)
        assert isinstance(result["strengths"], list)
        assert len(result["strengths"]) > 0
        # AI keyword should produce a technology strength
        text = " ".join(result["strengths"])
        assert "技术" in text or "AI" in text.upper() or "竞争力" in text

    def test_weaknesses_detected(self, analyzer, project):
        result = analyzer.analyze_swot(project)
        assert isinstance(result["weaknesses"], list)
        assert len(result["weaknesses"]) > 0
        # "初创" stage should produce a weakness
        text = " ".join(result["weaknesses"])
        assert "初创" in text or "阶段" in text or "早期" in text

    def test_opportunities_detected(self, analyzer, project):
        result = analyzer.analyze_swot(project)
        assert isinstance(result["opportunities"], list)
        assert len(result["opportunities"]) > 0
        # "教育公平" should produce social opportunity
        text = " ".join(result["opportunities"])
        assert "社会" in text or "教育" in text or "政策" in text or "红利" in text

    def test_threats_detected(self, analyzer, project):
        result = analyzer.analyze_swot(project)
        assert isinstance(result["threats"], list)
        assert len(result["threats"]) > 0

    def test_overall_assessment_is_string(self, analyzer, project):
        result = analyzer.analyze_swot(project)
        assert isinstance(result["overall_assessment"], str)
        assert len(result["overall_assessment"]) > 0

    def test_empty_project_produces_fallback(self, analyzer):
        result = analyzer.analyze_swot({})
        assert len(result["strengths"]) > 0
        assert len(result["weaknesses"]) > 0
        assert len(result["opportunities"]) > 0
        assert len(result["threats"]) > 0

    def test_technology_keywords_detected(self, analyzer):
        project = _make_project()
        project["technology"] = "区块链"
        result = analyzer.analyze_swot(project)
        text = " ".join(result["strengths"])
        assert "区块链" in text or "技术" in text

    def test_innovation_keywords_detected(self, analyzer):
        project = _make_project()
        project["innovation"] = "自主创新的核心算法"
        result = analyzer.analyze_swot(project)
        text = " ".join(result["strengths"])
        assert "创新" in text


# ---------------------------------------------------------------------------
# CompetitorAnalyzer - Competitor Comparison
# ---------------------------------------------------------------------------

class TestCompetitorComparison:
    """Test the compare_competitors method."""

    def test_returns_matrix_and_advantage(self, analyzer, project, competitors):
        result = analyzer.compare_competitors(project, competitors)
        assert "comparison_matrix" in result
        assert "competitive_advantage" in result

    def test_matrix_includes_all_parties(self, analyzer, project, competitors):
        result = analyzer.compare_competitors(project, competitors)
        matrix = result["comparison_matrix"]
        # 1 our project + 2 competitors = 3 rows
        assert len(matrix) == 3
        names = [row["name"] for row in matrix]
        assert "我方项目" in names
        assert "竞品A" in names
        assert "竞品B" in names

    def test_matrix_rows_have_required_keys(self, analyzer, project, competitors):
        result = analyzer.compare_competitors(project, competitors)
        for row in result["comparison_matrix"]:
            assert "name" in row
            assert "strength_count" in row
            assert "weakness_count" in row
            assert "competitive_score" in row
            assert "market_share" in row

    def test_competitive_scores_are_numeric(self, analyzer, project, competitors):
        result = analyzer.compare_competitors(project, competitors)
        for row in result["comparison_matrix"]:
            assert isinstance(row["competitive_score"], (int, float))
            assert 0 <= row["competitive_score"] <= 100

    def test_advantage_is_string(self, analyzer, project, competitors):
        result = analyzer.compare_competitors(project, competitors)
        assert isinstance(result["competitive_advantage"], str)
        assert len(result["competitive_advantage"]) > 0

    def test_empty_competitors_returns_empty_matrix(self, analyzer, project):
        result = analyzer.compare_competitors(project, [])
        assert result["comparison_matrix"] == []

    def test_market_share_formatting(self, analyzer, project):
        competitors = [
            {"name": "对手X", "strengths": ["强"], "weaknesses": [], "market_share": 25}
        ]
        result = analyzer.compare_competitors(project, competitors)
        comp_row = result["comparison_matrix"][1]
        assert comp_row["market_share"] == "25%"


# ---------------------------------------------------------------------------
# CompetitorAnalyzer - Competitive Strategy
# ---------------------------------------------------------------------------

class TestCompetitiveStrategy:
    """Test the generate_competitive_strategy method."""

    def test_returns_strategies(self, analyzer, project, competitors):
        result = analyzer.generate_competitive_strategy(project, competitors)
        assert "strategies" in result
        assert "total_count" in result
        assert isinstance(result["strategies"], list)
        assert len(result["strategies"]) > 0
        assert result["total_count"] == len(result["strategies"])

    def test_strategy_structure(self, analyzer, project, competitors):
        result = analyzer.generate_competitive_strategy(project, competitors)
        for strategy in result["strategies"]:
            assert "name" in strategy
            assert "priority" in strategy
            assert "description" in strategy
            assert strategy["priority"] in ("高", "中", "低")

    def test_strategies_sorted_by_priority(self, analyzer, project, competitors):
        result = analyzer.generate_competitive_strategy(project, competitors)
        priority_order = {"高": 0, "中": 1, "低": 2}
        for i in range(len(result["strategies"]) - 1):
            curr = priority_order.get(result["strategies"][i]["priority"], 3)
            nxt = priority_order.get(result["strategies"][i + 1]["priority"], 3)
            assert curr <= nxt

    def test_ai_project_gets_tech_strategy(self, analyzer):
        project = _make_project()
        result = analyzer.generate_competitive_strategy(project, [])
        names = [s["name"] for s in result["strategies"]]
        assert "技术壁垒构建" in names

    def test_startup_stage_gets_iteration_strategy(self, analyzer):
        project = _make_project()
        result = analyzer.generate_competitive_strategy(project, [])
        names = [s["name"] for s in result["strategies"]]
        assert "快速验证与迭代" in names

    def test_saas_model_gets_platform_strategy(self, analyzer):
        project = _make_project()
        result = analyzer.generate_competitive_strategy(project, [])
        names = [s["name"] for s in result["strategies"]]
        assert "平台生态构建" in names

    def test_education_market_gets_vertical_strategy(self, analyzer):
        project = _make_project()
        result = analyzer.generate_competitive_strategy(project, [])
        names = [s["name"] for s in result["strategies"]]
        assert "垂直领域深耕" in names

    def test_strong_competitors_trigger_differentiation(self, analyzer, project):
        competitors = [
            {"name": "巨头", "strengths": ["垄断"], "weaknesses": [], "market_share": 50}
        ]
        result = analyzer.generate_competitive_strategy(project, competitors)
        names = [s["name"] for s in result["strategies"]]
        assert "差异化竞争" in names

    def test_empty_project_gets_fallback_strategy(self, analyzer):
        result = analyzer.generate_competitive_strategy({}, [])
        assert len(result["strategies"]) >= 1

    def test_social_impact_strategy(self, analyzer):
        project = _make_project()
        result = analyzer.generate_competitive_strategy(project, [])
        names = [s["name"] for s in result["strategies"]]
        assert "社会价值驱动" in names


# ---------------------------------------------------------------------------
# CompetitorAnalyzer - Market Position
# ---------------------------------------------------------------------------

class TestMarketPosition:
    """Test the analyze_market_position method."""

    def test_returns_position_keys(self, analyzer, project):
        result = analyzer.analyze_market_position(project)
        assert "position" in result
        assert "score" in result
        assert "analysis" in result
        assert "recommendations" in result

    def test_position_is_valid_label(self, analyzer, project):
        result = analyzer.analyze_market_position(project)
        assert result["position"] in ("leader", "challenger", "follower", "niche")

    def test_score_between_zero_and_one(self, analyzer, project):
        result = analyzer.analyze_market_position(project)
        assert 0.0 <= result["score"] <= 1.0

    def test_analysis_is_string(self, analyzer, project):
        result = analyzer.analyze_market_position(project)
        assert isinstance(result["analysis"], str)
        assert len(result["analysis"]) > 0

    def test_recommendations_are_list(self, analyzer, project):
        result = analyzer.analyze_market_position(project)
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0

    def test_leader_position_with_strong_data(self, analyzer):
        project = {
            "technology": "AI人工智能",
            "innovation": "自主创新核心技术",
            "project_stage": "成熟",
            "business_model": "SaaS平台",
            "team_background": "博士名校资深专家",
            "target_market": "教育",
            "social_impact": "教育公平可持续发展",
        }
        market_data = {
            "our_market_share": 40,
            "growth_rate": 30,
            "competitor_count": 2,
        }
        result = analyzer.analyze_market_position(project, market_data)
        assert result["position"] == "leader"

    def test_niche_position_for_weak_project(self, analyzer):
        project = {
            "technology": "简单工具",
            "project_stage": "初创种子",
            "target_market": "小众市场",
        }
        market_data = {
            "competitor_count": 15,
        }
        result = analyzer.analyze_market_position(project, market_data)
        assert result["position"] in ("follower", "niche")

    def test_no_market_data_still_works(self, analyzer, project):
        result = analyzer.analyze_market_position(project)
        assert result["position"] in ("leader", "challenger", "follower", "niche")

    def test_leader_recommendations(self, analyzer):
        project = {
            "technology": "AI人工智能",
            "innovation": "自主创新",
            "project_stage": "成熟",
            "business_model": "SaaS",
            "team_background": "博士资深专家",
            "target_market": "教育",
        }
        market_data = {"our_market_share": 50}
        result = analyzer.analyze_market_position(project, market_data)
        if result["position"] == "leader":
            assert any("研发" in r for r in result["recommendations"])


# ---------------------------------------------------------------------------
# Tool Registration and Dispatch
# ---------------------------------------------------------------------------

class TestCompetitorToolsRegistration:
    """Test that competitor tools register correctly."""

    def test_tools_register(self):
        from aurora.tools.competitor_tools import _register_tools
        registry = ToolRegistry()
        _register_tools(registry)
        tools = registry.list_tools()
        assert "competitor_swot" in tools
        assert "competitor_compare" in tools
        assert "competitor_strategy" in tools
        assert "competitor_market_position" in tools

    def test_tool_count(self):
        from aurora.tools.competitor_tools import _register_tools
        registry = ToolRegistry()
        _register_tools(registry)
        assert len(registry.list_tools()) == 4

    def test_schemas_are_valid(self):
        from aurora.tools.competitor_tools import _register_tools
        registry = ToolRegistry()
        _register_tools(registry)
        schemas = registry.get_schemas()
        assert len(schemas) == 4
        for schema in schemas:
            assert schema["type"] == "function"
            assert "function" in schema
            assert "name" in schema["function"]
            assert "description" in schema["function"]


class TestCompetitorToolsDispatch:
    """Test competitor tool dispatch (end-to-end via registry)."""

    def _make_registry(self):
        from aurora.tools.competitor_tools import _register_tools
        registry = ToolRegistry()
        _register_tools(registry)
        return registry

    def test_swot_dispatch(self):
        registry = self._make_registry()
        result_str = registry.dispatch("competitor_swot", {
            "project_info": _make_project()
        })
        result = json.loads(result_str)
        assert "result" in result
        assert "data" in result
        data = result["data"]
        assert "strengths" in data
        assert "weaknesses" in data
        assert "opportunities" in data
        assert "threats" in data

    def test_swot_dispatch_missing_params(self):
        registry = self._make_registry()
        result_str = registry.dispatch("competitor_swot", {})
        result = json.loads(result_str)
        assert "error" in result

    def test_compare_dispatch(self):
        registry = self._make_registry()
        result_str = registry.dispatch("competitor_compare", {
            "our_project": _make_project(),
            "competitors": _make_competitors(),
        })
        result = json.loads(result_str)
        assert "result" in result
        assert "data" in result
        data = result["data"]
        assert "comparison_matrix" in data
        assert "competitive_advantage" in data
        assert len(data["comparison_matrix"]) == 3

    def test_compare_dispatch_missing_project(self):
        registry = self._make_registry()
        result_str = registry.dispatch("competitor_compare", {
            "competitors": []
        })
        result = json.loads(result_str)
        assert "error" in result

    def test_compare_dispatch_empty_competitors(self):
        registry = self._make_registry()
        result_str = registry.dispatch("competitor_compare", {
            "our_project": _make_project(),
            "competitors": [],
        })
        result = json.loads(result_str)
        # Empty competitors list returns an error from the handler
        assert "error" in result

    def test_strategy_dispatch(self):
        registry = self._make_registry()
        result_str = registry.dispatch("competitor_strategy", {
            "project_info": _make_project(),
            "competitors": _make_competitors(),
        })
        result = json.loads(result_str)
        assert "result" in result
        data = result["data"]
        assert "strategies" in data
        assert len(data["strategies"]) > 0

    def test_strategy_dispatch_missing_project(self):
        registry = self._make_registry()
        result_str = registry.dispatch("competitor_strategy", {
            "competitors": []
        })
        result = json.loads(result_str)
        assert "error" in result

    def test_market_position_dispatch(self):
        registry = self._make_registry()
        result_str = registry.dispatch("competitor_market_position", {
            "project_info": _make_project(),
            "market_data": {"growth_rate": 25, "competitor_count": 5},
        })
        result = json.loads(result_str)
        assert "result" in result
        data = result["data"]
        assert data["position"] in ("leader", "challenger", "follower", "niche")

    def test_market_position_dispatch_no_market_data(self):
        registry = self._make_registry()
        result_str = registry.dispatch("competitor_market_position", {
            "project_info": _make_project(),
        })
        result = json.loads(result_str)
        assert "result" in result

    def test_market_position_dispatch_missing_project(self):
        registry = self._make_registry()
        result_str = registry.dispatch("competitor_market_position", {})
        result = json.loads(result_str)
        assert "error" in result

    def test_unknown_tool_returns_error(self):
        registry = self._make_registry()
        result_str = registry.dispatch("nonexistent_competitor_tool", {})
        result = json.loads(result_str)
        assert "error" in result

    def test_dispatch_results_are_valid_json(self):
        registry = self._make_registry()
        project = _make_project()
        competitors = _make_competitors()

        for tool_name, args in [
            ("competitor_swot", {"project_info": project}),
            ("competitor_compare", {"our_project": project, "competitors": competitors}),
            ("competitor_strategy", {"project_info": project, "competitors": competitors}),
            ("competitor_market_position", {"project_info": project}),
        ]:
            result_str = registry.dispatch(tool_name, args)
            # Should not raise
            parsed = json.loads(result_str)
            assert isinstance(parsed, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
