"""甘特图生成器."""

from typing import Dict, List
from datetime import datetime
import json


class GanttChart:
    """项目甘特图."""

    def __init__(self):
        self.tasks = []

    def add_task(self, name: str, start: str, end: str, progress: float = 0, dependencies: List[str] = None):
        self.tasks.append({
            "name": name,
            "start": start,
            "end": end,
            "progress": progress,
            "dependencies": dependencies or [],
        })

    def export_to_json(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        print(f"甘特图数据已导出: {filepath}")

    def generate_html(self, filepath: str):
        html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>甘特图</title>
<style>
body{font-family:Arial,sans-serif;margin:20px}
.gantt{position:relative;margin-top:20px}
.task{height:30px;margin:5px 0;background:#f0f0f0;border-radius:4px;position:relative}
.task-bar{height:100%;background:#2E5EAA;border-radius:4px;position:absolute}
.task-label{position:absolute;left:10px;line-height:30px;font-size:12px}
</style></head><body>
<h2>项目进度甘特图</h2>
<div class="gantt">"""
        for task in self.tasks:
            html += f'<div class="task"><div class="task-bar" style="width:{task["progress"]}%"></div><span class="task-label">{task["name"]} ({task["start"]} - {task["end"]})</span></div>'
        html += "</div></body></html>"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"甘特图HTML已导出: {filepath}")
