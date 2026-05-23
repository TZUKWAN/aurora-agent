"""大创项目结题报告生成器.

本模块提供中国大学生创新创业训练计划项目结题报告的生成与导出功能。
报告涵盖项目完成情况、成果清单、经费使用情况、总结与展望等核心内容，
符合教育部及各高校结题验收的标准格式要求。

典型用法:
    generator = FinalReportGenerator()
    report = generator.generate(report_info)
    generator.export_to_docx(report, "结题报告.docx")
    generator.export_to_json(report, "结题报告.json")
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


class FinalReportGenerator:
    """大创项目结题报告生成器.

    根据项目最终执行结果数据，生成结构化的结题报告。
    报告严格遵循教育部《国家级大学生创新创业训练计划管理办法》中
    关于项目结题验收的内容规范。

    Attributes:
        default_font: 文档默认字体名称。
        title_font_size: 标题字号（磅）。
        subtitle_font_size: 二级标题字号（磅）。
        body_font_size: 正文字号（磅）。
    """

    # 成果类型枚举
    ACHIEVEMENT_TYPES = ["论文", "专利", "软件著作权", "实物作品", "竞赛获奖", "其他"]

    def __init__(self) -> None:
        """初始化结题报告生成器."""
        self.default_font = "宋体"
        self.title_font_size = 22
        self.subtitle_font_size = 16
        self.body_font_size = 12

    def generate(self, report_info: dict[str, Any]) -> dict[str, Any]:
        """生成完整的结题报告内容.

        对输入信息进行校验、结构化处理，生成符合标准格式的结题报告字典。

        Args:
            report_info: 报告信息字典，必须包含以下字段:
                - project_name (str): 项目名称
                - project_type (str): 项目类型（创新训练/创业训练/创业实践）
                - leader_name (str): 负责人姓名
                - leader_id (str): 负责人学号
                - advisor_name (str): 指导教师姓名
                - start_date (str): 项目开始日期 YYYY-MM-DD
                - end_date (str): 项目结束日期 YYYY-MM-DD
                - completion_status (str): 完成情况（按期完成/延期完成/未完成）
                - project_summary (str): 项目完成情况概述
                - achievements (list[dict]): 成果清单，每项包含:
                    - type (str): 成果类型（论文/专利/软件著作权/实物作品/竞赛获奖/其他）
                    - title (str): 成果名称
                    - status (str): 状态（已发表/已授权/已登记/已完成/获奖/其他）
                    - date (str): 日期 YYYY-MM-DD
                    - description (str): 详细说明
                - budget_final (dict): 最终经费使用情况，包含:
                    - allocated (float): allocated 经费总额
                    - spent (float): 实际使用金额
                    - details (list[dict]): 使用明细
                - research_summary (str): 研究内容总结
                - innovation_summary (str): 创新点总结
                - experience_summary (str): 经验与收获
                - future_outlook (str): 不足与展望
                - team_contributions (list[dict]): 团队成员贡献，每项包含:
                    - name (str): 姓名
                    - contribution (str): 具体贡献
                - advisor_evaluation (str, optional): 指导教师评价
                - department_evaluation (str, optional): 院系验收意见

        Returns:
            包含完整结题报告内容的结构化字典，包含以下键:
                - meta: 元数据
                - basic_info: 项目基本信息
                - completion_status: 完成情况
                - project_summary: 项目完成情况概述
                - achievements: 成果清单
                - budget_final: 经费使用情况
                - research_summary: 研究内容总结
                - innovation_summary: 创新点总结
                - experience_summary: 经验与收获
                - future_outlook: 不足与展望
                - team_contributions: 团队成员贡献
                - advisor_evaluation: 指导教师评价
                - department_evaluation: 院系验收意见

        Raises:
            ValueError: 必填字段缺失、日期格式错误、成果类型不合法或经费数据不合法。
            TypeError: 字段类型不匹配。
        """
        self._validate_report_info(report_info)

        content: dict[str, Any] = {
            "meta": {
                "generator": "FinalReportGenerator",
                "version": "1.0.0",
                "generated_at": datetime.now().isoformat(),
                "document_type": "大创项目结题报告",
            },
            "basic_info": {
                "project_name": report_info.get("project_name", ""),
                "project_type": report_info.get("project_type", ""),
                "leader": {
                    "name": report_info.get("leader_name", ""),
                    "student_id": report_info.get("leader_id", ""),
                },
                "advisor_name": report_info.get("advisor_name", ""),
                "duration": {
                    "start_date": report_info.get("start_date", ""),
                    "end_date": report_info.get("end_date", ""),
                },
            },
            "completion_status": report_info.get("completion_status", ""),
            "project_summary": report_info.get("project_summary", ""),
            "achievements": report_info.get("achievements", []),
            "budget_final": self._process_budget_final(report_info.get("budget_final", {})),
            "research_summary": report_info.get("research_summary", ""),
            "innovation_summary": report_info.get("innovation_summary", ""),
            "experience_summary": report_info.get("experience_summary", ""),
            "future_outlook": report_info.get("future_outlook", ""),
            "team_contributions": report_info.get("team_contributions", []),
            "advisor_evaluation": report_info.get("advisor_evaluation", ""),
            "department_evaluation": report_info.get("department_evaluation", ""),
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

        valid_statuses = ["按期完成", "延期完成", "未完成"]
        if report_info.get("completion_status") and report_info["completion_status"] not in valid_statuses:
            raise ValueError(f"completion_status 必须是以下之一: {', '.join(valid_statuses)}")

        # 校验日期格式（如果有）
        for date_field in ["start_date", "end_date"]:
            if not report_info.get(date_field):
                continue
            try:
                datetime.strptime(report_info[date_field], "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError(f"{date_field} 日期格式错误，应为 YYYY-MM-DD") from exc

        if report_info.get("start_date") and report_info.get("end_date") and report_info["start_date"] > report_info["end_date"]:
            raise ValueError("开始日期不能晚于结束日期")

        # 校验成果列表
        achievements = report_info.get("achievements", [])
        if achievements and not isinstance(achievements, list):
            raise TypeError("achievements 必须是列表类型")

        for idx, ach in enumerate(achievements):
            if not isinstance(ach, dict):
                raise TypeError(f"成果第 {idx + 1} 项必须是字典类型")
            if ach.get("type") and ach["type"] not in self.ACHIEVEMENT_TYPES:
                raise ValueError(
                    f"成果类型必须是以下之一: {', '.join(self.ACHIEVEMENT_TYPES)}"
                )

        # 校验经费数据
        budget = report_info.get("budget_final", {})
        if budget:
            if "allocated" in budget and "spent" in budget:
                if float(budget["spent"]) > float(budget["allocated"]):
                    raise ValueError("实际使用经费不能超过 allocated 经费总额")

    def _process_budget_final(self, budget_final: dict[str, Any]) -> dict[str, Any]:
        """处理最终经费使用数据.

        Args:
            budget_final: 原始经费使用字典。

        Returns:
            包含 allocated、使用、余额、使用率及明细的经费字典。
        """
        allocated = float(budget_final.get("allocated", 0))
        spent = float(budget_final.get("spent", 0))
        details = budget_final.get("details", [])

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
        """将结题报告导出为 Word 文档.

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
        run = title.add_run("大学生创新创业训练计划项目结题报告")
        run.font.size = Pt(self.title_font_size)
        run.font.bold = True
        run.font.name = self.default_font
        run._element.rPr.rFonts.set(qn("w:eastAsia"), self.default_font)
        doc.add_paragraph()

        # 一、项目基本信息
        self._add_section_title(doc, "一、项目基本信息")
        basic = content["basic_info"]
        info_table = doc.add_table(rows=4, cols=4)
        info_table.style = "Table Grid"

        rows_data = [
            ("项目名称", basic["project_name"], "项目类型", basic["project_type"]),
            ("负责人", f"{basic['leader']['name']} ({basic['leader']['student_id']})", "指导教师", basic["advisor_name"]),
            ("起止时间", f"{basic['duration']['start_date']} 至 {basic['duration']['end_date']}", "", ""),
        ]
        for idx, (label1, val1, label2, val2) in enumerate(rows_data):
            row = info_table.rows[idx]
            row.cells[0].text = label1
            row.cells[1].text = val1
            row.cells[2].text = label2
            row.cells[3].text = val2

        doc.add_paragraph()

        # 二、完成情况
        self._add_section_title(doc, "二、项目完成情况")
        status_text = f"完成状态: {content['completion_status']}"
        self._add_body_text(doc, status_text)
        self._add_body_text(doc, content["project_summary"])

        # 三、成果清单
        self._add_section_title(doc, "三、成果清单")
        if content["achievements"]:
            ach_table = doc.add_table(rows=len(content["achievements"]) + 1, cols=5)
            ach_table.style = "Table Grid"
            headers = ["成果类型", "成果名称", "状态", "日期", "详细说明"]
            for idx, header in enumerate(headers):
                cell = ach_table.rows[0].cells[idx]
                cell.text = header
                for paragraph in cell.paragraphs:
                    for r in paragraph.runs:
                        r.font.bold = True

            for idx, ach in enumerate(content["achievements"], start=1):
                row = ach_table.rows[idx]
                row.cells[0].text = ach.get("type", "")
                row.cells[1].text = ach.get("title", "")
                row.cells[2].text = ach.get("status", "")
                row.cells[3].text = ach.get("date", "")
                row.cells[4].text = ach.get("description", "")
        else:
            self._add_body_text(doc, "本项目未产出可登记成果。")

        # 四、经费使用情况
        self._add_section_title(doc, "四、经费使用情况")
        budget = content["budget_final"]
        budget_summary = (
            f" allocated 经费: {budget['allocated']} 元\n"
            f"实际使用: {budget['spent']} 元\n"
            f"结余: {budget['remaining']} 元\n"
            f"经费使用率: {budget['usage_rate']}%"
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

        doc.add_paragraph()

        # 五、研究内容总结
        self._add_section_title(doc, "五、研究内容总结")
        self._add_body_text(doc, content["research_summary"])

        # 六、创新点总结
        self._add_section_title(doc, "六、创新点总结")
        self._add_body_text(doc, content["innovation_summary"])

        # 七、经验与收获
        self._add_section_title(doc, "七、经验与收获")
        self._add_body_text(doc, content["experience_summary"])

        # 八、不足与展望
        self._add_section_title(doc, "八、不足与展望")
        self._add_body_text(doc, content["future_outlook"])

        # 九、团队成员贡献
        self._add_section_title(doc, "九、团队成员贡献")
        if content["team_contributions"]:
            contrib_table = doc.add_table(rows=len(content["team_contributions"]) + 1, cols=2)
            contrib_table.style = "Table Grid"
            headers = ["姓名", "具体贡献"]
            for idx, header in enumerate(headers):
                cell = contrib_table.rows[0].cells[idx]
                cell.text = header
                for paragraph in cell.paragraphs:
                    for r in paragraph.runs:
                        r.font.bold = True

            for idx, contrib in enumerate(content["team_contributions"], start=1):
                row = contrib_table.rows[idx]
                row.cells[0].text = contrib.get("name", "")
                row.cells[1].text = contrib.get("contribution", "")
        else:
            self._add_body_text(doc, "暂无团队成员贡献记录。")

        # 十、指导教师评价
        if content.get("advisor_evaluation"):
            self._add_section_title(doc, "十、指导教师评价")
            self._add_body_text(doc, content["advisor_evaluation"])

        # 十一、院系验收意见
        if content.get("department_evaluation"):
            self._add_section_title(doc, "十一、院系验收意见")
            self._add_body_text(doc, content["department_evaluation"])

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
        """将结题报告导出为 JSON 文件.

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
        "start_date": "2025-06-01",
        "end_date": "2026-05-31",
        "completion_status": "按期完成",
        "project_summary": "本项目按照计划完成了所有预定目标。构建了包含10万字符标注的古籍文字数据集，开发了基于ResNet+Transformer混合架构的识别模型，在测试集上达到了87.3%的识别准确率，超额完成了85%的预期目标。同时开发了配套的Web端用户界面，形成了完整的古籍数字化解决方案。",
        "achievements": [
            {
                "type": "论文",
                "title": "基于深度学习的古籍文字识别方法研究",
                "status": "已发表",
                "date": "2026-03-15",
                "description": "发表于《计算机学报》（核心期刊），第一作者为项目负责人张三",
            },
            {
                "type": "软件著作权",
                "title": "古籍文字智能识别系统V1.0",
                "status": "已登记",
                "date": "2026-04-20",
                "description": "登记号: 2026SRXXXXXX，团队共同完成",
            },
            {
                "type": "竞赛获奖",
                "title": "全国大学生计算机设计大赛一等奖",
                "status": "获奖",
                "date": "2026-05-10",
                "description": "以本项目成果参赛，获得全国一等奖",
            },
        ],
        "budget_final": {
            "allocated": 10000.0,
            "spent": 9650.0,
            "details": [
                {"category": "设备费", "amount": 3000.0, "description": "GPU服务器租赁（12个月）"},
                {"category": "材料费", "amount": 1500.0, "description": "古籍扫描图像数据集采购"},
                {"category": "测试费", "amount": 800.0, "description": "第三方模型评测服务"},
                {"category": "差旅费", "amount": 1200.0, "description": "古籍馆实地调研（3次）"},
                {"category": "出版费", "amount": 2000.0, "description": "核心期刊论文版面费"},
                {"category": "劳务费", "amount": 1150.0, "description": "数据标注外包服务"},
            ],
        },
        "research_summary": "本项目围绕古籍文字识别这一核心问题，开展了以下研究工作：首先，系统收集了来自国家图书馆、故宫博物院等机构的5000页古籍扫描图像，经过清洗、去噪、增强等预处理，构建了高质量的训练数据集。其次，设计了基于ResNet-50特征提取器和Transformer序列建模器的混合架构，引入了注意力机制和多任务学习框架。最后，开发了基于Flask的Web服务端和基于Vue.js的前端界面，实现了端到端的古籍数字化流水线。",
        "innovation_summary": "本项目的创新点主要体现在三个方面：第一，首次提出了专门针对古籍文字的深度学习识别模型，针对古籍中常见的异体字、模糊字、残缺字等问题进行了专门优化；第二，引入了多任务学习框架，同时进行文字检测、识别和语义理解，提升了整体识别效果；第三，实现了从图像采集到文字输出的全自动化处理流程，大幅降低了古籍数字化的技术门槛和人工成本。",
        "experience_summary": "通过参与本项目，团队成员在以下方面获得了宝贵的经验：在学术研究方面，掌握了从问题定义、文献调研、方案设计到实验验证的完整科研流程；在技术能力方面，深入学习了深度学习、计算机视觉、自然语言处理等前沿技术，并具备了独立开发和部署AI系统的能力；在团队协作方面，通过明确的分工和定期的沟通，培养了良好的项目管理意识和团队合作精神。",
        "future_outlook": "本项目仍存在一些不足之处：模型对于严重破损页面的识别效果仍有提升空间；系统目前仅支持简体中文古籍，对繁体字和少数民族文字的支持尚不完善；用户界面的交互体验还可以进一步优化。未来计划从以下方向继续深入研究：引入图像修复技术提升破损页面识别率；扩展模型以支持更多文字类型；探索将模型部署到移动端，实现随时随地的古籍文字识别。",
        "team_contributions": [
            {"name": "张三", "contribution": "项目负责人，负责整体方案设计、模型架构设计与训练、论文撰写"},
            {"name": "李四", "contribution": "负责算法实现、实验设计与数据分析、模型调优"},
            {"name": "王五", "contribution": "负责数据集构建、数据标注管理、数据预处理 pipeline 开发"},
            {"name": "赵六", "contribution": "负责前端界面设计与开发、后端 API 接口开发、系统部署"},
        ],
        "advisor_evaluation": "该项目团队表现优秀，能够按照计划有序推进各项工作。项目选题具有重要的学术价值和实际应用意义，技术路线清晰，创新点突出。团队成员分工明确、协作良好，最终成果超出预期。建议评定为优秀等级。",
        "department_evaluation": "经审核，该项目已完成全部预定目标，成果丰硕，同意结题。建议评定为优秀等级。",
    }

    generator = FinalReportGenerator()
    report = generator.generate(sample_report)
    print(f"结题报告生成成功，成果数量: {len(report['achievements'])} 项")
    print(f"经费使用率: {report['budget_final']['usage_rate']}%")

    # generator.export_to_docx(report, "结题报告.docx")
    # generator.export_to_json(report, "结题报告.json")
