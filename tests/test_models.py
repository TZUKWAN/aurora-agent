"""Tests for Pydantic models and parser."""

import pytest

from aurora.models.project import ProjectInfo
from aurora.models.plan import BusinessPlan, PlanSection, PlanMetadata
from aurora.models.evaluation import EvaluationResult, DimensionScore
from aurora.parser import _keyword_extract, parse_project_input


class TestProjectInfo:
    def test_default_values(self):
        info = ProjectInfo()
        assert info.project_name == ""
        assert info.funding == "50万"

    def test_from_dict(self):
        data = {"technology": "AI", "target_market": "K-12", "unknown_field": "ignored"}
        info = ProjectInfo.from_dict(data)
        assert info.technology == "AI"
        assert info.target_market == "K-12"

    def test_to_dict_excludes_empty(self):
        info = ProjectInfo(technology="AI", project_name="")
        d = info.to_dict()
        assert "technology" in d
        assert "project_name" not in d

    def test_to_dict_includes_nonempty(self):
        info = ProjectInfo(technology="AI", project_name="Test")
        d = info.to_dict()
        assert d["technology"] == "AI"
        assert d["project_name"] == "Test"


class TestBusinessPlan:
    def test_empty_plan(self):
        plan = BusinessPlan()
        assert plan.sections == {}

    def test_plan_with_sections(self):
        plan = BusinessPlan(
            metadata=PlanMetadata(competition="internet_plus"),
            sections={"exec": PlanSection(title="Summary", content="Test content")}
        )
        assert plan.metadata.competition == "internet_plus"
        assert "exec" in plan.sections

    def test_section_word_count(self):
        s = PlanSection(title="Test", content="Hello world", word_count=2)
        assert s.word_count == 2


class TestEvaluationResult:
    def test_empty_result(self):
        r = EvaluationResult()
        assert r.overall_score == 0.0
        assert r.dimensions == []

    def test_result_with_dimensions(self):
        r = EvaluationResult(
            overall_score=75.0,
            dimensions=[
                DimensionScore(name="Innovation", score=80.0, weight=0.3),
            ]
        )
        assert r.overall_score == 75.0
        assert len(r.dimensions) == 1


class TestParser:
    def test_keyword_extract_ai(self):
        info = _keyword_extract("Our project uses AI for education")
        assert "AI" in info.technology or "人工智能" in info.technology

    def test_keyword_extract_k12(self):
        info = _keyword_extract("Targeting K-12 students")
        assert info.target_market in ("K-12学生", "教育")

    def test_parse_falls_back_to_keyword(self):
        # Without API key, should fall back to keyword extraction
        info = parse_project_input("AI education project")
        assert isinstance(info, ProjectInfo)

    def test_parse_returns_project_info(self):
        info = parse_project_input("We are building an AI-powered learning platform")
        assert isinstance(info, ProjectInfo)
