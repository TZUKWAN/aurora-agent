"""Conversation history management with edit/undo/redo support."""

from typing import Dict, List, Optional, Tuple


class ConversationHistory:
    """Manages message list with edit, undo, and redo support."""

    def __init__(self):
        self._messages: List[Dict[str, str]] = []
        self._undo_stack: List[Tuple[str, dict]] = []
        self._redo_stack: List[Tuple[str, dict]] = []

    def add(self, role: str, content: str) -> None:
        """Add a message to history."""
        self._messages.append({"role": role, "content": content})
        self._redo_stack.clear()

    def edit(self, index: int, new_content: str) -> bool:
        """Edit a message at the given index. Truncates all messages after it.

        Args:
            index: 0-based index of the message to edit
            new_content: New content for the message

        Returns:
            True if edit succeeded, False if index was invalid
        """
        if index < 0 or index >= len(self._messages):
            return False

        old_message = dict(self._messages[index])
        old_tail = [dict(m) for m in self._messages[index + 1:]]

        self._undo_stack.append(("edit", {
            "index": index,
            "old_message": old_message,
            "old_tail": old_tail,
            "old_count": len(self._messages),
        }))
        self._redo_stack.clear()

        self._messages[index] = {"role": self._messages[index]["role"], "content": new_content}
        self._messages = self._messages[: index + 1]
        return True

    def undo(self) -> bool:
        """Undo the last operation. Returns True if successful."""
        if not self._undo_stack:
            return False

        action, state = self._undo_stack.pop()

        self._redo_stack.append(("undo", {
            "action": action,
            "state": state,
            "current_messages": [dict(m) for m in self._messages],
        }))

        if action == "edit":
            idx = state["index"]
            self._messages = self._messages[:idx]
            self._messages.append(state["old_message"])
            self._messages.extend(state["old_tail"])

        return True

    def redo(self) -> bool:
        """Redo the last undone operation. Returns True if successful."""
        if not self._redo_stack:
            return False

        _, redo_state = self._redo_stack.pop()
        action = redo_state["action"]
        state = redo_state["state"]

        self._undo_stack.append(("edit", state))

        self._messages = redo_state["current_messages"]
        return True

    def get_messages(self) -> List[Dict[str, str]]:
        """Return current message list (copies)."""
        return [dict(m) for m in self._messages]

    def __len__(self) -> int:
        return len(self._messages)

    def clear(self) -> None:
        """Clear all messages and history."""
        self._messages.clear()
        self._undo_stack.clear()
        self._redo_stack.clear()
