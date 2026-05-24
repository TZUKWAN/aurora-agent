"""Error recovery manager for AuroraAgent.

Provides automatic retry with exponential backoff
for transient tool execution failures.
"""

import logging
import time
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class RecoveryManager:
    """Automatically retry failed tool executions with backoff.

    Register as a HookManager handler on tool.error (priority=50).
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self._retry_counts: Dict[str, int] = {}

    def classify_error(self, error: str, error_type: str = "") -> str:
        """Classify an error to determine recovery strategy.

        Returns:
            Error category: "transient", "auth", "rate_limit", or "permanent".
        """
        error_lower = error.lower()
        error_type_lower = error_type.lower()

        # Rate limit errors
        rate_keywords = ["rate limit", "rate_limit", "too many requests", "429", "throttl"]
        if any(kw in error_lower or kw in error_type_lower for kw in rate_keywords):
            return "rate_limit"

        # Auth errors
        auth_keywords = ["unauthorized", "forbidden", "401", "403", "invalid api key", "authentication"]
        if any(kw in error_lower or kw in error_type_lower for kw in auth_keywords):
            return "auth"

        # Transient errors
        transient_keywords = [
            "timeout", "timed out", "connection", "network", "temporary",
            "503", "502", "500", "internal server error",
        ]
        if any(kw in error_lower or kw in error_type_lower for kw in transient_keywords):
            return "transient"

        return "permanent"

    def get_delay(self, retry_count: int, error_category: str) -> float:
        """Calculate delay before next retry based on error category.

        Args:
            retry_count: Current retry attempt number (0-based).
            error_category: Classified error category.

        Returns:
            Delay in seconds.
        """
        if error_category == "rate_limit":
            return min(self.base_delay * (2 ** retry_count) * 2, self.max_delay)
        if error_category == "transient":
            return min(self.base_delay * (2 ** retry_count), self.max_delay)
        return 0

    def should_retry(self, tool_name: str, error_category: str) -> bool:
        """Determine if a failed tool call should be retried.

        Args:
            tool_name: Name of the tool that failed.
            error_category: Classified error category.

        Returns:
            True if retry is recommended.
        """
        if error_category == "permanent":
            return False
        if error_category == "auth":
            return False

        count = self._retry_counts.get(tool_name, 0)
        return count < self.max_retries

    def record_retry(self, tool_name: str):
        """Record a retry attempt for a tool."""
        self._retry_counts[tool_name] = self._retry_counts.get(tool_name, 0) + 1

    def record_success(self, tool_name: str):
        """Record a successful execution, clearing retry count."""
        self._retry_counts.pop(tool_name, None)

    def handle_error_hook(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Hook handler for tool.error events.

        Analyzes the error and sets recovery suggestions in context.
        """
        tool_name = context.get("tool", "")
        error = context.get("error", "")
        error_type = context.get("error_type", "")

        category = self.classify_error(error, error_type)
        context["error_category"] = category

        if self.should_retry(tool_name, category):
            delay = self.get_delay(self._retry_counts.get(tool_name, 0), category)
            context["retry_recommended"] = True
            context["retry_delay"] = delay
            self.record_retry(tool_name)
            logger.info(
                "Recovery: tool '%s' error classified as '%s', retry %d/%d in %.1fs",
                tool_name, category,
                self._retry_counts.get(tool_name, 0), self.max_retries, delay,
            )
        else:
            context["retry_recommended"] = False
            logger.info(
                "Recovery: tool '%s' error classified as '%s', no retry",
                tool_name, category,
            )

        return context

    def reset(self):
        """Reset all retry counts."""
        self._retry_counts.clear()
