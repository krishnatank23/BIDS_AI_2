"""
API routes for brand identity creation and management.
SIMPLIFIED VERSION - Database skipped for testing
"""
from uuid import uuid4, UUID
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException

# In-memory storage for testing (no database)
projects_store = {}

class ProjectSimple:
    def __init__(self, idea: str, user_id: str = None):
        self.id = str(uuid4())
        self.idea = idea
        self.user_id = user_id
        self.current_step = 0
        self.status = "created"
        self.created_at = datetime.now().isoformat()
        self.agent_outputs = {}

router = APIRouter(prefix="/api/brand", tags=["Brand"])


# ── Create Project ────────────────────────────────────────────────────
@router.post("/project", status_code=201)
async def create_project(payload: dict):
    """Create a new brand identity project (in-memory)."""
    try:
        idea = payload.get("idea")
        user_id = payload.get("user_id")
        
        if not idea:
            raise HTTPException(status_code=400, detail="Idea is required")
        
        project = ProjectSimple(idea=idea, user_id=user_id)
        projects_store[project.id] = project
        
        print(f"✅ Created project {project.id}")
        
        return {
            "id": project.id,
            "idea": project.idea,
            "status": project.status,
            "current_step": project.current_step,
            "created_at": project.created_at,
        }
    except Exception as e:
        print(f"ERROR creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Background Worker for Full Workflow ───────────────────────────────
async def _run_workflow_background(project_id: str) -> None:
    """Background task: runs workflow end-to-end (mock)."""
    project = projects_store.get(project_id)
    if not project:
        print(f"❌ Project {project_id} not found")
        return
    
    try:
        print(f"🚀 Starting workflow for project {project_id}")
        
        # Mock agent steps - just simulate with delays
        agents = [
            'idea_discovery',
            'market_research',
            'competitor_analysis',
            'brand_strategy',
            'naming',
            'design_agent',
            'logo_generator',
            'content_agent',
            'guidelines_agent',
            'export_agent',
        ]
        
        for i, agent_name in enumerate(agents):
            # Simulate agent work
            await mock_agent_run(agent_name)
            
            # Store mock output
            project.agent_outputs[agent_name] = {
                "agent_name": agent_name,
                "output_json": {"status": "completed", "agent": agent_name},
                "explanation": f"{agent_name} completed successfully",
                "version": 1,
                "created_at": datetime.now().isoformat(),
            }
            
            # Update progress
            project.current_step = i + 1
            project.status = "running"
            
            print(f"  ✅ {agent_name} completed ({i+1}/10)")
        
        # Mark as completed
        project.status = "completed"
        project.current_step = 10
        print(f"✅ Workflow completed for project {project_id}")
        
    except Exception as e:
        print(f"❌ ERROR in workflow: {e}")
        project.status = "error"


async def mock_agent_run(agent_name: str):
    """Mock agent execution - simulates work."""
    import asyncio
    # Simulate different processing times
    wait_time = 1  # Fast for testing
    await asyncio.sleep(wait_time)
    print(f"  Processing {agent_name}...")


# ── Run Full Workflow (Non-Blocking) ────────────────────────────────
@router.post("/project/{project_id}/run")
async def run_workflow(project_id: str, background_tasks: BackgroundTasks):
    """
    Fire-and-forget: Start the brand identity pipeline.
    Returns immediately with current status.
    """
    try:
        project = projects_store.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.status == "completed":
            raise HTTPException(status_code=400, detail="Project workflow already completed")

        # Mark as running
        project.status = "running"
        project.current_step = 0

        # Queue background task
        background_tasks.add_task(_run_workflow_background, project_id)

        print(f"📍 Workflow queued for project {project_id}")

        return {
            "status": "running",
            "project_id": project_id,
            "message": "Workflow started in background. Poll for progress."
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in run_workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Run Next Step (Non-Blocking) ─────────────────────────────────────
@router.post("/project/{project_id}/step")
async def run_next_step(project_id: str, background_tasks: BackgroundTasks):
    """
    Fire-and-forget: Run the next step in the pipeline.
    Returns immediately with current step info.
    """
    try:
        project = projects_store.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.status == "completed":
            raise HTTPException(status_code=400, detail="Workflow already completed")

        current = project.current_step or 0
        step_map = [0, 1, 3, 4, 5, 6, 7, 8, 9]
        
        if current >= len(step_map):
            raise HTTPException(status_code=400, detail="All steps completed")

        step = step_map[current]
        
        # Mark as running
        project.status = "running"

        print(f"📍 Step {step} queued for project {project_id}")

        return {
            "status": "running",
            "step_requested": step,
            "message": f"Step {step} queued in background. Poll for progress."
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in run_next_step: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Get Project State ─────────────────────────────────────────────────
@router.get("/project/{project_id}")
async def get_project(project_id: str):
    """Get the current state of a project including all agent outputs."""
    project = projects_store.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "project": {
            "id": project.id,
            "idea": project.idea,
            "current_step": project.current_step,
            "status": project.status,
            "created_at": project.created_at,
        },
        "agent_outputs": project.agent_outputs,
    }


# ── List Projects ────────────────────────────────────────────────────
@router.get("/projects")
async def list_projects():
    """List all projects."""
    return [
        {
            "id": p.id,
            "idea": p.idea[:100],
            "status": p.status,
            "current_step": p.current_step,
            "created_at": p.created_at,
        }
        for p in projects_store.values()
    ]


# ── Download Brand Kit ───────────────────────────────────────────────
@router.get("/project/{project_id}/export")
async def get_export(project_id: str):
    """Get export file paths for a completed project."""
    project = projects_store.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status != "completed":
        raise HTTPException(status_code=400, detail="Project not completed yet")

    return {
        "project_id": project_id,
        "export_path": f"/exports/{project_id}/brand_kit.pdf",
        "created_at": project.created_at,
    }
