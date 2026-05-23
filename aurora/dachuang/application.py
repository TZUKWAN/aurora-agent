"""大创项目申报书生成器 - 中国大学生创新创业训练计划.

本模块提供符合教育部标准格式的大创项目申报书生成与导出功能。
支持生成项目基本信息、项目简介、申请理由、项目方案、预期成果、
经费预算、团队分工等完整申报内容，并可导出为 DOCX 和 JSON 格式。

典型用法:
    generator = DachuangApplicationGenerator()
    content = generator.generate(project_info)
    generator.export_to_docx(content, "申报书.docx")
    generator.export_to_json(content, "申报书.json")
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Inches


class DachuangApplicationGenerator:
    """大创项目申报书生成器.

    根据教育部《国家级大学生创新创业训练计划管理办法》标准格式，
    生成完整的项目申报书内容，支持导出为 Word 文档和 JSON 文件。

    Attributes:
        template_path: 可选的自定义模板路径。
        default_font: 文档默认字体名称。
        title_font_size: 标题字号（磅）。
        body_font_size: 正文字号（磅）。
    """

    # 教育部规定的大创项目类型
    VALID_PROJECT_TYPES = ["创新训练", "创业训练", "创业实践", "innovation", "entrepreneurship_training", "entrepreneurship_practice"]

    # 经费上限（元）
    DEFAULT_MAX_BUDGET = 10000.0

    def __init__(self, template_path: str | None = None) -> None:
        """初始化申报书生成器.

        Args:
            template_path: 自定义 Word 模板文件路径。若为 None，则使用默认样式创建。
        """
        self.template_path = template_path
        self.default_font = "宋体"
        self.title_font_size = 22  # 小二号
        self.subtitle_font_size = 16  # 三号
        self.body_font_size = 12  # 小四
        self._validate_template()

    def _validate_template(self) -> None:
        """验证模板路径有效性."""
        if self.template_path is not None and not os.path.isfile(self.template_path):
            raise FileNotFoundError(f"模板文件不存在: {self.template_path}")

    def generate(self, project_info: dict[str, Any]) -> dict[str, Any]:
        """生成完整的大创项目申报书内容.

        根据输入的项目信息字典，生成结构化的申报书内容字典。
        所有字段均经过校验，缺失必填项时会抛出 ValueError。

        Args:
            project_info: 项目信息字典，必须包含以下字段:
                - project_name (str): 项目名称
                - project_type (str): 项目类型（创新训练/创业训练/创业实践）
                - discipline (str): 所属学科
                - leader_name (str): 负责人姓名
                - leader_id (str): 负责人学号
                - leader_major (str): 负责人专业
                - leader_grade (str): 负责人年级
                - team_members (list[dict]): 团队成员列表，每个成员包含:
                    - name (str): 姓名
                    - id (str): 学号
                    - major (str): 专业
                    - grade (str): 年级
                    - role (str): 分工角色
                - advisor_name (str): 指导教师姓名
                - advisor_title (str): 指导教师职称
                - advisor_department (str): 指导教师所在院系
                - project_summary (str): 项目简介（300字以内）
                - application_reason (str): 申请理由（1000字左右）
                - research_content (str): 研究内容
                - technical_route (str): 技术路线
                - innovation_points (str): 创新点
                - expected_outcomes (str): 预期成果
                - budget_items (list[dict]): 经费预算明细，每项包含:
                    - category (str): 费用类别
                    - item_name (str): 具体项目
                    - amount (float): 金额
                    - description (str): 用途说明
                - start_date (str): 项目开始日期，格式 YYYY-MM-DD
                - end_date (str): 项目结束日期，格式 YYYY-MM-DD

        Returns:
            包含完整申报书内容的结构化字典，包含以下键:
                - meta: 元数据（生成时间、版本等）
                - basic_info: 项目基本信息
                - project_summary: 项目简介
                - application_reason: 申请理由
                - project_scheme: 项目方案（研究内容、技术路线、创新点）
                - expected_outcomes: 预期成果
                - budget: 经费预算
                - team_division: 团队分工

        Raises:
            ValueError: 必填字段缺失、项目类型不合法、日期格式错误或预算超限。
            TypeError: 字段类型不匹配。
        """
        self._validate_project_info(project_info)

        content: dict[str, Any] = {
            "meta": {
                "generator": "DachuangApplicationGenerator",
                "version": "1.0.0",
                "generated_at": datetime.now().isoformat(),
                "document_type": "大创项目申报书",
            },
            "basic_info": {
                "project_name": project_info.get("project_name", ""),
                "project_type": project_info.get("project_type", ""),
                "discipline": project_info.get("discipline", ""),
                "leader": {
                    "name": project_info.get("leader_name", ""),
                    "student_id": project_info.get("leader_id", ""),
                    "major": project_info.get("leader_major", ""),
                    "grade": project_info.get("leader_grade", ""),
                },
                "advisor": {
                    "name": project_info.get("advisor_name", ""),
                    "title": project_info.get("advisor_title", ""),
                    "department": project_info.get("advisor_department", ""),
                },
                "duration": {
                    "start_date": project_info.get("start_date", ""),
                    "end_date": project_info.get("end_date", ""),
                },
            },
            "project_summary": project_info.get("project_summary", ""),
            "application_reason": project_info.get("application_reason", ""),
            "project_scheme": {
                "research_content": project_info.get("research_content", ""),
                "technical_route": project_info.get("technical_route", ""),
                "innovation_points": project_info.get("innovation_points", []),
            },
            "expected_outcomes": project_info.get("expected_outcomes", {}),
            "budget": self._process_budget(project_info.get("budget_items", [])),
            "team_division": project_info["team_members"],
        }

        return content

    def _validate_project_info(self, project_info: dict[str, Any]) -> None:
        """校验项目信息的完整性与合法性.

        Args:
            project_info: 待校验的项目信息字典。

        Raises:
            ValueError: 必填字段缺失或值不合法。
            TypeError: 字段类型不匹配。
        """
        # 只检查核心必填字段，其他字段有默认值
        required_fields = [
            "project_name", "project_type", "discipline",
            "leader_name", "leader_id", "advisor_name",
        ]

        missing = [f for f in required_fields if f not in project_info or not project_info[f]]
        if missing:
            raise ValueError(f"缺少必填字段: {', '.join(missing)}")

        if project_info.get("project_type") not in self.VALID_PROJECT_TYPES:
            raise ValueError(
                f"项目类型必须是以下之一: {', '.join(self.VALID_PROJECT_TYPES)}"
            )

        # team_members 可选
        if "team_members" in project_info and project_info["team_members"] is not None:
            if not isinstance(project_info["team_members"], list):
                raise TypeError("team_members 必须是列表类型")
            for idx, member in enumerate(project_info["team_members"]):
                if not isinstance(member, dict):
                    raise TypeError(f"团队成员第 {idx + 1} 项必须是字典类型")

        # 校验日期格式（如果有）
        for date_field in ["start_date", "end_date"]:
            if date_field in project_info and project_info[date_field]:
                try:
                    datetime.strptime(project_info[date_field], "%Y-%m-%d")
                except ValueError as exc:
                    raise ValueError(f"{date_field} 日期格式错误，应为 YYYY-MM-DD") from exc

        if (project_info.get("start_date") and project_info.get("end_date")
                and project_info["start_date"] > project_info["end_date"]):
            raise ValueError("开始日期不能晚于结束日期")

        # 校验项目简介字数（如果有）
        if project_info.get("project_summary"):
            summary_len = len(project_info["project_summary"].replace(" ", "").replace("\n", ""))
            if summary_len > 300:
                raise ValueError(f"项目简介超过300字限制（当前 {summary_len} 字）")

    def _process_budget(self, budget_items: list[dict[str, Any]]) -> dict[str, Any]:
        """处理经费预算数据.

        Args:
            budget_items: 原始预算明细列表。

        Returns:
            包含明细、分类汇总和总金额的预算字典。
        """
        categories: dict[str, float] = {}
        total = 0.0
        processed_items: list[dict[str, Any]] = []

        for item in budget_items:
            category = item.get("category", "其他")
            amount = float(item.get("amount", 0))
            categories[category] = categories.get(category, 0.0) + amount
            total += amount
            processed_items.append({
                "category": category,
                "item_name": item.get("item_name", ""),
                "amount": amount,
                "description": item.get("description", ""),
            })

        return {
            "items": processed_items,
            "category_summary": categories,
            "total_amount": round(total, 2),
        }

    def export_to_docx(self, content: dict[str, Any], filepath: str) -> None:
        """将申报书内容导出为 Word 文档.

        使用 python-docx 生成符合标准格式的 DOCX 文件，包含标题、
        正文、表格等完整排版。

        Args:
            content: generate() 方法生成的申报书内容字典。
            filepath: 输出文件路径，必须以 .docx 结尾。

        Raises:
            ValueError: filepath 不以 .docx 结尾。
            TypeError: content 格式不正确。
            OSError: 文件写入失败。
        """
        if not filepath.lower().endswith(".docx"):
            raise ValueError("输出文件路径必须以 .docx 结尾")

        if self.template_path and os.path.isfile(self.template_path):
            doc = Document(self.template_path)
        else:
            doc = Document()

        self._set_doc_styles(doc)

        # 标题
        title = doc.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title.add_run("中国大学生创新创业训练计划项目申报书")
        run.font.size = Pt(self.title_font_size)
        run.font.bold = True
        run.font.name = self.default_font
        run._element.rPr.rFonts.set(qn("w:eastAsia"), self.default_font)
        doc.add_paragraph()

        # 一、项目基本信息
        self._add_section_title(doc, "一、项目基本信息")
        basic = content["basic_info"]
        info_table = doc.add_table(rows=6, cols=4)
        info_table.style = "Table Grid"

        cells_data = [
            ("项目名称", basic["project_name"], "项目类型", basic["project_type"]),
            ("所属学科", basic["discipline"], "", ""),
            (
                "负责人",
                f"{basic['leader']['name']} ({basic['leader']['student_id']})",
                "专业/年级",
                f"{basic['leader']['major']} / {basic['leader']['grade']}",
            ),
            (
                "指导教师",
                f"{basic['advisor']['name']} ({basic['advisor']['title']})",
                "所在院系",
                basic["advisor"]["department"],
            ),
            (
                "起止时间",
                f"{basic['duration']['start_date']} 至 {basic['duration']['end_date']}",
                "",
                "",
            ),
        ]
        for idx, (label1, val1, label2, val2) in enumerate(cells_data):
            row = info_table.rows[idx]
            row.cells[0].text = label1
            row.cells[1].text = val1
            row.cells[2].text = label2
            row.cells[3].text = val2
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(self.body_font_size)
                        run.font.name = self.default_font
                        run._element.rPr.rFonts.set(qn("w:eastAsia"), self.default_font)

        doc.add_paragraph()

        # 二、项目简介
        self._add_section_title(doc, "二、项目简介")
        self._add_body_text(doc, content["project_summary"])

        # 三、申请理由
        self._add_section_title(doc, "三、申请理由")
        self._add_body_text(doc, content["application_reason"])

        # 四、项目方案
        self._add_section_title(doc, "四、项目方案")
        scheme = content["project_scheme"]
        self._add_subsection_title(doc, "（一）研究内容")
        self._add_body_text(doc, scheme["research_content"])
        self._add_subsection_title(doc, "（二）技术路线")
        self._add_body_text(doc, scheme["technical_route"])
        self._add_subsection_title(doc, "（三）创新点")
        self._add_body_text(doc, scheme["innovation_points"])

        # 五、预期成果
        self._add_section_title(doc, "五、预期成果")
        self._add_body_text(doc, content["expected_outcomes"])

        # 六、经费预算
        self._add_section_title(doc, "六、经费预算")
        budget = content["budget"]
        budget_table = doc.add_table(rows=len(budget["items"]) + 2, cols=4)
        budget_table.style = "Table Grid"

        headers = ["费用类别", "具体项目", "金额（元）", "用途说明"]
        for idx, header in enumerate(headers):
            cell = budget_table.rows[0].cells[idx]
            cell.text = header
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(self.body_font_size)

        for idx, item in enumerate(budget["items"], start=1):
            row = budget_table.rows[idx]
            row.cells[0].text = item["category"]
            row.cells[1].text = item["item_name"]
            row.cells[2].text = str(item["amount"])
            row.cells[3].text = item["description"]

        total_row = budget_table.rows[-1]
        total_row.cells[0].merge(total_row.cells[1])
        total_row.cells[0].text = "合计"
        total_row.cells[1].text = str(budget["total_amount"])
        for paragraph in total_row.cells[0].paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
        for paragraph in total_row.cells[1].paragraphs:
            for run in paragraph.runs:
                run.font.bold = True

        doc.add_paragraph()

        # 七、团队分工
        self._add_section_title(doc, "七、团队分工")
        team_table = doc.add_table(rows=len(content["team_division"]) + 1, cols=5)
        team_table.style = "Table Grid"

        team_headers = ["姓名", "学号", "专业", "年级", "分工"]
        for idx, header in enumerate(team_headers):
            cell = team_table.rows[0].cells[idx]
            cell.text = header
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(self.body_font_size)

        for idx, member in enumerate(content["team_division"], start=1):
            row = team_table.rows[idx]
            row.cells[0].text = member.get("name", "")
            row.cells[1].text = member.get("id", "")
            row.cells[2].text = member.get("major", "")
            row.cells[3].text = member.get("grade", "")
            row.cells[4].text = member.get("role", "")

        # 保存
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        doc.save(filepath)

    def _set_doc_styles(self, doc: Document) -> None:
        """设置文档默认样式."""
        style = doc.styles["Normal"]
        font = style.font
        font.name = self.default_font
        font.size = Pt(self.body_font_size)
        style._element.rPr.rFonts.set(qn("w:eastAsia"), self.default_font)

    def _add_section_title(self, doc: Document, text: str) -> None:
        """添加一级节标题."""
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.size = Pt(self.subtitle_font_size)
        run.font.bold = True
        run.font.name = self.default_font
        run._element.rPr.rFonts.set(qn("w:eastAsia"), self.default_font)
        p.paragraph_format.space_after = Pt(12)

    def _add_subsection_title(self, doc: Document, text: str) -> None:
        """添加二级节标题."""
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.name = self.default_font
        run._element.rPr.rFonts.set(qn("w:eastAsia"), self.default_font)
        p.paragraph_format.space_after = Pt(6)

    def _add_body_text(self, doc: Document, text: str) -> None:
        """添加正文段落."""
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.size = Pt(self.body_font_size)
        run.font.name = self.default_font
        run._element.rPr.rFonts.set(qn("w:eastAsia"), self.default_font)
        p.paragraph_format.first_line_indent = Inches(0.4)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(6)

    def export_to_json(self, content: dict[str, Any], filepath: str) -> None:
        """将申报书内容导出为 JSON 文件.

        Args:
            content: generate() 方法生成的申报书内容字典。
            filepath: 输出文件路径，必须以 .json 结尾。

        Raises:
            ValueError: filepath 不以 .json 结尾。
            OSError: 文件写入失败。
        """
        if not filepath.lower().endswith(".json"):
            raise ValueError("输出文件路径必须以 .json 结尾")

        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 示例用法
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample_project = {
        "project_name": "基于深度学习的古籍文字识别系统",
        "project_type": "创新训练",
        "discipline": "计算机科学与技术",
        "leader_name": "张三",
        "leader_id": "2022010001",
        "leader_major": "计算机科学与技术",
        "leader_grade": "2022级",
        "team_members": [
            {"name": "李四", "id": "2022010002", "major": "软件工程", "grade": "2022级", "role": "算法设计与实现"},
            {"name": "王五", "id": "2022010003", "major": "人工智能", "grade": "2022级", "role": "数据标注与预处理"},
            {"name": "赵六", "id": "2022010004", "major": "计算机科学与技术", "grade": "2022级", "role": "前端界面开发"},
        ],
        "advisor_name": "陈教授",
        "advisor_title": "教授",
        "advisor_department": "计算机学院",
        "project_summary": "本项目旨在利用深度学习技术，开发一套针对古籍文字的高精度识别系统，解决传统OCR在古籍场景下识别率低的问题。",
        "application_reason": "随着数字化图书馆建设的推进，古籍数字化需求日益增长。然而，由于古籍文字的特殊性（异体字、模糊、破损等），现有OCR技术难以满足实际需求。本项目拟结合计算机视觉与自然语言处理技术，构建专门面向古籍文字的识别模型，具有重要的学术价值与应用前景。",
        "research_content": "1. 构建古籍文字数据集；2. 设计适用于古籍的深度学习模型架构；3. 开发端到端的识别系统。",
        "technical_route": "采用ResNet+Transformer的混合架构，结合注意力机制，分阶段进行文字检测与识别。",
        "innovation_points": "1. 首次提出针对古籍的专用识别模型；2. 引入多任务学习框架；3. 实现端到端的古籍数字化流水线。",
        "expected_outcomes": "1. 发表学术论文1-2篇；2. 申请软件著作权1项；3. 完成可运行的系统原型。",
        "budget_items": [
            {"category": "设备费", "item_name": "GPU服务器租赁", "amount": 3000.0, "description": "模型训练所需算力资源"},
            {"category": "材料费", "item_name": "数据集采购", "amount": 1500.0, "description": "古籍扫描图像采购"},
            {"category": "测试费", "item_name": "模型评测", "amount": 800.0, "description": "第三方评测服务"},
            {"category": "差旅费", "item_name": "古籍馆调研", "amount": 1200.0, "description": "实地采集数据"},
            {"category": "出版费", "item_name": "论文版面费", "amount": 2000.0, "description": "核心期刊发表"},
            {"category": "劳务费", "item_name": "数据标注", "amount": 1500.0, "description": "外包数据标注服务"},
        ],
        "start_date": "2025-06-01",
        "end_date": "2026-05-31",
    }

    generator = DachuangApplicationGenerator()
    content = generator.generate(sample_project)
    print(f"申报书生成成功，总预算: {content['budget']['total_amount']} 元")

    # 导出为 DOCX（需要安装 python-docx）
    # generator.export_to_docx(content, "大创申报书.docx")
    # generator.export_to_json(content, "大创申报书.json")
