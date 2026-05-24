"""Loop management tools for AuroraAgent."""

import json
import logging

from aurora.loop import LoopManager

logger = logging.getLogger(__name__)


def _register_tools(registry, loop_manager=None):
    """Register loop management tools.

    Args:
        registry: ToolRegistry instance.
        loop_manager: Optional LoopManager instance. When provided,
            tool handlers will delegate to it. When None, handlers
            return an error indicating the loop system is not initialized.
    """
    lm = loop_manager

    def _loop_start_handler(args):
        if lm is None:
            return json.dumps({"error": "Loop manager not initialized"})
        action_prompt = args.get("action_prompt", "")
        interval_seconds = args.get("interval_seconds", 300)
        max_iterations = args.get("max_iterations", 0)
        loop_id = lm.start(
            action_prompt=action_prompt,
            interval_seconds=interval_seconds,
            max_iterations=max_iterations,
        )
        return json.dumps({
            "result": f"Loop '{loop_id}' started",
            "data": {"loop_id": loop_id, "interval_seconds": interval_seconds, "max_iterations": max_iterations},
        })

    def _loop_stop_handler(args):
        if lm is None:
            return json.dumps({"error": "Loop manager not initialized"})
        loop_id = args.get("loop_id", "")
        success = lm.stop(loop_id)
        if success:
            return json.dumps({"result": f"Loop '{loop_id}' stopped"})
        return json.dumps({"error": f"Loop '{loop_id}' not found"})

    def _loop_pause_handler(args):
        if lm is None:
            return json.dumps({"error": "Loop manager not initialized"})
        loop_id = args.get("loop_id", "")
        success = lm.pause(loop_id)
        if success:
            return json.dumps({"result": f"Loop '{loop_id}' paused"})
        return json.dumps({"error": f"Loop '{loop_id}' not found or not running"})

    def _loop_resume_handler(args):
        if lm is None:
            return json.dumps({"error": "Loop manager not initialized"})
        loop_id = args.get("loop_id", "")
        success = lm.resume(loop_id)
        if success:
            return json.dumps({"result": f"Loop '{loop_id}' resumed"})
        return json.dumps({"error": f"Loop '{loop_id}' not found or not paused"})

    def _loop_list_handler(args):
        if lm is None:
            return json.dumps({"error": "Loop manager not initialized"})
        loops = lm.list_loops()
        return json.dumps({"result": f"Found {len(loops)} loop(s)", "data": loops})

    registry.register(
        "loop_start",
        "启动一个自主循环，定期执行指定任务",
        {
            "type": "object",
            "properties": {
                "action_prompt": {"type": "string", "description": "每次循环执行的提示词"},
                "interval_seconds": {"type": "integer", "description": "循环间隔（秒），最小10秒，默认300"},
                "max_iterations": {"type": "integer", "description": "最大迭代次数，0表示无限"},
            },
            "required": ["action_prompt"],
        },
        _loop_start_handler,
    )

    registry.register(
        "loop_stop",
        "停止一个运行中的循环",
        {
            "type": "object",
            "properties": {
                "loop_id": {"type": "string", "description": "循环ID"},
            },
            "required": ["loop_id"],
        },
        _loop_stop_handler,
    )

    registry.register(
        "loop_pause",
        "暂停一个运行中的循环",
        {
            "type": "object",
            "properties": {
                "loop_id": {"type": "string", "description": "循环ID"},
            },
            "required": ["loop_id"],
        },
        _loop_pause_handler,
    )

    registry.register(
        "loop_resume",
        "恢复一个暂停的循环",
        {
            "type": "object",
            "properties": {
                "loop_id": {"type": "string", "description": "循环ID"},
            },
            "required": ["loop_id"],
        },
        _loop_resume_handler,
    )

    registry.register(
        "loop_list",
        "列出所有循环及其状态",
        {"type": "object", "properties": {}, "required": []},
        _loop_list_handler,
    )
