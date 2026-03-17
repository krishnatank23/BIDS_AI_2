"""
API routes for regeneration via the Feedback Agent.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Project
from app.schemas.brand_schema import RegenerateRequest
from app.workflows.brand_graph import regenerate_agents

router = APIRouter(prefix="/api/regenerate", tags=["Regenerate"])


@router.post("/")
async def regenerate(
    payload: RegenerateRequest, db: AsyncSession = Depends(get_db)
):
    """
    Regenerate specific brand elements based on user feedback.

    The Feedback Agent analyzes the feedback and decides which agent(s) to re-run.
    Supports regeneration of: design_agent, logo_generator, content_agent.
    """
    project = await db.get(Project, payload.project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    if project.status != "completed" and project.current_step < 8:
        raise HTTPException(
            400,
            "Project must have completed at least through the content stage before regeneration.",
        )

    result = await regenerate_agents(db, project, payload.feedback)

    return {
        "status": "regenerated",
        "project_id": str(payload.project_id),
        "result": result,
    }
