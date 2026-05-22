"""Presentation tools for AuroraAgent."""

import json

from aurora.presentation.ppt_generator import PPTGenerator


def _register_tools(registry):
    """Register presentation tools to the registry."""
    registry.register(
        "ppt_generate",
        "生成路演PPT内容",
        {
            "type": "object",
            "properties": {
                "project_info": {"type": "object", "description": "项目信息"},
                "competition_id": {"type": "string", "description": "目标竞赛ID"}
            },
            "required": ["project_info"]
        },
        _ppt_generate_handler
    )

    registry.register(
        "script_generate",
        "生成路演脚本",
        {
            "type": "object",
            "properties": {
                "ppt_content": {"type": "object", "description": "PPT内容"}
            },
            "required": ["ppt_content"]
        },
        _script_generate_handler
    )

    registry.register(
        "defense_practice",
        "答辩模拟练习",
        {
            "type": "object",
            "properties": {
                "project_info": {"type": "object", "description": "项目信息"},
                "question_count": {"type": "integer", "description": "题目数量"},
                "competition_id": {"type": "string", "description": "目标竞赛ID"}
            },
            "required": ["project_info"]
        },
        _defense_practice_handler
    )


def _ppt_generate_handler(args):
    """Generate PPT content."""
    generator = PPTGenerator()
    
    project_info = args.get("project_info", {})
    competition_id = args.get("competition_id", "internet_plus")
    
    ppt_content = generator.generate(project_info, competition_id)
    
    return json.dumps({
        "result": "PPT内容生成完成",
        "slide_count": ppt_content["slide_count"],
        "slides": ppt_content["slides"]
    }, ensure_ascii=False)


def _script_generate_handler(args):
    """Generate presentation script."""
    ppt_content = args.get("ppt_content", {})
    
    generator = PPTGenerator()
    script = generator.generate_script(ppt_content)
    
    return json.dumps({
        "result": "路演脚本生成完成",
        "script": script
    }, ensure_ascii=False)


def _defense_practice_handler(args):
    """Generate practice questions for defense."""
    project_info = args.get("project_info", {})
    question_count = args.get("question_count", 5)
    competition_id = args.get("competition_id", "internet_plus")
    
    questions = [
        {"question": "请介绍一下你们项目的核心创新点是什么？", "type": "技术"},
        {"question": "你们的商业模式是怎样的？如何盈利？", "type": "商业"},
        {"question": "目前项目处于什么阶段？有哪些运营数据？", "type": "运营"},
        {"question": "团队成员的背景和分工是怎样的？", "type": "团队"},
        {"question": "未来3-5年的发展规划是什么？", "type": "规划"},
        {"question": "你们的核心技术壁垒是什么？", "type": "技术"},
        {"question": "市场竞争情况如何？你们的竞争优势是什么？", "type": "商业"},
        {"question": "融资计划是怎样的？资金如何使用？", "type": "财务"},
    ]
    
    selected = questions[:min(question_count, len(questions))]
    
    return json.dumps({
        "result": f"生成了 {len(selected)} 道答辩练习题",
        "questions": selected
    }, ensure_ascii=False)
