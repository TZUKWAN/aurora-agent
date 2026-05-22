"""Business plan tools for AuroraAgent."""

import json

from aurora.business_plan.generator import BusinessPlanGenerator


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
        "撰写商业计划书章节",
        {
            "type": "object",
            "properties": {
                "section_id": {"type": "string", "description": "章节ID"},
                "project_info": {"type": "object", "description": "项目信息"}
            },
            "required": ["section_id", "project_info"]
        },
        _bp_section_write_handler
    )

    registry.register(
        "bp_export",
        "导出商业计划书",
        {
            "type": "object",
            "properties": {
                "plan": {"type": "object", "description": "商业计划书内容"},
                "format": {"type": "string", "description": "导出格式(md/docx)"},
                "filepath": {"type": "string", "description": "保存路径"}
            },
            "required": ["plan", "format", "filepath"]
        },
        _bp_export_handler
    )


def _bp_generate_handler(args):
    """Generate a complete business plan."""
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
    
    plan = generator.generate(project_info, competition_id)
    
    return json.dumps({
        "result": "商业计划书生成完成",
        "plan": plan
    }, ensure_ascii=False)


def _bp_section_write_handler(args):
    """Write a specific section of business plan."""
    section_id = args.get("section_id")
    project_info = args.get("project_info", {})
    
    generator = BusinessPlanGenerator()
    content = generator.generate_section(project_info, section_id)
    
    return json.dumps({
        "section_id": section_id,
        "section_title": generator.SECTION_TEMPLATES.get(section_id, {}).get("title", ""),
        "content": content
    }, ensure_ascii=False)


def _bp_export_handler(args):
    """Export business plan to file."""
    plan = args.get("plan")
    fmt = args.get("format", "md")
    filepath = args.get("filepath")
    
    generator = BusinessPlanGenerator()
    
    if fmt == "docx":
        result = generator.export_to_docx(plan, filepath)
    else:
        result = generator.export_to_markdown(plan, filepath)
    
    return json.dumps(result, ensure_ascii=False)
