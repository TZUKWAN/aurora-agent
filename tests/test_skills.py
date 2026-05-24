"""Tests for skill system."""

import os
import tempfile

import pytest

from aurora.skills.manager import SkillManager, Skill
from aurora.memory.session_db import MemoryManager


@pytest.fixture
def skill_mgr():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = MemoryManager(db_path=path)
    sm = SkillManager(db=db)
    yield sm
    os.unlink(path)


class TestSkillManager:
    def test_create_skill(self, skill_mgr):
        skill = skill_mgr.create_skill(
            "快速BP生成",
            "一键生成创新训练BP",
            steps=[{"tool": "bp_generate", "args": '{"type":"innovation"}'}],
            trigger_keywords=["快速生成", "BP"],
        )
        assert skill.id
        assert skill.name == "快速BP生成"
        assert skill.version == 1

    def test_get_skill(self, skill_mgr):
        skill = skill_mgr.create_skill("Test")
        retrieved = skill_mgr.get_skill(skill.id)
        assert retrieved is not None
        assert retrieved.name == "Test"

    def test_get_nonexistent(self, skill_mgr):
        assert skill_mgr.get_skill("nonexistent") is None

    def test_find_by_keyword(self, skill_mgr):
        skill_mgr.create_skill("BP生成器", trigger_keywords=["BP", "商业计划书"])
        skill_mgr.create_skill("评估工具", trigger_keywords=["评估", "打分"])

        results = skill_mgr.find_by_keyword("BP")
        assert len(results) == 1
        assert results[0].name == "BP生成器"

    def test_update_skill(self, skill_mgr):
        skill = skill_mgr.create_skill("Test", description="old")
        updated = skill_mgr.update_skill(skill.id, description="new description", version=2)
        assert updated.description == "new description"
        assert updated.version == 2

    def test_list_skills(self, skill_mgr):
        skill_mgr.create_skill("A")
        skill_mgr.create_skill("B")
        skills = skill_mgr.list_skills()
        assert len(skills) == 2

    def test_delete_skill(self, skill_mgr):
        skill = skill_mgr.create_skill("ToDelete")
        assert skill_mgr.delete_skill(skill.id) is True
        assert skill_mgr.get_skill(skill.id) is None

    def test_delete_nonexistent(self, skill_mgr):
        assert skill_mgr.delete_skill("nonexistent") is False

    def test_record_execution(self, skill_mgr):
        skill = skill_mgr.create_skill("Test")
        skill_mgr.record_execution(skill.id, success=True)
        skill_mgr.record_execution(skill.id, success=True)
        skill_mgr.record_execution(skill.id, success=False)

        updated = skill_mgr.get_skill(skill.id)
        assert updated.execution_count == 3
        assert updated.success_count == 2

    def test_skill_persistence(self, skill_mgr):
        skill = skill_mgr.create_skill("Persist", description="test persistence")

        # Create new manager with same DB
        sm2 = SkillManager(db=skill_mgr._db)
        retrieved = sm2.get_skill(skill.id)
        assert retrieved is not None
        assert retrieved.name == "Persist"
