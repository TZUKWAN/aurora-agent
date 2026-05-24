"""Export tools for AuroraAgent."""

import json
import logging

from aurora.export.pdf_exporter import PDFExporter

logger = logging.getLogger(__name__)


def _register_tools(registry):
    """Register export tools to the registry."""
    registry.register(
        "export_pdf",
        "导出商业计划书为PDF文件",
        {
            "type": "object",
            "properties": {
                "plan": {
                    "type": "object",
                    "description": "商业计划书数据，包含metadata和sections",
                },
                "output_path": {
                    "type": "string",
                    "description": "PDF输出文件路径",
                },
                "theme": {
                    "type": "string",
                    "description": "主题样式",
                    "enum": ["business", "tech", "minimal"],
                    "default": "business",
                },
            },
            "required": ["plan", "output_path"],
        },
        _export_pdf_handler,
    )


def _export_pdf_handler(args):
    """Handle export_pdf tool call."""
    try:
        plan = args.get("plan")
        if not plan:
            return json.dumps(
                {"error": "plan is required"}, ensure_ascii=False
            )

        output_path = args.get("output_path")
        if not output_path:
            return json.dumps(
                {"error": "output_path is required"}, ensure_ascii=False
            )

        theme = args.get("theme", "business")

        exporter = PDFExporter()
        success = exporter.export(plan, output_path, theme=theme)

        if success:
            return json.dumps(
                {
                    "result": "PDF exported successfully",
                    "output_path": output_path,
                    "theme": theme,
                },
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {"error": "PDF export failed"}, ensure_ascii=False
            )

    except Exception as e:
        logger.exception("export_pdf tool failed")
        return json.dumps(
            {"error": f"Export failed: {str(e)}"}, ensure_ascii=False
        )
