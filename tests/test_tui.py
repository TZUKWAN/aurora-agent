"""Tests for aurora.tui module - TUI display and interactive mode."""

import io
from unittest.mock import MagicMock, patch

from rich.console import Console

from aurora.tui.display import TUIDisplay
from aurora.tui.interactive import InteractiveTUI


def _make_display():
    """Create a TUIDisplay with a captured Console for testing."""
    d = TUIDisplay()
    buf = io.StringIO()
    d.console = Console(file=buf, force_terminal=True, width=80)
    return d, buf


# Sample data fixtures

SAMPLE_TOOLS = ["tool_a", "tool_b", "tool_c"]

SAMPLE_PLAN = {
    "metadata": {"project_name": "Test"},
    "sections": {
        "executive_summary": {"title": "Summary", "content": "Test content"},
        "market_analysis": {"title": "Market", "content": "Market data"},
    },
}

SAMPLE_EVALUATION = {
    "overall_score": 85.5,
    "dimensions": [
        {"name": "Innovation", "score": 90, "weight": 0.3},
        {"name": "Business", "score": 80, "weight": 0.3},
    ],
}

SAMPLE_MATCHES = [
    {"track_name": "AI Track", "confidence": 0.85, "competition_name": "Test Comp"},
    {"track_name": "Tech Track", "confidence": 0.65, "competition_name": "Other Comp"},
]

SAMPLE_SESSIONS = [
    {"session_id": "sess-001", "project_name": "Alpha Project", "last_updated": "2025-05-20T10:30:00"},
    {"session_id": "sess-002", "project_name": "Beta Project", "last_updated": "2025-05-21T14:45:00"},
]


# --- TUIDisplay creation ---


class TestTUIDisplayCreation:
    def test_display_creates_with_console(self):
        d = TUIDisplay()
        assert d.console is not None

    def test_display_console_is_rich_console(self):
        d = TUIDisplay()
        assert isinstance(d.console, Console)


# --- show_banner ---


class TestShowBanner:
    def test_banner_outputs_text(self):
        d, buf = _make_display()
        d.show_banner()
        output = buf.getvalue()
        assert "AuroraAgent" in output

    def test_banner_contains_version(self):
        d, buf = _make_display()
        d.show_banner()
        output = buf.getvalue()
        assert "v0.1.0" in output


# --- show_tool_list ---


class TestShowToolList:
    def test_tool_list_with_names(self):
        d, buf = _make_display()
        d.show_tool_list(SAMPLE_TOOLS)
        output = buf.getvalue()
        assert "tool_a" in output
        assert "tool_b" in output
        assert "tool_c" in output

    def test_tool_list_empty(self):
        d, buf = _make_display()
        d.show_tool_list([])
        output = buf.getvalue()
        assert "Registered Tools" in output

    def test_tool_list_with_dicts(self):
        d, buf = _make_display()
        d.show_tool_list([{"name": "search"}, {"name": "generate"}])
        output = buf.getvalue()
        assert "search" in output
        assert "generate" in output


# --- show_plan ---


class TestShowPlan:
    def test_plan_displays_project_name(self):
        d, buf = _make_display()
        d.show_plan(SAMPLE_PLAN)
        output = buf.getvalue()
        assert "Test" in output

    def test_plan_displays_sections(self):
        d, buf = _make_display()
        d.show_plan(SAMPLE_PLAN)
        output = buf.getvalue()
        assert "Summary" in output
        assert "Market" in output

    def test_plan_displays_content(self):
        d, buf = _make_display()
        d.show_plan(SAMPLE_PLAN)
        output = buf.getvalue()
        assert "Test content" in output
        assert "Market data" in output


# --- show_evaluation ---


class TestShowEvaluation:
    def test_evaluation_shows_overall_score(self):
        d, buf = _make_display()
        d.show_evaluation(SAMPLE_EVALUATION)
        output = buf.getvalue()
        assert "85.5" in output

    def test_evaluation_shows_dimensions(self):
        d, buf = _make_display()
        d.show_evaluation(SAMPLE_EVALUATION)
        output = buf.getvalue()
        assert "Innovation" in output
        assert "Business" in output

    def test_evaluation_shows_scores(self):
        d, buf = _make_display()
        d.show_evaluation(SAMPLE_EVALUATION)
        output = buf.getvalue()
        assert "90" in output
        assert "80" in output

    def test_evaluation_empty_dimensions(self):
        d, buf = _make_display()
        d.show_evaluation({"overall_score": 50, "dimensions": []})
        output = buf.getvalue()
        assert "50.0" in output


# --- show_session_list ---


class TestShowSessionList:
    def test_session_list_displays_sessions(self):
        d, buf = _make_display()
        d.show_session_list(SAMPLE_SESSIONS)
        output = buf.getvalue()
        assert "sess-001" in output
        assert "sess-002" in output

    def test_session_list_empty(self):
        d, buf = _make_display()
        d.show_session_list([])
        output = buf.getvalue()
        assert "No sessions found" in output


# --- show_error / show_success ---


class TestShowMessages:
    def test_error_displays_message(self):
        d, buf = _make_display()
        d.show_error("Something went wrong")
        output = buf.getvalue()
        assert "Something went wrong" in output

    def test_error_has_error_title(self):
        d, buf = _make_display()
        d.show_error("fail")
        output = buf.getvalue()
        assert "Error" in output

    def test_success_displays_message(self):
        d, buf = _make_display()
        d.show_success("Operation completed")
        output = buf.getvalue()
        assert "Operation completed" in output

    def test_success_has_success_title(self):
        d, buf = _make_display()
        d.show_success("ok")
        output = buf.getvalue()
        assert "Success" in output


# --- show_markdown ---


class TestShowMarkdown:
    def test_markdown_renders(self):
        d, buf = _make_display()
        d.show_markdown("# Hello\n\nThis is **bold** text.")
        output = buf.getvalue()
        assert "Hello" in output
        assert "bold" in output


# --- show_match_results ---


class TestShowMatchResults:
    def test_match_results_displays_tracks(self):
        d, buf = _make_display()
        d.show_match_results(SAMPLE_MATCHES)
        output = buf.getvalue()
        assert "AI Track" in output
        assert "Tech Track" in output

    def test_match_results_displays_competitions(self):
        d, buf = _make_display()
        d.show_match_results(SAMPLE_MATCHES)
        output = buf.getvalue()
        assert "Test Comp" in output
        assert "Other Comp" in output

    def test_match_results_empty(self):
        d, buf = _make_display()
        d.show_match_results([])
        output = buf.getvalue()
        assert "No matching tracks found" in output


# --- show_farewell ---


class TestShowFarewell:
    def test_farewell_outputs_message(self):
        d, buf = _make_display()
        d.show_farewell()
        output = buf.getvalue()
        assert "Goodbye" in output


# --- _score_style / _score_bar helpers ---


class TestScoreHelpers:
    def test_score_style_green(self):
        assert TUIDisplay._score_style(85) == "green"

    def test_score_style_yellow(self):
        assert TUIDisplay._score_style(65) == "yellow"

    def test_score_style_red(self):
        assert TUIDisplay._score_style(40) == "red"

    def test_score_bar_length(self):
        bar = TUIDisplay._score_bar(50)
        assert len(bar) == 22  # 20 + 2 brackets

    def test_score_bar_filled(self):
        bar = TUIDisplay._score_bar(100)
        assert bar.count("=") == 20

    def test_score_bar_empty(self):
        bar = TUIDisplay._score_bar(0)
        assert bar.count("=") == 0


# --- InteractiveTUI ---


class TestInteractiveTUICreation:
    def test_interactive_creates(self):
        tui = InteractiveTUI()
        assert tui.display is not None
        assert tui.agent is None
        assert tui._running is False

    def test_interactive_with_agent(self):
        mock_agent = MagicMock()
        tui = InteractiveTUI(agent=mock_agent)
        assert tui.agent is mock_agent


class TestInteractiveTUICommands:
    def _make_tui(self):
        tui = InteractiveTUI()
        buf = io.StringIO()
        tui.display.console = Console(file=buf, force_terminal=True, width=80)
        return tui, buf

    def test_exit_command_sets_running_false(self):
        tui, buf = self._make_tui()
        tui._running = True
        tui._handle_input("/exit")
        assert tui._running is False

    def test_quit_command_sets_running_false(self):
        tui, buf = self._make_tui()
        tui._running = True
        tui._handle_input("/quit")
        assert tui._running is False

    def test_q_command_sets_running_false(self):
        tui, buf = self._make_tui()
        tui._running = True
        tui._handle_input("/q")
        assert tui._running is False

    def test_exit_outputs_farewell(self):
        tui, buf = self._make_tui()
        tui._handle_input("/exit")
        output = buf.getvalue()
        assert "Goodbye" in output

    def test_help_command_outputs_help(self):
        tui, buf = self._make_tui()
        tui._handle_input("/help")
        output = buf.getvalue()
        assert "/tools" in output
        assert "/help" in output
        assert "/exit" in output

    def test_unknown_command_shows_error(self):
        tui, buf = self._make_tui()
        tui._handle_input("/unknown")
        output = buf.getvalue()
        assert "Unknown command" in output

    def test_tools_command_without_agent_shows_error(self):
        tui, buf = self._make_tui()
        tui._handle_input("/tools")
        output = buf.getvalue()
        assert "Agent not initialized" in output

    def test_tools_command_with_agent(self):
        mock_agent = MagicMock()
        mock_agent.get_tool_list.return_value = ["search", "generate"]
        tui, buf = self._make_tui()
        tui.agent = mock_agent
        tui._handle_input("/tools")
        output = buf.getvalue()
        assert "search" in output
        assert "generate" in output
        mock_agent.get_tool_list.assert_called_once()

    def test_chat_without_agent_shows_error(self):
        tui, buf = self._make_tui()
        tui._handle_input("hello")
        output = buf.getvalue()
        assert "Agent not initialized" in output

    def test_chat_with_agent_calls_run(self):
        mock_agent = MagicMock()
        mock_agent.run = MagicMock(return_value="mock response")

        tui, buf = self._make_tui()
        tui.agent = mock_agent

        with patch("asyncio.run", return_value="mock response"):
            tui._handle_input("hello")

        output = buf.getvalue()
        assert "mock response" in output
