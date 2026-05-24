"""Pydantic models for structured project input."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectInfo(BaseModel):
    """Structured project information for business plan generation."""

    project_name: str = Field(default="", description="Project name")
    technology: str = Field(default="", description="Core technology stack")
    problem: str = Field(default="", description="Problem being solved")
    solution: str = Field(default="", description="Proposed solution")
    product: str = Field(default="", description="Product/service name")
    target_market: str = Field(default="", description="Target market/audience")
    business_model: str = Field(default="", description="Business model (e.g. SaaS, marketplace)")
    team_background: str = Field(default="", description="Team background and expertise")
    innovation: str = Field(default="", description="Innovation differentiation")
    social_impact: str = Field(default="", description="Social impact and value")
    funding: str = Field(default="50万", description="Funding amount needed")
    team_size: str = Field(default="5", description="Team size")
    revenue_model: str = Field(default="", description="Revenue model")
    market_size: str = Field(default="", description="Market size estimate")
    competition_id: str = Field(default="internet_plus", description="Target competition ID")
    stage: str = Field(default="初创", description="Project stage (创意/初创/成长)")
    milestones: str = Field(default="", description="Key milestones achieved")
    intellectual_property: str = Field(default="", description="Patents and IP")

    def to_dict(self) -> dict:
        """Convert to plain dict, excluding empty fields."""
        return {k: v for k, v in self.model_dump().items() if v}

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectInfo":
        """Create from a dict, ignoring unknown keys."""
        known_fields = set(cls.model_fields.keys())
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)
