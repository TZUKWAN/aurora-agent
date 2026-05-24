"""Tests for PPTXExporter."""

import json
import os
import tempfile

import pytest

from aurora.presentation.ppt_generator import PPTGenerator, export_to_pptx
from aurora.presentation.pptx_exporter import PPTXExporter, THEMES
from aurora.tools.registry import ToolRegistry
from aurora.tools.presentation_tools import _register_tools


@pytest.fixture
def project_info():
    return {
        "project_name": "AI Smart Education",
        "team_name": "Team Alpha",
        "technology": "AI/NLP",
        "problem": "Inefficient learning",
        "solution": "Personalized AI tutor",
        "product": "AI Tutor App",
        "features": ["Adaptive learning", "Real-time feedback", "Progress tracking"],
        "target_market": "K-12 students",
        "market_size": "100 billion",
        "business_model": "SaaS subscription",
        "revenue_model": "Monthly subscription",
        "team_background": "Tsinghua University team",
        "funding": "500K",
        "equity": "10%",
        "tagline": "AI makes learning smarter",
    }


@pytest.fixture
def ppt_content(project_info):
    gen = PPTGenerator()
    return gen.generate(project_info)


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    for f in os.listdir(d):
        os.unlink(os.path.join(d, f))
    os.rmdir(d)


class TestPPTXExporter:
    def test_export_creates_file(self, ppt_content, tmp_dir):
        path = os.path.join(tmp_dir, "test.pptx")
        exporter = PPTXExporter()
        result = exporter.export(ppt_content, path)
        assert result["success"] is True
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_export_all_themes(self, ppt_content, tmp_dir):
        for theme_name in THEMES:
            path = os.path.join(tmp_dir, f"test_{theme_name}.pptx")
            exporter = PPTXExporter(theme=theme_name)
            result = exporter.export(ppt_content, path)
            assert result["success"] is True
            assert os.path.exists(path)

    def test_export_function(self, ppt_content, tmp_dir):
        path = os.path.join(tmp_dir, "func_test.pptx")
        result = export_to_pptx(ppt_content, path, theme="tech")
        assert result["success"] is True
        assert os.path.exists(path)

    def test_export_invalid_theme_uses_default(self, ppt_content, tmp_dir):
        path = os.path.join(tmp_dir, "invalid_theme.pptx")
        exporter = PPTXExporter(theme="nonexistent")
        result = exporter.export(ppt_content, path)
        assert result["success"] is True

    def test_slide_count_matches(self, ppt_content, tmp_dir):
        path = os.path.join(tmp_dir, "count.pptx")
        exporter = PPTXExporter()
        exporter.export(ppt_content, path)
        from pptx import Presentation
        prs = Presentation(path)
        assert len(prs.slides) == ppt_content["slide_count"]


class TestPPTExportTool:
    def test_ppt_export_tool_registered(self):
        tools = ToolRegistry()
        _register_tools(tools)
        assert "ppt_export" in tools.list_tools()

    def test_ppt_export_tool_works(self, ppt_content, tmp_dir):
        tools = ToolRegistry()
        _register_tools(tools)
        path = os.path.join(tmp_dir, "tool_test.pptx")
        result = json.loads(
            tools.dispatch("ppt_export", {
                "ppt_content": ppt_content,
                "filepath": path,
                "theme": "business_blue"
            })
        )
        assert result["success"] is True
        assert os.path.exists(path)

    def test_ppt_export_tool_missing_content(self, tmp_dir):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(
            tools.dispatch("ppt_export", {
                "filepath": os.path.join(tmp_dir, "fail.pptx")
            })
        )
        assert "error" in result
