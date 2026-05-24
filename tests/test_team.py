"""Tests for team management module."""

import json

import pytest

from aurora.team.models import TeamAnalysis, TeamMember, TeamRole
from aurora.team.manager import TEAM_ROLES, TeamManager, MAX_TEAM_SIZE, MIN_TEAM_SIZE
from aurora.tools.registry import ToolRegistry
from aurora.tools.team_tools import _register_tools


def _make_members():
    """Create a full sample team covering all roles."""
    return [
        {"name": "张三", "role": "leader", "skills": ["管理", "策划"], "background": "MBA"},
        {"name": "李四", "role": "tech", "skills": ["Python", "AI"], "background": "计算机"},
        {"name": "王五", "role": "business", "skills": ["市场", "运营"], "background": "商学院"},
        {"name": "赵六", "role": "design", "skills": ["UI", "PPT"], "background": "设计学院"},
        {"name": "钱七", "role": "finance", "skills": ["财务", "数据"], "background": "金融"},
        {"name": "孙八", "role": "advisor", "skills": ["AI", "科研"], "background": "教授"},
    ]


class TestTeamMember:
    """Test TeamMember dataclass."""

    def test_create_member(self):
        member = TeamMember(name="测试", role="tech")
        assert member.name == "测试"
        assert member.role == "tech"
        assert member.skills == []
        assert member.background == ""
        assert member.responsibilities == []

    def test_create_member_with_skills(self):
        member = TeamMember(
            name="测试",
            role="tech",
            skills=["Python", "AI"],
            background="计算机",
        )
        assert member.skills == ["Python", "AI"]
        assert member.background == "计算机"


class TestTeamRole:
    """Test TeamRole dataclass."""

    def test_create_role(self):
        role = TeamRole(
            role_id="test",
            name="测试角色",
            description="测试描述",
            required_skills=["技能1"],
            weight=0.5,
        )
        assert role.role_id == "test"
        assert role.name == "测试角色"
        assert role.weight == 0.5

    def test_team_roles_defined(self):
        assert len(TEAM_ROLES) == 7
        assert "leader" in TEAM_ROLES
        assert "tech" in TEAM_ROLES
        assert "business" in TEAM_ROLES
        assert "design" in TEAM_ROLES
        assert "marketing" in TEAM_ROLES
        assert "finance" in TEAM_ROLES
        assert "advisor" in TEAM_ROLES

    def test_team_roles_weights_sum(self):
        total = sum(r.weight for r in TEAM_ROLES.values())
        assert abs(total - 1.0) < 0.01


class TestTeamAnalysis:
    """Test TeamAnalysis dataclass."""

    def test_create_analysis(self):
        analysis = TeamAnalysis(
            completeness_score=85.0,
            role_coverage={"tech": 100.0},
            missing_roles=[],
            strength_areas=["技术"],
            weakness_areas=[],
            recommendations=["团队配置合理"],
        )
        assert analysis.completeness_score == 85.0
        assert analysis.missing_roles == []


class TestTeamManager:
    """Test TeamManager class."""

    def setup_method(self):
        self.manager = TeamManager()

    def test_init(self):
        assert len(self.manager.roles) == 7

    def test_analyze_full_team(self):
        members = _make_members()
        analysis = self.manager.analyze_team(members)
        assert analysis.completeness_score > 0
        # Full team should have no missing roles for the 6 covered roles
        # marketing is missing from sample data
        assert "marketing" in analysis.missing_roles
        assert isinstance(analysis.role_coverage, dict)
        assert isinstance(analysis.recommendations, list)

    def test_analyze_full_team_all_roles(self):
        members = [
            {"name": "张三", "role": "leader", "skills": ["管理", "策划", "沟通"], "background": "MBA"},
            {"name": "李四", "role": "tech", "skills": ["Python", "AI", "编程", "产品设计"], "background": "计算机"},
            {"name": "王五", "role": "business", "skills": ["市场", "运营", "商业分析"], "background": "商学院"},
            {"name": "赵六", "role": "design", "skills": ["UI", "UX", "PPT", "视觉设计"], "background": "设计学院"},
            {"name": "周九", "role": "marketing", "skills": ["营销", "推广", "用户增长"], "background": "传媒"},
            {"name": "钱七", "role": "finance", "skills": ["财务", "数据分析", "投资"], "background": "金融"},
            {"name": "孙八", "role": "advisor", "skills": ["科研", "指导"], "background": "教授"},
        ]
        analysis = self.manager.analyze_team(members)
        assert analysis.completeness_score > 50
        assert len(analysis.missing_roles) == 0
        assert len(analysis.strength_areas) > 0

    def test_analyze_partial_team(self):
        members = [
            {"name": "张三", "role": "leader", "skills": ["管理"]},
            {"name": "李四", "role": "tech", "skills": ["Python"]},
        ]
        analysis = self.manager.analyze_team(members)
        assert analysis.completeness_score < 100
        assert len(analysis.missing_roles) > 0
        # Should be missing business, design, marketing, finance, advisor
        assert "business" in analysis.missing_roles
        assert "advisor" in analysis.missing_roles
        assert len(analysis.recommendations) > 0

    def test_analyze_empty_team(self):
        analysis = self.manager.analyze_team([])
        assert analysis.completeness_score == 0
        assert len(analysis.missing_roles) == 7
        assert any("为空" in r for r in analysis.recommendations)

    def test_analyze_role_coverage_calculation(self):
        members = [
            {"name": "李四", "role": "tech", "skills": ["Python", "AI", "编程", "产品设计"]},
        ]
        analysis = self.manager.analyze_team(members)
        # Tech role has required_skills ["Python", "AI", "编程", "产品设计"]
        # Member has all 4 -> 100% coverage
        assert analysis.role_coverage["tech"] == 100.0

    def test_analyze_partial_skills_coverage(self):
        members = [
            {"name": "李四", "role": "tech", "skills": ["Python"]},
        ]
        analysis = self.manager.analyze_team(members)
        # Tech role has 4 required skills, member has 1 -> 25%
        assert analysis.role_coverage["tech"] == 25.0

    def test_analyze_no_skills_coverage(self):
        members = [
            {"name": "李四", "role": "tech", "skills": []},
        ]
        analysis = self.manager.analyze_team(members)
        # Member exists but no skills -> 60% default
        assert analysis.role_coverage["tech"] == 60.0

    def test_suggest_formation_tech_project(self):
        formation = self.manager.suggest_formation({"type": "tech"})
        assert len(formation) > 0
        # Tech projects should prioritize tech role
        role_ids = [r.role_id for r in formation]
        assert "leader" in role_ids
        assert "tech" in role_ids
        # tech should be at index 1 (right after leader)
        assert role_ids[1] == "tech"
        # design should come before business for tech projects
        design_idx = role_ids.index("design")
        business_idx = role_ids.index("business")
        assert design_idx < business_idx

    def test_suggest_formation_business_project(self):
        formation = self.manager.suggest_formation({"type": "business"})
        role_ids = [r.role_id for r in formation]
        # Business projects should prioritize business role
        assert role_ids[1] == "business"
        # finance should come before tech for business projects
        finance_idx = role_ids.index("finance")
        tech_idx = role_ids.index("tech")
        assert finance_idx < tech_idx

    def test_suggest_formation_default(self):
        formation = self.manager.suggest_formation({"type": "unknown"})
        assert len(formation) == 7
        role_ids = [r.role_id for r in formation]
        assert role_ids[0] == "leader"

    def test_suggest_formation_ai_project(self):
        formation = self.manager.suggest_formation({
            "type": "tech",
            "technology": "AI人工智能",
        })
        role_ids = [r.role_id for r in formation]
        # AI projects should still have tech high priority
        assert role_ids[1] == "tech"

    def test_suggest_formation_social_project(self):
        formation = self.manager.suggest_formation({"type": "social"})
        role_ids = [r.role_id for r in formation]
        assert "marketing" in role_ids
        assert "business" in role_ids

    def test_generate_responsibilities(self):
        members = _make_members()
        project_info = {"name": "AI教育平台", "type": "tech"}
        assignments = self.manager.generate_responsibilities(members, project_info)

        assert "张三" in assignments
        assert "李四" in assignments
        assert len(assignments["张三"]) > 0
        assert any("统筹" in r or "AI教育平台" in r for r in assignments["张三"])
        assert any("技术" in r or "研发" in r for r in assignments["李四"])

    def test_generate_responsibilities_unknown_role(self):
        members = [{"name": "测试", "role": "unknown_role"}]
        assignments = self.manager.generate_responsibilities(members, {"name": "测试项目"})
        assert "测试" in assignments
        assert len(assignments["测试"]) > 0

    def test_generate_responsibilities_all_roles(self):
        members = _make_members()
        assignments = self.manager.generate_responsibilities(members, {"name": "项目"})
        assert len(assignments) == 6
        for name, resps in assignments.items():
            assert len(resps) > 0

    def test_validate_valid_team(self):
        members = _make_members()
        result = self.manager.validate_team(members)
        assert result["valid"] is True
        assert len(result["issues"]) == 0

    def test_validate_empty_team(self):
        result = self.manager.validate_team([])
        assert result["valid"] is False
        assert any("不能为空" in i for i in result["issues"])

    def test_validate_small_team(self):
        members = [
            {"name": "张三", "role": "leader"},
        ]
        result = self.manager.validate_team(members)
        assert result["valid"] is False
        assert any("不足" in i for i in result["issues"])

    def test_validate_oversized_team(self):
        members = []
        for i in range(MAX_TEAM_SIZE + 3):
            members.append({"name": f"成员{i}", "role": "tech"})
        result = self.manager.validate_team(members)
        assert result["valid"] is False
        assert any("超过" in i for i in result["issues"])

    def test_validate_duplicate_names(self):
        members = [
            {"name": "张三", "role": "leader"},
            {"name": "张三", "role": "tech"},
            {"name": "李四", "role": "business"},
        ]
        result = self.manager.validate_team(members)
        assert any("重复" in i for i in result["issues"])

    def test_validate_no_leader(self):
        members = [
            {"name": "李四", "role": "tech"},
            {"name": "王五", "role": "business"},
            {"name": "赵六", "role": "design"},
        ]
        result = self.manager.validate_team(members)
        assert any("队长" in w for w in result["warnings"])

    def test_validate_duplicate_roles_warning(self):
        members = [
            {"name": "张三", "role": "leader"},
            {"name": "李四", "role": "tech"},
            {"name": "王五", "role": "tech"},
            {"name": "赵六", "role": "business"},
        ]
        result = self.manager.validate_team(members)
        assert any("重叠" in w for w in result["warnings"])

    def test_validate_internet_plus(self):
        # 5 members for internet_plus should be fine
        members = [
            {"name": "张三", "role": "leader"},
            {"name": "李四", "role": "tech"},
            {"name": "王五", "role": "business"},
            {"name": "赵六", "role": "design"},
            {"name": "钱七", "role": "advisor"},
        ]
        result = self.manager.validate_team(members, competition_id="internet_plus")
        assert result["valid"] is True

    def test_validate_internet_plus_too_many(self):
        members = []
        for i in range(6):
            members.append({"name": f"成员{i}", "role": "tech"})
        result = self.manager.validate_team(members, competition_id="internet_plus")
        assert any("互联网" in i for i in result["issues"])

    def test_validate_missing_critical_roles(self):
        members = [
            {"name": "张三", "role": "design"},
            {"name": "李四", "role": "finance"},
            {"name": "王五", "role": "marketing"},
        ]
        result = self.manager.validate_team(members)
        # Missing leader, tech, business
        assert any("leader" in w or "队长" in w for w in result["warnings"])

    def test_validate_multiple_advisors_ok(self):
        members = [
            {"name": "张三", "role": "leader"},
            {"name": "李四", "role": "tech"},
            {"name": "王五", "role": "business"},
            {"name": "导师A", "role": "advisor"},
            {"name": "导师B", "role": "advisor"},
        ]
        result = self.manager.validate_team(members)
        # Multiple advisors should not generate a warning
        advisor_warnings = [w for w in result["warnings"] if "advisor" in w.lower() or "指导" in w]
        assert len(advisor_warnings) == 0


class TestTeamTools:
    """Test team tool registration and dispatch."""

    def setup_method(self):
        self.registry = ToolRegistry()
        _register_tools(self.registry)

    def test_tools_registered(self):
        tool_names = self.registry.list_tools()
        assert "team_analyze" in tool_names
        assert "team_suggest" in tool_names
        assert "team_assign" in tool_names
        assert "team_validate" in tool_names

    def test_team_analyze_tool(self):
        result = json.loads(
            self.registry.dispatch(
                "team_analyze",
                {"members": _make_members()},
            )
        )
        assert "result" in result
        assert "data" in result
        assert "completeness_score" in result["data"]
        assert "missing_roles" in result["data"]

    def test_team_suggest_tool(self):
        result = json.loads(
            self.registry.dispatch(
                "team_suggest",
                {"project_type": "tech"},
            )
        )
        assert "result" in result
        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 7

    def test_team_assign_tool(self):
        result = json.loads(
            self.registry.dispatch(
                "team_assign",
                {
                    "members": _make_members(),
                    "project_info": {"name": "AI平台", "type": "tech"},
                },
            )
        )
        assert "result" in result
        assert "data" in result
        assert "张三" in result["data"]

    def test_team_validate_tool(self):
        result = json.loads(
            self.registry.dispatch(
                "team_validate",
                {"members": _make_members()},
            )
        )
        assert "result" in result
        assert "data" in result
        assert "valid" in result["data"]

    def test_team_validate_with_competition(self):
        result = json.loads(
            self.registry.dispatch(
                "team_validate",
                {
                    "members": _make_members(),
                    "competition_id": "internet_plus",
                },
            )
        )
        assert "data" in result

    def test_unknown_tool_returns_error(self):
        result = json.loads(self.registry.dispatch("nonexistent_tool", {}))
        assert "error" in result

    def test_analyze_empty_members_tool(self):
        result = json.loads(
            self.registry.dispatch("team_analyze", {"members": []})
        )
        assert result["data"]["completeness_score"] == 0

    def test_suggest_with_technology(self):
        result = json.loads(
            self.registry.dispatch(
                "team_suggest",
                {
                    "project_type": "tech",
                    "technology": "AI人工智能",
                    "market": "enterprise",
                },
            )
        )
        assert "data" in result
        assert len(result["data"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
