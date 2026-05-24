"""Tests for visual chart generation and tool registration."""

import json

import pytest

from aurora.visuals.charts import ChartGenerator
from aurora.tools.registry import ToolRegistry
from aurora.tools.visual_tools import _register_tools


# --- Sample data ---

BAR_DATA = {"labels": ["Q1", "Q2", "Q3", "Q4"], "values": [100, 200, 150, 300]}
PIE_DATA = {"labels": ["A", "B", "C"], "values": [40, 35, 25]}
LINE_DATA = {
    "labels": ["Jan", "Feb", "Mar"],
    "series": [{"name": "Revenue", "values": [10, 20, 30]}],
}
TABLE_DATA = {
    "headers": ["Feature", "Us", "Comp A"],
    "rows": [["Price", "$10", "$20"], ["Speed", "Fast", "Slow"]],
}
KPI_DATA = [
    {"label": "Revenue", "value": "$1M", "change": "+20%"},
    {"label": "Users", "value": "50K", "change": "-5%"},
    {"label": "NPS", "value": "72", "change": "+3%"},
]


class TestBarChart:
    def test_generates_html(self):
        gen = ChartGenerator()
        html = gen.generate_bar_chart(BAR_DATA, "Quarterly Revenue")
        assert "<!DOCTYPE html>" in html
        assert "Quarterly Revenue" in html
        assert "<svg" in html
        assert "</svg>" in html

    def test_contains_all_labels(self):
        gen = ChartGenerator()
        html = gen.generate_bar_chart(BAR_DATA, "Test")
        for label in BAR_DATA["labels"]:
            assert label in html

    def test_contains_all_values(self):
        gen = ChartGenerator()
        html = gen.generate_bar_chart(BAR_DATA, "Test")
        for v in BAR_DATA["values"]:
            assert str(v) in html

    def test_empty_data(self):
        gen = ChartGenerator()
        html = gen.generate_bar_chart({"labels": [], "values": []}, "Empty")
        assert "No data provided" in html

    def test_custom_options(self):
        gen = ChartGenerator()
        html = gen.generate_bar_chart(
            BAR_DATA, "Custom",
            options={"width": 800, "height": 500, "show_legend": False}
        )
        assert "<svg" in html

    def test_zero_values(self):
        gen = ChartGenerator()
        html = gen.generate_bar_chart(
            {"labels": ["A", "B"], "values": [0, 0]}, "Zeros"
        )
        assert "<svg" in html


class TestPieChart:
    def test_generates_html(self):
        gen = ChartGenerator()
        html = gen.generate_pie_chart(PIE_DATA, "Market Share")
        assert "<!DOCTYPE html>" in html
        assert "Market Share" in html
        assert "<svg" in html

    def test_contains_percentages(self):
        gen = ChartGenerator()
        html = gen.generate_pie_chart(PIE_DATA, "Test")
        # Should contain percentage labels
        assert "%" in html

    def test_donut_mode(self):
        gen = ChartGenerator()
        html = gen.generate_pie_chart(
            PIE_DATA, "Donut", options={"donut": True, "donut_radius": 60}
        )
        assert "<svg" in html
        assert "Total" in html

    def test_empty_data(self):
        gen = ChartGenerator()
        html = gen.generate_pie_chart({"labels": [], "values": []}, "Empty")
        assert "No data provided" in html


class TestLineChart:
    def test_generates_html(self):
        gen = ChartGenerator()
        html = gen.generate_line_chart(LINE_DATA, "Revenue Trend")
        assert "<!DOCTYPE html>" in html
        assert "Revenue Trend" in html
        assert "<svg" in html

    def test_contains_series_name(self):
        gen = ChartGenerator()
        html = gen.generate_line_chart(LINE_DATA, "Test")
        assert "Revenue" in html

    def test_contains_labels(self):
        gen = ChartGenerator()
        html = gen.generate_line_chart(LINE_DATA, "Test")
        for label in LINE_DATA["labels"]:
            assert label in html

    def test_multiple_series(self):
        data = {
            "labels": ["Jan", "Feb", "Mar"],
            "series": [
                {"name": "Revenue", "values": [10, 20, 30]},
                {"name": "Cost", "values": [5, 12, 18]},
            ],
        }
        gen = ChartGenerator()
        html = gen.generate_line_chart(data, "Multi")
        assert "Revenue" in html
        assert "Cost" in html

    def test_empty_data(self):
        gen = ChartGenerator()
        html = gen.generate_line_chart({"labels": [], "series": []}, "Empty")
        assert "No data provided" in html


class TestComparisonTable:
    def test_generates_html(self):
        gen = ChartGenerator()
        html = gen.generate_comparison_table(TABLE_DATA, "Feature Comparison")
        assert "<!DOCTYPE html>" in html
        assert "Feature Comparison" in html
        assert "<table" in html

    def test_contains_headers(self):
        gen = ChartGenerator()
        html = gen.generate_comparison_table(TABLE_DATA, "Test")
        for h in TABLE_DATA["headers"]:
            assert h in html

    def test_contains_all_cells(self):
        gen = ChartGenerator()
        html = gen.generate_comparison_table(TABLE_DATA, "Test")
        for row in TABLE_DATA["rows"]:
            for cell in row:
                assert cell in html

    def test_empty_data(self):
        gen = ChartGenerator()
        html = gen.generate_comparison_table({"headers": [], "rows": []}, "Empty")
        assert "No data provided" in html


class TestKPICard:
    def test_generates_html(self):
        gen = ChartGenerator()
        html = gen.generate_kpi_card(KPI_DATA, "Key Metrics")
        assert "<!DOCTYPE html>" in html
        assert "Key Metrics" in html

    def test_contains_values(self):
        gen = ChartGenerator()
        html = gen.generate_kpi_card(KPI_DATA, "Test")
        assert "$1M" in html
        assert "50K" in html
        assert "72" in html

    def test_contains_changes(self):
        gen = ChartGenerator()
        html = gen.generate_kpi_card(KPI_DATA, "Test")
        assert "+20%" in html
        assert "-5%" in html

    def test_empty_metrics(self):
        gen = ChartGenerator()
        html = gen.generate_kpi_card([], "Empty")
        assert "No metrics provided" in html


class TestVisualToolsRegistration:
    def test_all_tools_registered(self):
        tools = ToolRegistry()
        _register_tools(tools)
        registered = tools.list_tools()
        assert "visual_bar_chart" in registered
        assert "visual_pie_chart" in registered
        assert "visual_line_chart" in registered
        assert "visual_comparison_table" in registered
        assert "visual_kpi_card" in registered

    def test_bar_chart_tool_dispatch(self):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(
            tools.dispatch("visual_bar_chart", {"data": BAR_DATA, "title": "Test Bar"})
        )
        assert "html" in result
        assert "<svg" in result["html"]

    def test_pie_chart_tool_dispatch(self):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(
            tools.dispatch("visual_pie_chart", {"data": PIE_DATA, "title": "Test Pie"})
        )
        assert "html" in result
        assert "<svg" in result["html"]

    def test_line_chart_tool_dispatch(self):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(
            tools.dispatch("visual_line_chart", {"data": LINE_DATA, "title": "Test Line"})
        )
        assert "html" in result
        assert "<svg" in result["html"]

    def test_comparison_table_tool_dispatch(self):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(
            tools.dispatch("visual_comparison_table", {"data": TABLE_DATA, "title": "Test Table"})
        )
        assert "html" in result
        assert "<table" in result["html"]

    def test_kpi_card_tool_dispatch(self):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(
            tools.dispatch("visual_kpi_card", {"metrics": KPI_DATA, "title": "Test KPI"})
        )
        assert "html" in result
        assert "$1M" in result["html"]

    def test_unknown_tool_returns_error(self):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(tools.dispatch("visual_nonexistent", {}))
        assert "error" in result
