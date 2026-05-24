"""Rich-based interactive TUI chat mode for AuroraAgent."""

from typing import Optional

from rich.panel import Panel

from aurora.tui.display import TUIDisplay


class InteractiveTUI:
    """Rich-based interactive chat mode."""

    def __init__(self, agent=None) -> None:
        self.display = TUIDisplay()
        self.agent = agent
        self._running = False

    def start(self, agent=None) -> None:
        """Start interactive TUI mode."""
        if agent:
            self.agent = agent
        self._running = True
        self.display.show_banner()

        while self._running:
            try:
                user_input = self.display.console.input("[bold cyan]You>[/] ")
                if not user_input.strip():
                    continue
                self._handle_input(user_input)
            except (KeyboardInterrupt, EOFError):
                self._running = False
                self.display.show_farewell()

    def _handle_input(self, user_input: str) -> None:
        """Handle user input with command routing."""
        stripped = user_input.strip()
        if stripped in ("/exit", "/quit", "/q"):
            self._running = False
            self.display.show_farewell()
        elif stripped == "/tools":
            if self.agent:
                self.display.show_tool_list(self.agent.get_tool_list())
            else:
                self.display.show_error("Agent not initialized")
        elif stripped == "/help":
            self._show_help()
        elif stripped.startswith("/"):
            self.display.show_error(f"Unknown command: {stripped}")
        else:
            self._chat(stripped)

    def _chat(self, message: str) -> None:
        """Send message to agent and display response."""
        if not self.agent:
            self.display.show_error("Agent not initialized")
            return
        import asyncio

        try:
            result = asyncio.run(self.agent.run(message))
            self.display.console.print()
            self.display.show_markdown(result)
            self.display.console.print()
        except Exception as e:
            self.display.show_error(str(e))

    def _show_help(self) -> None:
        """Show help panel."""
        help_text = (
            "Available commands:\n"
            "  /tools  - List available tools\n"
            "  /help   - Show this help\n"
            "  /exit   - Exit the program\n"
        )
        self.display.console.print(Panel(help_text, title="Help"))
