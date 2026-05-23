"""Task decomposer for AuroraAgent's swarm system."""

from typing import Dict, List


class TaskDecomposer:
    """Decompose complex tasks into smaller subtasks."""

    def decompose(self, task: str) -> List[Dict[str, str]]:
        """Decompose a task into smaller subtasks."""
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
