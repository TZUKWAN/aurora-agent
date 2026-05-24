"""Tests for plan editor."""

import json

import pytest

from aurora.business_plan.editor import PlanEditor
from aurora.tools.registry import ToolRegistry
from aurora.tools.editor_tools import _register_tools


def _make_plan():
    return {
        "metadata": {"competition": "test"},
        "sections": {
            "executive_summary": {"title": "Summary", "content": "A" * 300},
            "project_overview": {"title": "Overview", "content": "B" * 300},
            "market_analysis": {"title": "Market", "content": "C" * 300},
            "business_model": {"title": "Model", "content": "D" * 300},
            "financial_analysis": {"title": "Finance", "content": "E" * 300},
        },
    }


class TestPlanEditor:
    def test_update_section(self):
        editor = PlanEditor(_make_plan())
        assert editor.update_section("executive_summary", "New content")
        assert editor.plan["sections"]["executive_summary"]["content"] == "New content"

    def test_update_nonexistent(self):
        editor = PlanEditor(_make_plan())
        assert not editor.update_section("nonexistent", "x")

    def test_reorder_sections(self):
        editor = PlanEditor(_make_plan())
        assert editor.reorder_sections(["market_analysis", "executive_summary"])
        keys = list(editor.plan["sections"].keys())
        assert keys[0] == "market_analysis"

    def test_merge_sections(self):
        editor = PlanEditor(_make_plan())
        assert editor.merge_sections(["executive_summary", "project_overview"], "Combined")
        assert "executive_summary_project_overview" in editor.plan["sections"]
        assert "executive_summary" not in editor.plan["sections"]

    def test_merge_needs_two(self):
        editor = PlanEditor(_make_plan())
        assert not editor.merge_sections(["executive_summary"])

    def test_split_section(self):
        editor = PlanEditor(_make_plan())
        assert editor.split_section("executive_summary", [150])
        assert "executive_summary_1" in editor.plan["sections"]
        assert "executive_summary" not in editor.plan["sections"]

    def test_validate_valid(self):
        editor = PlanEditor(_make_plan())
        result = editor.validate_plan()
        assert result["valid"] is True

    def test_validate_missing_section(self):
        plan = {"metadata": {}, "sections": {"executive_summary": {"title": "S", "content": "A" * 300}}}
        editor = PlanEditor(plan)
        result = editor.validate_plan()
        assert result["valid"] is False
        assert any(i["issue"] == "missing" for i in result["issues"])

    def test_get_diff(self):
        editor = PlanEditor(_make_plan())
        editor.update_section("executive_summary", "Completely new")
        diff = editor.get_diff()
        assert isinstance(diff, str)

    def test_to_dict(self):
        editor = PlanEditor(_make_plan())
        d = editor.to_dict()
        assert "sections" in d
        assert "metadata" in d


class TestEditorTools:
    def test_tools_registered(self):
        tools = ToolRegistry()
        _register_tools(tools)
        assert "plan_edit_section" in tools.list_tools()
        assert "plan_validate" in tools.list_tools()
        assert "plan_word_count" in tools.list_tools()

    def test_edit_tool(self):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(tools.dispatch("plan_edit_section", {
            "plan": _make_plan(),
            "section_id": "executive_summary",
            "new_content": "Updated"
        }))
        assert "plan" in result

    def test_validate_tool(self):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(tools.dispatch("plan_validate", {"plan": _make_plan()}))
        assert result["validation"]["valid"] is True

    def test_word_count_tool(self):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(tools.dispatch("plan_word_count", {"plan": _make_plan()}))
        assert "counts" in result
