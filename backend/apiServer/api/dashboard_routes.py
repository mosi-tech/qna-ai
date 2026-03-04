"""
Dashboard API Routes — Phase 7 + Phase 11

POST   /api/dashboard/create
POST   /api/dashboard/run-headless
GET    /api/dashboard/session/{session_id}
GET    /api/dashboard/{dashboard_id}
GET    /api/dashboard/{dashboard_id}/blocks/{block_id}
POST   /api/dashboard/{dashboard_id}/blocks/{block_id}/refresh
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from .auth import UserContext, require_authenticated_user

logger = logging.getLogger("dashboard-routes")

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class CreateDashboardRequest(BaseModel):
    question: str
    sessionId: str
    messageId: str
    forceRefresh: bool = False


class HeadlessRunRequest(BaseModel):
    question: str
    timeout_seconds: int = 120


class DashboardResponse(BaseModel):
    """Thin wrapper — data is returned as a raw dict from the orchestrator/repo."""
    success: bool
    data: Any
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ok(data: Any) -> Dict[str, Any]:
    return {"success": True, "data": data, "timestamp": datetime.utcnow().isoformat()}


def _get_orchestrator(request: Request):
    orch = getattr(request.app.state, "dashboard_orch", None)
    if orch is None:
        raise HTTPException(
            status_code=503,
            detail="Dashboard orchestrator is not available. "
                   "Check that the server started correctly.",
        )
    return orch


def _get_dashboard_repo(request: Request):
    repo_manager = getattr(request.app.state, "repo_manager", None)
    if repo_manager is None:
        raise HTTPException(status_code=503, detail="Repository service not available")
    return repo_manager.dashboard


# ---------------------------------------------------------------------------
# POST /api/dashboard/create
# ---------------------------------------------------------------------------


@router.post("/create")
async def create_dashboard(
    body: CreateDashboardRequest,
    request: Request,
    user_context: UserContext = Depends(require_authenticated_user),
):
    """
    Plan, persist, and dispatch a new dashboard.

    Runs UIPlanner to decompose the question into blocks, persists the
    DashboardPlanModel, checks cache per block, and dispatches cache-miss
    blocks into the analysis pipeline.

    Returns the full initial plan (<2 s) — cached blocks include result_data
    immediately; pending blocks will arrive via ``block_update`` SSE events.
    """
    orch = _get_orchestrator(request)
    try:
        plan = await orch.create_dashboard(
            question=body.question,
            user_id=user_context.user_id,
            session_id=body.sessionId,
            message_id=body.messageId,
            force_refresh=body.forceRefresh,
        )
        logger.info(
            "✅ Dashboard created: %s (%d blocks) for user %s",
            plan.get("dashboard_id"),
            len(plan.get("blocks", [])),
            user_context.user_id,
        )
        return _ok(plan)
    except Exception as exc:
        logger.exception("Error creating dashboard: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# POST /api/dashboard/run-headless  — must come before /{dashboard_id} routes
# ---------------------------------------------------------------------------


@router.post("/run-headless")
async def run_headless(
    body: HeadlessRunRequest,
    request: Request,
    user_context: UserContext = Depends(require_authenticated_user),
):
    """
    Run the full dashboard pipeline synchronously.
    Waits for all blocks to complete (or timeout) before returning.
    Useful for smoke-tests, CI, and debugging without a browser.
    """
    orch = _get_orchestrator(request)
    repo = _get_dashboard_repo(request)

    timeout = body.timeout_seconds
    try:
        plan = await orch.create_dashboard(
            question=body.question,
            user_id=user_context.user_id,
            session_id="",        # no SSE session needed for headless
            message_id="headless",
            force_refresh=False,
        )
    except Exception as exc:
        logger.exception("Error planning headless dashboard: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    dashboard_id = plan["dashboard_id"]
    logger.info(
        "[headless] Dashboard created: %s (%d blocks)",
        dashboard_id,
        len(plan.get("blocks", [])),
    )

    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    current = plan

    while loop.time() < deadline:
        statuses = {b["status"] for b in current.get("blocks", [])}
        if statuses.issubset({"complete", "cached", "failed"}):
            logger.info("[headless] All blocks settled for dashboard %s", dashboard_id)
            return _ok(current)
        await asyncio.sleep(1)
        try:
            current = await repo.get_by_id(dashboard_id)
        except Exception as exc:
            logger.exception("[headless] Error polling dashboard %s: %s", dashboard_id, exc)
            raise HTTPException(status_code=500, detail=str(exc))

    logger.warning(
        "[headless] Timeout after %ds for dashboard %s", timeout, dashboard_id
    )
    return {"success": False, "error": "timeout", "data": current, "timestamp": datetime.utcnow().isoformat()}


# ---------------------------------------------------------------------------
# GET /api/dashboard/session/{session_id}   — must come before parameterised
# route so FastAPI doesn't match "session" as a dashboard_id
# ---------------------------------------------------------------------------


@router.get("/session/{session_id}")
async def list_session_dashboards(
    session_id: str,
    request: Request,
    user_context: UserContext = Depends(require_authenticated_user),
):
    """Return all dashboard plans belonging to *session_id* (newest first)."""
    repo = _get_dashboard_repo(request)
    try:
        dashboards = await repo.list_by_session(session_id)
        return _ok(dashboards)
    except Exception as exc:
        logger.exception("Error listing dashboards for session %s: %s", session_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# GET /api/dashboard/{dashboard_id}
# ---------------------------------------------------------------------------


@router.get("/{dashboard_id}")
async def get_dashboard(
    dashboard_id: str,
    request: Request,
    user_context: UserContext = Depends(require_authenticated_user),
):
    """Return the full DashboardPlanModel with current block statuses."""
    repo = _get_dashboard_repo(request)
    doc = await repo.get_by_id(dashboard_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Dashboard {dashboard_id} not found")

    # Ownership check
    if doc.get("userId") != user_context.user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return _ok(doc)


# ---------------------------------------------------------------------------
# GET /api/dashboard/{dashboard_id}/blocks/{block_id}
# ---------------------------------------------------------------------------


@router.get("/{dashboard_id}/blocks/{block_id}")
async def get_block(
    dashboard_id: str,
    block_id: str,
    request: Request,
    user_context: UserContext = Depends(require_authenticated_user),
):
    """Return a single BlockPlanModel (status + result_data)."""
    repo = _get_dashboard_repo(request)
    doc = await repo.get_by_id(dashboard_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Dashboard {dashboard_id} not found")

    if doc.get("userId") != user_context.user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    blocks = doc.get("blocks", [])
    for block in blocks:
        if block.get("block_id") == block_id:
            return _ok(block)

    raise HTTPException(
        status_code=404,
        detail=f"Block {block_id} not found in dashboard {dashboard_id}",
    )


# ---------------------------------------------------------------------------
# POST /api/dashboard/{dashboard_id}/blocks/{block_id}/refresh
# ---------------------------------------------------------------------------


class RefreshBlockRequest(BaseModel):
    """Body is optional — sending an empty JSON body `{}` is fine."""
    pass


@router.post("/{dashboard_id}/blocks/{block_id}/refresh")
async def refresh_block(
    dashboard_id: str,
    block_id: str,
    request: Request,
    user_context: UserContext = Depends(require_authenticated_user),
):
    """Force cache bypass and re-run a single block's sub_question."""
    repo = _get_dashboard_repo(request)
    doc = await repo.get_by_id(dashboard_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Dashboard {dashboard_id} not found")

    if doc.get("userId") != user_context.user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Find the target block
    target_block = next(
        (b for b in doc.get("blocks", []) if b.get("block_id") == block_id),
        None,
    )
    if target_block is None:
        raise HTTPException(
            status_code=404,
            detail=f"Block {block_id} not found in dashboard {dashboard_id}",
        )

    orch = _get_orchestrator(request)
    try:
        # Re-enqueue just this block using the orchestrator's private helper.
        # We reconstruct a minimal BlockPlanModel-like object from the raw doc.
        from shared.db.schemas import BlockPlanModel, BlockStatus

        block_model = BlockPlanModel(
            block_id=target_block["block_id"],
            sequence=target_block.get("sequence", 0),
            block_spec_id=target_block.get("block_spec_id", ""),
            category=target_block.get("category", ""),
            title=target_block.get("title", ""),
            data_contract=target_block.get("dataContract", target_block.get("data_contract", {})),
            sub_question=target_block.get("sub_question", ""),
            canonical_params=target_block.get("canonical_params", {}),
            cache_key=target_block.get("cache_key", ""),
        )

        job_id = await orch._enqueue_block(
            block=block_model,
            dashboard_id=dashboard_id,
            user_id=user_context.user_id,
            session_id=doc.get("sessionId", ""),
        )

        await repo.update_block_status(
            dashboard_id,
            block_id,
            status=BlockStatus.PENDING,
            analysis_id=job_id,
        )

        logger.info(
            "🔄 Block refreshed: dashboard=%s block=%s job=%s",
            dashboard_id,
            block_id,
            job_id,
        )
        return _ok({"block_id": block_id, "job_id": job_id, "status": "pending"})

    except Exception as exc:
        logger.exception(
            "Error refreshing block %s in dashboard %s: %s",
            block_id, dashboard_id, exc,
        )
        raise HTTPException(status_code=500, detail=str(exc))
