"""工作分解结构."""

from typing import Dict, List
import json


class WBSDecomposer:
    """工作分解结构分解器."""

    TEMPLATES = {
        "innovation": [
            {"phase": "立项准备", "tasks": ["选题确定", "文献调研", "可行性分析", "申报书撰写"]},
            {"phase": "研究实施", "tasks": ["需求分析", "方案设计", "原型开发", "实验验证"]},
            {"phase": "成果总结", "tasks": ["数据分析", "论文撰写", "专利申请", "结题报告"]},
        ],
        "entrepreneurship": [
            {"phase": "市场调研", "tasks": ["行业分析", "竞品调研", "用户访谈", "需求验证"]},
            {"phase": "商业规划", "tasks": ["商业模式设计", "财务预测", "团队组建", "商业计划书撰写"]},
            {"phase": "实践运营", "tasks": ["产品开发", "市场推广", "用户获取", "融资路演"]},
        ],
    }

    def decompose_project(self, project_type: str) -> Dict:
        template = self.TEMPLATES.get(project_type, self.TEMPLATES["innovation"])
        return {"project_type": project_type, "phases": template}

    def generate_checklist(self, project_type: str) -> List[str]:
        wbs = self.decompose_project(project_type)
        checklist = []
        for phase in wbs["phases"]:
            for task in phase["tasks"]:
                checklist.append(f"[{phase['phase']}] {task}")
        return checklist

    def export_wbs(self, data: Dict, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
