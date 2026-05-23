"""进度跟踪器."""

from typing import Dict, List
from datetime import datetime


class ProgressTracker:
    """项目进度跟踪."""

    def __init__(self):
        self.milestones = []

    def add_milestone(self, name: str, deadline: str, status: str = "pending"):
        self.milestones.append({
            "name": name,
            "deadline": deadline,
            "status": status,
            "progress": 0 if status == "pending" else 50 if status == "in_progress" else 100,
        })

    def update_progress(self, milestone_name: str, progress: float):
        for m in self.milestones:
            if m["name"] == milestone_name:
                m["progress"] = min(max(progress, 0), 100)
                if m["progress"] >= 100:
                    m["status"] = "completed"
                elif m["progress"] > 0:
                    m["status"] = "in_progress"
                break

    def get_overall_progress(self) -> float:
        if not self.milestones:
            return 0.0
        return sum(m["progress"] for m in self.milestones) / len(self.milestones)

    def get_delayed_items(self) -> List[Dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        delayed = []
        for m in self.milestones:
            if m["deadline"] < today and m["status"] != "completed":
                delayed.append(m)
        return delayed

    def generate_status_report(self) -> Dict:
        return {
            "total_milestones": len(self.milestones),
            "completed": sum(1 for m in self.milestones if m["status"] == "completed"),
            "in_progress": sum(1 for m in self.milestones if m["status"] == "in_progress"),
            "pending": sum(1 for m in self.milestones if m["status"] == "pending"),
            "overall_progress": self.get_overall_progress(),
            "delayed": len(self.get_delayed_items()),
        }
