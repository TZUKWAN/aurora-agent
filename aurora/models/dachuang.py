"""Pydantic models for Dachuang (Undergraduate Innovation Training Program) applications."""

from typing import List, Optional

from pydantic import BaseModel


class TeamMemberInfo(BaseModel):
    """Team member information."""
    name: str = ""
    student_id: str = ""
    major: str = ""
    role: str = ""  # 负责人/成员
    grade: str = ""  # 年级
    phone: str = ""
    email: str = ""


class AdvisorInfo(BaseModel):
    """Advisor (指导教师) information."""
    name: str = ""
    title: str = ""  # 职称
    department: str = ""
    research_area: str = ""
    phone: str = ""
    email: str = ""


class BudgetItem(BaseModel):
    """Single budget line item."""
    category: str
    amount: float
    justification: str = ""


class DachuangProjectInfo(BaseModel):
    """Complete project information for a Dachuang application."""
    project_name: str = ""
    project_type: str = "innovation"  # innovation / entrepreneurship
    level: str = "school"  # national / provincial / school
    leader: str = ""
    members: List[TeamMemberInfo] = []
    advisor: Optional[AdvisorInfo] = None
    department: str = ""
    technology: str = ""
    problem: str = ""
    solution: str = ""
    target_market: str = ""
    innovation: str = ""
    social_impact: str = ""
    expected_outcomes: str = ""
    duration_months: int = 12
    total_budget: float = 10000.0

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.model_fields})


class DachuangApplication(BaseModel):
    """Complete generated application document."""
    metadata: dict = {}
    sections: dict = {}

    def to_dict(self):
        return {"metadata": self.metadata, "sections": self.sections}
