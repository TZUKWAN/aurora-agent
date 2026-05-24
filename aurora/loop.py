"""Autonomous loop system for AuroraAgent.

Background daemon threads that execute a prompt on interval,
with SQLite persistence for loop state.
"""

import json
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class LoopConfig:
    loop_id: str = ""
    action_prompt: str = ""
    interval_seconds: int = 300
    max_iterations: int = 0  # 0 = unlimited
    status: str = "stopped"  # stopped, running, paused
    iterations: int = 0
    last_run_at: str = ""
    created_at: str = ""


class LoopManager:
    """Manage autonomous execution loops.

    Loops run in background daemon threads, executing a prompt
    at regular intervals. State is persisted to SQLite.
    """

    def __init__(self, db=None, hooks=None):
        self._db = db
        self._hooks = hooks
        self._loops: Dict[str, LoopConfig] = {}
        self._threads: Dict[str, threading.Thread] = {}
        self._stop_events: Dict[str, threading.Event] = {}
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        if self._db is None:
            return
        try:
            conn = self._db._get_conn()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS loops (
                    id TEXT PRIMARY KEY,
                    config_json TEXT NOT NULL,
                    status TEXT DEFAULT 'stopped',
                    iterations INTEGER DEFAULT 0,
                    last_run_at TEXT DEFAULT '',
                    created_at TEXT DEFAULT ''
                )
            """)
            conn.commit()
            self._load_loops()
        except Exception as e:
            logger.warning("Failed to init loops table: %s", e)

    def _load_loops(self):
        if self._db is None:
            return
        try:
            conn = self._db._get_conn()
            rows = conn.execute("SELECT id, config_json, status, iterations, last_run_at FROM loops").fetchall()
            for row in rows:
                loop_id, config_json, status, iterations, last_run_at = row
                config = LoopConfig(**json.loads(config_json))
                config.status = status
                config.iterations = iterations
                config.last_run_at = last_run_at or ""
                self._loops[loop_id] = config
        except Exception as e:
            logger.warning("Failed to load loops: %s", e)

    def _save_loop(self, config: LoopConfig):
        if self._db is None:
            return
        try:
            conn = self._db._get_conn()
            conn.execute(
                """INSERT OR REPLACE INTO loops (id, config_json, status, iterations, last_run_at, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    config.loop_id,
                    json.dumps({
                        "loop_id": config.loop_id,
                        "action_prompt": config.action_prompt,
                        "interval_seconds": config.interval_seconds,
                        "max_iterations": config.max_iterations,
                    }),
                    config.status,
                    config.iterations,
                    config.last_run_at,
                    config.created_at,
                ),
            )
            conn.commit()
        except Exception as e:
            logger.warning("Failed to save loop %s: %s", config.loop_id, e)

    def start(self, action_prompt: str, interval_seconds: int = 300, max_iterations: int = 0, loop_id: str = "") -> str:
        """Start a new loop.

        Returns:
            The loop ID.
        """
        if not loop_id:
            loop_id = uuid.uuid4().hex[:12]

        from datetime import datetime
        config = LoopConfig(
            loop_id=loop_id,
            action_prompt=action_prompt,
            interval_seconds=max(interval_seconds, 10),
            max_iterations=max_iterations,
            status="running",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        with self._lock:
            self._loops[loop_id] = config
            self._save_loop(config)

        stop_event = threading.Event()
        self._stop_events[loop_id] = stop_event

        thread = threading.Thread(
            target=self._run_loop,
            args=(loop_id, stop_event),
            daemon=True,
            name=f"loop-{loop_id}",
        )
        self._threads[loop_id] = thread
        thread.start()

        logger.info("Loop '%s' started: interval=%ds, max_iter=%d", loop_id, interval_seconds, max_iterations)
        return loop_id

    def stop(self, loop_id: str) -> bool:
        """Stop a running loop."""
        with self._lock:
            config = self._loops.get(loop_id)
            if not config:
                return False

            config.status = "stopped"
            self._save_loop(config)

        stop_event = self._stop_events.get(loop_id)
        if stop_event:
            stop_event.set()

        logger.info("Loop '%s' stopped", loop_id)
        return True

    def pause(self, loop_id: str) -> bool:
        """Pause a running loop."""
        with self._lock:
            config = self._loops.get(loop_id)
            if not config or config.status != "running":
                return False
            config.status = "paused"
            self._save_loop(config)

        stop_event = self._stop_events.get(loop_id)
        if stop_event:
            stop_event.set()

        logger.info("Loop '%s' paused", loop_id)
        return True

    def resume(self, loop_id: str) -> bool:
        """Resume a paused loop."""
        with self._lock:
            config = self._loops.get(loop_id)
            if not config or config.status != "paused":
                return False
            config.status = "running"
            self._save_loop(config)

        stop_event = threading.Event()
        self._stop_events[loop_id] = stop_event

        thread = threading.Thread(
            target=self._run_loop,
            args=(loop_id, stop_event),
            daemon=True,
            name=f"loop-{loop_id}",
        )
        self._threads[loop_id] = thread
        thread.start()

        logger.info("Loop '%s' resumed", loop_id)
        return True

    def list_loops(self) -> List[Dict[str, Any]]:
        """List all loops and their status."""
        result = []
        with self._lock:
            for loop_id, config in self._loops.items():
                result.append({
                    "loop_id": config.loop_id,
                    "action_prompt": config.action_prompt[:100],
                    "interval_seconds": config.interval_seconds,
                    "max_iterations": config.max_iterations,
                    "status": config.status,
                    "iterations": config.iterations,
                    "last_run_at": config.last_run_at,
                })
        return result

    def _run_loop(self, loop_id: str, stop_event: threading.Event):
        """Main loop execution thread."""
        while not stop_event.is_set():
            config = self._loops.get(loop_id)
            if not config or config.status != "running":
                break

            # Check max iterations
            if config.max_iterations > 0 and config.iterations >= config.max_iterations:
                from datetime import datetime
                config.status = "stopped"
                config.last_run_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_loop(config)
                logger.info("Loop '%s' completed after %d iterations", loop_id, config.iterations)
                break

            # Execute the prompt
            self._execute_tick(loop_id)

            # Wait for interval or stop signal
            stop_event.wait(timeout=config.interval_seconds)

    def _execute_tick(self, loop_id: str):
        """Execute one iteration of a loop."""
        config = self._loops.get(loop_id)
        if not config:
            return

        from datetime import datetime

        try:
            logger.info("Loop '%s' tick #%d", loop_id, config.iterations + 1)

            if self._hooks:
                self._hooks.emit("loop.tick", {"loop_id": loop_id, "iteration": config.iterations + 1})

            config.iterations += 1
            config.last_run_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._save_loop(config)

        except Exception as e:
            logger.error("Loop '%s' tick failed: %s", loop_id, e)
            if self._hooks:
                self._hooks.emit("loop.error", {"loop_id": loop_id, "error": str(e)})
