"""FastAPI web API for Aurora Agent."""

import logging
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

app = FastAPI(title="Aurora Agent API", version="1.0.0")

# ---------------------------------------------------------------------------
# Lazy singletons
# ---------------------------------------------------------------------------

_agent = None
_sessions: Dict[str, object] = {}


def get_agent():
    """Return a shared AuroraAgent (lazy-init)."""
    global _agent
    if _agent is None:
        from aurora.agent import AuroraAgent
        _agent = AuroraAgent()
    return _agent


def get_session_agent(session_id: str):
    """Return an AuroraAgent bound to *session_id*, creating one if needed."""
    if session_id in _sessions:
        return _sessions[session_id]

    from aurora.agent import AuroraAgent
    agent = AuroraAgent()
    agent.start_session({})
    _sessions[agent.session_id] = agent
    return agent


# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


class PlanRequest(BaseModel):
    project_info: dict
    competition_id: str = ""


class EvaluateRequest(BaseModel):
    plan: dict
    competition_id: str = ""


class MatchRequest(BaseModel):
    project_info: dict
    competition_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Chat with the agent. Creates a new session when *session_id* is absent."""
    try:
        if req.session_id and req.session_id in _sessions:
            agent = _sessions[req.session_id]
        elif req.session_id:
            # Attempt to resume a persisted session
            agent = get_session_agent(req.session_id)
            loaded = agent.load_session(req.session_id)
            if not loaded:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            agent = get_session_agent(None)

        result = await agent.run(req.message)
        return ChatResponse(response=result, session_id=agent.session_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Chat endpoint failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/plan/generate")
def generate_plan(req: PlanRequest):
    """Generate a complete business plan."""
    try:
        from aurora.business_plan.generator import BusinessPlanGenerator

        generator = BusinessPlanGenerator()
        comp_id = req.competition_id or "internet_plus"
        plan = generator.generate(req.project_info, competition_id=comp_id)
        return {"success": True, "plan": plan}
    except Exception as exc:
        logger.exception("Plan generation failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/plan/evaluate")
def evaluate_plan(req: EvaluateRequest):
    """Evaluate a business plan against competition criteria."""
    try:
        from aurora.evaluation.engine import EvaluationEngine

        engine = EvaluationEngine()
        comp_id = req.competition_id or "internet_plus"
        result = engine.evaluate(req.plan, competition_id=comp_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return {"success": True, "evaluation": result}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Plan evaluation failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/plan/match")
def match_tracks(req: MatchRequest):
    """Match a project to suitable competition tracks."""
    try:
        from aurora.competition.track_matcher import TrackMatcher

        matcher = TrackMatcher()
        results = matcher.match(req.project_info, competition_id=req.competition_id)
        return {"success": True, "matches": results}
    except Exception as exc:
        logger.exception("Track matching failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/tools")
def list_tools():
    """List all registered tool names."""
    agent = get_agent()
    return {"tools": agent.get_tool_list()}


@app.get("/api/sessions")
def list_sessions():
    """List all persisted sessions."""
    try:
        agent = get_agent()
        return {"sessions": agent.list_sessions()}
    except Exception as exc:
        logger.exception("List sessions failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/sessions/{session_id}/resume")
def resume_session(session_id: str):
    """Resume a previously stored session."""
    try:
        agent = get_session_agent(session_id)
        loaded = agent.load_session(session_id)
        if not loaded:
            raise HTTPException(status_code=404, detail="Session not found")
        _sessions[session_id] = agent
        return {"success": True, "session_id": session_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Resume session failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    """Delete a session and its data."""
    try:
        agent = get_agent()
        deleted = agent.memory.delete_session(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        _sessions.pop(session_id, None)
        return {"success": True, "deleted": session_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Delete session failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/health")
def health_check():
    """Health check."""
    agent = get_agent()
    return {"status": "ok", "tools_count": len(agent.get_tool_list())}


# ------------------------------------------------------------------
# Dachuang endpoints
# ------------------------------------------------------------------

@app.post("/api/dachuang/generate")
def dachuang_generate(request: dict):
    """Generate a complete Dachuang application."""
    try:
        from aurora.dachuang.generator import DachuangGenerator
        gen = DachuangGenerator()
        project_info = {k: v for k, v in request.items() if k != "project_type"}
        project_type = request.get("project_type", "innovation")
        application = gen.generate(project_info, project_type)
        return {"success": True, "application": application}
    except Exception as exc:
        logger.exception("Dachuang generate failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/dachuang/evaluate")
def dachuang_evaluate(request: dict):
    """Evaluate a Dachuang application."""
    try:
        from aurora.dachuang.evaluator import DachuangEvaluator
        evl = DachuangEvaluator()
        result = evl.evaluate(
            request.get("project_info", {}),
            request.get("application", {}),
            request.get("project_type", "innovation"),
        )
        return {"success": True, "evaluation": result}
    except Exception as exc:
        logger.exception("Dachuang evaluate failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/dachuang/export")
def dachuang_export(request: dict):
    """Export a Dachuang application to DOCX or PDF."""
    try:
        from aurora.dachuang.exporter import DachuangDocxExporter, DachuangPDFExporter
        application = request.get("application")
        fmt = request.get("format", "docx")
        filepath = request.get("filepath")

        if not application or not filepath:
            raise HTTPException(status_code=400, detail="Missing application or filepath")

        if fmt == "pdf":
            exporter = DachuangPDFExporter()
        else:
            exporter = DachuangDocxExporter()

        result = exporter.export(application, filepath)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Dachuang export failed")
        raise HTTPException(status_code=500, detail=str(exc))
