"""Quality audit and optimization tools."""

import json
import logging

from aurora.quality.auditor import PlanAuditor
from aurora.quality.optimizer import PlanOptimizer

logger = logging.getLogger(__name__)


def _register_tools(registry):
    registry.register(
        "plan_audit",
        "Audit business plan quality",
        {
            "type": "object",
            "properties": {
                "plan": {"type": "object", "description": "Business plan to audit"}
            },
            "required": ["plan"]
        },
        _plan_audit_handler,
    )

    registry.register(
        "plan_optimize",
        "Optimize business plan based on audit report",
        {
            "type": "object",
            "properties": {
                "plan": {"type": "object", "description": "Business plan"},
                "audit_report": {"type": "object", "description": "Audit report from plan_audit"}
            },
            "required": ["plan", "audit_report"]
        },
        _plan_optimize_handler,
    )


def _plan_audit_handler(args):
    try:
        plan = args.get("plan")
        if not plan:
            return json.dumps({"error": "plan is required"})

        auditor = PlanAuditor()
        report = auditor.audit(plan)
        return json.dumps({"result": "Audit complete", "report": report}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _plan_optimize_handler(args):
    try:
        plan = args.get("plan")
        audit_report = args.get("audit_report")
        if not plan or not audit_report:
            return json.dumps({"error": "plan and audit_report are required"})

        optimizer = PlanOptimizer()
        optimized = optimizer.optimize(plan, audit_report)
        return json.dumps({"result": "Optimization complete", "plan": optimized}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
