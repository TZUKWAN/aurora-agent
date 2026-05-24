"""Editor tools for business plan."""

import json
import logging

from aurora.business_plan.editor import PlanEditor

logger = logging.getLogger(__name__)


def _register_tools(registry):
    registry.register(
        "plan_edit_section",
        "Edit a section of the business plan",
        {
            "type": "object",
            "properties": {
                "plan": {"type": "object", "description": "Current plan"},
                "section_id": {"type": "string"},
                "new_content": {"type": "string"},
            },
            "required": ["plan", "section_id", "new_content"]
        },
        _plan_edit_handler,
    )

    registry.register(
        "plan_validate",
        "Validate plan completeness",
        {
            "type": "object",
            "properties": {
                "plan": {"type": "object"}
            },
            "required": ["plan"]
        },
        _plan_validate_handler,
    )

    registry.register(
        "plan_word_count",
        "Count words in each section",
        {
            "type": "object",
            "properties": {
                "plan": {"type": "object"}
            },
            "required": ["plan"]
        },
        _plan_word_count_handler,
    )


def _plan_edit_handler(args):
    try:
        plan = args.get("plan", {})
        section_id = args.get("section_id", "")
        new_content = args.get("new_content", "")
        editor = PlanEditor(plan)
        if editor.update_section(section_id, new_content):
            return json.dumps({"result": "Section updated", "plan": editor.to_dict()}, ensure_ascii=False)
        return json.dumps({"error": f"Section {section_id} not found"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _plan_validate_handler(args):
    try:
        plan = args.get("plan", {})
        editor = PlanEditor(plan)
        result = editor.validate_plan()
        return json.dumps({"result": "Validation complete", "validation": result}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _plan_word_count_handler(args):
    try:
        plan = args.get("plan", {})
        counts = {}
        for sid, sec in plan.get("sections", {}).items():
            content = sec.get("content", "") if isinstance(sec, dict) else str(sec)
            counts[sid] = {"chars": len(content), "words": len(content.split())}
        return json.dumps({"result": "Word count", "counts": counts}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})
