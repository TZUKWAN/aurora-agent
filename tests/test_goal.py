"""Tests for goal management system."""

import os
import tempfile

import pytest

from aurora.goal import GoalManager
from aurora.memory.session_db import MemoryManager


@pytest.fixture
def goal_mgr():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = MemoryManager(db_path=path)
    gm = GoalManager(db=db)
    yield gm
    os.unlink(path)


class TestGoalManager:
    def test_create_goal(self, goal_mgr):
        goal = goal_mgr.create_goal("完成申报书", "撰写大创申报书")
        assert goal.id
        assert goal.title == "完成申报书"
        assert goal.status == "pending"

    def test_update_goal_status(self, goal_mgr):
        goal = goal_mgr.create_goal("Test")
        updated = goal_mgr.update_goal(goal.id, status="in_progress")
        assert updated.status == "in_progress"

    def test_update_goal_progress(self, goal_mgr):
        goal = goal_mgr.create_goal("Test")
        updated = goal_mgr.update_goal(goal.id, progress=0.5)
        assert updated.progress == 0.5

    def test_complete_sets_progress_to_1(self, goal_mgr):
        goal = goal_mgr.create_goal("Test")
        updated = goal_mgr.update_goal(goal.id, status="completed")
        assert updated.progress == 1.0

    def test_progress_clamped(self, goal_mgr):
        goal = goal_mgr.create_goal("Test")
        updated = goal_mgr.update_goal(goal.id, progress=2.0)
        assert updated.progress == 1.0
        updated = goal_mgr.update_goal(goal.id, progress=-1.0)
        assert updated.progress == 0.0

    def test_get_nonexistent(self, goal_mgr):
        assert goal_mgr.get_goal("nonexistent") is None

    def test_list_goals(self, goal_mgr):
        goal_mgr.create_goal("A")
        goal_mgr.create_goal("B")
        goals = goal_mgr.list_goals()
        assert len(goals) == 2

    def test_list_goals_by_status(self, goal_mgr):
        g1 = goal_mgr.create_goal("Pending")
        g2 = goal_mgr.create_goal("Active")
        goal_mgr.update_goal(g2.id, status="in_progress")
        active = goal_mgr.list_goals(status="in_progress")
        assert len(active) == 1
        assert active[0].id == g2.id

    def test_hierarchical_goals(self, goal_mgr):
        parent = goal_mgr.create_goal("Parent")
        child1 = goal_mgr.create_goal("Child 1", parent_id=parent.id)
        child2 = goal_mgr.create_goal("Child 2", parent_id=parent.id)

        goal_mgr.update_goal(child1.id, progress=0.5)
        goal_mgr.update_goal(child2.id, progress=1.0)

        parent_updated = goal_mgr.get_goal(parent.id)
        assert parent_updated.progress > 0

    def test_goal_tree(self, goal_mgr):
        p = goal_mgr.create_goal("Parent")
        goal_mgr.create_goal("Child A", parent_id=p.id)
        goal_mgr.create_goal("Child B", parent_id=p.id)

        tree = goal_mgr.get_goal_tree()
        assert len(tree) == 1
        assert tree[0]["title"] == "Parent"
        assert len(tree[0]["children"]) == 2

    def test_delete_goal(self, goal_mgr):
        goal = goal_mgr.create_goal("To Delete")
        assert goal_mgr.delete_goal(goal.id) is True
        assert goal_mgr.get_goal(goal.id) is None

    def test_calculate_progress_no_children(self, goal_mgr):
        goal = goal_mgr.create_goal("No children")
        progress = goal_mgr.calculate_progress(goal.id)
        assert progress == 0.0
