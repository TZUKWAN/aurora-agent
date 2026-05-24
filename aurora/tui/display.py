"""Rich-based TUI display manager for AuroraAgent."""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text

from typing import Dict, List, Optional

import aurora


class TUIDisplay:
    """Rich-based terminal display manager."""

    def __init__(self) -> None:
        self.console = Console()

    def show_banner(self) -> None:
        """Display AuroraAgent banner with version and model info."""
        version = aurora.__version__
        banner_text = Text()
        banner_text.append("AuroraAgent", style="bold cyan")
        banner_text.append(f" v{version}", style="dim")
        banner_text.append("\n")
        banner_text.append("Competition AI Assistant", style="italic")

        try:
            from aurora.config import load_config
            config = load_config()
            model_name = config.model.name if hasattr(config, "model") else "unknown"
            banner_text.append(f"\nModel: {model_name}", style="dim")
        except Exception:
            banner_text.append("\nModel: not configured", style="dim yellow")

        self.console.print(Panel(banner_text, border_style="cyan", padding=(1, 2)))

    def show_tool_list(self, tools: list) -> None:
        """Display tools in a Rich table."""
        table = Table(title="Registered Tools", show_lines=False)
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("Tool Name", style="cyan")

        for i, tool in enumerate(tools, 1):
            if isinstance(tool, dict):
                name = tool.get("name", str(tool))
            else:
                name = str(tool)
            table.add_row(str(i), name)

        self.console.print(table)

    def show_plan(self, plan: dict) -> None:
        """Display business plan summary with sections."""
        metadata = plan.get("metadata", {})
        project_name = metadata.get("project_name", "Untitled")
        sections = plan.get("sections", {})

        self.console.print()
        self.console.print(Panel(
            Text(project_name, style="bold cyan"),
            title="Business Plan",
            border_style="cyan",
        ))

        for key, section in sections.items():
            if isinstance(section, dict):
                title = section.get("title", key.replace("_", " ").title())
                content = section.get("content", "")
            else:
                title = key.replace("_", " ").title()
                content = str(section)

            self.console.print(Panel(
                content,
                title=title,
                border_style="blue",
                padding=(0, 1),
            ))

        self.console.print()

    def show_evaluation(self, result: dict) -> None:
        """Display evaluation scores in a table with color coding."""
        overall = result.get("overall_score", 0)
        dimensions = result.get("dimensions", [])

        overall_style = self._score_style(overall)
        self.console.print(Panel(
            Text(f"Overall Score: {overall:.1f}", style=f"bold {overall_style}"),
            title="Evaluation Result",
            border_style=overall_style,
        ))

        if dimensions:
            table = Table(title="Dimension Scores", show_lines=False)
            table.add_column("Dimension", style="bold")
            table.add_column("Score", justify="right")
            table.add_column("Weight", justify="right")
            table.add_column("Bar", min_width=20)

            for dim in dimensions:
                name = dim.get("name", "Unknown")
                score = dim.get("score", 0)
                weight = dim.get("weight", 0)
                style = self._score_style(score)
                bar = self._score_bar(score)
                table.add_row(
                    name,
                    f"[{style}]{score}[/{style}]",
                    f"{weight:.0%}",
                    f"[{style}]{bar}[/{style}]",
                )

            self.console.print(table)

    def show_session_list(self, sessions: list) -> None:
        """Display sessions in a table."""
        if not sessions:
            self.console.print("[dim]No sessions found.[/dim]")
            return

        table = Table(title="Sessions", show_lines=False)
        table.add_column("Session ID", style="cyan")
        table.add_column("Project", style="bold")
        table.add_column("Updated", style="dim")

        for s in sessions:
            sid = s.get("session_id", "unknown")
            project = s.get("project_name", "unknown")[:20]
            updated = s.get("last_updated", "unknown")[:19]
            table.add_row(sid, project, updated)

        self.console.print(table)

    def show_error(self, message: str) -> None:
        """Display error in red panel."""
        self.console.print(Panel(
            Text(message, style="red"),
            title="[bold red]Error[/]",
            border_style="red",
        ))

    def show_success(self, message: str) -> None:
        """Display success in green panel."""
        self.console.print(Panel(
            Text(message, style="green"),
            title="[bold green]Success[/]",
            border_style="green",
        ))

    def show_progress(self, task: str = "Processing..."):
        """Return a Rich Progress context manager."""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
        )
        return progress

    def show_markdown(self, content: str) -> None:
        """Render markdown content."""
        md = Markdown(content)
        self.console.print(md)

    def show_match_results(self, matches: list) -> None:
        """Display track match results with confidence bars."""
        if not matches:
            self.console.print("[dim]No matching tracks found.[/dim]")
            return

        table = Table(title="Track Matches", show_lines=False)
        table.add_column("Competition", style="bold")
        table.add_column("Track", style="cyan")
        table.add_column("Confidence", justify="right")
        table.add_column("Bar", min_width=20)

        for m in matches:
            track = m.get("track_name", "Unknown")
            confidence = m.get("confidence", 0)
            competition = m.get("competition_name", "Unknown")
            style = self._score_style(confidence * 100)
            bar = self._score_bar(confidence * 100)
            table.add_row(
                competition,
                track,
                f"[{style}]{confidence:.0%}[/{style}]",
                f"[{style}]{bar}[/{style}]",
            )

        self.console.print(table)

    def show_farewell(self) -> None:
        """Display farewell message."""
        self.console.print("[dim]Goodbye![/dim]")

    @staticmethod
    def _score_style(score: float) -> str:
        """Return color style based on score value."""
        if score >= 80:
            return "green"
        if score >= 60:
            return "yellow"
        return "red"

    @staticmethod
    def _score_bar(score: float, width: int = 20) -> str:
        """Return a text-based progress bar for a score."""
        filled = int(score / 100 * width)
        empty = width - filled
        return "[" + "=" * filled + " " * empty + "]"
