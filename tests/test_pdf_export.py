"""Tests for PDF export functionality."""

import json
import os

import pytest

from aurora.export.pdf_exporter import PDFExporter, THEMES
from aurora.tools.registry import ToolRegistry


def _make_plan():
    """Create a sample plan for testing."""
    return {
        "metadata": {
            "project_name": "Test Project",
            "team_name": "Test Team",
            "competition": "Internet Plus",
            "track": "AI Track",
        },
        "sections": {
            "executive_summary": {
                "title": "Executive Summary",
                "content": "A" * 300,
            },
            "project_overview": {
                "title": "Project Overview",
                "content": "B" * 200,
            },
            "market_analysis": {
                "title": "Market Analysis",
                "content": (
                    "Market content with 【sub-heading】 details here.\n"
                    "- First bullet point\n"
                    "- Second bullet point\n"
                    "1. First numbered item\n"
                    "2. Second numbered item"
                ),
            },
        },
    }


class TestPDFExporterCreation:
    """Test PDFExporter instantiation."""

    def test_create_default(self):
        exporter = PDFExporter()
        assert exporter is not None
        assert exporter.config == {}
        assert exporter.font is not None

    def test_create_with_config(self):
        config = {"page_size": "A4"}
        exporter = PDFExporter(config=config)
        assert exporter.config == config


class TestPDFExportBasic:
    """Test basic PDF export functionality."""

    def test_export_valid_plan_produces_file(self, tmp_path):
        exporter = PDFExporter()
        plan = _make_plan()
        output = str(tmp_path / "output.pdf")

        result = exporter.export(plan, output)

        assert result is True
        assert os.path.isfile(output)
        assert os.path.getsize(output) > 0

    def test_export_file_is_valid_pdf(self, tmp_path):
        exporter = PDFExporter()
        plan = _make_plan()
        output = str(tmp_path / "valid.pdf")

        exporter.export(plan, output)

        with open(output, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"

    def test_export_creates_parent_directory(self, tmp_path):
        exporter = PDFExporter()
        plan = _make_plan()
        output = str(tmp_path / "subdir" / "nested" / "output.pdf")

        result = exporter.export(plan, output)

        assert result is True
        assert os.path.isfile(output)


class TestPDFExportThemes:
    """Test PDF export with different themes."""

    @pytest.mark.parametrize("theme", ["business", "tech", "minimal"])
    def test_export_with_theme(self, tmp_path, theme):
        exporter = PDFExporter()
        plan = _make_plan()
        output = str(tmp_path / f"{theme}.pdf")

        result = exporter.export(plan, output, theme=theme)

        assert result is True
        assert os.path.isfile(output)
        assert os.path.getsize(output) > 0

    def test_export_with_invalid_theme_falls_back(self, tmp_path):
        exporter = PDFExporter()
        plan = _make_plan()
        output = str(tmp_path / "fallback.pdf")

        result = exporter.export(plan, output, theme="nonexistent")

        assert result is True
        assert os.path.isfile(output)

    def test_themes_have_required_keys(self):
        required_keys = {"header_color", "accent_color", "text_color", "light_bg"}
        for theme_name, theme_data in THEMES.items():
            assert required_keys.issubset(set(theme_data.keys())), (
                f"Theme {theme_name} missing keys"
            )


class TestPDFExportEmptySections:
    """Test export with empty or minimal sections."""

    def test_export_empty_sections(self, tmp_path):
        exporter = PDFExporter()
        plan = {"metadata": {}, "sections": {}}
        output = str(tmp_path / "empty.pdf")

        result = exporter.export(plan, output)

        assert result is True
        assert os.path.isfile(output)

    def test_export_with_empty_content_strings(self, tmp_path):
        exporter = PDFExporter()
        plan = {
            "metadata": {"project_name": "Empty Content Test"},
            "sections": {
                "executive_summary": {
                    "title": "Empty Summary",
                    "content": "",
                },
                "project_overview": {
                    "title": "Whitespace Overview",
                    "content": "   ",
                },
            },
        }
        output = str(tmp_path / "empty_content.pdf")

        result = exporter.export(plan, output)

        assert result is True
        assert os.path.isfile(output)

    def test_export_no_metadata(self, tmp_path):
        exporter = PDFExporter()
        plan = {
            "sections": {
                "executive_summary": {
                    "title": "Summary",
                    "content": "Some content",
                }
            }
        }
        output = str(tmp_path / "no_meta.pdf")

        result = exporter.export(plan, output)

        assert result is True


class TestPDFBuildCover:
    """Test cover page building."""

    def test_build_cover_with_metadata(self):
        exporter = PDFExporter()
        theme_data = THEMES["business"]
        styles = exporter._build_styles(theme_data)
        metadata = {
            "project_name": "Cover Test",
            "team_name": "Team Alpha",
            "competition": "Test Comp",
            "track": "Track A",
        }

        elements = exporter._build_cover(metadata, styles, theme_data)

        assert len(elements) > 0
        # Should end with PageBreak
        from reportlab.platypus import PageBreak as PB

        assert any(isinstance(e, PB) for e in elements)

    def test_build_cover_empty_metadata(self):
        exporter = PDFExporter()
        theme_data = THEMES["business"]
        styles = exporter._build_styles(theme_data)

        elements = exporter._build_cover({}, styles, theme_data)

        assert len(elements) > 0


class TestPDFBuildSection:
    """Test section building with various content formats."""

    def test_build_section_with_subheadings(self):
        exporter = PDFExporter()
        theme_data = THEMES["business"]
        styles = exporter._build_styles(theme_data)
        section = {
            "title": "Test Section",
            "content": "【Important Point】This is the detail that follows.\nRegular text after.",
        }

        elements = exporter._build_section("test", section, styles, theme_data)

        assert len(elements) > 0

    def test_build_section_with_bullet_points(self):
        exporter = PDFExporter()
        theme_data = THEMES["business"]
        styles = exporter._build_styles(theme_data)
        section = {
            "title": "Bullet Section",
            "content": (
                "Intro line\n"
                "- First bullet\n"
                "- Second bullet\n"
                "• Third bullet with unicode char"
            ),
        }

        elements = exporter._build_section("test", section, styles, theme_data)

        assert len(elements) > 0

    def test_build_section_with_numbered_items(self):
        exporter = PDFExporter()
        theme_data = THEMES["business"]
        styles = exporter._build_styles(theme_data)
        section = {
            "title": "Numbered Section",
            "content": "1. First item\n2. Second item\n3. Third item",
        }

        elements = exporter._build_section("test", section, styles, theme_data)

        assert len(elements) > 0

    def test_build_section_standalone_subheading(self):
        exporter = PDFExporter()
        theme_data = THEMES["business"]
        styles = exporter._build_styles(theme_data)
        section = {
            "title": "Subheading Test",
            "content": "Intro\n【Standalone Heading】\nMore content",
        }

        elements = exporter._build_section("test", section, styles, theme_data)

        assert len(elements) > 0

    def test_build_section_string_section(self):
        exporter = PDFExporter()
        theme_data = THEMES["business"]
        styles = exporter._build_styles(theme_data)

        elements = exporter._build_section(
            "test", "Just a plain string", styles, theme_data
        )

        assert len(elements) > 0

    def test_build_section_with_xml_chars(self):
        exporter = PDFExporter()
        theme_data = THEMES["business"]
        styles = exporter._build_styles(theme_data)
        section = {
            "title": "XML <Test>",
            "content": "Content with <brackets> & special <chars>",
        }

        elements = exporter._build_section("test", section, styles, theme_data)

        assert len(elements) > 0


class TestExportToolRegistration:
    """Test tool registration and dispatch."""

    def test_register_export_tool(self):
        registry = ToolRegistry()
        from aurora.tools.export_tools import _register_tools

        _register_tools(registry)

        tools = registry.list_tools()
        assert "export_pdf" in tools

    def test_dispatch_export_pdf(self, tmp_path):
        from aurora.tools.export_tools import _register_tools

        registry = ToolRegistry()
        _register_tools(registry)

        output = str(tmp_path / "tool_export.pdf")
        result_str = registry.dispatch(
            "export_pdf",
            {
                "plan": _make_plan(),
                "output_path": output,
                "theme": "business",
            },
        )

        result = json.loads(result_str)
        assert "result" in result
        assert result["result"] == "PDF exported successfully"
        assert os.path.isfile(output)

    def test_dispatch_export_pdf_missing_plan(self):
        from aurora.tools.export_tools import _register_tools

        registry = ToolRegistry()
        _register_tools(registry)

        result_str = registry.dispatch("export_pdf", {"output_path": "/tmp/x.pdf"})

        result = json.loads(result_str)
        assert "error" in result

    def test_dispatch_export_pdf_missing_path(self):
        from aurora.tools.export_tools import _register_tools

        registry = ToolRegistry()
        _register_tools(registry)

        result_str = registry.dispatch("export_pdf", {"plan": _make_plan()})

        result = json.loads(result_str)
        assert "error" in result
