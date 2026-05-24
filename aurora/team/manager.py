"""Team management logic."""

from typing import Dict, List

from aurora.team.models import TeamAnalysis, TeamMember, TeamRole

# Predefined team roles for competition teams
TEAM_ROLES: Dict[str, TeamRole] = {
    "leader": TeamRole(
        role_id="leader",
        name="队长",
        description="项目统筹、汇报答辩",
        required_skills=["管理", "策划", "沟通"],
        weight=0.20,
    ),
    "tech": TeamRole(
        role_id="tech",
        name="技术",
        description="技术研发、产品设计",
        required_skills=["Python", "AI", "编程", "产品设计"],
        weight=0.20,
    ),
    "business": TeamRole(
        role_id="business",
        name="商业",
        description="商业模式、市场分析",
        required_skills=["市场", "运营", "商业分析"],
        weight=0.20,
    ),
    "design": TeamRole(
        role_id="design",
        name="设计",
        description="UI/UX、PPT设计",
        required_skills=["UI", "UX", "PPT", "视觉设计"],
        weight=0.10,
    ),
    "marketing": TeamRole(
        role_id="marketing",
        name="市场",
        description="市场推广、用户增长",
        required_skills=["营销", "推广", "用户增长"],
        weight=0.10,
    ),
    "finance": TeamRole(
        role_id="finance",
        name="财务",
        description="财务规划、数据分析",
        required_skills=["财务", "数据分析", "投资"],
        weight=0.10,
    ),
    "advisor": TeamRole(
        role_id="advisor",
        name="指导老师",
        description="技术指导、资源对接",
        required_skills=["科研", "指导"],
        weight=0.10,
    ),
}

# Maximum recommended team size for most competitions
MAX_TEAM_SIZE = 7
MIN_TEAM_SIZE = 3


def _dict_to_member(data: dict) -> TeamMember:
    """Convert a dict to a TeamMember instance."""
    return TeamMember(
        name=data.get("name", ""),
        role=data.get("role", ""),
        skills=data.get("skills", []),
        background=data.get("background", ""),
        responsibilities=data.get("responsibilities", []),
    )


class TeamManager:
    """Manage team composition, analysis, and validation."""

    def __init__(self) -> None:
        self.roles: Dict[str, TeamRole] = dict(TEAM_ROLES)

    def analyze_team(self, members: list) -> TeamAnalysis:
        """Analyze team composition against predefined roles.

        Args:
            members: List of dicts, each representing a team member.

        Returns:
            TeamAnalysis with completeness score, role coverage, and recommendations.
        """
        member_objects = [_dict_to_member(m) for m in members]

        # Build coverage map
        role_coverage: Dict[str, float] = {}
        for role_id, role_def in self.roles.items():
            matching = [m for m in member_objects if m.role == role_id]
            if matching:
                # Coverage depends on skill overlap with required skills
                best_member = matching[0]
                if role_def.required_skills and best_member.skills:
                    overlap = len(
                        set(best_member.skills) & set(role_def.required_skills)
                    )
                    coverage = min(100.0, (overlap / len(role_def.required_skills)) * 100)
                else:
                    coverage = 60.0  # member exists but no skill data
            else:
                coverage = 0.0
            role_coverage[role_id] = coverage

        # Calculate completeness score (weighted by role importance)
        total_weight = sum(r.weight for r in self.roles.values())
        if total_weight > 0:
            weighted_sum = sum(
                self.roles[rid].weight * role_coverage[rid]
                for rid in self.roles
            )
            completeness_score = weighted_sum / total_weight
        else:
            completeness_score = 0.0

        # Identify missing roles
        missing_roles = [
            rid for rid, cov in role_coverage.items() if cov == 0.0
        ]

        # Identify strength and weakness areas
        strength_areas: List[str] = []
        weakness_areas: List[str] = []
        for rid, cov in role_coverage.items():
            role_name = self.roles[rid].name
            if cov >= 80.0:
                strength_areas.append(role_name)
            elif cov < 40.0 and cov > 0.0:
                weakness_areas.append(role_name)

        # Generate recommendations
        recommendations: List[str] = []
        if not member_objects:
            recommendations.append("团队为空，请先添加团队成员")
        else:
            if "leader" in missing_roles:
                recommendations.append(
                    "建议指定一名队长负责项目统筹和汇报答辩"
                )
            if "tech" in missing_roles:
                recommendations.append(
                    "缺少技术人员，建议招募具有开发能力的成员"
                )
            if "business" in missing_roles:
                recommendations.append(
                    "缺少商业人员，建议补充具备市场分析能力的成员"
                )
            if "design" in missing_roles:
                recommendations.append(
                    "缺少设计人员，PPT和UI设计可能受影响"
                )
            if "finance" in missing_roles:
                recommendations.append(
                    "建议安排专人负责财务规划和数据分析"
                )
            if len(member_objects) < MIN_TEAM_SIZE:
                recommendations.append(
                    f"团队人数过少，建议至少{MIN_TEAM_SIZE}人"
                )
            if len(member_objects) > MAX_TEAM_SIZE:
                recommendations.append(
                    f"团队人数过多，建议控制在{MAX_TEAM_SIZE}人以内"
                )

        if not recommendations:
            recommendations.append("团队配置合理，继续保持")

        return TeamAnalysis(
            completeness_score=completeness_score,
            role_coverage=role_coverage,
            missing_roles=missing_roles,
            strength_areas=strength_areas,
            weakness_areas=weakness_areas,
            recommendations=recommendations,
        )

    def suggest_formation(self, project_info: dict) -> list:
        """Suggest ideal team formation based on project type.

        Args:
            project_info: Dict with keys like 'type', 'technology', 'market'.

        Returns:
            List of TeamRole objects ordered by priority.
        """
        project_type = project_info.get("type", "").lower()
        technology = project_info.get("technology", "").lower()
        market = project_info.get("market", "").lower()

        # Start with base priority order
        priority_order = ["leader", "tech", "business", "design", "marketing", "finance", "advisor"]

        # Adjust priorities based on project type
        if project_type in ("tech", "技术"):
            # Tech projects: prioritize tech and design
            priority_order = ["leader", "tech", "design", "business", "finance", "advisor", "marketing"]
        elif project_type in ("business", "商业"):
            # Business projects: prioritize business and finance
            priority_order = ["leader", "business", "finance", "marketing", "tech", "design", "advisor"]
        elif project_type in ("social", "公益"):
            # Social impact: prioritize marketing and business
            priority_order = ["leader", "business", "marketing", "tech", "design", "finance", "advisor"]

        # Further adjust based on technology keywords
        if any(kw in technology for kw in ("ai", "人工智能", "ml", "机器学习")):
            if "tech" in priority_order:
                idx = priority_order.index("tech")
                if idx > 1:
                    priority_order.remove("tech")
                    priority_order.insert(1, "tech")

        # Adjust based on market keywords
        if any(kw in market for kw in ("consumer", "b2c", "消费者")):
            if "marketing" in priority_order:
                idx = priority_order.index("marketing")
                if idx > 2:
                    priority_order.remove("marketing")
                    priority_order.insert(2, "marketing")

        # Return ordered TeamRole objects
        result: List[TeamRole] = []
        for role_id in priority_order:
            if role_id in self.roles:
                result.append(self.roles[role_id])

        return result

    def generate_responsibilities(self, members: list, project_info: dict) -> dict:
        """Generate responsibility assignments for each member.

        Args:
            members: List of dicts representing team members.
            project_info: Dict with project details.

        Returns:
            Dict mapping member name to list of responsibilities.
        """
        member_objects = [_dict_to_member(m) for m in members]
        assignments: Dict[str, List[str]] = {}

        project_name = project_info.get("name", "项目")
        project_type = project_info.get("type", "")

        # Define default responsibilities per role
        role_responsibilities = {
            "leader": [
                f"统筹{project_name}整体规划与进度管理",
                "组织团队会议与分工协调",
                "负责项目汇报与答辩",
                "把控项目整体方向与质量",
            ],
            "tech": [
                f"负责{project_name}核心技术研发",
                "产品原型设计与开发",
                "技术方案选型与架构设计",
                "技术文档编写与维护",
            ],
            "business": [
                "商业模式设计与优化",
                "市场调研与竞品分析",
                "商业计划书商业部分撰写",
                "合作伙伴与客户关系维护",
            ],
            "design": [
                "UI/UX界面设计",
                "PPT演示文稿设计",
                "品牌视觉设计与统一规范",
                "产品原型交互设计",
            ],
            "marketing": [
                "市场推广策略制定",
                "用户增长与获客计划",
                "社交媒体运营",
                "市场数据分析与反馈",
            ],
            "finance": [
                "财务规划与预算编制",
                "收入模型设计与优化",
                "财务数据分析与报告",
                "投融资计划与资料准备",
            ],
            "advisor": [
                "技术方向指导与建议",
                "行业资源对接与引荐",
                "项目关键节点审查",
                "团队培训与能力提升",
            ],
        }

        for member in member_objects:
            if member.role in role_responsibilities:
                assignments[member.name] = list(role_responsibilities[member.role])
            else:
                assignments[member.name] = [
                    f"参与{project_name}相关工作"
                ]

        return assignments

    def validate_team(self, members: list, competition_id: str = "") -> dict:
        """Validate team against competition requirements.

        Args:
            members: List of dicts representing team members.
            competition_id: Optional competition identifier for specific rules.

        Returns:
            Dict with 'valid' (bool), 'issues' (list), 'warnings' (list).
        """
        member_objects = [_dict_to_member(m) for m in members]
        issues: List[str] = []
        warnings: List[str] = []

        # Check team size
        if len(member_objects) == 0:
            issues.append("团队不能为空")
        elif len(member_objects) < MIN_TEAM_SIZE:
            issues.append(
                f"团队人数不足，最少需要{MIN_TEAM_SIZE}人"
            )

        if len(member_objects) > MAX_TEAM_SIZE:
            issues.append(
                f"团队人数超过{MAX_TEAM_SIZE}人，多数竞赛不允许"
            )

        # Check for leader
        roles_present = {m.role for m in member_objects}
        if "leader" not in roles_present and len(member_objects) > 0:
            warnings.append("未指定队长，建议指定一名队长")

        # Check for duplicate roles (except advisor can be multiple)
        role_counts: Dict[str, int] = {}
        for m in member_objects:
            role_counts[m.role] = role_counts.get(m.role, 0) + 1

        for role_id, count in role_counts.items():
            if role_id == "advisor":
                continue  # Multiple advisors are fine
            if count > 1:
                warnings.append(
                    f"角色'{self.roles[role_id].name}'有{count}人担任，可能造成职责重叠"
                )

        # Check for missing critical roles
        critical_roles = {"leader", "tech", "business"}
        missing_critical = critical_roles - roles_present
        if missing_critical and len(member_objects) > 0:
            for role_id in missing_critical:
                warnings.append(
                    f"缺少关键角色：{self.roles[role_id].name}"
                )

        # Check name uniqueness
        names = [m.name for m in member_objects]
        seen: set = set()
        for name in names:
            if name in seen:
                issues.append(f"成员名称重复：{name}")
            seen.add(name)

        # Competition-specific validation
        if competition_id == "internet_plus":
            if len(member_objects) > 5:
                issues.append("互联网+大赛每队最多5人")
            if "advisor" not in roles_present:
                warnings.append("互联网+大赛建议配备指导老师")

        valid = len(issues) == 0

        return {
            "valid": valid,
            "issues": issues,
            "warnings": warnings,
        }
