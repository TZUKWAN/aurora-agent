"""PDF exporter for business plans using reportlab."""

import logging
import os
from typing import Dict, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

logger = logging.getLogger(__name__)

# Chinese font registration
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_CHINESE_FONT = "Helvetica"
_FONT_REGISTERED = False

for _font_name, _font_file in [
    ("SimSun", "simsun.ttc"),
    ("SimHei", "simhei.ttf"),
    ("Microsoft YaHei", "msyh.ttc"),
]:
    try:
        pdfmetrics.registerFont(TTFont(_font_name, _font_file))
        _CHINESE_FONT = _font_name
        _FONT_REGISTERED = True
        logger.info("Registered Chinese font: %s", _font_name)
        break
    except Exception:
        continue

if not _FONT_REGISTERED:
    logger.warning("No Chinese font found, falling back to Helvetica")

THEMES = {
    "business": {
        "header_color": HexColor("#1a3a5c"),
        "accent_color": HexColor("#2c5f8a"),
        "text_color": HexColor("#333333"),
        "light_bg": HexColor("#eef3f8"),
    },
    "tech": {
        "header_color": HexColor("#1a1a2e"),
        "accent_color": HexColor("#16213e"),
        "text_color": HexColor("#e0e0e0"),
        "light_bg": HexColor("#0f3460"),
    },
    "minimal": {
        "header_color": HexColor("#333333"),
        "accent_color": HexColor("#666666"),
        "text_color": HexColor("#444444"),
        "light_bg": HexColor("#f5f5f5"),
    },
}


class PDFExporter:
    """Export business plans to PDF using reportlab."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.font = _CHINESE_FONT

    def export(self, plan: dict, output_path: str, theme: str = "business") -> bool:
        """Export business plan to PDF.

        Args:
            plan: Business plan dict with metadata and sections.
            output_path: Destination file path for the PDF.
            theme: Color theme name (business, tech, minimal).

        Returns:
            True on success, False on failure.
        """
        try:
            theme_data = THEMES.get(theme, THEMES["business"])
            styles = self._build_styles(theme_data)

            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                topMargin=2 * cm,
                bottomMargin=2 * cm,
                leftMargin=2.5 * cm,
                rightMargin=2.5 * cm,
            )

            elements = []

            metadata = plan.get("metadata", {})
            sections = plan.get("sections", {})

            elements.extend(self._build_cover(metadata, styles, theme_data))
            elements.extend(self._build_toc(sections, styles, theme_data))

            section_order = [
                "executive_summary",
                "project_overview",
                "market_analysis",
                "product_service",
                "business_model",
                "marketing_strategy",
                "operation_plan",
                "team_introduction",
                "financial_analysis",
                "risk_assessment",
            ]

            for section_id in section_order:
                section = sections.get(section_id)
                if not section:
                    continue
                if isinstance(section, dict):
                    content = section.get("content", "")
                    if not content or not content.strip():
                        continue
                elements.extend(
                    self._build_section(section_id, section, styles, theme_data)
                )

            # Also render any sections not in the standard order
            for section_id, section in sections.items():
                if section_id in section_order:
                    continue
                if not section:
                    continue
                if isinstance(section, dict):
                    content = section.get("content", "")
                    if not content or not content.strip():
                        continue
                elements.extend(
                    self._build_section(section_id, section, styles, theme_data)
                )

            doc.build(elements)
            logger.info("PDF exported to %s", output_path)
            return True

        except Exception as e:
            logger.exception("PDF export failed: %s", e)
            return False

    def _build_styles(self, theme_data: dict) -> Dict[str, ParagraphStyle]:
        """Build paragraph styles for the PDF."""
        base = getSampleStyleSheet()

        styles = {
            "cover_title": ParagraphStyle(
                "cover_title",
                parent=base["Title"],
                fontName=self.font,
                fontSize=28,
                leading=36,
                alignment=1,
                textColor=theme_data["header_color"],
                spaceAfter=12,
            ),
            "cover_subtitle": ParagraphStyle(
                "cover_subtitle",
                parent=base["Normal"],
                fontName=self.font,
                fontSize=16,
                leading=22,
                alignment=1,
                textColor=theme_data["accent_color"],
                spaceAfter=8,
            ),
            "cover_info": ParagraphStyle(
                "cover_info",
                parent=base["Normal"],
                fontName=self.font,
                fontSize=12,
                leading=18,
                alignment=1,
                textColor=theme_data["text_color"],
                spaceAfter=6,
            ),
            "toc_title": ParagraphStyle(
                "toc_title",
                parent=base["Heading1"],
                fontName=self.font,
                fontSize=20,
                leading=28,
                textColor=theme_data["header_color"],
                spaceBefore=0,
                spaceAfter=20,
            ),
            "toc_entry": ParagraphStyle(
                "toc_entry",
                parent=base["Normal"],
                fontName=self.font,
                fontSize=12,
                leading=20,
                textColor=theme_data["text_color"],
                leftIndent=20,
                spaceAfter=4,
            ),
            "section_title": ParagraphStyle(
                "section_title",
                parent=base["Heading1"],
                fontName=self.font,
                fontSize=18,
                leading=26,
                textColor=theme_data["header_color"],
                spaceBefore=16,
                spaceAfter=12,
                borderWidth=0,
                borderPadding=0,
            ),
            "sub_heading": ParagraphStyle(
                "sub_heading",
                parent=base["Heading2"],
                fontName=self.font,
                fontSize=14,
                leading=20,
                textColor=theme_data["accent_color"],
                spaceBefore=12,
                spaceAfter=6,
            ),
            "body": ParagraphStyle(
                "body",
                parent=base["Normal"],
                fontName=self.font,
                fontSize=11,
                leading=18,
                textColor=theme_data["text_color"],
                spaceAfter=6,
                firstLineIndent=0,
            ),
            "bullet": ParagraphStyle(
                "bullet",
                parent=base["Normal"],
                fontName=self.font,
                fontSize=11,
                leading=18,
                textColor=theme_data["text_color"],
                leftIndent=20,
                bulletIndent=6,
                spaceAfter=4,
            ),
        }
        return styles

    def _build_cover(
        self, metadata: dict, styles: dict, theme_data: dict
    ) -> list:
        """Build cover page elements."""
        elements = []

        elements.append(Spacer(1, 6 * cm))

        competition = metadata.get("competition", "")
        title_text = f"{competition} 商业计划书" if competition else "商业计划书"
        elements.append(Paragraph(title_text, styles["cover_title"]))

        elements.append(Spacer(1, 1 * cm))

        project_name = metadata.get("project_name", "")
        if project_name:
            elements.append(Paragraph(project_name, styles["cover_subtitle"]))

        team_name = metadata.get("team_name", "")
        if team_name:
            elements.append(Spacer(1, 0.5 * cm))
            elements.append(
                Paragraph(f"团队: {team_name}", styles["cover_info"])
            )

        track = metadata.get("track", "")
        if track:
            elements.append(Paragraph(f"赛道: {track}", styles["cover_info"]))

        generated_at = metadata.get("generated_at", "")
        if generated_at:
            elements.append(Spacer(1, 0.5 * cm))
            elements.append(Paragraph(generated_at, styles["cover_info"]))

        elements.append(PageBreak())
        return elements

    def _build_toc(
        self, sections: dict, styles: dict, theme_data: dict
    ) -> list:
        """Build table of contents."""
        elements = []

        elements.append(Paragraph("目录", styles["toc_title"]))
        elements.append(Spacer(1, 0.5 * cm))

        index = 1
        section_order = [
            "executive_summary",
            "project_overview",
            "market_analysis",
            "product_service",
            "business_model",
            "marketing_strategy",
            "operation_plan",
            "team_introduction",
            "financial_analysis",
            "risk_assessment",
        ]

        for section_id in section_order:
            section = sections.get(section_id)
            if not section:
                continue
            if isinstance(section, dict):
                title = section.get("title", section_id)
                content = section.get("content", "")
                if not content or not content.strip():
                    continue
            else:
                title = str(section)
            escaped_title = self._escape_xml(title)
            elements.append(
                Paragraph(
                    f"{index}. {escaped_title}",
                    styles["toc_entry"],
                )
            )
            index += 1

        for section_id, section in sections.items():
            if section_id in section_order:
                continue
            if not section:
                continue
            if isinstance(section, dict):
                title = section.get("title", section_id)
                content = section.get("content", "")
                if not content or not content.strip():
                    continue
            else:
                title = str(section)
            escaped_title = self._escape_xml(title)
            elements.append(
                Paragraph(
                    f"{index}. {escaped_title}",
                    styles["toc_entry"],
                )
            )
            index += 1

        elements.append(PageBreak())
        return elements

    def _build_section(
        self,
        section_id: str,
        section: dict,
        styles: dict,
        theme_data: dict,
    ) -> list:
        """Build section content elements."""
        elements = []

        if isinstance(section, dict):
            title = section.get("title", section_id)
            content = section.get("content", "")
        else:
            title = section_id
            content = str(section)

        escaped_title = self._escape_xml(title)
        elements.append(Paragraph(escaped_title, styles["section_title"]))

        # Separator line
        sep_data = [["", ""]]
        sep_table = Table(sep_data, colWidths=[16 * cm, 0])
        sep_table.setStyle(
            TableStyle([
                ("LINEBELOW", (0, 0), (0, 0), 1.5, theme_data["accent_color"]),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ])
        )
        elements.append(sep_table)
        elements.append(Spacer(1, 0.3 * cm))

        paragraphs = content.split("\n")
        for para_text in paragraphs:
            para_text = para_text.strip()
            if not para_text:
                continue

            # Standalone sub-heading marker: 【xxx】
            if para_text.startswith("【") and para_text.endswith("】"):
                heading = para_text.strip("【】")
                escaped_heading = self._escape_xml(heading)
                elements.append(
                    Paragraph(f"<b>{escaped_heading}</b>", styles["sub_heading"])
                )
                continue

            # Inline sub-heading: 【xxx】 rest of text
            if para_text.startswith("【"):
                parts = para_text.split("】", 1)
                if len(parts) == 2:
                    heading = parts[0].lstrip("【")
                    rest = parts[1].strip()
                    escaped_heading = self._escape_xml(heading)
                    elements.append(
                        Paragraph(
                            f"<b>{escaped_heading}</b>", styles["sub_heading"]
                        )
                    )
                    if rest:
                        escaped_rest = self._escape_xml(rest)
                        elements.append(
                            Paragraph(escaped_rest, styles["body"])
                        )
                else:
                    escaped_text = self._escape_xml(para_text)
                    elements.append(Paragraph(escaped_text, styles["body"]))
                continue

            # Bullet points: lines starting with - or bullet char
            if para_text.startswith("- ") or para_text.startswith("• "):
                bullet_text = para_text[2:]
                escaped_bullet = self._escape_xml(bullet_text)
                elements.append(
                    Paragraph(
                        f"•  {escaped_bullet}", styles["bullet"]
                    )
                )
                continue

            # Numbered items: 1. 2. etc.
            if len(para_text) > 2 and para_text[0].isdigit() and para_text[1] == ".":
                escaped_text = self._escape_xml(para_text)
                elements.append(
                    Paragraph(f"<b>{escaped_text[:2]}</b> {escaped_text[2:].lstrip()}", styles["body"])
                )
                continue

            # Regular paragraph
            escaped_text = self._escape_xml(para_text)
            elements.append(Paragraph(escaped_text, styles["body"]))

        elements.append(PageBreak())
        return elements

    @staticmethod
    def _escape_xml(text: str) -> str:
        """Escape XML special characters for reportlab Paragraph."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
