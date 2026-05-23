"""论文大纲生成器."""

from typing import Dict, List


class PaperOutlineGenerator:
    """学术论文大纲生成器."""

    def generate_outline(self, topic: str, paper_type: str = "research") -> Dict:
        if paper_type == "research":
            return {
                "title": topic,
                "abstract": "摘要：研究背景、方法、结果、结论（300字）",
                "keywords": ["关键词1", "关键词2", "关键词3"],
                "sections": [
                    {"title": "1 引言", "content": "研究背景、意义、目标"},
                    {"title": "2 相关工作", "content": "国内外研究现状综述"},
                    {"title": "3 方法", "content": "提出的方法/模型/算法"},
                    {"title": "4 实验", "content": "实验设置、数据集、评价指标、结果分析"},
                    {"title": "5 结论", "content": "工作总结、贡献、局限、未来方向"},
                    {"title": "参考文献", "content": "引用的文献列表"},
                ],
            }
        else:
            return {
                "title": topic,
                "sections": [
                    {"title": "1 绪论", "content": "研究背景与意义"},
                    {"title": "2 理论基础", "content": "相关理论和概念"},
                    {"title": "3 研究设计", "content": "研究方法和技术路线"},
                    {"title": "4 结果分析", "content": "数据分析和讨论"},
                    {"title": "5 结论", "content": "研究结论和建议"},
                ],
            }

    def generate_abstract(self, outline: Dict) -> str:
        return f"""【摘要】本文针对{outline['title']}展开研究。首先分析了研究背景和现状，
然后提出了创新性的解决方案，通过实验验证了方法的有效性。实验结果表明，
所提方法在关键指标上取得了显著改进。本文为相关领域的研究和实践提供了有价值的参考。

【关键词】{', '.join(outline.get('keywords', ['关键词1', '关键词2']))}"""

    def generate_keywords(self, topic: str) -> List[str]:
        words = topic.split()
        return [words[0] if words else "关键词"] + ["创新", "应用"]
