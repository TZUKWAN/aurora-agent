"""Tool guardrails for AuroraAgent.

Enforces consecutive call limits and per-minute rate limits
on tool dispatches to prevent runaway tool usage.
"""

import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ToolGuardrails:
    """Enforce rate limits and consecutive call limits on tools.

    Register as a HookManager handler on tool.pre_dispatch (priority=10).
    """

    def __init__(
        self,
        consecutive_limits: Optional[Dict[str, int]] = None,
        rate_limits: Optional[Dict[str, int]] = None,
        default_consecutive: int = 10,
        default_rate: int = 60,
    ):
        self.consecutive_limits = consecutive_limits or {}
        self.rate_limits = rate_limits or {}
        self.default_consecutive = default_consecutive
        self.default_rate = default_rate

        self._consecutive_counts: Dict[str, int] = {}
        self._last_tool: Optional[str] = None
        self._rate_timestamps: Dict[str, List[float]] = {}

    def check(self, tool_name: str) -> tuple:
        """Check if a tool call is allowed.

        Returns:
            (allowed, reason) tuple.
        """
        # Check consecutive limit
        limit = self.consecutive_limits.get(tool_name, self.default_consecutive)
        if tool_name == self._last_tool:
            count = self._consecutive_counts.get(tool_name, 0) + 1
        else:
            count = 1

        if count > limit:
            return False, f"工具'{tool_name}'连续调用超过{limit}次上限"

        # Check rate limit
        rate_limit = self.rate_limits.get(tool_name, self.default_rate)
        now = time.time()
        timestamps = self._rate_timestamps.get(tool_name, [])
        # Keep only timestamps within the last 60 seconds
        timestamps = [t for t in timestamps if now - t < 60]

        if len(timestamps) >= rate_limit:
            return False, f"工具'{tool_name}'每分钟调用超过{rate_limit}次上限"

        return True, ""

    def record(self, tool_name: str):
        """Record a successful tool dispatch."""
        # Update consecutive tracking
        if tool_name == self._last_tool:
            self._consecutive_counts[tool_name] = self._consecutive_counts.get(tool_name, 0) + 1
        else:
            self._consecutive_counts = {tool_name: 1}
            self._last_tool = tool_name

        # Update rate tracking
        now = time.time()
        if tool_name not in self._rate_timestamps:
            self._rate_timestamps[tool_name] = []
        self._rate_timestamps[tool_name].append(now)

    def check_hook(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Hook handler for tool.pre_dispatch."""
        tool_name = context.get("tool", "")
        allowed, reason = self.check(tool_name)
        if not allowed:
            context["blocked"] = True
            context["block_reason"] = reason
            logger.warning("Guardrail blocked tool '%s': %s", tool_name, reason)
            return context

        self.record(tool_name)
        return context

    def reset(self):
        """Reset all tracking state."""
        self._consecutive_counts.clear()
        self._last_tool = None
        self._rate_timestamps.clear()
