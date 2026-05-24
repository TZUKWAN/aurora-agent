"""SQLite-based session memory and persistence layer."""

import json
import logging
import os
import uuid
from contextlib import closing
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import sqlite3

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages persistent sessions using Python's native sqlite3."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            from aurora.config import load_config
            cfg = load_config()
            db_path = cfg.session.db_path
        self.db_path = os.path.expanduser(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        project_info TEXT,
                        created_at TIMESTAMP,
                        last_updated TIMESTAMP
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sections (
                        session_id TEXT,
                        section_id TEXT,
                        content TEXT,
                        version INTEGER,
                        updated_at TIMESTAMP,
                        PRIMARY KEY (session_id, section_id)
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        role TEXT,
                        content TEXT,
                        created_at TIMESTAMP
                    )
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_messages_session
                    ON messages(session_id, id)
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        key TEXT NOT NULL,
                        content TEXT NOT NULL,
                        metadata_json TEXT DEFAULT '{}',
                        access_count INTEGER DEFAULT 0,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_memories_category
                    ON memories(category)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_memories_key
                    ON memories(key)
                ''')

    def create_or_update_session(
        self, session_id: str, project_info: Dict[str, Any]
    ) -> str:
        """Create a new session or update project info for an existing one."""
        if not session_id:
            session_id = uuid.uuid4().hex[:12]

        now = datetime.now().isoformat()
        info_json = json.dumps(project_info, ensure_ascii=False)

        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE sessions SET project_info = ?, last_updated = ? WHERE session_id = ?",
                    (info_json, now, session_id),
                )
                if cursor.rowcount == 0:
                    cursor.execute(
                        "INSERT INTO sessions (session_id, project_info, created_at, last_updated) VALUES (?, ?, ?, ?)",
                        (session_id, info_json, now, now),
                    )

        return session_id

    def save_section(self, session_id: str, section_id: str, content: str) -> None:
        """Save generated content for a specific business plan section."""
        now = datetime.now().isoformat()

        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT version FROM sections WHERE session_id = ? AND section_id = ?",
                    (session_id, section_id),
                )
                row = cursor.fetchone()
                version = (row[0] + 1) if row else 1

                cursor.execute(
                    '''INSERT INTO sections (session_id, section_id, content, version, updated_at)
                       VALUES (?, ?, ?, ?, ?)
                       ON CONFLICT(session_id, section_id) DO UPDATE SET
                       content=excluded.content, version=excluded.version, updated_at=excluded.updated_at''',
                    (session_id, section_id, content, version, now),
                )

    def save_message(self, session_id: str, role: str, content: str) -> None:
        """Save a chat message to the session."""
        now = datetime.now().isoformat()
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute(
                    "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                    (session_id, role, content, now),
                )

    def load_messages(self, session_id: str) -> List[Dict[str, str]]:
        """Load all messages for a session."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id",
                (session_id,),
            )
            return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load full session state including project info and all saved sections."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT project_info FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            project_info = json.loads(row[0])

            cursor.execute(
                "SELECT section_id, content FROM sections WHERE session_id = ?",
                (session_id,),
            )
            sections = {r[0]: r[1] for r in cursor.fetchall()}

            return {
                "session_id": session_id,
                "project_info": project_info,
                "sections": sections,
            }

    def list_sessions(self) -> List[Dict[str, Any]]:
        """Return a summary list of all sessions."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT session_id, project_info, created_at, last_updated FROM sessions ORDER BY last_updated DESC"
            )
            results = []
            for row in cursor.fetchall():
                info = json.loads(row[1]) if row[1] else {}
                results.append({
                    "session_id": row[0],
                    "project_name": info.get("project_name", info.get("technology", "")),
                    "created_at": row[2],
                    "last_updated": row[3],
                })
            return results

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its associated data."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM sessions WHERE session_id = ?", (session_id,)
                )
                deleted = cursor.rowcount > 0
                cursor.execute(
                    "DELETE FROM sections WHERE session_id = ?", (session_id,)
                )
                cursor.execute(
                    "DELETE FROM messages WHERE session_id = ?", (session_id,)
                )
            return deleted

    def search_sessions(self, keyword: str) -> List[Dict[str, Any]]:
        """Search sessions by keyword in project_info."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT session_id, project_info, created_at, last_updated FROM sessions WHERE project_info LIKE ?",
                (f"%{keyword}%",),
            )
            results = []
            for row in cursor.fetchall():
                info = json.loads(row[1]) if row[1] else {}
                results.append({
                    "session_id": row[0],
                    "project_name": info.get("project_name", info.get("technology", "")),
                    "created_at": row[2],
                    "last_updated": row[3],
                })
            return results

    def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        """Delete sessions older than max_age_days. Returns count deleted."""
        cutoff = (datetime.now() - timedelta(days=max_age_days)).isoformat()
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT session_id FROM sessions WHERE last_updated < ?", (cutoff,)
                )
                old_ids = [row[0] for row in cursor.fetchall()]
                if not old_ids:
                    return 0
                placeholders = ",".join("?" for _ in old_ids)
                cursor.execute(
                    f"DELETE FROM sections WHERE session_id IN ({placeholders})", old_ids
                )
                cursor.execute(
                    f"DELETE FROM messages WHERE session_id IN ({placeholders})", old_ids
                )
                cursor.execute(
                    f"DELETE FROM sessions WHERE session_id IN ({placeholders})", old_ids
                )
            return len(old_ids)

    # ------------------------------------------------------------------
    # Categorized memory system
    # ------------------------------------------------------------------

    def store_memory(self, category: str, key: str, content: str, metadata: Optional[Dict] = None) -> int:
        """Store a categorized memory item.

        Args:
            category: One of preference, domain_knowledge, project_context, fact, note.
            key: Unique identifier within the category.
            content: The memory content.
            metadata: Optional metadata dict.

        Returns:
            The memory item ID.
        """
        now = datetime.now().isoformat()
        meta_json = json.dumps(metadata or {}, ensure_ascii=False)

        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cursor = conn.cursor()
                # Upsert by category + key
                cursor.execute(
                    "SELECT id FROM memories WHERE category = ? AND key = ?",
                    (category, key),
                )
                existing = cursor.fetchone()
                if existing:
                    cursor.execute(
                        """UPDATE memories SET content = ?, metadata_json = ?, updated_at = ?
                           WHERE category = ? AND key = ?""",
                        (content, meta_json, now, category, key),
                    )
                    return existing[0]
                else:
                    cursor.execute(
                        """INSERT INTO memories (category, key, content, metadata_json, access_count, created_at, updated_at)
                           VALUES (?, ?, ?, ?, 0, ?, ?)""",
                        (category, key, content, meta_json, now, now),
                    )
                    return cursor.lastrowid

    def recall_memory(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Recall memories matching a keyword query.

        Searches key and content fields. Results ranked by access count (descending).
        """
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute(
                    """SELECT id, category, key, content, metadata_json, access_count
                       FROM memories
                       WHERE category = ? AND (key LIKE ? OR content LIKE ?)
                       ORDER BY access_count DESC
                       LIMIT ?""",
                    (category, f"%{query}%", f"%{query}%", limit),
                )
            else:
                cursor.execute(
                    """SELECT id, category, key, content, metadata_json, access_count
                       FROM memories
                       WHERE key LIKE ? OR content LIKE ?
                       ORDER BY access_count DESC
                       LIMIT ?""",
                    (f"%{query}%", f"%{query}%", limit),
                )

            results = []
            for row in cursor.fetchall():
                mid, cat, key, content, meta_json, access_count = row
                results.append({
                    "id": mid,
                    "category": cat,
                    "key": key,
                    "content": content,
                    "metadata": json.loads(meta_json) if meta_json else {},
                    "access_count": access_count,
                })
            return results

    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory item by ID."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                return cursor.rowcount > 0

    def build_memory_context(self, query: str, max_items: int = 5) -> str:
        """Build a context string from relevant memories for injection.

        Recalls memories matching the query, increments access counts,
        and formats them for context injection.
        """
        memories = self.recall_memory(query, limit=max_items)
        if not memories:
            return ""

        # Increment access counts
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                for mem in memories:
                    conn.execute(
                        "UPDATE memories SET access_count = access_count + 1 WHERE id = ?",
                        (mem["id"],),
                    )

        parts = []
        for mem in memories:
            parts.append(f"[{mem['category']}/{mem['key']}] {mem['content']}")
        return "\n".join(parts)

    def list_memory_categories(self) -> List[str]:
        """List all distinct memory categories."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM memories ORDER BY category")
            return [row[0] for row in cursor.fetchall()]
