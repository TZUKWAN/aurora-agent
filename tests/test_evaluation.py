"""Tests for evaluation module."""

import pytest
from aurora.evaluation.engine import EvaluationEngine


class TestEvaluationEngine:
    """Test evaluation engine functionality."""

    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = EvaluationEngine()
        assert engine._comp_db is not None

    def test_evaluate_basic_project(self):
        """Test evaluating a basic project."""
        engine = EvaluationEngine()
        
        project_info = {
            "technology": "AI人工智能",
            "innovation": "原创算法",
            "team_background": "985高校团队",
            "business_model": "盈利模式清晰",
            "social_impact": "带动就业"
        }
        
        result = engine.evaluate(project_info, competition_id="internet_plus")
        
        assert "overall_score" in result
        assert "dimensions" in result
        assert "feedback" in result
        assert "suggestions" in result
        
        # Check score range
        assert 0 <= result["overall_score"] <= 100

    def test_evaluate_dimensions_count(self):
        """Test that all dimensions are evaluated."""
        engine = EvaluationEngine()
        
        project_info = {"technology": "AI"}
        result = engine.evaluate(project_info)
        
        # Should have 5 dimensions for internet_plus
        assert len(result["dimensions"]) == 5

    def test_evaluate_specific_dimensions(self):
        """Test evaluating specific dimensions only."""
        engine = EvaluationEngine()
        
        project_info = {"technology": "AI"}
        dimensions = ["创新性", "团队情况"]
        
        result = engine.evaluate(project_info, dimensions=dimensions)
        
        assert len(result["dimensions"]) == 2
        dim_names = [d["name"] for d in result["dimensions"]]
        assert "创新性" in dim_names
        assert "团队情况" in dim_names

    def test_evaluate_unknown_competition(self):
        """Test evaluating with unknown competition."""
        engine = EvaluationEngine()
        
        project_info = {"technology": "AI"}
        result = engine.evaluate(project_info, competition_id="unknown")
        
        assert "error" in result

    def test_evaluate_innovation_dimension(self):
        """Test innovation dimension evaluation."""
        engine = EvaluationEngine()
        
        # High innovation project
        project_info = {
            "technology": "AI人工智能",
            "innovation": "原创算法",
            "intellectual_property": "已申请专利"
        }
        
        result = engine.evaluate(project_info)
        innovation_dim = next(d for d in result["dimensions"] if d["name"] == "创新性")
        
        assert innovation_dim["score"] >= 70

    def test_evaluate_team_dimension(self):
        """Test team dimension evaluation."""
        engine = EvaluationEngine()
        
        # Good team background
        project_info = {
            "team_background": "985高校团队，创业经验丰富",
            "team_size": "5"
        }
        
        result = engine.evaluate(project_info)
        team_dim = next(d for d in result["dimensions"] if d["name"] == "团队情况")
        
        assert team_dim["score"] >= 60

    def test_evaluate_business_model_dimension(self):
        """Test business model dimension evaluation."""
        engine = EvaluationEngine()
        
        project_info = {
            "business_model": "盈利模式清晰，多元化收入",
            "revenue_model": "订阅+定制"
        }
        
        result = engine.evaluate(project_info)
        business_dim = next(d for d in result["dimensions"] if d["name"] == "商业模式")
        
        assert business_dim["score"] >= 60

    def test_suggestions_generation(self):
        """Test that suggestions are generated."""
        engine = EvaluationEngine()
        
        # Low scoring project
        project_info = {"technology": "一般技术"}
        
        result = engine.evaluate(project_info)
        
        assert len(result["suggestions"]) > 0

    def test_feedback_generation(self):
        """Test that feedback is generated."""
        engine = EvaluationEngine()
        
        project_info = {"technology": "AI"}
        result = engine.evaluate(project_info)
        
        assert len(result["feedback"]) > 0
        assert "综合评价" in result["feedback"]


class TestEvaluationDimensions:
    """Test individual evaluation dimensions."""

    def setup_method(self):
        """Setup for each test."""
        self.engine = EvaluationEngine()

    def test_innovation_evaluation_high(self):
        """Test high innovation evaluation."""
        info = {
            "technology": "AI人工智能",
            "innovation": "原创自主研发",
            "intellectual_property": "已申请专利"
        }
        
        score, feedback, suggestions = self.engine._evaluate_innovation(info)
        
        assert score >= 80
        assert "创新" in feedback or "技术" in feedback

    def test_innovation_evaluation_low(self):
        """Test low innovation evaluation."""
        info = {"technology": "一般技术"}
        
        score, feedback, suggestions = self.engine._evaluate_innovation(info)
        
        assert score < 80
        assert len(suggestions) > 0

    def test_team_evaluation_high(self):
        """Test high team evaluation."""
        info = {
            "team_background": "985高校团队，创业经验丰富",
            "team_size": "5"
        }
        
        score, feedback, suggestions = self.engine._evaluate_team(info)
        
        assert score >= 70

    def test_team_evaluation_low(self):
        """Test low team evaluation."""
        info = {"team_background": "普通团队"}
        
        score, feedback, suggestions = self.engine._evaluate_team(info)
        
        assert score < 70
        assert len(suggestions) > 0

    def test_business_model_evaluation(self):
        """Test business model evaluation."""
        info = {
            "business_model": "盈利模式清晰，多元化收入，可扩展",
            "revenue_model": "订阅+定制"
        }
        
        score, feedback, suggestions = self.engine._evaluate_business_model(info)
        
        assert score >= 60

    def test_employment_evaluation(self):
        """Test employment evaluation."""
        info = {"social_impact": "带动就业，乡村振兴"}
        
        score, feedback, suggestions = self.engine._evaluate_employment(info)
        
        assert score >= 60

    def test_education_evaluation(self):
        """Test education dimension evaluation."""
        info = {"team_background": "大学生团队，专业对口"}
        
        score, feedback, suggestions = self.engine._evaluate_education(info)
        
        assert score >= 60

    def test_social_value_evaluation(self):
        """Test social value evaluation."""
        info = {"social_impact": "乡村振兴，环保绿色，公益"}
        
        score, feedback, suggestions = self.engine._evaluate_social_value(info)
        
        assert score >= 60


class TestEvaluationForDifferentCompetitions:
    """Test evaluation for different competitions."""

    def test_evaluate_for_internet_plus(self):
        """Test evaluation for Internet+ competition."""
        engine = EvaluationEngine()
        
        project_info = {"technology": "AI"}
        result = engine.evaluate(project_info, competition_id="internet_plus")
        
        assert result["competition"] == "互联网+大赛"
        dim_names = [d["name"] for d in result["dimensions"]]
        assert "创新性" in dim_names
        assert "带动就业" in dim_names

    def test_evaluate_for_challenge_cup(self):
        """Test evaluation for Challenge Cup."""
        engine = EvaluationEngine()
        
        project_info = {"technology": "AI"}
        result = engine.evaluate(project_info, competition_id="challenge_cup")
        
        assert result["competition"] == "挑战杯"
        dim_names = [d["name"] for d in result["dimensions"]]
        assert "社会价值" in dim_names
        assert "科技创新" in dim_names

    def test_evaluate_for_san_chuang(self):
        """Test evaluation for San Chuang."""
        engine = EvaluationEngine()
        
        project_info = {"technology": "AI"}
        result = engine.evaluate(project_info, competition_id="san_chuang")
        
        assert result["competition"] == "三创赛"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
