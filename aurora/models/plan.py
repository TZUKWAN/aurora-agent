"""Pydantic models for business plan structure."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PlanSection(BaseModel):
    """A single section of a business plan."""
    title: str = ""
    content: str = ""
    word_count: int = 0


class PlanMetadata(BaseModel):
    """Metadata for a business plan."""
    competition: str = ""
    track: str = ""
    generated_at: str = ""


class BusinessPlan(BaseModel):
    """Complete business plan structure."""
    metadata: PlanMetadata = Field(default_factory=PlanMetadata)
    sections: Dict[str, PlanSection] = Field(default_factory=dict)
