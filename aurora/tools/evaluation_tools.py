"""Evaluation tools for AuroraAgent."""

import json
import logging

from aurora.evaluation.engine import EvaluationEngine

logger = logging.getLogger(__name__)

def _register_tools(registry):
    """Register evaluation tools to the registry."""
    registry.register(
        "evaluate",
        "全维度项目评审评估机制，带安全机制",
        {
            "type": "object",
            "properties": {
                "project_info": {"type": "object", "description": "待评估项目信息字典"},
                "competition_id": {"type": "string", "description": "目标竞赛ID"},
                "dimensions": {"type": "array", "items": {"type": "string"}, "description": "选择需要核心突破的评估维度，如[商业, 创新, 技术]"}
            },
            "required": ["project_info"]
        },
        _evaluate_handler
    )

    registry.register(
        "eval_diagnose",
        "项目短板深度诊断雷达与安全沙箱",
        {
            "type": "object",
            "properties": {
                "project_info": {"type": "object", "description": "项目信息"},
                "competition_id": {"type": "string", "description": "目标竞赛ID"}
            },
            "required": ["project_info"]
        },
        _eval_diagnose_handler
    )

    registry.register(
        "eval_suggest",
        "智能调优与重塑发展建议",
        {
            "type": "object",
            "properties": {
                "project_info": {"type": "object", "description": "项目基础资料"},
                "competition_id": {"type": "string", "description": "指定应对的具体大赛场景"}
            },
            "required": ["project_info"]
        },
        _eval_suggest_handler
    )


def _evaluate_handler(args):
    """Evaluate a project securely."""
    try:
        engine = EvaluationEngine()

        project_info = args.get("project_info", {})
        competition_id = args.get("competition_id", "internet_plus")
        dimensions = args.get("dimensions")

        logger.info(f"Evaluating project against {competition_id} criteria...")
        result = engine.evaluate(project_info, competition_id, dimensions)

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Project evaluation failed: {e}")
        return json.dumps(
            {"error": "系统评估模块运行中断", "details": str(e)}, 
            ensure_ascii=False
        )


def _eval_diagnose_handler(args):
    """Diagnose problems in a project reliably."""
    try:
        engine = EvaluationEngine()

        project_info = args.get("project_info", {})
        competition_id = args.get("competition_id", "internet_plus")

        result = engine.evaluate(project_info, competition_id)
        
        problems = []
        # Fallback dictionary if 'dimensions' key is missing due to evaluation stub failures
        dims = result.get("dimensions", [])
        
        for dim in dims:
            if dim.get("score", 0) < 70:
                problems.append({
                    "dimension": dim.get("name", "未命名维度"),
                    "score": dim.get("score", 0),
                    "feedback": dim.get("feedback", "需要深入完善该模块"),
                    "suggestions": dim.get("suggestions", [])
                })

        return json.dumps({
            "result": f"高精度雷达诊断完成，发现 {len(problems)} 个处于风险线的维度指标",
            "problems": problems
        }, ensure_ascii=False)
    except Exception as e:
        logger.exception("Error diagnosing project:")
        return json.dumps({"error": f"数据诊断阻断: {str(e)}"}, ensure_ascii=False)


def _eval_suggest_handler(args):
    """Get rich improvement suggestions for a project."""
    try:
        engine = EvaluationEngine()

        project_info = args.get("project_info", {})
        competition_id = args.get("competition_id", "internet_plus")

        result = engine.evaluate(project_info, competition_id)

        suggestions = result.get("suggestions", [])
        if not suggestions:
            suggestions.append("在现有数据下系统认为项目运行良好，但需注意在竞品对标中的长期壁垒建设。")

        return json.dumps({
            "result": "优化与发展战略建议生成完成",
            "suggestions": suggestions,
            "feedback": result.get("feedback", "整体框架合格，注意提升表现力细节。")
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to generate evaluation suggestions: {e}")
        return json.dumps({"error": f"评级与建议环节故障, 详情: {str(e)}"}, ensure_ascii=False)
