"""Defense simulation tools for AuroraAgent."""

import json
import logging

from aurora.defense.simulator import DefenseSimulator

logger = logging.getLogger(__name__)


def _register_tools(registry):
    """Register defense simulation tools to the registry."""
    registry.register(
        "defense_generate_questions",
        "Generate defense questions based on business plan content and competition type",
        {
            "type": "object",
            "properties": {
                "plan": {"type": "object", "description": "Current business plan"},
                "competition_id": {"type": "string", "description": "Target competition ID"},
                "num_questions": {"type": "integer", "description": "Number of questions to generate"},
            },
            "required": ["plan"],
        },
        _defense_generate_questions_handler,
    )

    registry.register(
        "defense_simulate",
        "Run a full defense simulation with questions, rubric, and tips",
        {
            "type": "object",
            "properties": {
                "plan": {"type": "object", "description": "Current business plan"},
                "competition_id": {"type": "string", "description": "Target competition ID"},
            },
            "required": ["plan"],
        },
        _defense_simulate_handler,
    )

    registry.register(
        "defense_score_answer",
        "Score a defense answer using keyword matching against plan content",
        {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "The defense question"},
                "answer": {"type": "string", "description": "The answer to score"},
                "plan": {"type": "object", "description": "Current business plan"},
            },
            "required": ["question", "answer", "plan"],
        },
        _defense_score_answer_handler,
    )

    registry.register(
        "defense_tips",
        "Get defense preparation tips based on competition type",
        {
            "type": "object",
            "properties": {
                "competition_id": {"type": "string", "description": "Target competition ID"},
            },
            "required": [],
        },
        _defense_tips_handler,
    )


def _defense_generate_questions_handler(args):
    """Generate defense questions."""
    try:
        simulator = DefenseSimulator()
        plan = args.get("plan", {})
        competition_id = args.get("competition_id", "")
        num_questions = args.get("num_questions", 10)
        result = simulator.generate_questions(plan, competition_id, num_questions)
        return json.dumps({"result": "Questions generated", "data": result}, ensure_ascii=False)
    except Exception as e:
        logger.error("Defense question generation failed: %s", e)
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _defense_simulate_handler(args):
    """Run defense simulation."""
    try:
        simulator = DefenseSimulator()
        plan = args.get("plan", {})
        competition_id = args.get("competition_id", "")
        result = simulator.simulate_defense(plan, competition_id)
        return json.dumps({"result": "Defense simulation complete", "data": result}, ensure_ascii=False)
    except Exception as e:
        logger.error("Defense simulation failed: %s", e)
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _defense_score_answer_handler(args):
    """Score a defense answer."""
    try:
        simulator = DefenseSimulator()
        question = args.get("question", "")
        answer = args.get("answer", "")
        plan = args.get("plan", {})
        result = simulator.score_answer(question, answer, plan)
        return json.dumps({"result": "Answer scored", "data": result}, ensure_ascii=False)
    except Exception as e:
        logger.error("Defense answer scoring failed: %s", e)
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _defense_tips_handler(args):
    """Get defense tips."""
    try:
        simulator = DefenseSimulator()
        competition_id = args.get("competition_id", "")
        tips = simulator.get_defense_tips(competition_id)
        return json.dumps({"result": "Defense tips", "tips": tips}, ensure_ascii=False)
    except Exception as e:
        logger.error("Defense tips retrieval failed: %s", e)
        return json.dumps({"error": str(e)}, ensure_ascii=False)
