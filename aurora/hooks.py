"""Event hook system for AuroraAgent.

The nervous system of the agent -- all mechanisms (Guardrails, Recovery,
Learning, Loop, etc.) plug into this via register/emit.

Usage:
    hooks = HookManager()
    hooks.register(HookEvent.TOOL_PRE_DISPATCH, my_handler, priority=50)
    ctx = hooks.emit(HookEvent.TOOL_PRE_DISPATCH, {"tool": "bp_generate", "args": {...}})
    if ctx.get("blocked"):
        # handler blocked the dispatch
"""

import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class HookEvent:
    """Predefined event names used throughout AuroraAgent."""

    # Agent lifecycle
    AGENT_START = "agent.start"
    AGENT_MESSAGE = "agent.message"
    AGENT_RESPONSE = "agent.response"
    AGENT_ERROR = "agent.error"
    AGENT_STOP = "agent.stop"

    # Tool lifecycle
    TOOL_PRE_DISPATCH = "tool.pre_dispatch"
    TOOL_POST_DISPATCH = "tool.post_dispatch"
    TOOL_ERROR = "tool.error"

    # Swarm lifecycle
    SWARM_START = "swarm.start"
    SWARM_STAGE_START = "swarm.stage_start"
    SWARM_STAGE_COMPLETE = "swarm.stage_complete"
    SWARM_COMPLETE = "swarm.complete"
    SWARM_ERROR = "swarm.error"

    # Loop lifecycle
    LOOP_TICK = "loop.tick"
    LOOP_COMPLETE = "loop.complete"
    LOOP_ERROR = "loop.error"

    # Goal lifecycle
    GOAL_CREATE = "goal.create"
    GOAL_UPDATE = "goal.update"
    GOAL_COMPLETE = "goal.complete"

    # Memory
    MEMORY_STORE = "memory.store"
    MEMORY_RECALL = "memory.recall"

    # Context
    CONTEXT_COMPRESS = "context.compress"

    # Learning
    LEARNING_RECORD = "learning.record"
    LEARNING_ANALYSIS = "learning.analysis"

    # Guardrail
    GUARDRAIL_BLOCK = "guardrail.block"

    # Security
    SECURITY_ALERT = "security.alert"


class HookManager:
    """Central event hook manager.

    Handlers are called in priority order (lower = earlier).
    Each handler receives and can modify the context dict.
    If a handler sets context["blocked"] = True, subsequent handlers
    are skipped and the emit returns early.
    """

    def __init__(self):
        self._hooks: Dict[str, List[Dict[str, Any]]] = {}

    def register(
        self,
        event: str,
        handler: Callable[[Dict[str, Any]], Optional[Dict[str, Any]]],
        priority: int = 100,
        name: Optional[str] = None,
    ) -> None:
        """Register a hook handler for an event.

        Args:
            event: Event name (use HookEvent constants).
            handler: Callable taking a context dict, returning an updated
                     context dict or None (context used as-is).
            priority: Lower numbers run first. Default 100.
            name: Optional name for easy removal.
        """
        if event not in self._hooks:
            self._hooks[event] = []

        entry = {
            "handler": handler,
            "priority": priority,
            "name": name or handler.__name__,
        }
        self._hooks[event].append(entry)
        self._hooks[event].sort(key=lambda x: x["priority"])
        logger.debug(
            "Hook registered: event=%s, name=%s, priority=%d",
            event, entry["name"], priority,
        )

    def emit(self, event: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Emit an event, running all registered handlers in priority order.

        Args:
            event: Event name.
            context: Initial context dict. Modified in-place by handlers.

        Returns:
            The (possibly modified) context dict.
        """
        if context is None:
            context = {}

        handlers = self._hooks.get(event, [])
        if not handlers:
            return context

        for entry in handlers:
            try:
                result = entry["handler"](context)
                if result is not None:
                    context = result
            except Exception as e:
                logger.warning(
                    "Hook handler '%s' failed for event '%s': %s",
                    entry["name"], event, e,
                )

            if context.get("blocked"):
                logger.debug(
                    "Hook chain blocked at '%s' for event '%s': %s",
                    entry["name"], event, context.get("block_reason", ""),
                )
                break

        return context

    def remove(
        self,
        event: str,
        handler: Optional[Callable] = None,
        name: Optional[str] = None,
    ) -> bool:
        """Remove a handler by reference or name.

        Returns True if a handler was removed.
        """
        if event not in self._hooks:
            return False

        original_len = len(self._hooks[event])
        if handler:
            self._hooks[event] = [
                h for h in self._hooks[event] if h["handler"] is not handler
            ]
        elif name:
            self._hooks[event] = [
                h for h in self._hooks[event] if h["name"] != name
            ]
        else:
            return False

        removed = len(self._hooks[event]) < original_len
        if removed:
            logger.debug("Hook removed: event=%s", event)
        return removed

    def remove_all(self, event: Optional[str] = None) -> None:
        """Remove all handlers for an event, or all events if event is None."""
        if event:
            self._hooks.pop(event, None)
        else:
            self._hooks.clear()

    def list_hooks(self, event: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """List registered hooks, optionally filtered by event.

        Returns a dict mapping event names to lists of handler info dicts.
        """
        if event:
            entries = self._hooks.get(event, [])
            return {event: [{"name": h["name"], "priority": h["priority"]} for h in entries]}
        return {
            ev: [{"name": h["name"], "priority": h["priority"]} for h in handlers]
            for ev, handlers in self._hooks.items()
        }

    def has_hooks(self, event: str) -> bool:
        """Check if any handlers are registered for an event."""
        return bool(self._hooks.get(event))
