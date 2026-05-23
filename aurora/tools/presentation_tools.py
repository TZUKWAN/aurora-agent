"""Presentation tools for AuroraAgent."""

import json
import logging

from aurora.presentation.ppt_generator import PPTGenerator

logger = logging.getLogger(__name__)

def _register_tools(registry):
    """Register presentation tools to the registry."""
    registry.register(
        "ppt_generate",
        "智能生成路演PPT大纲与具体结构、每一页核心讲稿",
        {
            "type": "object",
            "properties": {
                "project_info": {"type": "object", "description": "提取自商业计划书的核心项目信息"},
                "competition_id": {"type": "string", "description": "目标竞赛环境，如互联网+等"},
                "slides_count": {"type": "integer", "description": "期望的PPT总页数（参考）"}
            },
            "required": ["project_info"]
        },
        _ppt_generate_handler
    )

    registry.register(
        "script_generate",
        "生成引人入胜的现场路演逐字讲稿",
        {
            "type": "object",
            "properties": {
                "ppt_content": {"type": "object", "description": "系统已生成的PPT内容结构"}
            },
            "required": ["ppt_content"]
        },
        _script_generate_handler
    )

    registry.register(
        "defense_practice",
        "多维度答辩模拟问题与应对策略演练",
        {
            "type": "object",
            "properties": {
                "project_info": {"type": "object", "description": "项目信息"},
                "question_count": {"type": "integer", "description": "需要生成的题目数量"},
                "competition_id": {"type": "string", "description": "目标竞赛环境"},
                "focus_domain": {"type": "string", "description": "偏向的提问类型，例如：技术、商业、财务等"}
            },
            "required": ["project_info"]
        },
        _defense_practice_handler
    )


def _ppt_generate_handler(args):
    """Generate PPT content with error safety."""
    try:
        generator = PPTGenerator()

        project_info = args.get("project_info", {})
        competition_id = args.get("competition_id", "internet_plus")

        logger.info("Generating PPT structure...")
        ppt_content = generator.generate(project_info, competition_id)

        # Ensure return contract
        if not ppt_content or "slides" not in ppt_content:
            raise ValueError("PPT Generator failed to produce 'slides'.")

        return json.dumps({
            "result": "PPT内容生成完成",
            "slide_count": ppt_content.get("slide_count", len(ppt_content["slides"])),
            "slides": ppt_content["slides"]
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to generate PPT outline: {e}")
        return json.dumps({"error": f"PPT大纲生成失败: {str(e)}"}, ensure_ascii=False)


def _script_generate_handler(args):
    """Generate presentation script robustly."""
    try:
        ppt_content = args.get("ppt_content", {})
        if not ppt_content:
            return json.dumps({"error": "缺少有效的 PPT 内容结构"}, ensure_ascii=False)

        generator = PPTGenerator()
        script = generator.generate_script(ppt_content)

        return json.dumps({
            "result": "路演讲稿生成完成",
            "script": script
        }, ensure_ascii=False)
    except Exception as e:
        logger.exception("Error generating presentation script")
        return json.dumps({"error": f"讲稿生成过程崩溃: {str(e)}"}, ensure_ascii=False)


def _defense_practice_handler(args):
    """Generate intelligent practice defense questions."""
    try:
        question_count = args.get("question_count", 5)
        focus_domain = args.get("focus_domain", "all")

        # 更丰富的数据源和多维打靶
        base_questions = [
            {"question": "请介绍一下你们项目的核心创新点是什么？它是如何建立防线壁垒的？", "type": "技术"},
            {"question": "市面上已经有类似竞品，你们凭什么相信能抢占他们的市场？", "type": "商业"},
            {"question": "冷启动阶段的用户是如何获取的？你们的获客成本(CAC)是多少？", "type": "运营"},
            {"question": "请说说各阶段团队成员具体分工；如果项目转型，你们是否能快速适应？", "type": "团队"},
            {"question": "在你们的发展规划中，哪一个里程碑节点最依赖外部环境的催化？", "type": "规划"},
            {"question": "针对这种开源的底层框架，你们怎么保证在应用层不被巨头快速复刻？", "type": "技术"},
            {"question": "商业闭环是如何实现的？付费意愿的转化率目标是多少？", "type": "商业"},
            {"question": "项目资金缺口目前是多少？这笔融资主要用在什么刀刃上？", "type": "财务"},
            {"question": "未来的退出机制是什么？如果是并购，潜在买家有哪些？", "type": "规划"}
        ]

        if focus_domain != "all":
            filtered = [q for q in base_questions if q["type"] == focus_domain]
            if len(filtered) > 0:
                base_questions = filtered

        import random
        # 增加一点随机性，避免每次生成重复的答辩题
        selected = random.sample(base_questions, min(question_count, len(base_questions)))

        return json.dumps({
            "result": f"为您专项生成了 {len(selected)} 道核心答辩切入题",
            "domain_bias": focus_domain,
            "questions": selected
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to generate defense practice: {e}")
        return json.dumps({"error": f"答辩题目生成异常: {str(e)}"}, ensure_ascii=False)
