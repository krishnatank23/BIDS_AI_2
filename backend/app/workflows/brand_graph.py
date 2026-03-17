"""
Brand Identity Workflow Orchestrator
Implements a graph-based pipeline with:
  - Sequential execution for most agents
  - PARALLEL execution for Market Research + Competitor Analysis
  - DB persistence after each step
  - Regeneration support via the Feedback Agent
"""
import asyncio
import json
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.models import AgentOutput, Project, BrandKit
from app.schemas.brand_schema import AgentResult, WorkflowState

from app.agents import (
    idea_discovery,
    market_research,
    competitor_analysis,
    brand_strategy,
    naming,
    design_agent,
    logo_generator,
    content_agent,
    guidelines_agent,
    export_agent,
    feedback_agent,
)

# Agent execution order (index = step number)
AGENT_SEQUENCE = [
    "idea_discovery",       # 0
    "market_research",      # 1  ─┐ PARALLEL
    "competitor_analysis",  # 2  ─┘
    "brand_strategy",       # 3
    "naming",               # 4
    "design_agent",         # 5
    "logo_generator",       # 6
    "content_agent",        # 7
    "guidelines_agent",     # 8
    "export_agent",         # 9
]


async def _save_agent_output(
    db: AsyncSession,
    project_id: UUID,
    agent_name: str,
    result: AgentResult,
) -> None:
    """Persist an agent's output to the database, auto-incrementing version."""
    # Determine next version
    stmt = select(func.coalesce(func.max(AgentOutput.version), 0)).where(
        AgentOutput.project_id == project_id,
        AgentOutput.agent_name == agent_name,
    )
    result_row = await db.execute(stmt)
    current_max = result_row.scalar() or 0

    output = AgentOutput(
        project_id=project_id,
        agent_name=agent_name,
        output_json=result.data,
        explanation=result.explanation,
        version=current_max + 1,
    )
    db.add(output)
    await db.flush()


async def _get_latest_output(
    db: AsyncSession, project_id: UUID, agent_name: str
) -> dict | None:
    """Fetch the latest version of an agent output for a project."""
    stmt = (
        select(AgentOutput)
        .where(
            AgentOutput.project_id == project_id,
            AgentOutput.agent_name == agent_name,
        )
        .order_by(AgentOutput.version.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()
    return row.output_json if row else None


async def run_step(
    db: AsyncSession,
    project: Project,
    step: int,
    state: WorkflowState,
) -> WorkflowState:
    """Run a single step (or parallel pair) in the pipeline."""

    # ── Step 0: Idea Discovery ────────────────────────────────────────
    if step == 0:
        result = await idea_discovery.run(state.idea)
        state.idea_discovery = result.data
        await _save_agent_output(db, project.id, "idea_discovery", result)

    # ── Steps 1+2: Market Research + Competitor Analysis (PARALLEL) ──
    elif step == 1:
        mr_task = market_research.run(state.idea_discovery)
        ca_task = competitor_analysis.run(state.idea_discovery)

        mr_result, ca_result = await asyncio.gather(mr_task, ca_task)

        state.market_research = mr_result.data
        state.competitor_analysis = ca_result.data

        await _save_agent_output(db, project.id, "market_research", mr_result)
        await _save_agent_output(db, project.id, "competitor_analysis", ca_result)

    # ── Step 3: Brand Strategy (waits for both parallel outputs) ─────
    elif step == 3:
        result = await brand_strategy.run(
            state.idea_discovery,
            state.market_research,
            state.competitor_analysis,
        )
        state.brand_strategy = result.data
        await _save_agent_output(db, project.id, "brand_strategy", result)

    # ── Step 4: Naming ────────────────────────────────────────────────
    elif step == 4:
        result = await naming.run(state.brand_strategy)
        state.naming = result.data
        await _save_agent_output(db, project.id, "naming", result)

    # ── Step 5: Design Intelligence ──────────────────────────────────
    elif step == 5:
        result = await design_agent.run(state.brand_strategy, state.naming)
        state.design_agent = result.data
        await _save_agent_output(db, project.id, "design_agent", result)

    # ── Step 6: Logo Generation ──────────────────────────────────────
    elif step == 6:
        result = await logo_generator.run(state.naming, state.design_agent)
        state.logo_generator = result.data
        await _save_agent_output(db, project.id, "logo_generator", result)

    # ── Step 7: Brand Content ────────────────────────────────────────
    elif step == 7:
        result = await content_agent.run(
            state.brand_strategy, state.naming, state.design_agent
        )
        state.content_agent = result.data
        await _save_agent_output(db, project.id, "content_agent", result)

    # ── Step 8: Brand Guidelines ─────────────────────────────────────
    elif step == 8:
        result = await guidelines_agent.run(
            state.brand_strategy, state.naming, state.design_agent, state.content_agent
        )
        state.guidelines_agent = result.data
        await _save_agent_output(db, project.id, "guidelines_agent", result)

    # ── Step 9: Export ───────────────────────────────────────────────
    elif step == 9:
        brand_data = {
            "idea_discovery": state.idea_discovery,
            "market_research": state.market_research,
            "competitor_analysis": state.competitor_analysis,
            "brand_strategy": state.brand_strategy,
            "naming": state.naming,
            "design_agent": state.design_agent,
            "content_agent": state.content_agent,
            "guidelines_agent": state.guidelines_agent,
        }
        result = await export_agent.run(str(project.id), brand_data)
        state.export_agent = result.data
        await _save_agent_output(db, project.id, "export_agent", result)

        # Save brand kit
        kit = BrandKit(
            project_id=project.id,
            final_output=brand_data,
            export_path=result.data.get("pdf_path"),
        )
        db.add(kit)

    # Update project step
    project.current_step = step + 1
    if step >= 9:
        project.status = "completed"
    else:
        project.status = "running"
    await db.flush()

    return state


async def build_state_from_db(db: AsyncSession, project: Project) -> WorkflowState:
    """Reconstruct the workflow state from saved DB outputs."""
    state = WorkflowState(project_id=project.id, idea=project.idea)

    for agent_name in AGENT_SEQUENCE:
        data = await _get_latest_output(db, project.id, agent_name)
        if data:
            setattr(state, agent_name, data)

    return state


async def run_full_workflow(db: AsyncSession, project: Project) -> WorkflowState:
    """Run ALL steps of the brand identity pipeline end-to-end."""
    state = WorkflowState(project_id=project.id, idea=project.idea)
    project.status = "running"
    await db.flush()

    # Steps: 0 → 1(parallel 1+2) → 3 → 4 → 5 → 6 → 7 → 8 → 9
    ordered_steps = [0, 1, 3, 4, 5, 6, 7, 8, 9]
    for step in ordered_steps:
        state = await run_step(db, project, step, state)

    await db.commit()
    return state


async def regenerate_agents(
    db: AsyncSession,
    project: Project,
    feedback_text: str,
) -> dict:
    """Use the Feedback Agent to interpret feedback, then re-run specified agents."""
    state = await build_state_from_db(db, project)

    current_outputs = {
        "design_agent": state.design_agent,
        "logo_generator": state.logo_generator,
        "content_agent": state.content_agent,
    }

    # Step 1: Let the Feedback Agent decide what to regenerate
    fb_result = await feedback_agent.run(feedback_text, current_outputs)
    await _save_agent_output(db, project.id, "feedback_agent", fb_result)

    agents_to_regen = fb_result.data.get("agents_to_regenerate", [])
    modifications = fb_result.data.get("modifications", {})
    regenerated = {}

    # Step 2: Re-run each specified agent with modified instructions
    for agent_name in agents_to_regen:
        mod = modifications.get(agent_name, feedback_text)

        if agent_name == "design_agent":
            result = await design_agent.run(state.brand_strategy, state.naming, feedback=mod)
            state.design_agent = result.data

        elif agent_name == "logo_generator":
            result = await logo_generator.run(state.naming, state.design_agent, feedback=mod)
            state.logo_generator = result.data

        elif agent_name == "content_agent":
            result = await content_agent.run(
                state.brand_strategy, state.naming, state.design_agent, feedback=mod
            )
            state.content_agent = result.data

        else:
            continue

        await _save_agent_output(db, project.id, agent_name, result)
        regenerated[agent_name] = result.model_dump()

    await db.commit()
    return {
        "feedback_analysis": fb_result.model_dump(),
        "regenerated": regenerated,
    }
