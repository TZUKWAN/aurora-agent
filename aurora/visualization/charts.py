"""图表引擎."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List


class ChartEngine:
    """数据可视化图表引擎."""

    THEMES = {
        "morandi": ["#8B9DC3", "#B8C5D6", "#D4C5B9", "#C9B8A8", "#A8B5A0", "#B5A8A0", "#A0B5B8"],
        "business": ["#1E3A5F", "#2E5EAA", "#4A90E2", "#87CEEB", "#B0C4DE", "#D6EAF8"],
        "warm": ["#E07A5F", "#F2CC8F", "#81B29A", "#3D405B", "#F4A261", "#E9C46A"],
    }

    def __init__(self, theme: str = "business"):
        self.theme = theme
        self.colors = self.THEMES.get(theme, self.THEMES["business"])
        plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
        plt.rcParams["axes.unicode_minus"] = False

    def set_theme(self, theme: str):
        self.theme = theme
        self.colors = self.THEMES.get(theme, self.THEMES["business"])

    def bar_chart(self, data: Dict, title: str, filepath: str):
        fig, ax = plt.subplots(figsize=(10, 6))
        labels = list(data.keys())
        values = list(data.values())
        bars = ax.bar(labels, values, color=self.colors[:len(labels)])
        ax.set_title(title, fontsize=16, fontweight="bold")
        ax.set_ylabel("数值")
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{val}",
                   ha="center", va="bottom", fontsize=10)
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"柱状图已保存: {filepath}")

    def line_chart(self, data: Dict, title: str, filepath: str):
        fig, ax = plt.subplots(figsize=(10, 6))
        for label, values in data.items():
            ax.plot(values, label=label, marker="o", linewidth=2)
        ax.set_title(title, fontsize=16, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"折线图已保存: {filepath}")

    def pie_chart(self, data: Dict, title: str, filepath: str):
        fig, ax = plt.subplots(figsize=(8, 8))
        labels = list(data.keys())
        values = list(data.values())
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct="%1.1f%%",
                                           colors=self.colors[:len(labels)], startangle=90)
        ax.set_title(title, fontsize=16, fontweight="bold")
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"饼图已保存: {filepath}")

    def radar_chart(self, data: Dict, title: str, filepath: str):
        categories = list(data.keys())
        values = list(data.values())
        N = len(categories)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        ax.fill(angles, values, color=self.colors[0], alpha=0.25)
        ax.plot(angles, values, color=self.colors[0], linewidth=2)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"雷达图已保存: {filepath}")
