"""Role templates for AuroraAgent's swarm system."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RoleTemplate:
    role_id: str
    name: str
    description: str
    system_prompt: str
    allowed_tools: List[str] = field(default_factory=list)
    expertise: List[str] = field(default_factory=list)
    needs_tools: bool = True


def _role(
    role_id: str,
    name: str,
    description: str,
    system_prompt: str,
    tools: Optional[List[str]] = None,
    expertise: Optional[List[str]] = None,
    needs_tools: bool = True,
) -> RoleTemplate:
    return RoleTemplate(
        role_id=role_id,
        name=name,
        description=description,
        system_prompt=system_prompt,
        allowed_tools=tools or [],
        expertise=expertise or [],
        needs_tools=needs_tools,
    )


ROLE_TEMPLATES = [
    _role(
        "competition_analyst",
        "竞赛分析师",
        "分析竞赛规则、匹配赛道、竞争对手分析",
        "你是竞赛分析专家。擅长分析教育部A类赛事的规则要求、匹配最适合的赛道、分析竞争对手情况。",
        [
            "competition_search",
            "track_matcher",
            "competitor_analysis",
            "case_library",
            "deadline_reminder",
        ],
        ["竞赛", "互联网+", "挑战杯", "赛道", "报名", "竞争对手"],
    ),
    _role(
        "business_analyst",
        "商业分析师",
        "市场分析、商业模式设计、财务规划",
        "你是商业分析专家。擅长市场调研、商业模式设计、财务预测和投资分析。",
        [
            "market_analysis",
            "business_model_design",
            "financial_plan",
            "user_research",
        ],
        ["市场分析", "商业模式", "财务", "用户研究", "盈利模式"],
    ),
    _role(
        "tech_expert",
        "技术专家",
        "技术可行性评估、技术壁垒分析",
        "你是技术专家。擅长评估技术可行性、分析技术壁垒、设计技术路线图。",
        ["tech_analysis", "patent_search", "tech_roadmap", "tech_feasibility"],
        ["技术", "专利", "可行性", "技术壁垒", "技术路线"],
    ),
    _role(
        "writing_expert",
        "写作专家",
        "商业计划书撰写、语言润色",
        "你是学术写作专家。擅长撰写高质量的商业计划书、优化语言表达、确保格式规范。",
        [
            "bp_generate",
            "bp_section_write",
            "bp_optimize",
            "language_polish",
            "format_check",
        ],
        ["商业计划书", "写作", "文案", "润色", "格式"],
    ),
    _role(
        "evaluation_expert",
        "评审专家",
        "模拟评审、问题诊断、优化建议",
        "你是评审专家。熟悉竞赛评审标准，擅长模拟评审、诊断问题、提供优化建议。",
        ["evaluate", "diagnose", "suggest_improve", "score_predict"],
        ["评审", "评分", "诊断", "优化", "建议"],
    ),
    _role(
        "presentation_coach",
        "路演教练",
        "PPT设计、脚本撰写、答辩训练",
        "你是路演专家。擅长PPT设计、脚本撰写、答辩训练和演讲指导。",
        [
            "ppt_generate",
            "script_write",
            "video_plan",
            "defense_simulate",
            "question_practice",
        ],
        ["PPT", "路演", "答辩", "脚本", "视频"],
    ),
    _role(
        "team_coordinator",
        "团队协调员",
        "任务分解、进度协调、结果汇总",
        "你是团队协调专家。擅长任务分解、进度协调、资源分配和结果汇总。",
        ["task_decompose", "progress_track", "resource_allocate", "result_synthesize"],
        ["任务", "进度", "协调", "团队", "管理"],
    ),
]


class RoleTemplateBank:
    """Bank of role templates for the swarm system."""

    def __init__(self):
        self._templates = {r.role_id: r for r in ROLE_TEMPLATES}

    def get_role(self, role_id: str) -> Optional[RoleTemplate]:
        """Get a role template by ID."""
        return self._templates.get(role_id)

    def list_roles(self) -> List[str]:
        """List all available role IDs."""
        return list(self._templates.keys())

    def find_by_expertise(self, query: str) -> List[RoleTemplate]:
        """Find roles by expertise keywords."""
        results = []
        query_lower = query.lower()
        for role in ROLE_TEMPLATES:
            for exp in role.expertise:
                if exp.lower() in query_lower:
                    results.append(role)
                    break
        return results

    def recommend_roles(self, task_description: str) -> List[RoleTemplate]:
        """Recommend roles based on task description."""
        roles = []
        for role in ROLE_TEMPLATES:
            for exp in role.expertise:
                if exp in task_description:
                    roles.append(role)
                    break
        return roles
