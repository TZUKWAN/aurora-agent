"""Swarm bus for inter-agent communication."""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BusMessage:
    """Message passed between swarm agents."""
    sender: str
    recipient: str
    content: Any
    message_type: str = "informational"
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time())
    correlation_id: Optional[str] = None


class SwarmBus:
    """Thread-safe message bus for swarm communication."""

    def __init__(self):
        self._messages: List[BusMessage] = []
        self._listeners: Dict[str, List[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def send(self, message: BusMessage):
        """Send a message to the bus."""
        async with self._lock:
            self._messages.append(message)

            if message.recipient in self._listeners:
                for queue in self._listeners[message.recipient]:
                    await queue.put(message)

    async def broadcast(self, sender: str, content: Any, message_type: str = "informational"):
        """Broadcast a message to all listeners."""
        async with self._lock:
            message = BusMessage(
                sender=sender,
                recipient="*",
                content=content,
                message_type=message_type,
            )
            self._messages.append(message)

            for queues in self._listeners.values():
                for queue in queues:
                    await queue.put(message)

    def subscribe(self, recipient: str) -> asyncio.Queue:
        """Subscribe to messages for a specific recipient."""
        queue = asyncio.Queue()
        if recipient not in self._listeners:
            self._listeners[recipient] = []
        self._listeners[recipient].append(queue)
        return queue

    async def get_messages(self, recipient: str) -> List[BusMessage]:
        """Get all messages for a recipient."""
        async with self._lock:
            return [m for m in self._messages if m.recipient == recipient or m.recipient == "*"]

    def get_history(self) -> List[BusMessage]:
        """Get all messages in history."""
        return self._messages.copy()

    def clear_history(self):
        """Clear message history."""
        self._messages.clear()
