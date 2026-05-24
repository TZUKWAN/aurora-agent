"""Team management data models."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TeamMember:
    """A member of a competition team."""

    name: str
    role: str  # leader, tech, business, design, marketing, finance, advisor
    skills: List[str] = field(default_factory=list)
    background: str = ""
    responsibilities: List[str] = field(default_factory=list)


@dataclass
class TeamRole:
    """A predefined role in a competition team."""

    role_id: str
    name: str
    description: str
    required_skills: List[str] = field(default_factory=list)
    weight: float = 0.0  # importance weight for this role


@dataclass
class TeamAnalysis:
    """Analysis result of a team's composition."""

    completeness_score: float  # 0-100
    role_coverage: Dict[str, float]  # role_id -> coverage percentage
    missing_roles: List[str]
    strength_areas: List[str]
    weakness_areas: List[str]
    recommendations: List[str]
