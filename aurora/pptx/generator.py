"""PPT文件生成器."""

from typing import Dict, List, Optional

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN
    from pptx.dml.color import RGBColor
    HAS_PPTX = True
except ImportError:
    HAS_PPTX = False


class PPTXGenerator:
    """路演PPT文件生成器."""

    THEME_COLORS = {
        "primary": RGBColor(0x1E, 0x3A, 0x5F),      # 深蓝
        "secondary": RGBColor(0x2E, 0x5E, 0xAA),    # 中蓝
        "accent": RGBColor(0xF5, 0xA6, 0x23),       # 橙色强调
        "text": RGBColor(0x33, 0x33, 0x33),          # 深灰文字
        "light": RGBColor(0xF5, 0xF5, 0xF5),         # 浅灰背景
    }

    def __init__(self, template_path: Optional[str] = None):
        self.template_path = template_path

    def generate_full_presentation(self, project_info: Dict, output_path: str):
        """生成完整路演PPT."""
        if not HAS_PPTX:
            raise ImportError("需要安装 python-pptx 库")

        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        slides_data = [
            ("cover", self._create_cover_slide),
            ("problem", self._create_problem_slide),
            ("solution", self._create_solution_slide),
            ("product", self._create_product_slide),
            ("technology", self._create_technology_slide),
            ("market", self._create_market_slide),
            ("business", self._create_business_slide),
            ("team", self._create_team_slide),
            ("plan", self._create_plan_slide),
            ("closing", self._create_closing_slide),
        ]

        for slide_id, creator in slides_data:
            creator(prs, project_info)

        prs.save(output_path)
        print(f"PPT已生成: {output_path}")

    def _create_cover_slide(self, prs, info):
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
        title_box = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11.333), Inches(1.5))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = info.get("project_name", "项目名称")
        p.font.size = Pt(44)
        p.font.bold = True
        p.font.color.rgb = self.THEME_COLORS["primary"]
        p.alignment = PP_ALIGN.CENTER

        subtitle = slide.shapes.add_textbox(Inches(1), Inches(4.2), Inches(11.333), Inches(1))
        tf2 = subtitle.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = info.get("tagline", "项目标语")
        p2.font.size = Pt(24)
        p2.font.color.rgb = self.THEME_COLORS["secondary"]
        p2.alignment = PP_ALIGN.CENTER

    def _create_problem_slide(self, prs, info):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_title(slide, "行业痛点")
        problems = info.get("problems", ["痛点1：现有方案效率低", "痛点2：成本居高不下", "痛点3：用户体验差"])
        self._add_bullet_list(slide, problems, Inches(1), Inches(2), Inches(11.333))

    def _create_solution_slide(self, prs, info):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_title(slide, "解决方案")
        solution = info.get("solution", "我们提出了一套创新的解决方案...")
        box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11.333), Inches(4))
        tf = box.text_frame
        tf.text = solution
        tf.paragraphs[0].font.size = Pt(24)

    def _create_product_slide(self, prs, info):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_title(slide, "产品与服务")
        features = info.get("features", ["核心功能一", "核心功能二", "核心功能三"])
        self._add_bullet_list(slide, features, Inches(1), Inches(2), Inches(11.333))

    def _create_technology_slide(self, prs, info):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_title(slide, "核心技术")
        tech = info.get("technology_stack", "采用前沿技术架构")
        box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11.333), Inches(4))
        tf = box.text_frame
        tf.text = tech
        tf.paragraphs[0].font.size = Pt(22)

    def _create_market_slide(self, prs, info):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_title(slide, "市场分析")
        market_data = [
            f"目标市场：{info.get('target_market', '待定')}",
            f"市场规模：{info.get('market_size', '百亿级')}",
            f"竞争优势：{info.get('competitive_advantage', '技术领先')}",
        ]
        self._add_bullet_list(slide, market_data, Inches(1), Inches(2), Inches(11.333))

    def _create_business_slide(self, prs, info):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_title(slide, "商业模式")
        model = info.get("business_model", "订阅制 + 增值服务")
        box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11.333), Inches(4))
        tf = box.text_frame
        tf.text = model
        tf.paragraphs[0].font.size = Pt(24)

    def _create_team_slide(self, prs, info):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_title(slide, "团队介绍")
        team = info.get("team_members", [])
        for i, member in enumerate(team[:3]):
            x = Inches(1 + i * 4)
            box = slide.shapes.add_textbox(x, Inches(2.5), Inches(3.5), Inches(3))
            tf = box.text_frame
            tf.text = f"{member.get('name', '')}\n{member.get('role', '')}\n{member.get('background', '')}"

    def _create_plan_slide(self, prs, info):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._add_title(slide, "发展规划")
        milestones = info.get("milestones", [
            {"phase": "短期", "desc": "产品打磨与市场验证"},
            {"phase": "中期", "desc": "规模扩张与营收增长"},
            {"phase": "长期", "desc": "生态构建与行业领先"},
        ])
        for i, m in enumerate(milestones):
            x = Inches(1 + i * 4)
            box = slide.shapes.add_textbox(x, Inches(2.5), Inches(3.5), Inches(2))
            tf = box.text_frame
            tf.text = f"{m.get('phase', '')}\n{m.get('desc', '')}"

    def _create_closing_slide(self, prs, info):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        title_box = slide.shapes.add_textbox(Inches(1), Inches(3), Inches(11.333), Inches(1.5))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = "感谢聆听"
        p.font.size = Pt(48)
        p.font.bold = True
        p.font.color.rgb = self.THEME_COLORS["primary"]
        p.alignment = PP_ALIGN.CENTER

    def _add_title(self, slide, text):
        box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12.333), Inches(1))
        tf = box.text_frame
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = self.THEME_COLORS["primary"]

    def _add_bullet_list(self, slide, items, left, top, width):
        box = slide.shapes.add_textbox(left, top, width, Inches(4))
        tf = box.text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(24)
            p.space_after = Pt(12)
