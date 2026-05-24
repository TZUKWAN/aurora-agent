"""Tests for quality auditor and optimizer."""

import json

import pytest

from aurora.quality.auditor import PlanAuditor
from aurora.quality.optimizer import PlanOptimizer
from aurora.tools.registry import ToolRegistry
from aurora.tools.quality_tools import _register_tools


def _make_plan(sections_override=None):
    """Create a test plan."""
    default_sections = {
        "executive_summary": {"title": "Summary", "content": "A" * 200, "word_count": 100},
        "project_overview": {"title": "Overview", "content": "B" * 200, "word_count": 100},
        "market_analysis": {"title": "Market", "content": "C" * 200, "word_count": 100},
        "business_model": {"title": "Model", "content": "D" * 200, "word_count": 100},
        "financial_analysis": {"title": "Finance", "content": "Revenue 100万", "word_count": 100},
    }
    if sections_override:
        default_sections.update(sections_override)
    return {
        "metadata": {"competition": "test"},
        "sections": default_sections,
    }


class TestPlanAuditor:
    def test_audit_good_plan(self):
        plan = _make_plan()
        auditor = PlanAuditor()
        report = auditor.audit(plan)
        assert report["score"] >= 70
        assert "issues" in report

    def test_audit_empty_section(self):
        plan = _make_plan({"executive_summary": {"title": "Summary", "content": "", "word_count": 0}})
        auditor = PlanAuditor()
        report = auditor.audit(plan)
        assert any(i["severity"] == "critical" for i in report["issues"])

    def test_audit_short_section(self):
        plan = _make_plan({"project_overview": {"title": "Overview", "content": "short", "word_count": 1}})
        auditor = PlanAuditor()
        report = auditor.audit(plan)
        assert any("too short" in i["message"] for i in report["issues"])

    def test_audit_weak_phrases(self):
        plan = _make_plan({
            "market_analysis": {"title": "Market", "content": "我们将不断优化产品，持续提升服务质量", "word_count": 20}
        })
        auditor = PlanAuditor()
        report = auditor.audit(plan)
        assert any("Vague phrase" in i["message"] for i in report["issues"])

    def test_audit_missing_section(self):
        plan = {"metadata": {}, "sections": {}}
        auditor = PlanAuditor()
        report = auditor.audit(plan)
        assert len(report["critical"]) >= 1

    def test_audit_section_single(self):
        auditor = PlanAuditor()
        result = auditor.audit_section("test", "")
        assert len(result["issues"]) > 0

    def test_audit_score_range(self):
        plan = _make_plan()
        auditor = PlanAuditor()
        report = auditor.audit(plan)
        assert 0 <= report["score"] <= 100


class TestPlanOptimizer:
    def test_optimize_no_issues(self):
        plan = _make_plan()
        audit = {"critical": [], "warnings": [], "score": 100}
        optimizer = PlanOptimizer()
        result = optimizer.optimize(plan, audit)
        assert result == plan

    def test_optimize_empty_section(self):
        plan = _make_plan({"executive_summary": {"title": "Summary", "content": "", "word_count": 0}})
        audit = {"critical": [{"section": "executive_summary", "severity": "critical", "message": "empty"}], "warnings": []}
        optimizer = PlanOptimizer()
        result = optimizer.optimize(plan, audit)
        content = result["sections"]["executive_summary"]["content"]
        assert len(content) > 0

    def test_optimize_section_short(self):
        optimizer = PlanOptimizer()
        result = optimizer.optimize_section("test", "hi", [{"message": "too short"}])
        assert len(result) > 2


class TestQualityTools:
    def test_tools_registered(self):
        tools = ToolRegistry()
        _register_tools(tools)
        assert "plan_audit" in tools.list_tools()
        assert "plan_optimize" in tools.list_tools()

    def test_audit_tool(self):
        tools = ToolRegistry()
        _register_tools(tools)
        plan = _make_plan()
        result = json.loads(tools.dispatch("plan_audit", {"plan": plan}))
        assert "report" in result
        assert result["report"]["score"] >= 0

    def test_optimize_tool(self):
        tools = ToolRegistry()
        _register_tools(tools)
        plan = _make_plan({"executive_summary": {"title": "Summary", "content": "", "word_count": 0}})
        audit_report = {"critical": [{"section": "executive_summary", "severity": "critical", "message": "empty"}], "warnings": []}
        result = json.loads(tools.dispatch("plan_optimize", {"plan": plan, "audit_report": audit_report}))
        assert "plan" in result
