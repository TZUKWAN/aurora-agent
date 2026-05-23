"""竞品分析工具."""

from typing import Dict, List
import json


class CompetitorAnalyzer:
    """竞品分析工具."""

    def __init__(self):
        self.competitors = []

    def add_competitor(self, name: str, info: Dict):
        self.competitors.append({"name": name, **info})

    def compare_features(self, features: List[str]) -> Dict:
        result = {"features": features, "comparison": []}
        for comp in self.competitors:
            row = {"name": comp["name"]}
            for f in features:
                row[f] = comp.get(f, "-")
            result["comparison"].append(row)
        return result

    def differentiation_analysis(self) -> Dict:
        if len(self.competitors) < 2:
            return {"error": "至少需要2个竞品才能进行差异化分析"}

        our_strengths = []
        our_weaknesses = []

        # 简单分析：假设第一个是自己的产品
        us = self.competitors[0]
        others = self.competitors[1:]

        for key in ["price", "features", "technology", "market_share"]:
            our_val = us.get(key, 0)
            other_vals = [c.get(key, 0) for c in others]
            avg_other = sum(other_vals) / len(other_vals) if other_vals else 0

            if isinstance(our_val, (int, float)) and isinstance(avg_other, (int, float)):
                if our_val > avg_other:
                    our_strengths.append(f"{key}: 高于竞品平均水平")
                else:
                    our_weaknesses.append(f"{key}: 低于竞品平均水平")

        return {
            "our_product": us["name"],
            "strengths": our_strengths,
            "weaknesses": our_weaknesses,
        }

    def generate_report(self) -> str:
        lines = ["# 竞品分析报告", ""]
        for comp in self.competitors:
            lines.append(f"## {comp['name']}")
            for k, v in comp.items():
                if k != "name":
                    lines.append(f"- {k}: {v}")
            lines.append("")
        return "\n".join(lines)

    def export_to_json(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.competitors, f, ensure_ascii=False, indent=2)
