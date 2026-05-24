"""Task decomposer for AuroraAgent's swarm system."""

import json
import re
from typing import Dict, List


class TaskDecomposer:
    """Decompose complex tasks into smaller subtasks.

    Supports LLM-based decomposition with automatic keyword fallback.
    """

    def __init__(self, config=None):
        """Initialize TaskDecomposer with optional LLM configuration.

        Args:
            config: Optional configuration object with a ``model`` attribute
                containing ``api_key``, ``base_url``, and ``name`` fields.
                If provided and valid, LLM-based decomposition will be
                attempted first before falling back to keyword matching.
        """
        self._config = config
        self._client = None
        if config:
            try:
                import os

                from openai import OpenAI

                api_key = config.model.api_key or os.environ.get("AURORA_API_KEY")
                base_url = config.model.base_url or os.environ.get("AURORA_BASE_URL")
                if api_key:
                    self._client = OpenAI(api_key=api_key, base_url=base_url)
                    self._model = config.model.name or os.environ.get(
                        "AURORA_MODEL", "glm-4.7-flash"
                    )
            except Exception:
                pass

    def decompose(self, task: str) -> List[Dict[str, str]]:
        """Decompose a task into smaller subtasks.

        Attempts LLM-based decomposition first when a client is available,
        then falls back to keyword-based decomposition.
        """
        if self._client:
            try:
                return self._llm_decompose(task)
            except Exception:
                pass
        return self._keyword_decompose(task)

    def _keyword_decompose(self, task: str) -> List[Dict[str, str]]:
        """Decompose a task using keyword matching."""
        self._extract_keywords(task)

        if "商业计划书" in task or "BP" in task:
            return self._decompose_business_plan(task)
        elif "PPT" in task or "路演" in task or "答辩" in task:
            return self._decompose_presentation(task)
        elif "分析" in task or "评估" in task:
            return self._decompose_analysis(task)
        elif "项目" in task or "方案" in task:
            return self._decompose_project(task)
        else:
            return self._default_decompose(task)

    def _extract_keywords(self, task: str) -> List[str]:
        """Extract relevant keywords from task."""
        keywords = []
        keyword_list = [
            "互联网+", "挑战杯", "竞赛", "商业计划书", "BP",
            "PPT", "路演", "答辩", "分析", "评估", "项目", "方案"
        ]
        for kw in keyword_list:
            if kw in task:
                keywords.append(kw)
        return keywords

    def _decompose_business_plan(self, task: str) -> List[Dict[str, str]]:
        """Decompose business plan task."""
        tasks = [
            {"id": "1", "description": "分析项目背景和市场需求"},
            {"id": "2", "description": "分析目标市场和竞争对手"},
            {"id": "3", "description": "设计商业模式和盈利模式"},
            {"id": "4", "description": "规划运营策略和发展路径"},
            {"id": "5", "description": "撰写执行摘要"},
        ]
        if "互联网+" in task:
            tasks.append({"id": "6", "description": "匹配互联网+大赛赛道并优化内容"})
        if "挑战杯" in task:
            tasks.append({"id": "6", "description": "匹配挑战杯组别并优化内容"})
        return tasks

    def _decompose_presentation(self, task: str) -> List[Dict[str, str]]:
        """Decompose presentation task."""
        tasks = [
            {"id": "1", "description": "设计PPT结构和内容大纲"},
            {"id": "2", "description": "撰写路演脚本和讲稿"},
            {"id": "3", "description": "准备常见答辩问题和回答"},
        ]
        if "视频" in task:
            tasks.append({"id": "4", "description": "规划一分钟视频内容"})
        return tasks

    def _decompose_analysis(self, task: str) -> List[Dict[str, str]]:
        """Decompose analysis task."""
        tasks = [
            {"id": "1", "description": "分析项目的创新性和技术壁垒"},
            {"id": "2", "description": "评估商业模式的可行性"},
            {"id": "3", "description": "分析团队构成和能力"},
            {"id": "4", "description": "提供优化建议和改进方向"},
        ]
        return tasks

    def _decompose_project(self, task: str) -> List[Dict[str, str]]:
        """Decompose project task."""
        tasks = [
            {"id": "1", "description": "分析项目创意和创新性"},
            {"id": "2", "description": "设计商业模式"},
            {"id": "3", "description": "规划团队组建和分工"},
            {"id": "4", "description": "制定参赛策略和时间规划"},
        ]
        return tasks

    def _default_decompose(self, task: str) -> List[Dict[str, str]]:
        """Default decomposition for unknown tasks."""
        return [
            {"id": "1", "description": task},
        ]

    def _llm_decompose(self, task: str) -> List[Dict[str, str]]:
        """Decompose a task using an LLM API call.

        Sends the task to the configured LLM model and parses the JSON
        response into a list of subtask dictionaries.

        Raises:
            ValueError: If the LLM response cannot be parsed as valid
                subtask list.
        """
        prompt = f"""将以下任务分解为具体的子任务。每个子任务需要简明扼要的描述。

任务：{task}

请按以下JSON格式返回，不要其他文字：
[{{"id": "1", "description": "子任务描述"}}, ...]"""

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": "你是任务分解专家。将复杂任务分解为可执行的子任务。只返回JSON。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        content = response.choices[0].message.content or ""
        if not content.strip():
            rc = getattr(response.choices[0].message, "reasoning_content", None)
            if rc and rc.strip():
                content = rc

        # Try to find JSON array in the response
        match = re.search(r"\[.*\]", content, re.DOTALL)
        if match:
            tasks = json.loads(match.group())
            if isinstance(tasks, list) and all(
                "id" in t and "description" in t for t in tasks
            ):
                return tasks

        raise ValueError("Failed to parse LLM decomposition")

    def estimate_task_count(self, task: str) -> int:
        """Estimate the number of subtasks a task will decompose into.

        Args:
            task: The task description to estimate.

        Returns:
            Estimated number of subtasks.
        """
        if any(kw in task for kw in ("完整", "全部", "商业计划书")):
            return 7
        if any(kw in task for kw in ("PPT", "路演")):
            return 4
        if any(kw in task for kw in ("分析", "评估")):
            return 4
        return 2
