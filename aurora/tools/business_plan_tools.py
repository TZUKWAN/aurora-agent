"""Business plan tools for AuroraAgent."""

import json
import logging

from aurora.business_plan.generator import BusinessPlanGenerator

logger = logging.getLogger(__name__)

def _register_tools(registry):
    """Register business plan tools to the registry."""
    registry.register(
        "bp_generate",
        "生成完整商业计划书",
        {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "项目名称"},
                "technology": {"type": "string", "description": "技术领域"},
                "problem": {"type": "string", "description": "解决的问题"},
                "solution": {"type": "string", "description": "解决方案"},
                "product": {"type": "string", "description": "产品名称"},
                "target_market": {"type": "string", "description": "目标市场"},
                "business_model": {"type": "string", "description": "商业模式"},
                "team_background": {"type": "string", "description": "团队背景"},
                "competition_id": {"type": "string", "description": "目标竞赛ID"}
            },
            "required": ["project_name", "technology", "target_market"]
        },
        _bp_generate_handler
    )

    registry.register(
        "bp_section_write",
        "撰写商业计划书特定章节，支持高并发调用",
        {
            "type": "object",
            "properties": {
                "section_id": {
                    "type": "string", 
                    "description": "章节ID (executive_summary, project_overview, market_analysis, 等)"
                },
                "project_info": {"type": "object", "description": "项目相关详细信息，包含产品、目标、成员等"}
            },
            "required": ["section_id", "project_info"]
        },
        _bp_section_write_handler
    )

    registry.register(
        "bp_export",
        "导出商业计划书（支持健壮的异常重试与容错捕获）",
        {
            "type": "object",
            "properties": {
                "plan": {"type": "object", "description": "商业计划书结构与内容字典"},
                "format": {"type": "string", "description": "导出格式(md/docx)", "enum": ["md", "docx"]},
                "filepath": {"type": "string", "description": "保存的绝对路径或相对路径"}
            },
            "required": ["plan", "format", "filepath"]
        },
        _bp_export_handler
    )


def _bp_generate_handler(args):
    """Generate a complete business plan with fault tolerance."""
    try:
        generator = BusinessPlanGenerator()

        project_info = {
            "project_name": args.get("project_name", ""),
            "technology": args.get("technology", ""),
            "problem": args.get("problem", ""),
            "solution": args.get("solution", ""),
            "product": args.get("product", ""),
            "target_market": args.get("target_market", ""),
            "business_model": args.get("business_model", ""),
            "team_background": args.get("team_background", "")
        }

        competition_id = args.get("competition_id", "internet_plus")

        logger.info(f"Generating full business plan for {project_info['project_name']}...")
        plan = generator.generate(project_info, competition_id)

        return json.dumps({
            "result": "商业计划书生成完成",
            "plan": plan
        }, ensure_ascii=False)
    except Exception as e:
        logger.exception("Failed to generate complete business plan")
        return json.dumps({
            "error": "生成完整商业计划书失败",
            "reason": str(e)
        }, ensure_ascii=False)


def _bp_section_write_handler(args):
    """Write a specific section of business plan with robust exception handling."""
    try:
        section_id = args.get("section_id")
        project_info = args.get("project_info", {})

        generator = BusinessPlanGenerator()
        content = generator.generate_section(project_info, section_id)

        title = generator.SECTION_TEMPLATES.get(section_id, {}).get("title", f"未知章节({section_id})")

        return json.dumps({
            "section_id": section_id,
            "section_title": title,
            "content": content
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to generate section {args.get('section_id')}: {e}")
        return json.dumps({
            "section_id": args.get("section_id", "unknown"),
            "section_title": "生成失败",
            "content": f"[错误: 无法生成内容详情，原因: {str(e)}]",
            "error": True
        }, ensure_ascii=False)


def _bp_export_handler(args):
    """Export business plan to file securely."""
    try:
        plan = args.get("plan")
        if not plan:
            raise ValueError("提供的商业计划书内容为空")
            
        fmt = args.get("format", "md").lower()
        filepath = args.get("filepath")
        if not filepath:
            raise ValueError("必须提供有效的文件导出路径")

        generator = BusinessPlanGenerator()

        if fmt == "docx":
            result = generator.export_to_docx(plan, filepath)
        else:
            result = generator.export_to_markdown(plan, filepath)

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.exception("Failed during document export")
        return json.dumps({
            "success": False,
            "message": f"导出失败: {str(e)}"
        }, ensure_ascii=False)
