"""SQLite-based session memory and persistence layer."""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import sqlite3
from contextlib import closing

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages persistent sessions using Python's native sqlite3."""
    
    def __init__(self, db_path: str = ".aurora_sessions.db"):
        self.db_path = db_path
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

    def create_or_update_session(self, session_id: str, project_info: Dict[str, Any]) -> str:
        """Create a new session or update project info for an existing one."""
        if not session_id:
            import uuid
            session_id = uuid.uuid4().hex[:12]
            
        now = datetime.now().isoformat()
        info_json = json.dumps(project_info, ensure_ascii=False)
        
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE sessions SET project_info = ?, last_updated = ? WHERE session_id = ?",
                    (info_json, now, session_id)
                )
                if cursor.rowcount == 0:
                    cursor.execute(
                        "INSERT INTO sessions (session_id, project_info, created_at, last_updated) VALUES (?, ?, ?, ?)",
                        (session_id, info_json, now, now)
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
                    (session_id, section_id)
                )
                row = cursor.fetchone()
                version = (row[0] + 1) if row else 1
                
                cursor.execute(
                    '''INSERT INTO sections (session_id, section_id, content, version, updated_at) 
                       VALUES (?, ?, ?, ?, ?)
                       ON CONFLICT(session_id, section_id) DO UPDATE SET 
                       content=excluded.content, version=excluded.version, updated_at=excluded.updated_at''',
                    (session_id, section_id, content, version, now)
                )

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load full session state including project info and all saved sections."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT project_info FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if not row:
                return None
                
            project_info = json.loads(row[0])
            
            cursor.execute("SELECT section_id, content FROM sections WHERE session_id = ?", (session_id,))
            sections = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "session_id": session_id,
                "project_info": project_info,
                "sections": sections
            }
