"""Learning manager for AuroraAgent.

Records tool executions, analyzes patterns, and suggests improvements.
Integrates with the skill system for auto-discovery.
"""

import json
import logging
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class LearningManager:
    """Track tool usage patterns and suggest improvements.

    Register as a HookManager handler on tool.post_dispatch (priority=90).
    """

    def __init__(self, db=None):
        self._db = db
        self._logs: List[Dict[str, Any]] = []
        self._init_db()

    def _init_db(self):
        if self._db is None:
            return
        try:
            conn = self._db._get_conn() if hasattr(self._db, '_get_conn') else None
            if conn is None and hasattr(self._db, 'db_path'):
                import sqlite3
                conn = sqlite3.connect(self._db.db_path)
            if conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS learning_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tool_name TEXT NOT NULL,
                        args_json TEXT,
                        result_summary TEXT,
                        score REAL DEFAULT 0.5,
                        timestamp TEXT
                    )
                """)
                conn.commit()
                conn.close()
        except Exception as e:
            logger.warning("Failed to init learning_logs table: %s", e)

    def record_execution(self, tool_name: str, args: Dict = None, result: str = "", score: float = 0.5):
        """Record a tool execution for pattern analysis."""
        entry = {
            "tool_name": tool_name,
            "args": args or {},
            "result_summary": result[:200] if result else "",
            "score": score,
            "timestamp": datetime.now().isoformat(),
        }
        self._logs.append(entry)

        if self._db and hasattr(self._db, 'db_path'):
            try:
                import sqlite3
                conn = sqlite3.connect(self._db.db_path)
                conn.execute(
                    "INSERT INTO learning_logs (tool_name, args_json, result_summary, score, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (tool_name, json.dumps(args or {}, ensure_ascii=False), result[:200], score, entry["timestamp"]),
                )
                conn.commit()
                conn.close()
            except Exception:
                pass

    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze execution patterns from recorded logs."""
        if not self._logs:
            return {"tool_frequency": {}, "error_tools": [], "workflow_sequences": []}

        tool_counts = Counter(log["tool_name"] for log in self._logs)

        # Find tools with low scores (error-prone)
        tool_scores = {}
        for log in self._logs:
            name = log["tool_name"]
            if name not in tool_scores:
                tool_scores[name] = []
            tool_scores[name].append(log["score"])

        error_tools = [
            name for name, scores in tool_scores.items()
            if sum(scores) / len(scores) < 0.3
        ]

        # Find common tool sequences (2-step patterns)
        sequences = []
        for i in range(len(self._logs) - 1):
            pair = (self._logs[i]["tool_name"], self._logs[i + 1]["tool_name"])
            sequences.append(pair)
        sequence_counts = Counter(sequences)
        common_sequences = [
            {"steps": list(pair), "count": count}
            for pair, count in sequence_counts.most_common(10)
            if count >= 2
        ]

        return {
            "tool_frequency": dict(tool_counts.most_common(20)),
            "error_tools": error_tools,
            "workflow_sequences": common_sequences,
            "total_executions": len(self._logs),
        }

    def suggest_improvements(self) -> List[str]:
        """Suggest improvements based on analyzed patterns."""
        patterns = self.analyze_patterns()
        suggestions = []

        # Suggest automation for frequent sequences
        for seq in patterns.get("workflow_sequences", []):
            if seq["count"] >= 3:
                steps_desc = " -> ".join(seq["steps"])
                suggestions.append(
                    f"频繁工作流检测（{seq['count']}次）：{steps_desc}，建议创建技能自动化"
                )

        # Flag error-prone tools
        for tool in patterns.get("error_tools", []):
            suggestions.append(f"工具'{tool}'执行成功率较低，建议检查参数或优化调用方式")

        # Suggest skill creation for frequent standalone tools
        for tool, count in patterns.get("tool_frequency", {}).items():
            if count >= 5:
                suggestions.append(f"工具'{tool}'被高频使用（{count}次），可考虑封装为快捷技能")

        return suggestions

    def post_dispatch_hook(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Hook handler for tool.post_dispatch events."""
        tool_name = context.get("tool", "")
        result = context.get("result", "")
        args = context.get("args", {})

        # Score based on result content
        score = 0.5
        if '"error"' in result:
            score = 0.1
        elif result and len(result) > 50:
            score = 0.8

        self.record_execution(tool_name, args, result, score)
        return context
