"""Tests for the FastAPI web API."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_agent():
    """Build a lightweight mock that satisfies the API surface."""
    agent = MagicMock()
    agent.session_id = "test-session-001"
    agent.run = AsyncMock(return_value="Mocked LLM response")
    agent.start_session = MagicMock(return_value="test-session-001")
    agent.load_session = MagicMock(return_value=True)
    agent.list_sessions = MagicMock(return_value=[])
    agent.get_tool_list = MagicMock(return_value=[
        "search_competition",
        "generate_business_plan",
        "evaluate_project",
    ])
    agent.memory = MagicMock()
    agent.memory.delete_session = MagicMock(return_value=True)
    return agent


# Patch get_agent / get_session_agent at import level so every endpoint uses
# the mock without touching real config or network.
@pytest.fixture(autouse=True)
def _patch_agent_functions():
    mock_agent = _make_mock_agent()

    with patch("aurora.web.app.get_agent", return_value=mock_agent), \
         patch("aurora.web.app.get_session_agent", return_value=mock_agent):
        yield mock_agent


@pytest.fixture()
def client():
    from aurora.web.app import app
    # Reset in-memory session store for each test
    from aurora.web import app as _app_module  # noqa: F811
    _app_module._sessions.clear()
    return TestClient(app)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class TestHealthEndpoint:

    def test_health_returns_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert isinstance(data["tools_count"], int)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

class TestToolsEndpoint:

    def test_list_tools(self, client):
        resp = client.get("/api/tools")
        assert resp.status_code == 200
        data = resp.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)
        assert len(data["tools"]) > 0


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

class TestSessionsEndpoint:

    def test_list_sessions(self, client, _patch_agent_functions):
        resp = client.get("/api/sessions")
        assert resp.status_code == 200
        data = resp.json()
        assert "sessions" in data

    def test_delete_session(self, client, _patch_agent_functions):
        resp = client.delete("/api/sessions/nonexistent-session")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    def test_resume_session(self, client, _patch_agent_functions):
        resp = client.post("/api/sessions/test-session-001/resume")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    def test_resume_missing_session(self, client, _patch_agent_functions):
        _patch_agent_functions.load_session = MagicMock(return_value=False)
        resp = client.post("/api/sessions/missing-session/resume")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

class TestChatEndpoint:

    def test_chat_creates_session(self, client, _patch_agent_functions):
        resp = client.post("/api/chat", json={"message": "Hello"})
        assert resp.status_code == 200
        data = resp.json()
        assert "response" in data
        assert "session_id" in data
        assert data["response"] == "Mocked LLM response"

    def test_chat_with_existing_session(self, client, _patch_agent_functions):
        resp = client.post("/api/chat", json={
            "message": "Continue",
            "session_id": "test-session-001",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == "test-session-001"


# ---------------------------------------------------------------------------
# Plan generation
# ---------------------------------------------------------------------------

class TestPlanGenerateEndpoint:

    def test_generate_plan(self, client):
        mock_plan = {
            "metadata": {"competition": "test", "track": "", "generated_at": "2026-01-01"},
            "sections": {},
        }
        with patch("aurora.business_plan.generator.BusinessPlanGenerator") as MockGen:
            MockGen.return_value.generate.return_value = mock_plan
            resp = client.post("/api/plan/generate", json={
                "project_info": {"technology": "AI", "problem": "efficiency"},
                "competition_id": "internet_plus",
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "plan" in data


# ---------------------------------------------------------------------------
# Plan evaluation
# ---------------------------------------------------------------------------

class TestPlanEvaluateEndpoint:

    def test_evaluate_plan(self, client):
        mock_eval = {
            "competition": "test",
            "dimensions": [],
            "overall_score": 75.0,
            "feedback": [],
            "suggestions": [],
        }
        with patch("aurora.evaluation.engine.EvaluationEngine") as MockEngine:
            MockEngine.return_value.evaluate.return_value = mock_eval
            resp = client.post("/api/plan/evaluate", json={
                "plan": {"technology": "AI"},
                "competition_id": "internet_plus",
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "evaluation" in data


# ---------------------------------------------------------------------------
# Track matching (uses TrackMatcher directly, no LLM)
# ---------------------------------------------------------------------------

class TestMatchEndpoint:

    def test_match_tracks(self, client):
        mock_matches = [
            {
                "competition_id": "internet_plus",
                "competition_name": "internet_plus",
                "track_name": "Test Track",
                "track_description": "desc",
                "confidence": 0.85,
                "reasons": ["reason 1"],
            }
        ]
        with patch("aurora.competition.track_matcher.TrackMatcher") as MockMatcher:
            MockMatcher.return_value.match.return_value = mock_matches
            resp = client.post("/api/plan/match", json={
                "project_info": {"technology": "AI"},
                "competition_id": "internet_plus",
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["matches"]) > 0

    def test_match_no_competition(self, client):
        with patch("aurora.competition.track_matcher.TrackMatcher") as MockMatcher:
            MockMatcher.return_value.match.return_value = []
            resp = client.post("/api/plan/match", json={
                "project_info": {"technology": "AI"},
            })
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Invalid requests
# ---------------------------------------------------------------------------

class TestInvalidRequests:

    def test_chat_missing_body(self, client):
        resp = client.post("/api/chat")
        assert resp.status_code == 422

    def test_chat_empty_message(self, client):
        resp = client.post("/api/chat", json={"message": ""})
        # Empty string passes pydantic validation; the agent processes it.
        # The endpoint should still return 200 with the mocked response.
        assert resp.status_code == 200

    def test_generate_missing_project_info(self, client):
        resp = client.post("/api/plan/generate", json={"competition_id": "x"})
        assert resp.status_code == 422

    def test_evaluate_missing_plan(self, client):
        resp = client.post("/api/plan/evaluate", json={"competition_id": "x"})
        assert resp.status_code == 422

    def test_match_missing_project_info(self, client):
        resp = client.post("/api/plan/match", json={})
        assert resp.status_code == 422
