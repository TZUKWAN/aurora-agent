"""Swarm bus for inter-agent communication."""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BusMessage:
    """Message passed between swarm agents."""
    sender: str
    recipient: str
    content: Any
    message_type: str = "informational"
    timestamp: float = field(default_factory=lambda: time.monotonic())
    correlation_id: Optional[str] = None


@dataclass
class PriorityBusMessage(BusMessage):
    """BusMessage with priority for ordered processing."""
    priority: int = 0


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

    async def send_priority(self, message: BusMessage, priority: int = 0):
        """Send a message with priority. Higher priority messages are processed first."""
        priority_msg = PriorityBusMessage(
            sender=message.sender,
            recipient=message.recipient,
            content=message.content,
            message_type=message.message_type,
            timestamp=message.timestamp,
            correlation_id=message.correlation_id,
            priority=priority,
        )
        async with self._lock:
            self._messages.append(priority_msg)

            if priority_msg.recipient in self._listeners:
                for queue in self._listeners[priority_msg.recipient]:
                    await queue.put(priority_msg)

    async def request_response(
        self, sender: str, recipient: str, content: Any, timeout: float = 5.0
    ) -> Any:
        """Send a message and wait for a response with timeout."""
        temp_queue = self.subscribe(sender)
        message = BusMessage(
            sender=sender,
            recipient=recipient,
            content=content,
            message_type="request",
        )
        await self.send(message)

        try:
            response = await asyncio.wait_for(temp_queue.get(), timeout=timeout)
            return response.content
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"No response from '{recipient}' within {timeout}s"
            )
        finally:
            if sender in self._listeners:
                self._listeners[sender] = [
                    q for q in self._listeners[sender] if q is not temp_queue
                ]

    def get_stats(self) -> dict:
        """Return bus statistics."""
        message_types: Dict[str, int] = {}
        for msg in self._messages:
            message_types[msg.message_type] = message_types.get(msg.message_type, 0) + 1

        active_listeners = sum(len(queues) for queues in self._listeners.values())

        return {
            "total_messages": len(self._messages),
            "active_listeners": active_listeners,
            "message_types": message_types,
        }

    async def get_recent(self, count: int = 10) -> List[BusMessage]:
        """Get most recent N messages."""
        async with self._lock:
            return self._messages[-count:] if count > 0 else []
