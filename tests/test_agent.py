"""Tests for AuroraAgent core functionality."""

import pytest

from aurora.agent import AuroraAgent
from aurora.competition.database import CompetitionDatabase
from aurora.competition.track_matcher import TrackMatcher


class TestCompetitionDatabase:
    """Test competition database functionality."""

    def test_list_competitions(self):
        """Test listing all competitions."""
        db = CompetitionDatabase()
        competitions = db.list_competitions()
        assert len(competitions) > 0

    def test_search_competitions(self):
        """Test searching competitions."""
        db = CompetitionDatabase()
        results = db.search_competitions("互联网")
        assert len(results) >= 1
        assert any(c.name == "互联网+大赛" for c in results)

    def test_get_competition(self):
        """Test getting a specific competition."""
        db = CompetitionDatabase()
        comp = db.get_competition("internet_plus")
        assert comp is not None
        assert comp.name == "互联网+大赛"


class TestTrackMatcher:
    """Test track matching functionality."""

    def test_match_basic(self):
        """Test basic track matching."""
        matcher = TrackMatcher()
        project_info = {
            "technology": "AI人工智能",
            "target_market": "企业服务",
            "business_model": "SaaS订阅",
            "project_stage": "初创"
        }
        results = matcher.match(project_info)
        assert len(results) > 0

    def test_match_rural(self):
        """Test matching rural track."""
        matcher = TrackMatcher()
        project_info = {
            "technology": "农业科技",
            "target_market": "乡村农村",
            "social_impact": "乡村振兴"
        }
        results = matcher.match(project_info)
        assert len(results) > 0


class TestBusinessPlanGenerator:
    """Test business plan generation."""

    def test_generate_plan(self):
        """Test generating a business plan."""
        from aurora.business_plan.generator import BusinessPlanGenerator
        
        generator = BusinessPlanGenerator()
        project_info = {
            "project_name": "AI智能助手",
            "technology": "人工智能",
            "problem": "效率低下",
            "solution": "智能解决方案",
            "product": "AI助手",
            "target_market": "企业",
            "business_model": "订阅",
            "team_background": "高校团队"
        }
        
        plan = generator.generate(project_info)
        assert "metadata" in plan
        assert "sections" in plan
        assert len(plan["sections"]) == 10


class TestEvaluationEngine:
    """Test evaluation engine."""

    def test_evaluate(self):
        """Test project evaluation."""
        from aurora.evaluation.engine import EvaluationEngine
        
        engine = EvaluationEngine()
        project_info = {
            "technology": "AI人工智能",
            "innovation": "原创算法",
            "team_background": "985高校团队",
            "business_model": "盈利模式清晰",
            "social_impact": "带动就业"
        }
        
        result = engine.evaluate(project_info)
        assert "overall_score" in result
        assert "dimensions" in result
        assert 0 <= result["overall_score"] <= 100


class TestPPTGenerator:
    """Test PPT generation."""

    def test_generate_ppt(self):
        """Test generating PPT content."""
        from aurora.presentation.ppt_generator import PPTGenerator
        
        generator = PPTGenerator()
        project_info = {
            "project_name": "创新项目",
            "team_name": "创新团队",
            "technology": "AI",
            "problem": "痛点",
            "solution": "方案"
        }
        
        ppt = generator.generate(project_info)
        assert "slides" in ppt
        assert ppt["slide_count"] == 12


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
