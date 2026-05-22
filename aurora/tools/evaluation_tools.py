"""Evaluation tools for AuroraAgent."""

import json

from aurora.evaluation.engine import EvaluationEngine


def _register_tools(registry):
    """Register evaluation tools to the registry."""
    registry.register(
        "evaluate",
        "项目评审评估",
        {
            "type": "object",
            "properties": {
                "project_info": {"type": "object", "description": "项目信息"},
                "competition_id": {"type": "string", "description": "目标竞赛ID"},
                "dimensions": {"type": "array", "items": {"type": "string"}, "description": "评估维度列表"}
            },
            "required": ["project_info"]
        },
        _evaluate_handler
    )

    registry.register(
        "eval_diagnose",
        "项目问题诊断",
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
        "获取优化建议",
        {
            "type": "object",
            "properties": {
                "project_info": {"type": "object", "description": "项目信息"},
                "competition_id": {"type": "string", "description": "目标竞赛ID"}
            },
            "required": ["project_info"]
        },
        _eval_suggest_handler
    )


def _evaluate_handler(args):
    """Evaluate a project."""
    engine = EvaluationEngine()
    
    project_info = args.get("project_info", {})
    competition_id = args.get("competition_id", "internet_plus")
    dimensions = args.get("dimensions")
    
    result = engine.evaluate(project_info, competition_id, dimensions)
    
    return json.dumps(result, ensure_ascii=False)


def _eval_diagnose_handler(args):
    """Diagnose problems in a project."""
    engine = EvaluationEngine()
    
    project_info = args.get("project_info", {})
    competition_id = args.get("competition_id", "internet_plus")
    
    result = engine.evaluate(project_info, competition_id)
    
    problems = []
    for dim in result.get("dimensions", []):
        if dim["score"] < 70:
            problems.append({
                "dimension": dim["name"],
                "score": dim["score"],
                "feedback": dim["feedback"],
                "suggestions": dim["suggestions"]
            })
    
    return json.dumps({
        "result": f"诊断完成，发现 {len(problems)} 个待改进维度",
        "problems": problems
    }, ensure_ascii=False)


def _eval_suggest_handler(args):
    """Get improvement suggestions for a project."""
    engine = EvaluationEngine()
    
    project_info = args.get("project_info", {})
    competition_id = args.get("competition_id", "internet_plus")
    
    result = engine.evaluate(project_info, competition_id)
    
    return json.dumps({
        "result": "优化建议已生成",
        "suggestions": result.get("suggestions", []),
        "feedback": result.get("feedback", "")
    }, ensure_ascii=False)
