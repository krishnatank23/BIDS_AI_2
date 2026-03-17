"""
API routes for brand identity creation and management.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import Project, AgentOutput, BrandKit
from app.schemas.brand_schema import (
    ProjectCreate,
    ProjectOut,
    AgentOutputOut,
    WorkflowState,
)
from app.workflows.brand_graph import (
    run_full_workflow,
    run_step,
    build_state_from_db,
    AGENT_SEQUENCE,
)

router = APIRouter(prefix="/api/brand", tags=["Brand"])


# ── Create Project ────────────────────────────────────────────────────
@router.post("/project", response_model=ProjectOut, status_code=201)
async def create_project(
    payload: ProjectCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new brand identity project."""
    project = Project(idea=payload.idea, user_id=payload.user_id)
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return project


# ── Run Full Workflow ─────────────────────────────────────────────────
@router.post("/project/{project_id}/run")
async def run_workflow(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """Run the entire brand identity pipeline for a project."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if project.status == "completed":
        raise HTTPException(400, "Project workflow already completed")

    state = await run_full_workflow(db, project)
    return {
        "status": "completed",
        "project_id": str(project_id),
        "state": state.model_dump(),
    }


# ── Run Next Step ─────────────────────────────────────────────────────
@router.post("/project/{project_id}/step")
async def run_next_step(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """Run the next step in the pipeline (for step-by-step approval)."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if project.status == "completed":
        raise HTTPException(400, "Workflow already completed")

    current = project.current_step or 0

    # Map step numbers: step 1 runs parallel (1+2), then jump to 3
    step_map = [0, 1, 3, 4, 5, 6, 7, 8, 9]
    if current >= len(step_map):
        raise HTTPException(400, "All steps completed")

    step = step_map[current]
    state = await build_state_from_db(db, project)
    state = await run_step(db, project, step, state)
    await db.commit()

    return {
        "step_completed": step,
        "next_step": current + 1 if current + 1 < len(step_map) else None,
        "status": project.status,
        "state": state.model_dump(),
    }


# ── Get Project State ─────────────────────────────────────────────────
@router.get("/project/{project_id}")
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get the current state of a project including all agent outputs."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    stmt = (
        select(AgentOutput)
        .where(AgentOutput.project_id == project_id)
        .order_by(AgentOutput.agent_name, AgentOutput.version.desc())
    )
    result = await db.execute(stmt)
    outputs = result.scalars().all()

    # Group by agent_name, keep latest version
    latest: dict = {}
    for o in outputs:
        if o.agent_name not in latest:
            latest[o.agent_name] = {
                "agent_name": o.agent_name,
                "output_json": o.output_json,
                "explanation": o.explanation,
                "version": o.version,
                "created_at": str(o.created_at),
            }

    return {
        "project": {
            "id": str(project.id),
            "idea": project.idea,
            "current_step": project.current_step,
            "status": project.status,
            "created_at": str(project.created_at),
        },
        "agent_outputs": latest,
    }


# ── List Projects ────────────────────────────────────────────────────
@router.get("/projects")
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all projects."""
    stmt = select(Project).order_by(Project.created_at.desc())
    result = await db.execute(stmt)
    projects = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "idea": p.idea[:100],
            "status": p.status,
            "current_step": p.current_step,
            "created_at": str(p.created_at),
        }
        for p in projects
    ]


# ── Download Brand Kit ───────────────────────────────────────────────
@router.get("/project/{project_id}/export")
async def get_export(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get export file paths for a completed project."""
    stmt = select(BrandKit).where(BrandKit.project_id == project_id)
    result = await db.execute(stmt)
    kit = result.scalar_one_or_none()

    if not kit:
        raise HTTPException(404, "Brand kit not found. Run the full workflow first.")

    return {
        "project_id": str(project_id),
        "export_path": kit.export_path,
        "created_at": str(kit.created_at),
    }
