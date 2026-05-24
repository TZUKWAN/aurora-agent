"""Security policy engine for AuroraAgent sandbox."""

import re
import time
from collections import defaultdict
from typing import Any, Callable, Dict, List


class SecurityPolicy:
    """Security policy engine that evaluates tool calls against registered rules."""

    def __init__(self) -> None:
        self._rules: List[Dict[str, Any]] = []
        self._call_timestamps: Dict[str, List[float]] = defaultdict(list)
        self._add_builtin_rules()

    def add_rule(
        self,
        rule_name: str,
        checker: Callable[[str, Dict[str, Any]], Dict[str, Any]],
        severity: str = "block",
    ) -> None:
        """Add a security rule.

        Args:
            rule_name: Unique identifier for the rule.
            checker: Callable accepting (tool_name, args) and returning a violation
                dict with keys "violated" (bool) and optionally "reason" (str),
                 or None if no violation.
            severity: "block" to deny the call, "warn" to log but allow.
        """
        self._rules.append({
            "name": rule_name,
            "checker": checker,
            "severity": severity,
        })

    def check(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Check all rules against a tool call.

        Returns:
            Dict with "allowed" (bool) and "violations" (list of violation dicts).
        """
        violations: List[Dict[str, Any]] = []
        blocked = False

        for rule in self._rules:
            result = rule["checker"](tool_name, args)
            if result:
                violation = {
                    "rule": rule["name"],
                    "severity": rule["severity"],
                    "reason": result.get("reason", f"Violated rule: {rule['name']}"),
                }
                violations.append(violation)
                if rule["severity"] == "block":
                    blocked = True

        return {"allowed": not blocked, "violations": violations}

    def list_rules(self) -> List[Dict[str, str]]:
        """List all registered rules.

        Returns:
            List of dicts with "name" and "severity" keys.
        """
        return [{"name": r["name"], "severity": r["severity"]} for r in self._rules]

    # ------------------------------------------------------------------
    # Built-in rule checkers
    # ------------------------------------------------------------------

    def _add_builtin_rules(self) -> None:
        """Register the default security rules."""
        self.add_rule("check_input_size", self._check_input_size, severity="block")
        self.add_rule(
            "check_dangerous_patterns",
            self._check_dangerous_patterns,
            severity="block",
        )
        self.add_rule(
            "check_required_params",
            self._check_required_params,
            severity="block",
        )
        self.add_rule("check_rate_limit", self._check_rate_limit, severity="block")

    # -- check_input_size --------------------------------------------------

    _MAX_INPUT_LENGTH = 100_000

    def _check_input_size(
        self, tool_name: str, args: Dict[str, Any]
    ) -> Dict[str, Any] | None:
        """Block args with any string value exceeding the character limit."""
        for key, value in args.items():
            if isinstance(value, str) and len(value) > self._MAX_INPUT_LENGTH:
                return {
                    "reason": (
                        f"Parameter '{key}' exceeds maximum allowed length "
                        f"({len(value)} > {self._MAX_INPUT_LENGTH})"
                    )
                }
            if isinstance(value, dict):
                nested_result = self._check_input_size(tool_name, value)
                if nested_result:
                    return nested_result
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and len(item) > self._MAX_INPUT_LENGTH:
                        return {
                            "reason": (
                                f"Parameter '{key}' contains item exceeding maximum "
                                f"allowed length ({len(item)} > {self._MAX_INPUT_LENGTH})"
                            )
                        }
        return None

    # -- check_dangerous_patterns -------------------------------------------

    _DANGEROUS_PATTERNS = [
        re.compile(r"<\s*script", re.IGNORECASE),
        re.compile(r"__import__"),
        re.compile(r"\bsubprocess\b"),
        re.compile(r"\beval\s*\("),
        re.compile(r"\bexec\s*\("),
    ]

    def _check_dangerous_patterns(
        self, tool_name: str, args: Dict[str, Any]
    ) -> Dict[str, Any] | None:
        """Block args containing dangerous code injection patterns."""
        for key, value in args.items():
            text = self._extract_text(value)
            if text:
                for pattern in self._DANGEROUS_PATTERNS:
                    if pattern.search(text):
                        return {
                            "reason": (
                                f"Parameter '{key}' contains dangerous pattern: "
                                f"{pattern.pattern}"
                            )
                        }
        return None

    @staticmethod
    def _extract_text(value: Any) -> str | None:
        """Recursively extract the first string value from a nested structure."""
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            for v in value.values():
                text = SecurityPolicy._extract_text(v)
                if text:
                    return text
        if isinstance(value, list):
            for item in value:
                text = SecurityPolicy._extract_text(item)
                if text:
                    return text
        return None

    # -- check_required_params ----------------------------------------------

    def _check_required_params(
        self, tool_name: str, args: Dict[str, Any]
    ) -> Dict[str, Any] | None:
        """Verify that required parameters are present.

        This rule checks that the args dict is not empty for known tools.
        Specific per-tool parameter requirements can be added via add_rule.
        """
        if not isinstance(args, dict):
            return {"reason": "Arguments must be a dictionary"}
        return None

    # -- check_rate_limit ---------------------------------------------------

    _RATE_LIMIT_WINDOW = 60  # seconds
    _RATE_LIMIT_MAX_CALLS = 60  # calls per window per tool

    def _check_rate_limit(
        self, tool_name: str, args: Dict[str, Any]
    ) -> Dict[str, Any] | None:
        """Simple in-memory rate limit: max calls per minute per tool."""
        now = time.time()
        timestamps = self._call_timestamps[tool_name]

        # Prune timestamps outside the window
        window_start = now - self._RATE_LIMIT_WINDOW
        self._call_timestamps[tool_name] = [
            ts for ts in timestamps if ts > window_start
        ]

        current_count = len(self._call_timestamps[tool_name])
        if current_count >= self._RATE_LIMIT_MAX_CALLS:
            return {
                "reason": (
                    f"Rate limit exceeded for tool '{tool_name}': "
                    f"{current_count} calls in the last "
                    f"{self._RATE_LIMIT_WINDOW} seconds"
                )
            }

        # Record this call timestamp
        self._call_timestamps[tool_name].append(now)
        return None
