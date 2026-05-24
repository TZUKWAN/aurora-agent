"""Team management tools for AuroraAgent."""

import json

from aurora.team.manager import TeamManager


def _register_tools(registry):
    """Register team management tools to the registry."""
    registry.register(
        "team_analyze",
        "分析团队组成，评估团队完整性和角色覆盖",
        {
            "type": "object",
            "properties": {
                "members": {
                    "type": "array",
                    "description": "团队成员列表",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "成员姓名"},
                            "role": {
                                "type": "string",
                                "description": "角色: leader, tech, business, design, marketing, finance, advisor",
                            },
                            "skills": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "技能列表",
                            },
                            "background": {"type": "string", "description": "背景"},
                        },
                        "required": ["name", "role"],
                    },
                }
            },
            "required": ["members"],
        },
        _team_analyze_handler,
    )

    registry.register(
        "team_suggest",
        "根据项目类型建议理想团队配置",
        {
            "type": "object",
            "properties": {
                "project_type": {
                    "type": "string",
                    "description": "项目类型: tech, business, social 等",
                },
                "technology": {
                    "type": "string",
                    "description": "技术领域（可选）",
                },
                "market": {
                    "type": "string",
                    "description": "目标市场（可选）",
                },
            },
            "required": ["project_type"],
        },
        _team_suggest_handler,
    )

    registry.register(
        "team_assign",
        "为团队成员生成职责分配",
        {
            "type": "object",
            "properties": {
                "members": {
                    "type": "array",
                    "description": "团队成员列表",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "skills": {"type": "array", "items": {"type": "string"}},
                            "background": {"type": "string"},
                        },
                        "required": ["name", "role"],
                    },
                },
                "project_info": {
                    "type": "object",
                    "description": "项目信息",
                    "properties": {
                        "name": {"type": "string", "description": "项目名称"},
                        "type": {"type": "string", "description": "项目类型"},
                    },
                },
            },
            "required": ["members", "project_info"],
        },
        _team_assign_handler,
    )

    registry.register(
        "team_validate",
        "验证团队是否符合竞赛要求",
        {
            "type": "object",
            "properties": {
                "members": {
                    "type": "array",
                    "description": "团队成员列表",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "skills": {"type": "array", "items": {"type": "string"}},
                            "background": {"type": "string"},
                        },
                        "required": ["name", "role"],
                    },
                },
                "competition_id": {
                    "type": "string",
                    "description": "竞赛ID（可选）",
                },
            },
            "required": ["members"],
        },
        _team_validate_handler,
    )


def _team_analyze_handler(args):
    """Handle team_analyze tool call."""
    members = args.get("members", [])
    manager = TeamManager()
    analysis = manager.analyze_team(members)

    return json.dumps(
        {
            "result": f"团队完整度评分: {analysis.completeness_score:.1f}/100",
            "data": {
                "completeness_score": analysis.completeness_score,
                "role_coverage": analysis.role_coverage,
                "missing_roles": analysis.missing_roles,
                "strength_areas": analysis.strength_areas,
                "weakness_areas": analysis.weakness_areas,
                "recommendations": analysis.recommendations,
            },
        },
        ensure_ascii=False,
    )


def _team_suggest_handler(args):
    """Handle team_suggest tool call."""
    project_info = {
        "type": args.get("project_type", ""),
        "technology": args.get("technology", ""),
        "market": args.get("market", ""),
    }
    manager = TeamManager()
    formation = manager.suggest_formation(project_info)

    roles_data = []
    for role in formation:
        roles_data.append(
            {
                "role_id": role.role_id,
                "name": role.name,
                "description": role.description,
                "required_skills": role.required_skills,
                "weight": role.weight,
            }
        )

    return json.dumps(
        {
            "result": f"建议团队配置（按优先级排序）",
            "data": roles_data,
        },
        ensure_ascii=False,
    )


def _team_assign_handler(args):
    """Handle team_assign tool call."""
    members = args.get("members", [])
    project_info = args.get("project_info", {})
    manager = TeamManager()
    assignments = manager.generate_responsibilities(members, project_info)

    return json.dumps(
        {
            "result": f"已为{len(assignments)}名成员分配职责",
            "data": assignments,
        },
        ensure_ascii=False,
    )


def _team_validate_handler(args):
    """Handle team_validate tool call."""
    members = args.get("members", [])
    competition_id = args.get("competition_id", "")
    manager = TeamManager()
    validation = manager.validate_team(members, competition_id)

    status = "通过" if validation["valid"] else "未通过"
    return json.dumps(
        {
            "result": f"团队验证{status}",
            "data": validation,
        },
        ensure_ascii=False,
    )
