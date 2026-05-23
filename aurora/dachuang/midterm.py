"""大创项目中期检查报告生成器.

本模块提供中国大学生创新创业训练计划项目中期检查报告的生成与导出功能。
报告涵盖项目进展情况、已完成工作、存在问题与困难、下一步工作计划等核心内容，
符合教育部及各高校中期检查的标准格式要求。

典型用法:
    generator = MidtermReportGenerator()
    report = generator.generate(report_info)
    generator.export_to_docx(report, "中期检查报告.docx")
    generator.export_to_json(report, "中期检查报告.json")
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from docx import Document
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches


class MidtermReportGenerator:
    """大创项目中期检查报告生成器.

    根据项目执行过程中的实际进展数据，生成结构化的中期检查报告。
    报告严格遵循教育部《国家级大学生创新创业训练计划管理办法》中
    关于中期检查的内容规范。

    Attributes:
        default_font: 文档默认字体名称。
        title_font_size: 标题字号（磅）。
        subtitle_font_size: 二级标题字号（磅）。
        body_font_size: 正文字号（磅）。
    """

    def __init__(self) -> None:
        """初始化中期检查报告生成器."""
        self.default_font = "宋体"
        self.title_font_size = 22
        self.subtitle_font_size = 16
        self.body_font_size = 12

    def generate(self, report_info: dict[str, Any]) -> dict[str, Any]:
        """生成完整的中期检查报告内容.

        对输入信息进行校验、结构化处理，生成符合标准格式的中期检查报告字典。

        Args:
            report_info: 报告信息字典，必须包含以下字段:
                - project_name (str): 项目名称
                - project_type (str): 项目类型（创新训练/创业训练/创业实践）
                - leader_name (str): 负责人姓名
                - leader_id (str): 负责人学号
                - advisor_name (str): 指导教师姓名
                - report_date (str): 报告填写日期，格式 YYYY-MM-DD
                - project_progress (str): 项目整体进展情况描述
                - completed_work (list[dict]): 已完成工作列表，每项包含:
                    - phase (str): 阶段名称
                    - description (str): 工作内容描述
                    - completion_date (str): 完成日期 YYYY-MM-DD
                    - status (str): 完成状态（已完成/进行中/延期）
                - existing_problems (list[dict]): 存在问题列表，每项包含:
                    - problem (str): 问题描述
                    - impact (str): 对项目的影响
                    - solution (str): 已采取或拟采取的解决措施
                - next_steps (list[dict]): 下一步计划列表，每项包含:
                    - phase (str): 阶段名称
                    - plan (str): 计划内容
                    - deadline (str): 计划完成日期 YYYY-MM-DD
                    - responsible (str): 负责人
                - budget_usage (dict): 经费使用情况，包含:
                    - allocated (float):  allocated 经费总额
                    - spent (float): 已使用金额
                    - details (list[dict]): 使用明细，每项包含 category, amount, description
                - achievement_preview (str): 阶段性成果概述
                - advisor_comment (str, optional): 指导教师意见
                - department_comment (str, optional): 院系评审意见

        Returns:
            包含完整中期检查报告内容的结构化字典，包含以下键:
                - meta: 元数据
                - basic_info: 项目基本信息
                - project_progress: 项目进展情况
                - completed_work: 已完成工作
                - existing_problems: 存在问题与困难
                - next_steps: 下一步工作计划
                - budget_usage: 经费使用情况
                - achievement_preview: 阶段性成果
                - advisor_comment: 指导教师意见
                - department_comment: 院系评审意见

        Raises:
            ValueError: 必填字段缺失、日期格式错误或经费数据不合法。
            TypeError: 字段类型不匹配。
        """
        self._validate_report_info(report_info)

        content: dict[str, Any] = {
            "meta": {
                "generator": "MidtermReportGenerator",
                "version": "1.0.0",
                "generated_at": datetime.now().isoformat(),
                "document_type": "大创项目中期检查报告",
            },
            "basic_info": {
                "project_name": report_info.get("project_name", ""),
                "project_type": report_info.get("project_type", ""),
                "leader": {
                    "name": report_info.get("leader_name", ""),
                    "student_id": report_info.get("leader_id", ""),
                },
                "advisor_name": report_info.get("advisor_name", ""),
                "report_date": report_info.get("report_date", ""),
            },
            "project_progress": report_info.get("project_progress", ""),
            "completed_work": report_info.get("completed_work", []),
            "existing_problems": report_info.get("existing_problems", []),
            "next_steps": report_info.get("next_steps", []),
            "budget_usage": self._process_budget_usage(report_info.get("budget_usage", {})),
            "achievement_preview": report_info.get("achievement_preview", ""),
            "advisor_comment": report_info.get("advisor_comment", ""),
            "department_comment": report_info.get("department_comment", ""),
        }

        return content

    def _validate_report_info(self, report_info: dict[str, Any]) -> None:
        """校验报告信息的完整性与合法性.

        Args:
            report_info: 待校验的报告信息字典。

        Raises:
            ValueError: 必填字段缺失或值不合法。
            TypeError: 字段类型不匹配。
        """
        required_fields = [
            "project_name", "project_type", "leader_name",
        ]

        missing = [f for f in required_fields if f not in report_info or not report_info[f]]
        if missing:
            raise ValueError(f"缺少必填字段: {', '.join(missing)}")

        # 校验日期格式（如果有）
        if report_info.get("report_date"):
            try:
                datetime.strptime(report_info["report_date"], "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError("report_date 日期格式错误，应为 YYYY-MM-DD") from exc

        # 校验列表字段类型
        for list_field in ["completed_work", "existing_problems", "next_steps"]:
            if list_field in report_info and not isinstance(report_info[list_field], list):
                raise TypeError(f"{list_field} 必须是列表类型")

        # 校验经费数据
        budget = report_info.get("budget_usage", {})
        if budget:
            if "allocated" in budget and "spent" in budget:
                if float(budget["spent"]) > float(budget["allocated"]):
                    raise ValueError("已使用经费不能超过 allocated 经费总额")

    def _process_budget_usage(self, budget_usage: dict[str, Any]) -> dict[str, Any]:
        """处理经费使用数据.

        Args:
            budget_usage: 原始经费使用字典。

        Returns:
            包含使用明细、分类汇总和余额的经费字典。
        """
        allocated = float(budget_usage.get("allocated", 0))
        spent = float(budget_usage.get("spent", 0))
        details = budget_usage.get("details", [])

        categories: dict[str, float] = {}
        for item in details:
            category = item.get("category", "")
            amount = float(item.get("amount", 0))
            categories[category] = categories.get(category, 0.0) + amount

        return {
            "allocated": round(allocated, 2),
            "spent": round(spent, 2),
            "remaining": round(allocated - spent, 2),
            "usage_rate": round(spent / allocated * 100, 2) if allocated > 0 else 0.0,
            "details": details,
            "category_summary": categories,
        }

    def export_to_docx(self, content: dict[str, Any], filepath: str) -> None:
        """将中期检查报告导出为 Word 文档.

        Args:
            content: generate() 方法生成的报告内容字典。
            filepath: 输出文件路径，必须以 .docx 结尾。

        Raises:
            ValueError: filepath 不以 .docx 结尾。
            OSError: 文件写入失败。
        """
        if not filepath.lower().endswith(".docx"):
            raise ValueError("输出文件路径必须以 .docx 结尾")

        doc = Document()
        self._set_doc_styles(doc)

        # 标题
        title = doc.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title.add_run("大学生创新创业训练计划项目中期检查报告")
        run.font.size = Pt(self.title_font_size)
        run.font.bold = True
        run.font.name = self.default_font
        run._element.rPr.rFonts.set(qn("w:eastAsia"), self.default_font)
        doc.add_paragraph()

        # 基本信息
        self._add_section_title(doc, "一、项目基本信息")
        basic = content["basic_info"]
        info_table = doc.add_table(rows=4, cols=4)
        info_table.style = "Table Grid"

        rows_data = [
            ("项目名称", basic["project_name"], "项目类型", basic["project_type"]),
            ("负责人", f"{basic['leader']['name']} ({basic['leader']['student_id']})", "指导教师", basic["advisor_name"]),
            ("报告日期", basic["report_date"], "", ""),
        ]
        for idx, (label1, val1, label2, val2) in enumerate(rows_data):
            row = info_table.rows[idx]
            row.cells[0].text = label1
            row.cells[1].text = val1
            row.cells[2].text = label2
            row.cells[3].text = val2

        doc.add_paragraph()

        # 项目进展情况
        self._add_section_title(doc, "二、项目进展情况")
        self._add_body_text(doc, content["project_progress"])

        # 已完成工作
        self._add_section_title(doc, "三、已完成工作")
        if content["completed_work"]:
            work_table = doc.add_table(rows=len(content["completed_work"]) + 1, cols=4)
            work_table.style = "Table Grid"
            headers = ["阶段", "工作内容", "完成日期", "状态"]
            for idx, header in enumerate(headers):
                cell = work_table.rows[0].cells[idx]
                cell.text = header
                for paragraph in cell.paragraphs:
                    for r in paragraph.runs:
                        r.font.bold = True

            for idx, work in enumerate(content["completed_work"], start=1):
                row = work_table.rows[idx]
                if isinstance(work, dict):
                    row.cells[0].text = work.get("phase", "")
                    row.cells[1].text = work.get("description", "")
                    row.cells[2].text = work.get("completion_date", "")
                    row.cells[3].text = work.get("status", "")
                else:
                    row.cells[0].text = str(idx)
                    row.cells[1].text = str(work)
                    row.cells[2].text = ""
                    row.cells[3].text = "已完成"
        else:
            self._add_body_text(doc, "暂无已完成工作记录。")

        # 存在问题与困难
        self._add_section_title(doc, "四、存在问题与困难")
        if content["existing_problems"]:
            for problem in content["existing_problems"]:
                if isinstance(problem, dict):
                    p = doc.add_paragraph()
                    run = p.add_run(f"问题: {problem.get('problem', '')}")
                    run.font.bold = True
                    run.font.size = Pt(self.body_font_size)
                    self._add_body_text(doc, f"影响: {problem.get('impact', '')}")
                    self._add_body_text(doc, f"解决措施: {problem.get('solution', '')}")
                    doc.add_paragraph()
                else:
                    self._add_body_text(doc, f"- {problem}")
        else:
            self._add_body_text(doc, "目前项目进展顺利，暂未发现重大问题。")

        # 下一步工作计划
        self._add_section_title(doc, "五、下一步工作计划")
        if content["next_steps"]:
            step_table = doc.add_table(rows=len(content["next_steps"]) + 1, cols=4)
            step_table.style = "Table Grid"
            headers = ["阶段", "计划内容", "截止日期", "负责人"]
            for idx, header in enumerate(headers):
                cell = step_table.rows[0].cells[idx]
                cell.text = header
                for paragraph in cell.paragraphs:
                    for r in paragraph.runs:
                        r.font.bold = True

            for idx, step in enumerate(content["next_steps"], start=1):
                row = step_table.rows[idx]
                if isinstance(step, dict):
                    row.cells[0].text = step.get("phase", "")
                    row.cells[1].text = step.get("plan", "")
                    row.cells[2].text = step.get("deadline", "")
                    row.cells[3].text = step.get("responsible", "")
                else:
                    row.cells[0].text = str(idx)
                    row.cells[1].text = str(step)
                    row.cells[2].text = ""
                    row.cells[3].text = ""
        else:
            self._add_body_text(doc, "暂无下一步计划。")

        # 经费使用情况
        self._add_section_title(doc, "六、经费使用情况")
        budget = content["budget_usage"]
        budget_summary = (
            f" allocated 经费: {budget['allocated']} 元\n"
            f"已使用: {budget['spent']} 元\n"
            f"剩余: {budget['remaining']} 元\n"
            f"使用率: {budget['usage_rate']}%"
        )
        self._add_body_text(doc, budget_summary)

        if budget.get("details"):
            detail_table = doc.add_table(rows=len(budget["details"]) + 1, cols=3)
            detail_table.style = "Table Grid"
            headers = ["费用类别", "金额（元）", "用途说明"]
            for idx, header in enumerate(headers):
                cell = detail_table.rows[0].cells[idx]
                cell.text = header
                for paragraph in cell.paragraphs:
                    for r in paragraph.runs:
                        r.font.bold = True

            for idx, item in enumerate(budget["details"], start=1):
                row = detail_table.rows[idx]
                row.cells[0].text = item.get("category", "")
                row.cells[1].text = str(item.get("amount", ""))
                row.cells[2].text = item.get("description", "")

        # 阶段性成果
        self._add_section_title(doc, "七、阶段性成果")
        self._add_body_text(doc, content["achievement_preview"] or "暂无阶段性成果。")

        # 指导教师意见
        if content.get("advisor_comment"):
            self._add_section_title(doc, "八、指导教师意见")
            self._add_body_text(doc, content["advisor_comment"])

        # 院系评审意见
        if content.get("department_comment"):
            self._add_section_title(doc, "九、院系评审意见")
            self._add_body_text(doc, content["department_comment"])

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
        """将中期检查报告导出为 JSON 文件.

        Args:
            content: generate() 方法生成的报告内容字典。
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
    sample_report = {
        "project_name": "基于深度学习的古籍文字识别系统",
        "project_type": "创新训练",
        "leader_name": "张三",
        "leader_id": "2022010001",
        "advisor_name": "陈教授",
        "report_date": "2025-12-15",
        "project_progress": "项目整体进展良好，目前已完成数据集构建和模型初步设计，正在进行模型训练与调优阶段。",
        "completed_work": [
            {
                "phase": "第一阶段",
                "description": "收集并整理了5000页古籍扫描图像，完成数据清洗与预处理",
                "completion_date": "2025-09-30",
                "status": "已完成",
            },
            {
                "phase": "第二阶段",
                "description": "设计基于ResNet+Transformer的混合模型架构",
                "completion_date": "2025-11-15",
                "status": "已完成",
            },
            {
                "phase": "第三阶段",
                "description": "模型训练与参数调优",
                "completion_date": "2026-01-31",
                "status": "进行中",
            },
        ],
        "existing_problems": [
            {
                "problem": "古籍图像质量参差不齐，部分破损严重页面难以识别",
                "impact": "影响模型整体识别准确率，目前准确率约为78%，低于预期目标85%",
                "solution": "引入图像修复预处理模块，采用超分辨率重建技术提升图像质量",
            },
            {
                "problem": "GPU算力资源不足，模型训练周期较长",
                "impact": "单次完整训练需72小时，影响迭代效率",
                "solution": "申请使用学校高性能计算中心资源，同时优化模型结构减少参数量",
            },
        ],
        "next_steps": [
            {
                "phase": "第四阶段",
                "plan": "完成模型训练与调优，达到预期准确率目标",
                "deadline": "2026-02-28",
                "responsible": "张三",
            },
            {
                "phase": "第五阶段",
                "plan": "开发前端用户界面，实现端到端系统原型",
                "deadline": "2026-04-15",
                "responsible": "赵六",
            },
            {
                "phase": "第六阶段",
                "plan": "撰写学术论文，准备结题材料",
                "deadline": "2026-05-15",
                "responsible": "李四",
            },
        ],
        "budget_usage": {
            "allocated": 10000.0,
            "spent": 4800.0,
            "details": [
                {"category": "设备费", "amount": 2000.0, "description": "GPU服务器租赁（6个月）"},
                {"category": "材料费", "amount": 1000.0, "description": "数据集采购"},
                {"category": "测试费", "amount": 500.0, "description": "模型初步评测"},
                {"category": "差旅费", "amount": 800.0, "description": "古籍馆实地调研"},
                {"category": "劳务费", "amount": 500.0, "description": "数据标注外包"},
            ],
        },
        "achievement_preview": "目前已完成5000页古籍图像的数字化采集，构建了包含10万字符标注的训练数据集。模型在测试集上的初步识别准确率达到78%，相关成果已投稿至国内核心期刊（审稿中）。",
        "advisor_comment": "项目进展顺利，团队成员协作良好。建议在下一阶段重点关注模型准确率提升和系统原型开发，确保按时完成项目目标。",
        "department_comment": "同意中期检查通过，建议按计划推进后续工作。",
    }

    generator = MidtermReportGenerator()
    report = generator.generate(sample_report)
    print(f"中期检查报告生成成功，经费使用率: {report['budget_usage']['usage_rate']}%")

    # generator.export_to_docx(report, "中期检查报告.docx")
    # generator.export_to_json(report, "中期检查报告.json")
