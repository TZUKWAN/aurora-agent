"""Swarm orchestrator for AuroraAgent."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from aurora.swarm.bus import SwarmBus
from aurora.swarm.decomposer import TaskDecomposer
from aurora.swarm.roles import RoleTemplate, RoleTemplateBank

logger = logging.getLogger(__name__)


class FilteredToolRegistry:
    """Tool registry that filters tools based on role permissions."""

    def __init__(self, base_registry, allowed_tools: List[str]):
        self._base_registry = base_registry
        self._allowed_tools = set(allowed_tools)

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Return schemas for allowed tools only."""
        all_schemas = self._base_registry.get_schemas()
        return [
            s for s in all_schemas
            if s["function"]["name"] in self._allowed_tools
        ]

    def dispatch(self, name: str, args: Dict[str, Any]) -> str:
        """Dispatch tool call."""
        if name not in self._allowed_tools:
            import json
            return json.dumps({"error": f"Tool '{name}' not allowed for this role"}, ensure_ascii=False)
        return self._base_registry.dispatch(name, args)


class SwarmOrchestrator:
    """Main orchestrator for the swarm system."""

    def __init__(
        self,
        run_fn,
        llm_call_fn,
        tools_registry=None,
        hooks=None,
        max_workers: int = 3,
    ):
        self._run_fn = run_fn
        self._llm_call_fn = llm_call_fn
        self._tools_registry = tools_registry
        self._hooks = hooks
        self._max_workers = max_workers
        self._role_bank = RoleTemplateBank()
        self._bus = SwarmBus()
        self._decomposer = TaskDecomposer()

    async def run(self, task: str) -> str:
        """Run the swarm on a task."""
        if self._hooks:
            self._hooks.emit("swarm.start", {"task": task})

        try:
            plan = await self._analyze_and_plan(task)
            logger.info(f"Swarm plan: {plan}")

            results = await self._execute_plan(plan)
            final_result = await self._synthesize_results(results)

            if self._hooks:
                self._hooks.emit("swarm.complete", {"task": task, "result": final_result})

            return final_result

        except Exception as e:
            logger.exception("Swarm execution failed")
            if self._hooks:
                self._hooks.emit("swarm.error", {"task": task, "error": str(e)})
            return f"任务执行过程中出现错误: {e}"

    async def _analyze_and_plan(self, task: str) -> Dict:
        """Analyze task and create execution plan."""
        roles = self._role_bank.recommend_roles(task)
        decomposed_tasks = self._decomposer.decompose(task)

        return {
            "original_task": task,
            "selected_roles": [r.role_id for r in roles],
            "tasks": decomposed_tasks,
        }

    async def _execute_plan(self, plan: Dict) -> List[Dict]:
        """Execute the plan with parallel workers."""
        tasks = plan["tasks"]
        roles = [self._role_bank.get_role(r) for r in plan["selected_roles"]]

        semaphore = asyncio.Semaphore(self._max_workers)

        async def execute_task(task: Dict, role: RoleTemplate):
            async with semaphore:
                return await self._execute_with_role(task, role)

        tasks_to_execute = []
        for task in tasks:
            for role in roles:
                if any(exp in task["description"] for exp in role.expertise):
                    tasks_to_execute.append((task, role))
                    break

        if not tasks_to_execute:
            tasks_to_execute = [(tasks[0], roles[0])] if tasks and roles else []

        results = await asyncio.gather(
            *[execute_task(task, role) for task, role in tasks_to_execute]
        )

        return [r for r in results if r]

    async def _execute_with_role(self, task: Dict, role: RoleTemplate) -> Dict:
        """Execute a task with a specific role."""
        # Get tools from the agent instance
        # We need to pass tools reference during initialization instead of accessing through _run_fn
        filtered_registry = FilteredToolRegistry(
            self._tools_registry, role.allowed_tools
        )

        messages = [
            {"role": "system", "content": role.system_prompt},
            {"role": "user", "content": task["description"]},
        ]

        result = await self._llm_call_fn(
            messages,
            tools=filtered_registry.get_schemas(),
            tool_dispatch=filtered_registry.dispatch,
        )

        return {
            "role": role.role_id,
            "role_name": role.name,
            "task": task["description"],
            "result": result,
        }

    async def _synthesize_results(self, results: List[Dict]) -> str:
        """Synthesize results from all roles."""
        if not results:
            return "任务执行完成，但未获得任何结果。"

        context = "\n\n".join([
            f"【{r['role_name']}】\n{r['result']}"
            for r in results
        ])

        messages = [
            {"role": "system", "content": """
你是结果合成专家。请将以下各专家的工作成果综合整理成一份清晰、完整的报告，给用户一个统一的回复。

要求：
1. 保持专业性和条理性
2. 使用自然、友好的语言
3. 突出重点和关键结论
4. 避免技术术语
"""},
            {"role": "user", "content": f"请综合以下专家的分析结果：\n\n{context}"},
        ]

        result = await self._llm_call_fn(messages, tools=None)
        return result

    def should_trigger(self, message: str) -> bool:
        """Determine if swarm should be triggered for a message."""
        complexity = self._estimate_complexity(message)
        domain_count = self._count_domains(message)

        return complexity >= 3 or domain_count >= 2

    def _estimate_complexity(self, message: str) -> int:
        """Estimate message complexity on a scale of 1-5."""
        complexity = 1
        
        if any(phrase in message for phrase in ["帮我", "请帮我", "协助我"]):
            complexity += 1
        if any(phrase in message for phrase in ["商业计划书", "完整方案", "参赛项目"]):
            complexity += 2
        if "PPT" in message or "路演" in message or "答辩" in message:
            complexity += 1
        if "分析" in message or "评估" in message or "评审" in message:
            complexity += 1

        return min(complexity, 5)

    def _count_domains(self, message: str) -> int:
        """Count how many knowledge domains are involved."""
        domains = [
            ("竞赛", ["互联网+", "挑战杯", "竞赛", "比赛"]),
            ("商业", ["商业计划", "商业模式", "市场", "财务"]),
            ("技术", ["技术", "产品", "研发", "专利"]),
            ("写作", ["写", "撰写", "方案", "报告"]),
            ("路演", ["PPT", "路演", "答辩", "视频"]),
        ]

        count = 0
        for domain_name, keywords in domains:
            if any(kw in message for kw in keywords):
                count += 1

        return count
