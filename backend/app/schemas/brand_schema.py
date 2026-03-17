"""
Pydantic schemas for request / response validation.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ── Generic Agent Output ──────────────────────────────────────────────
class AgentResult(BaseModel):
    """Every agent returns this envelope."""
    data: dict[str, Any]
    explanation: str = Field(
        ..., description="6-7 line human-readable explanation of the agent's output"
    )


# ── Project ───────────────────────────────────────────────────────────
class ProjectCreate(BaseModel):
    idea: str = Field(..., min_length=5, max_length=2000)
    user_id: Optional[str] = None


class ProjectOut(BaseModel):
    id: UUID
    user_id: Optional[str]
    idea: str
    current_step: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Agent Output ──────────────────────────────────────────────────────
class AgentOutputOut(BaseModel):
    id: UUID
    project_id: UUID
    agent_name: str
    output_json: dict[str, Any]
    explanation: Optional[str]
    version: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Regeneration Request ──────────────────────────────────────────────
class RegenerateRequest(BaseModel):
    project_id: UUID
    agent_name: str = Field(
        ...,
        description="Agent to regenerate: design_agent | logo_generator | content_agent",
    )
    feedback: str = Field(
        ..., min_length=3, max_length=1000, description="User feedback for regeneration"
    )


# ── Brand Kit ─────────────────────────────────────────────────────────
class BrandKitOut(BaseModel):
    id: UUID
    project_id: UUID
    final_output: Optional[dict[str, Any]]
    export_path: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Workflow State (passed between agents) ────────────────────────────
class WorkflowState(BaseModel):
    project_id: UUID
    idea: str
    idea_discovery: Optional[dict[str, Any]] = None
    market_research: Optional[dict[str, Any]] = None
    competitor_analysis: Optional[dict[str, Any]] = None
    brand_strategy: Optional[dict[str, Any]] = None
    naming: Optional[dict[str, Any]] = None
    design_agent: Optional[dict[str, Any]] = None
    logo_generator: Optional[dict[str, Any]] = None
    content_agent: Optional[dict[str, Any]] = None
    guidelines_agent: Optional[dict[str, Any]] = None
    export_agent: Optional[dict[str, Any]] = None
