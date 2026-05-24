"""Pydantic models for evaluation results."""

from typing import List, Optional

from pydantic import BaseModel, Field


class DimensionScore(BaseModel):
    """Score for a single evaluation dimension."""
    name: str = ""
    weight: float = 0.0
    score: float = 0.0
    feedback: str = ""
    suggestions: List[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    """Complete evaluation result."""
    competition: str = ""
    dimensions: List[DimensionScore] = Field(default_factory=list)
    overall_score: float = 0.0
    feedback: str = ""
    suggestions: List[str] = Field(default_factory=list)
