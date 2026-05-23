"""SWOT分析增强工具."""

from typing import Dict, List
import json


class SWOTAnalyzer:
    """SWOT分析工具，支持TOWS矩阵."""

    def __init__(self):
        self.strengths = []
        self.weaknesses = []
        self.opportunities = []
        self.threats = []

    def set_factors(self, strengths: List[str], weaknesses: List[str], opportunities: List[str], threats: List[str]):
        self.strengths = strengths
        self.weaknesses = weaknesses
        self.opportunities = opportunities
        self.threats = threats

    def analyze(self, project_info: Dict) -> Dict:
        if not any([self.strengths, self.weaknesses, self.opportunities, self.threats]):
            # 自动生成
            tech = project_info.get("technology", "")
            team = project_info.get("team_background", "")
            market = project_info.get("target_market", "")

            self.strengths = [
                f"技术创新：采用{tech}，具备技术壁垒",
                "团队优势：多学科背景，协作能力强",
            ]
            self.weaknesses = [
                "品牌知名度有限",
                "资金实力相对薄弱",
            ]
            self.opportunities = [
                f"{market}市场需求持续增长",
                "国家政策大力支持创新创业",
            ]
            self.threats = [
                "市场竞争激烈，头部企业优势明显",
                "技术迭代快，需要持续投入研发",
            ]

        return {
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "opportunities": self.opportunities,
            "threats": self.threats,
        }

    def generate_tows(self) -> Dict:
        return {
            "SO_strategy": [f"利用{s}抓住{o}" for s in self.strengths[:2] for o in self.opportunities[:2]],
            "WO_strategy": [f"通过{o}弥补{w}" for w in self.weaknesses[:2] for o in self.opportunities[:2]],
            "ST_strategy": [f"利用{s}应对{t}" for s in self.strengths[:2] for t in self.threats[:2]],
            "WT_strategy": [f"规避{t}，改善{w}" for w in self.weaknesses[:2] for t in self.threats[:2]],
        }

    def export_to_json(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.analyze({}), f, ensure_ascii=False, indent=2)
