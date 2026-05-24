"""Goal management system for AuroraAgent.

Hierarchical goal tree with progress auto-calculation
and SQLite persistence.
"""

import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import sqlite3

logger = logging.getLogger(__name__)


@dataclass
class Goal:
    id: str = ""
    title: str = ""
    description: str = ""
    parent_id: str = ""
    status: str = "pending"  # pending, in_progress, completed, failed
    progress: float = 0.0
    created_at: str = ""


class GoalManager:
    """Manage hierarchical goals with SQLite persistence."""

    def __init__(self, db=None):
        self._db = db
        self._init_db()

    def _get_conn(self):
        if self._db and hasattr(self._db, 'db_path'):
            import sqlite3
            from contextlib import closing
            return sqlite3.connect(self._db.db_path)
        return None

    def _init_db(self):
        conn = self._get_conn()
        if conn is None:
            return
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    parent_id TEXT DEFAULT '',
                    status TEXT DEFAULT 'pending',
                    progress REAL DEFAULT 0.0,
                    created_at TEXT DEFAULT ''
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning("Failed to init goals table: %s", e)

    def create_goal(self, title: str, description: str = "", parent_id: str = "") -> Goal:
        """Create a new goal."""
        goal_id = uuid.uuid4().hex[:12]
        goal = Goal(
            id=goal_id,
            title=title,
            description=description,
            parent_id=parent_id,
            status="pending",
            progress=0.0,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self._save_goal(goal)
        return goal

    def update_goal(self, goal_id: str, status: Optional[str] = None, progress: Optional[float] = None) -> Optional[Goal]:
        """Update a goal's status and/or progress."""
        goal = self.get_goal(goal_id)
        if not goal:
            return None

        if status is not None:
            goal.status = status
        if progress is not None:
            goal.progress = min(max(progress, 0.0), 1.0)

        if goal.status == "completed":
            goal.progress = 1.0

        self._save_goal(goal)
        self._recalculate_parent(goal.parent_id)
        return goal

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get a goal by ID."""
        conn = self._get_conn()
        if conn is None:
            return None
        try:
            row = conn.execute(
                "SELECT id, title, description, parent_id, status, progress, created_at FROM goals WHERE id = ?",
                (goal_id,),
            ).fetchone()
            if row:
                return Goal(**dict(zip(
                    ["id", "title", "description", "parent_id", "status", "progress", "created_at"], row
                )))
        except Exception:
            pass
        finally:
            conn.close()
        return None

    def list_goals(self, status: Optional[str] = None) -> List[Goal]:
        """List goals, optionally filtered by status."""
        conn = self._get_conn()
        if conn is None:
            return []
        try:
            if status:
                rows = conn.execute(
                    "SELECT id, title, description, parent_id, status, progress, created_at FROM goals WHERE status = ?",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, title, description, parent_id, status, progress, created_at FROM goals"
                ).fetchall()

            return [
                Goal(**dict(zip(
                    ["id", "title", "description", "parent_id", "status", "progress", "created_at"], row
                )))
                for row in rows
            ]
        except Exception:
            return []
        finally:
            conn.close()

    def get_goal_tree(self) -> List[Dict[str, Any]]:
        """Get all goals as a hierarchical tree."""
        goals = self.list_goals()
        if not goals:
            return []

        goal_map = {g.id: {
            "id": g.id, "title": g.title, "description": g.description,
            "status": g.status, "progress": g.progress, "children": [],
        } for g in goals}

        roots = []
        for g in goals:
            if g.parent_id and g.parent_id in goal_map:
                goal_map[g.parent_id]["children"].append(goal_map[g.id])
            else:
                roots.append(goal_map[g.id])

        return roots

    def delete_goal(self, goal_id: str) -> bool:
        """Delete a goal (and orphan its children)."""
        conn = self._get_conn()
        if conn is None:
            return False
        try:
            conn.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    def calculate_progress(self, goal_id: str) -> float:
        """Calculate a goal's progress from its children."""
        conn = self._get_conn()
        if conn is None:
            return 0.0
        try:
            rows = conn.execute(
                "SELECT progress FROM goals WHERE parent_id = ?", (goal_id,)
            ).fetchall()
            if not rows:
                return 0.0
            return sum(r[0] for r in rows) / len(rows)
        except Exception:
            return 0.0
        finally:
            conn.close()

    def _save_goal(self, goal: Goal):
        conn = self._get_conn()
        if conn is None:
            return
        try:
            conn.execute(
                """INSERT OR REPLACE INTO goals (id, title, description, parent_id, status, progress, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (goal.id, goal.title, goal.description, goal.parent_id, goal.status, goal.progress, goal.created_at),
            )
            conn.commit()
        except Exception as e:
            logger.warning("Failed to save goal %s: %s", goal.id, e)
        finally:
            conn.close()

    def _recalculate_parent(self, parent_id: str):
        if not parent_id:
            return
        progress = self.calculate_progress(parent_id)
        parent = self.get_goal(parent_id)
        if parent:
            parent.progress = progress
            self._save_goal(parent)
