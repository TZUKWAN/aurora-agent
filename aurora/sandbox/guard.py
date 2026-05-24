"""Sandbox guard that integrates with ToolRegistry hooks."""

import json
import logging
from typing import Any, Callable, Dict, List, Optional

from aurora.sandbox.policy import SecurityPolicy

logger = logging.getLogger(__name__)


class SimpleHooks:
    """Lightweight event-driven hooks compatible with ToolRegistry.

    ToolRegistry calls hooks.emit(event_name, data_dict) and inspects
    the returned dict for a "blocked" key.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable]] = {}

    def on(self, event: str, handler: Callable) -> None:
        """Register a handler for an event."""
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    def emit(self, event: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Emit an event, running all registered handlers in order.

        Each handler receives and may mutate the data dict.
        Returns the (possibly modified) data dict.
        """
        result = dict(data)
        if event in self._handlers:
            for handler in self._handlers[event]:
                handler(result)
        return result


class SandboxGuard:
    """Guard that enforces security policy through ToolRegistry hooks."""

    def __init__(self, policy: Optional[SecurityPolicy] = None) -> None:
        """Initialize with an optional custom policy.

        Args:
            policy: SecurityPolicy instance. If None, a default policy is created.
        """
        self._policy = policy if policy is not None else SecurityPolicy()
        self._hooks = SimpleHooks()
        self._hooks.on("tool.pre_dispatch", self._on_pre_dispatch)
        self._hooks.on("tool.post_dispatch", self._on_post_dispatch)
        self._hooks.on("tool.error", self._on_error)

    @property
    def policy(self) -> SecurityPolicy:
        """Access the underlying security policy."""
        return self._policy

    def get_hooks(self) -> SimpleHooks:
        """Return the hooks object for registration with ToolRegistry.

        Usage:
            guard = SandboxGuard()
            registry = ToolRegistry()
            registry.set_hooks(guard.get_hooks())
        """
        return self._hooks

    # ------------------------------------------------------------------
    # Hook handlers
    # ------------------------------------------------------------------

    def _on_pre_dispatch(self, ctx: Dict[str, Any]) -> None:
        """Pre-dispatch handler: check security policy and block if violated."""
        tool_name = ctx.get("tool", "")
        args = ctx.get("args", {})
        if not isinstance(args, dict):
            args = {}

        result = self._policy.check(tool_name, args)

        if not result["allowed"]:
            violations = result["violations"]
            block_reasons = "; ".join(v["reason"] for v in violations)
            ctx["blocked"] = True
            ctx["block_reason"] = block_reasons
            logger.warning(
                "Blocked tool '%s': %s", tool_name, block_reasons
            )

    def _on_post_dispatch(self, ctx: Dict[str, Any]) -> None:
        """Post-dispatch handler: log successful tool execution."""
        tool_name = ctx.get("tool", "")
        logger.debug("Tool '%s' executed successfully", tool_name)

    def _on_error(self, ctx: Dict[str, Any]) -> None:
        """Error handler: log tool execution errors."""
        tool_name = ctx.get("tool", "")
        error = ctx.get("error", "Unknown error")
        error_type = ctx.get("error_type", "Unknown")
        logger.error(
            "Tool '%s' error [%s]: %s", tool_name, error_type, error
        )
