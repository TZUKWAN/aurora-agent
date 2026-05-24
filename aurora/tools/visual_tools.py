"""Visual chart tools for AuroraAgent."""

import json
import logging

from aurora.visuals.charts import ChartGenerator

logger = logging.getLogger(__name__)

_generator = ChartGenerator()


def _register_tools(registry):
    """Register visual chart tools to the registry."""
    registry.register(
        "visual_bar_chart",
        "Generate a bar chart as self-contained HTML with inline SVG",
        {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Chart data with 'labels' (array of strings) and 'values' (array of numbers)",
                    "properties": {
                        "labels": {"type": "array", "items": {"type": "string"}},
                        "values": {"type": "array", "items": {"type": "number"}},
                    },
                    "required": ["labels", "values"],
                },
                "title": {"type": "string", "description": "Chart title"},
                "options": {
                    "type": "object",
                    "description": "Optional settings: width, height, colors, show_legend, bar_width",
                },
            },
            "required": ["data", "title"],
        },
        _bar_chart_handler,
    )

    registry.register(
        "visual_pie_chart",
        "Generate a pie or donut chart as self-contained HTML with inline SVG",
        {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Chart data with 'labels' (array of strings) and 'values' (array of numbers)",
                    "properties": {
                        "labels": {"type": "array", "items": {"type": "string"}},
                        "values": {"type": "array", "items": {"type": "number"}},
                    },
                    "required": ["labels", "values"],
                },
                "title": {"type": "string", "description": "Chart title"},
                "options": {
                    "type": "object",
                    "description": "Optional settings: width, height, colors, show_legend, donut, donut_radius",
                },
            },
            "required": ["data", "title"],
        },
        _pie_chart_handler,
    )

    registry.register(
        "visual_line_chart",
        "Generate a line chart as self-contained HTML with inline SVG",
        {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Chart data with 'labels' (array) and 'series' (array of {name, values})",
                    "properties": {
                        "labels": {"type": "array", "items": {"type": "string"}},
                        "series": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "values": {"type": "array", "items": {"type": "number"}},
                                },
                                "required": ["name", "values"],
                            },
                        },
                    },
                    "required": ["labels", "series"],
                },
                "title": {"type": "string", "description": "Chart title"},
                "options": {
                    "type": "object",
                    "description": "Optional settings: width, height, colors, show_legend, show_dots",
                },
            },
            "required": ["data", "title"],
        },
        _line_chart_handler,
    )

    registry.register(
        "visual_comparison_table",
        "Generate a styled comparison table as self-contained HTML",
        {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Table data with 'headers' (array of strings) and 'rows' (array of arrays)",
                    "properties": {
                        "headers": {"type": "array", "items": {"type": "string"}},
                        "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    },
                    "required": ["headers", "rows"],
                },
                "title": {"type": "string", "description": "Table title"},
            },
            "required": ["data", "title"],
        },
        _comparison_table_handler,
    )

    registry.register(
        "visual_kpi_card",
        "Generate KPI metric cards as self-contained HTML",
        {
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "array",
                    "description": "Array of metric objects with label, value, and optional change",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "value": {"type": "string"},
                            "change": {"type": "string"},
                        },
                        "required": ["label", "value"],
                    },
                },
                "title": {"type": "string", "description": "Card section title"},
            },
            "required": ["metrics", "title"],
        },
        _kpi_card_handler,
    )


def _bar_chart_handler(args):
    """Handle bar chart generation."""
    try:
        data = args.get("data", {})
        title = args.get("title", "Bar Chart")
        options = args.get("options")
        html = _generator.generate_bar_chart(data, title, options)
        return json.dumps({"result": "Bar chart generated", "html": html}, ensure_ascii=False)
    except Exception as e:
        logger.exception("Bar chart generation failed")
        return json.dumps({"error": f"Bar chart generation failed: {e}"}, ensure_ascii=False)


def _pie_chart_handler(args):
    """Handle pie chart generation."""
    try:
        data = args.get("data", {})
        title = args.get("title", "Pie Chart")
        options = args.get("options")
        html = _generator.generate_pie_chart(data, title, options)
        return json.dumps({"result": "Pie chart generated", "html": html}, ensure_ascii=False)
    except Exception as e:
        logger.exception("Pie chart generation failed")
        return json.dumps({"error": f"Pie chart generation failed: {e}"}, ensure_ascii=False)


def _line_chart_handler(args):
    """Handle line chart generation."""
    try:
        data = args.get("data", {})
        title = args.get("title", "Line Chart")
        options = args.get("options")
        html = _generator.generate_line_chart(data, title, options)
        return json.dumps({"result": "Line chart generated", "html": html}, ensure_ascii=False)
    except Exception as e:
        logger.exception("Line chart generation failed")
        return json.dumps({"error": f"Line chart generation failed: {e}"}, ensure_ascii=False)


def _comparison_table_handler(args):
    """Handle comparison table generation."""
    try:
        data = args.get("data", {})
        title = args.get("title", "Comparison Table")
        html = _generator.generate_comparison_table(data, title)
        return json.dumps({"result": "Comparison table generated", "html": html}, ensure_ascii=False)
    except Exception as e:
        logger.exception("Comparison table generation failed")
        return json.dumps({"error": f"Comparison table generation failed: {e}"}, ensure_ascii=False)


def _kpi_card_handler(args):
    """Handle KPI card generation."""
    try:
        metrics = args.get("metrics", [])
        title = args.get("title", "KPI Dashboard")
        html = _generator.generate_kpi_card(metrics, title)
        return json.dumps({"result": "KPI cards generated", "html": html}, ensure_ascii=False)
    except Exception as e:
        logger.exception("KPI card generation failed")
        return json.dumps({"error": f"KPI card generation failed: {e}"}, ensure_ascii=False)
