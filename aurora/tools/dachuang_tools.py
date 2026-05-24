"""Dachuang (大学生创新创业训练计划) tools for AuroraAgent."""

import json
import logging

from aurora.dachuang.generator import DachuangGenerator
from aurora.dachuang.evaluator import DachuangEvaluator
from aurora.dachuang.budget import BudgetGenerator
from aurora.dachuang.exporter import DachuangDocxExporter, DachuangPDFExporter

logger = logging.getLogger(__name__)


def _register_tools(registry):
    """Register Dachuang tools to the registry."""

    registry.register(
        "dachuang_generate",
        "生成完整的大创项目申报书（创新训练或创业训练）",
        {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "项目名称"},
                "project_type": {"type": "string", "description": "项目类型: innovation(创新训练) 或 entrepreneurship(创业训练)"},
                "level": {"type": "string", "description": "申报等级: national(国家级) / provincial(省级) / school(校级)"},
                "technology": {"type": "string", "description": "核心技术/技术领域"},
                "problem": {"type": "string", "description": "要解决的问题/痛点"},
                "solution": {"type": "string", "description": "解决方案"},
                "target_market": {"type": "string", "description": "目标市场/用户"},
                "innovation": {"type": "string", "description": "创新点"},
                "social_impact": {"type": "string", "description": "社会效益"},
                "expected_outcomes": {"type": "string", "description": "预期成果"},
                "team_background": {"type": "string", "description": "团队背景"},
                "advisor": {"type": "string", "description": "指导教师"},
                "department": {"type": "string", "description": "所属院系"},
                "duration_months": {"type": "integer", "description": "项目周期(月), 默认12"},
            },
            "required": ["project_name", "project_type"]
        },
        _dachuang_generate_handler
    )

    registry.register(
        "dachuang_generate_section",
        "生成大创申报书的特定章节",
        {
            "type": "object",
            "properties": {
                "section_id": {"type": "string", "description": "章节ID"},
                "project_info": {"type": "object", "description": "项目详细信息"},
                "project_type": {"type": "string", "description": "项目类型: innovation 或 entrepreneurship"},
            },
            "required": ["section_id", "project_info", "project_type"]
        },
        _dachuang_generate_section_handler
    )

    registry.register(
        "dachuang_evaluate",
        "评估大创申报书质量",
        {
            "type": "object",
            "properties": {
                "application": {"type": "object", "description": "申报书内容字典"},
                "project_info": {"type": "object", "description": "项目信息"},
                "project_type": {"type": "string", "description": "项目类型"},
            },
            "required": ["application", "project_info", "project_type"]
        },
        _dachuang_evaluate_handler
    )

    registry.register(
        "dachuang_generate_budget",
        "生成大创项目经费预算",
        {
            "type": "object",
            "properties": {
                "project_info": {"type": "object", "description": "项目信息"},
                "total_amount": {"type": "number", "description": "总预算金额(元)"},
                "project_type": {"type": "string", "description": "项目类型: innovation 或 entrepreneurship"},
            },
            "required": ["total_amount", "project_type"]
        },
        _dachuang_generate_budget_handler
    )

    registry.register(
        "dachuang_validate_budget",
        "验证大创经费预算的合理性",
        {
            "type": "object",
            "properties": {
                "items": {"type": "array", "description": "预算明细列表，每项包含category和amount"},
                "max_amount": {"type": "number", "description": "最大预算限额(元)"},
            },
            "required": ["items", "max_amount"]
        },
        _dachuang_validate_budget_handler
    )

    registry.register(
        "dachuang_export",
        "导出大创申报书为DOCX或PDF",
        {
            "type": "object",
            "properties": {
                "application": {"type": "object", "description": "申报书内容字典"},
                "format": {"type": "string", "description": "导出格式: docx 或 pdf", "enum": ["docx", "pdf"]},
                "filepath": {"type": "string", "description": "保存路径"},
            },
            "required": ["application", "format", "filepath"]
        },
        _dachuang_export_handler
    )


def _dachuang_generate_handler(args):
    try:
        project_info = {
            "project_name": args.get("project_name", ""),
            "technology": args.get("technology", ""),
            "problem": args.get("problem", ""),
            "solution": args.get("solution", ""),
            "target_market": args.get("target_market", ""),
            "innovation": args.get("innovation", ""),
            "social_impact": args.get("social_impact", ""),
            "expected_outcomes": args.get("expected_outcomes", ""),
            "team_background": args.get("team_background", ""),
            "advisor": args.get("advisor", ""),
            "department": args.get("department", ""),
            "leader": args.get("leader", ""),
        }
        project_type = args.get("project_type", "innovation")
        level = args.get("level", "school")
        duration = args.get("duration_months", 12)

        generator = DachuangGenerator()
        application = generator.generate(project_info, project_type)

        application["metadata"]["level"] = level
        application["metadata"]["duration_months"] = duration

        return json.dumps({
            "result": "大创申报书生成完成",
            "project_type": project_type,
            "section_count": len(application.get("sections", {})),
            "application": application,
        }, ensure_ascii=False)
    except Exception as e:
        logger.exception("Failed to generate Dachuang application")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _dachuang_generate_section_handler(args):
    try:
        section_id = args.get("section_id")
        project_info = args.get("project_info", {})
        project_type = args.get("project_type", "innovation")

        generator = DachuangGenerator()
        content = generator.generate_section(project_info, section_id, project_type)

        templates = generator.INNOVATION_SECTIONS if project_type == "innovation" else generator.ENTREPRENEURSHIP_SECTIONS
        title = templates.get(section_id, {}).get("title", f"未知章节({section_id})")

        return json.dumps({
            "section_id": section_id,
            "section_title": title,
            "content": content,
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to generate section {args.get('section_id')}: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _dachuang_evaluate_handler(args):
    try:
        application = args.get("application", {})
        project_info = args.get("project_info", {})
        project_type = args.get("project_type", "innovation")

        evaluator = DachuangEvaluator()
        result = evaluator.evaluate(project_info, application, project_type)

        return json.dumps({
            "result": "申报书评估完成",
            "evaluation": result,
        }, ensure_ascii=False)
    except Exception as e:
        logger.exception("Evaluation failed")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _dachuang_generate_budget_handler(args):
    try:
        total_amount = args.get("total_amount", 10000.0)
        project_type = args.get("project_type", "innovation")
        project_info = args.get("project_info", {})

        generator = BudgetGenerator()
        items = generator.generate_budget(project_info, total_amount, project_type)

        return json.dumps({
            "result": "预算生成完成",
            "total": total_amount,
            "items": [{"category": i.category, "amount": i.amount, "justification": i.justification} for i in items],
        }, ensure_ascii=False)
    except Exception as e:
        logger.exception("Budget generation failed")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _dachuang_validate_budget_handler(args):
    try:
        from aurora.models.dachuang import BudgetItem
        raw_items = args.get("items", [])
        max_amount = args.get("max_amount")

        items = [BudgetItem(category=i["category"], amount=i["amount"], justification=i.get("justification", "")) for i in raw_items]

        generator = BudgetGenerator()
        result = generator.validate_budget(items, max_amount)

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.exception("Budget validation failed")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _dachuang_export_handler(args):
    try:
        application = args.get("application")
        fmt = args.get("format", "docx").lower()
        filepath = args.get("filepath")

        if not application:
            return json.dumps({"error": "申报书内容为空"}, ensure_ascii=False)
        if not filepath:
            return json.dumps({"error": "必须提供导出路径"}, ensure_ascii=False)

        if fmt == "pdf":
            exporter = DachuangPDFExporter()
            result = exporter.export(application, filepath)
        else:
            exporter = DachuangDocxExporter()
            result = exporter.export(application, filepath)

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.exception("Export failed")
        return json.dumps({"error": str(e)}, ensure_ascii=False)
