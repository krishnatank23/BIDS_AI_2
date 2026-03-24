"""
API routes for brand identity creation and management.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import Project, AgentOutput, BrandKit
from app.schemas.brand_schema import (
    ProjectCreate,
    ProjectOut,
    WorkflowState,
)
from app.workflows.brand_graph import (
    run_full_workflow,
    run_step,
    build_state_from_db,
)

router = APIRouter(prefix="/api/brand", tags=["Brand"])


# ── Create Project ────────────────────────────────────────────────────
@router.post("/project", response_model=ProjectOut, status_code=201)
async def create_project(
    payload: ProjectCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new brand identity project."""
    try:
        project = Project(idea=payload.idea, user_id=payload.user_id)
        db.add(project)
        await db.commit()  # ✅ COMMIT so project persists
        await db.refresh(project)  # Refresh after commit
        return project
    except Exception as e:
        await db.rollback()  # Rollback on error
        import traceback
        print(f"ERROR creating project: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ── Background Worker for Single Step ────────────────────────────────
async def _run_step_background(project_id: UUID, step: int) -> None:
    """Background task: runs a single step."""
    from app.db.database import async_session_factory
    
    async with async_session_factory() as db:
        project = await db.get(Project, project_id)
        if not project:
            return
        
        try:
            # Validate that previous steps are complete
            required_agents = {
                0: [],
                1: ["idea_discovery"],
                3: ["idea_discovery", "market_research", "competitor_analysis"],
                4: ["brand_strategy"],
                5: ["brand_strategy", "naming"],
                6: ["naming", "design_agent"],
                7: ["brand_strategy", "naming", "design_agent"],
                8: ["brand_strategy", "naming", "design_agent", "content_agent"],
                9: ["idea_discovery", "market_research", "competitor_analysis", "brand_strategy", "naming", "design_agent", "content_agent", "guidelines_agent"],
            }
            
            required = required_agents.get(step, [])
            state = await build_state_from_db(db, project)
            
            for agent in required:
                if getattr(state, agent, None) is None:
                    print(f"⚠️  Cannot run step {step}: missing {agent} output")
                    project.status = "error"
                    await db.commit()
                    return
            
            await run_step(db, project, step, state)
            await db.commit()
            print(f"✅ Step {step} completed for project {project_id}")
        except Exception as e:
            print(f"❌ ERROR in background step {step} for {project_id}: {e}")
            import traceback
            traceback.print_exc()
            # Update status to show error
            project.status = "error"
            try:
                await db.commit()
            except:
                await db.rollback()


# ── Background Worker for Full Workflow ───────────────────────────────
async def _run_workflow_background(project_id: UUID) -> None:
    """Background task: runs workflow end-to-end."""
    from app.db.database import async_session_factory
    
    async with async_session_factory() as db:
        project = await db.get(Project, project_id)
        if not project:
            return
        
        try:
            print(f"🚀 Starting workflow for project {project_id}")
            await run_full_workflow(db, project)
            print(f"✅ Workflow completed for project {project_id}")
        except Exception as e:
            print(f"❌ ERROR in background workflow for {project_id}: {e}")
            import traceback
            traceback.print_exc()
            # Update status to show error
            try:
                project.status = "error"
                await db.commit()
            except:
                await db.rollback()


# ── Run Full Workflow (Non-Blocking) ────────────────────────────────
@router.post("/project/{project_id}/run")
async def run_workflow(
    project_id: UUID, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Fire-and-forget: Start the brand identity pipeline.
    Returns immediately with current status.
    Frontend should poll /api/brand/project/{project_id} for progress.
    """
    try:
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.status == "completed":
            raise HTTPException(status_code=400, detail="Project workflow already completed")

        # Update project status to 'running'
        project.status = "running"
        # Don't commit here - let get_db() dependency handle it

        # Queue background task
        background_tasks.add_task(_run_workflow_background, project_id)

        return {
            "status": "running",
            "project_id": str(project_id),
            "message": "Workflow started in background. Poll for progress."
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in run_workflow: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ── Run Next Step (Non-Blocking) ─────────────────────────────────────
@router.post("/project/{project_id}/step")
async def run_next_step(
    project_id: UUID, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Fire-and-forget: Run the next step in the pipeline.
    Returns immediately with current step info.
    Frontend should poll /api/brand/project/{project_id} for progress.
    """
    try:
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.status == "completed":
            raise HTTPException(status_code=400, detail="Workflow already completed")

        current = project.current_step or 0

        # Map step numbers: step 1 runs parallel (1+2), then jump to 3
        step_map = [0, 1, 3, 4, 5, 6, 7, 8, 9]
        if current >= len(step_map):
            raise HTTPException(status_code=400, detail="All steps completed")

        step = step_map[current]
        
        # Update status and mark as running
        project.status = "running"
        # Don't commit here - let get_db() dependency handle it
        
        # Queue background task for the step
        background_tasks.add_task(_run_step_background, project_id, step)

        return {
            "status": "running",
            "step_requested": step,
            "message": f"Step {step} queued in background. Poll for progress."
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in run_next_step: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


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
