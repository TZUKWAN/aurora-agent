"""Context compression for AuroraAgent.

Prevents context window overflow by summarizing older messages
when token estimates exceed the configured threshold.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Approximate tokens per character for Chinese-heavy content
TOKEN_RATIO = 1.5


class ContextCompressor:
    """Compress conversation history when it exceeds token threshold.

    Strategy:
    1. Estimate total tokens in current messages.
    2. If below threshold * context_window, return as-is.
    3. If above, summarize older messages and keep recent ones.
    """

    def __init__(
        self,
        context_window: int = 32000,
        compress_threshold: float = 0.65,
        keep_recent: int = 5,
        llm_client=None,
        model_name: str = "",
    ):
        self.context_window = context_window
        self.compress_threshold = compress_threshold
        self.keep_recent = keep_recent
        self.llm_client = llm_client
        self.model_name = model_name

    def estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Estimate token count for messages.

        Uses a simple heuristic: Chinese chars ~1.5 tokens each,
        ASCII chars ~0.25 tokens each.
        """
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            if not content:
                continue
            for ch in content:
                if ord(ch) > 127:
                    total += TOKEN_RATIO
                else:
                    total += 0.25
        return int(total)

    def compress(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
    ) -> List[Dict[str, str]]:
        """Compress messages if they exceed the token threshold.

        Args:
            messages: Full message list (including system message).
            system_prompt: Original system prompt to prepend summary to.

        Returns:
            Compressed message list.
        """
        estimated = self.estimate_tokens(messages)
        threshold = int(self.context_window * self.compress_threshold)

        if estimated < threshold:
            return messages

        logger.info(
            "Context compression triggered: %d estimated tokens > %d threshold",
            estimated, threshold,
        )

        # Separate system message from conversation
        system_msg = None
        conv_messages = messages
        if messages and messages[0].get("role") == "system":
            system_msg = messages[0]
            conv_messages = messages[1:]

        if len(conv_messages) <= self.keep_recent:
            return messages

        # Split into old (to summarize) and recent (to keep)
        split_idx = len(conv_messages) - self.keep_recent
        old_messages = conv_messages[:split_idx]
        recent_messages = conv_messages[split_idx:]

        # Generate summary of old messages
        summary = self._summarize(old_messages)

        # Build compressed message list
        compressed = []
        if system_msg:
            new_content = system_msg["content"]
            if summary:
                new_content += f"\n\n[对话历史摘要]\n{summary}"
            compressed.append({"role": "system", "content": new_content})
        elif summary:
            compressed.append({"role": "system", "content": f"[对话历史摘要]\n{summary}"})

        compressed.extend(recent_messages)

        new_estimated = self.estimate_tokens(compressed)
        logger.info(
            "Context compressed: %d -> %d estimated tokens (%d messages -> %d)",
            estimated, new_estimated, len(messages), len(compressed),
        )

        return compressed

    def _summarize(self, messages: List[Dict[str, str]]) -> str:
        """Summarize a list of messages.

        Uses LLM if available, otherwise generates a simple extractive summary.
        """
        if not messages:
            return ""

        if self.llm_client:
            summary = self._llm_summarize(messages)
            if summary:
                return summary

        # Fallback: extractive summary
        return self._extractive_summarize(messages)

    def _llm_summarize(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Use LLM to generate a summary of messages."""
        try:
            text_parts = []
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if content:
                    text_parts.append(f"[{role}]: {content[:500]}")

            combined = "\n".join(text_parts)
            if len(combined) > 4000:
                combined = combined[:4000]

            resp = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "请用中文简洁地总结以下对话的关键信息，"
                            "保留所有重要的事实、决策和结论。"
                            "控制在200字以内。"
                        ),
                    },
                    {"role": "user", "content": combined},
                ],
                temperature=0.3,
                max_tokens=512,
            )

            content = resp.choices[0].message.content or ""
            rc = getattr(resp.choices[0].message, "reasoning_content", None)
            if not content.strip() and rc:
                content = rc
            return content.strip() if content.strip() else None

        except Exception as e:
            logger.warning("LLM summarization failed: %s", e)
            return None

    def _extractive_summarize(self, messages: List[Dict[str, str]]) -> str:
        """Generate a simple extractive summary by keeping key content."""
        parts = []
        total_chars = 0
        max_chars = 800

        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if not content:
                continue

            # Keep shorter messages in full, truncate longer ones
            if len(content) > 200:
                content = content[:200] + "..."

            parts.append(f"[{role}] {content}")
            total_chars += len(content)

            if total_chars >= max_chars:
                break

        return "\n".join(parts)
