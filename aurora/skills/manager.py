"""Skill manager for AuroraAgent.

SQLite-backed skill CRUD with execution history and version tracking.
"""

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    id: str = ""
    name: str = ""
    description: str = ""
    steps: List[Dict[str, str]] = field(default_factory=list)
    trigger_keywords: List[str] = field(default_factory=list)
    version: int = 1
    execution_count: int = 0
    success_count: int = 0
    created_at: str = ""


class SkillManager:
    """Manage skills with SQLite persistence."""

    def __init__(self, db=None):
        self._db = db
        self._skills: Dict[str, Skill] = {}
        self._init_db()

    def _get_conn(self):
        if self._db and hasattr(self._db, 'db_path'):
            import sqlite3
            return sqlite3.connect(self._db.db_path)
        return None

    def _init_db(self):
        conn = self._get_conn()
        if conn is None:
            return
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    steps_json TEXT DEFAULT '[]',
                    trigger_keywords_json TEXT DEFAULT '[]',
                    version INTEGER DEFAULT 1,
                    stats_json TEXT DEFAULT '{"execution_count":0,"success_count":0}',
                    created_at TEXT DEFAULT ''
                )
            """)
            conn.commit()
            self._load_skills()
        except Exception as e:
            logger.warning("Failed to init skills table: %s", e)
        finally:
            conn.close()

    def _load_skills(self):
        conn = self._get_conn()
        if conn is None:
            return
        try:
            rows = conn.execute(
                "SELECT id, name, description, steps_json, trigger_keywords_json, version, stats_json, created_at FROM skills"
            ).fetchall()
            for row in rows:
                sid, name, desc, steps_json, kw_json, version, stats_json, created = row
                stats = json.loads(stats_json) if stats_json else {}
                self._skills[sid] = Skill(
                    id=sid, name=name, description=desc,
                    steps=json.loads(steps_json) if steps_json else [],
                    trigger_keywords=json.loads(kw_json) if kw_json else [],
                    version=version,
                    execution_count=stats.get("execution_count", 0),
                    success_count=stats.get("success_count", 0),
                    created_at=created or "",
                )
        except Exception as e:
            logger.warning("Failed to load skills: %s", e)
        finally:
            conn.close()

    def create_skill(self, name: str, description: str = "", steps: List[Dict[str, str]] = None,
                     trigger_keywords: List[str] = None) -> Skill:
        """Create a new skill."""
        skill_id = uuid.uuid4().hex[:12]
        skill = Skill(
            id=skill_id, name=name, description=description,
            steps=steps or [], trigger_keywords=trigger_keywords or [],
            version=1, created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self._skills[skill_id] = skill
        self._save_skill(skill)
        return skill

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        return self._skills.get(skill_id)

    def find_by_keyword(self, query: str) -> List[Skill]:
        """Find skills matching a keyword query."""
        query_lower = query.lower()
        return [
            s for s in self._skills.values()
            if any(kw.lower() in query_lower or query_lower in kw.lower() for kw in s.trigger_keywords)
            or query_lower in s.name.lower()
        ]

    def update_skill(self, skill_id: str, **kwargs) -> Optional[Skill]:
        """Update a skill's properties."""
        skill = self._skills.get(skill_id)
        if not skill:
            return None

        for key, value in kwargs.items():
            if hasattr(skill, key):
                setattr(skill, key, value)

        self._save_skill(skill)
        return skill

    def list_skills(self) -> List[Dict[str, Any]]:
        """List all skills with summary info."""
        return [
            {
                "id": s.id, "name": s.name, "description": s.description,
                "version": s.version, "execution_count": s.execution_count,
                "success_count": s.success_count,
                "trigger_keywords": s.trigger_keywords,
            }
            for s in self._skills.values()
        ]

    def delete_skill(self, skill_id: str) -> bool:
        """Delete a skill."""
        if skill_id not in self._skills:
            return False
        del self._skills[skill_id]
        conn = self._get_conn()
        if conn:
            try:
                conn.execute("DELETE FROM skills WHERE id = ?", (skill_id,))
                conn.commit()
            except Exception:
                pass
            finally:
                conn.close()
        return True

    def record_execution(self, skill_id: str, success: bool = True):
        """Record a skill execution."""
        skill = self._skills.get(skill_id)
        if not skill:
            return
        skill.execution_count += 1
        if success:
            skill.success_count += 1
        self._save_skill(skill)

    def _save_skill(self, skill: Skill):
        conn = self._get_conn()
        if conn is None:
            return
        try:
            conn.execute(
                """INSERT OR REPLACE INTO skills (id, name, description, steps_json, trigger_keywords_json, version, stats_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    skill.id, skill.name, skill.description,
                    json.dumps(skill.steps, ensure_ascii=False),
                    json.dumps(skill.trigger_keywords, ensure_ascii=False),
                    skill.version,
                    json.dumps({"execution_count": skill.execution_count, "success_count": skill.success_count}),
                    skill.created_at,
                ),
            )
            conn.commit()
        except Exception as e:
            logger.warning("Failed to save skill %s: %s", skill.id, e)
        finally:
            conn.close()
