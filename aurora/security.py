"""Security manager for AuroraAgent.

Provides prompt injection detection, credential redaction,
and path traversal prevention.
"""

import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Patterns suggesting prompt injection attempts
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"forget\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+a\s+",
    r"system\s*:\s*",
    r"<\s*system\s*>",
    r"jailbreak",
    r"绕过\s*(所有\s*)?(之前的\s*)?指令",
    r"忽略\s*(所有\s*)?(之前的\s*)?指令",
    r"你现在是一个",
]

# Patterns for API keys and credentials
_CREDENTIAL_PATTERNS = [
    (r'(api[_-]?key\s*[:=]\s*["\']?)sk-[a-zA-Z0-9]{20,}', r'\1[REDACTED]'),
    (r'(api[_-]?key\s*[:=]\s*["\']?)[a-zA-Z0-9]{32,}', r'\1[REDACTED]'),
    (r'(password\s*[:=]\s*["\']?)\S{8,}', r'\1[REDACTED]'),
    (r'(token\s*[:=]\s*["\']?)eyJ[a-zA-Z0-9._-]+', r'\1[REDACTED]'),
    (r'(Bearer\s+)[a-zA-Z0-9._-]{20,}', r'\1[REDACTED]'),
]


class SecurityManager:
    """Detects and prevents security threats in tool inputs and outputs."""

    def __init__(self, injection_threshold: float = 0.0):
        self.injection_threshold = injection_threshold
        self._injection_regexes = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]

    def check_prompt_injection(self, text: str) -> Tuple[bool, str]:
        """Check text for prompt injection patterns.

        Returns:
            (is_injection, reason) tuple.
        """
        if not text:
            return False, ""

        matches = 0
        matched_patterns = []
        for regex in self._injection_regexes:
            if regex.search(text):
                matches += 1
                matched_patterns.append(regex.pattern)

        if matches > 0:
            score = min(matches / len(self._injection_regexes), 1.0)
            if score >= self.injection_threshold or matches >= 2:
                reason = f"检测到潜在的prompt注入（匹配{matches}个模式）"
                logger.warning("Prompt injection detected: %s", reason)
                return True, reason

        return False, ""

    def redact_credentials(self, text: str) -> str:
        """Redact API keys and credentials from text."""
        if not text:
            return text

        for pattern, replacement in _CREDENTIAL_PATTERNS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def validate_path(self, path: str) -> bool:
        """Check if a file path is safe (no traversal attacks).

        Returns:
            True if safe, False if path traversal detected.
        """
        if not path:
            return True

        # Normalize and check for traversal
        normalized = os.path.normpath(path)
        if ".." in normalized.split(os.sep):
            logger.warning("Path traversal detected: %s", path)
            return False

        # Check for absolute paths trying to access system directories
        if os.path.isabs(normalized):
            # Allow common output directories
            allowed_prefixes = (
                os.path.expanduser("~"),
                os.path.expanduser("~/Documents"),
                os.path.expanduser("~/Desktop"),
                os.getcwd(),
            )
            is_allowed = any(normalized.startswith(p) for p in allowed_prefixes)
            if not is_allowed:
                logger.warning("Absolute path outside allowed directories: %s", path)
                return False

        return True

    def check_hook(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Hook handler for tool.pre_dispatch security checks."""
        args = context.get("args", {})
        if isinstance(args, dict):
            for key, value in args.items():
                if isinstance(value, str):
                    is_injection, reason = self.check_prompt_injection(value)
                    if is_injection:
                        context["blocked"] = True
                        context["block_reason"] = reason
                        return context

        return context
