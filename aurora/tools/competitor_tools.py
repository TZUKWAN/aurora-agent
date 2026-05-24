"""Competitor analysis tools for AuroraAgent."""

import json
import logging

from aurora.competition.competitor_analyzer import CompetitorAnalyzer

logger = logging.getLogger(__name__)

_analyzer = CompetitorAnalyzer()


def _register_tools(registry):
    """Register competitor analysis tools to the registry."""
    registry.register(
        "competitor_swot",
        "SWOT分析: 分析项目的优势、劣势、机会和威胁",
        {
            "type": "object",
            "properties": {
                "project_info": {
                    "type": "object",
                    "description": "项目信息，包含technology, business_model, target_market, team_background, project_stage, innovation, social_impact等"
                }
            },
            "required": ["project_info"]
        },
        _competitor_swot_handler
    )

    registry.register(
        "competitor_compare",
        "竞争对手比较: 将我方项目与竞争对手进行多维度对比分析",
        {
            "type": "object",
            "properties": {
                "our_project": {
                    "type": "object",
                    "description": "我方项目信息"
                },
                "competitors": {
                    "type": "array",
                    "description": "竞争对手列表，每项包含name, strengths, weaknesses, market_share",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "竞争对手名称"},
                            "strengths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "对手优势"
                            },
                            "weaknesses": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "对手劣势"
                            },
                            "market_share": {
                                "description": "市场份额(%)",
                                "oneOf": [
                                    {"type": "number"},
                                    {"type": "string"}
                                ]
                            }
                        }
                    }
                }
            },
            "required": ["our_project", "competitors"]
        },
        _competitor_compare_handler
    )

    registry.register(
        "competitor_strategy",
        "竞争策略生成: 基于项目信息和竞争态势生成策略建议",
        {
            "type": "object",
            "properties": {
                "project_info": {
                    "type": "object",
                    "description": "项目信息"
                },
                "competitors": {
                    "type": "array",
                    "description": "竞争对手列表",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "strengths": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "weaknesses": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "market_share": {
                                "oneOf": [
                                    {"type": "number"},
                                    {"type": "string"}
                                ]
                            }
                        }
                    }
                }
            },
            "required": ["project_info", "competitors"]
        },
        _competitor_strategy_handler
    )

    registry.register(
        "competitor_market_position",
        "市场定位分析: 分析项目在市场中的竞争地位",
        {
            "type": "object",
            "properties": {
                "project_info": {
                    "type": "object",
                    "description": "项目信息"
                },
                "market_data": {
                    "type": "object",
                    "description": "市场数据（可选），可包含market_size, growth_rate, competitor_count, our_market_share等"
                }
            },
            "required": ["project_info"]
        },
        _competitor_market_position_handler
    )


def _competitor_swot_handler(args):
    """Handle SWOT analysis tool call."""
    project_info = args.get("project_info")
    if not project_info:
        return json.dumps({"error": "缺少project_info参数"}, ensure_ascii=False)

    try:
        result = _analyzer.analyze_swot(project_info)
        return json.dumps({
            "result": "SWOT分析完成",
            "data": result
        }, ensure_ascii=False)
    except Exception as e:
        logger.exception("SWOT analysis failed")
        return json.dumps({"error": f"SWOT分析失败: {str(e)}"}, ensure_ascii=False)


def _competitor_compare_handler(args):
    """Handle competitor comparison tool call."""
    our_project = args.get("our_project")
    competitors = args.get("competitors")

    if not our_project:
        return json.dumps({"error": "缺少our_project参数"}, ensure_ascii=False)
    if not competitors or not isinstance(competitors, list):
        return json.dumps({"error": "缺少competitors参数或格式不正确"}, ensure_ascii=False)

    try:
        result = _analyzer.compare_competitors(our_project, competitors)
        return json.dumps({
            "result": "竞争对手比较分析完成",
            "data": result
        }, ensure_ascii=False)
    except Exception as e:
        logger.exception("Competitor comparison failed")
        return json.dumps({"error": f"竞争对手比较失败: {str(e)}"}, ensure_ascii=False)


def _competitor_strategy_handler(args):
    """Handle competitive strategy tool call."""
    project_info = args.get("project_info")
    competitors = args.get("competitors", [])

    if not project_info:
        return json.dumps({"error": "缺少project_info参数"}, ensure_ascii=False)

    try:
        result = _analyzer.generate_competitive_strategy(project_info, competitors)
        return json.dumps({
            "result": "竞争策略生成完成",
            "data": result
        }, ensure_ascii=False)
    except Exception as e:
        logger.exception("Competitive strategy generation failed")
        return json.dumps({"error": f"竞争策略生成失败: {str(e)}"}, ensure_ascii=False)


def _competitor_market_position_handler(args):
    """Handle market position analysis tool call."""
    project_info = args.get("project_info")
    market_data = args.get("market_data")

    if not project_info:
        return json.dumps({"error": "缺少project_info参数"}, ensure_ascii=False)

    try:
        result = _analyzer.analyze_market_position(project_info, market_data)
        return json.dumps({
            "result": "市场定位分析完成",
            "data": result
        }, ensure_ascii=False)
    except Exception as e:
        logger.exception("Market position analysis failed")
        return json.dumps({"error": f"市场定位分析失败: {str(e)}"}, ensure_ascii=False)
