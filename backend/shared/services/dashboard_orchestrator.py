"""
DashboardOrchestrator — Phase 5

Thin glue that wires UIPlanner → DB persistence → cache lookup →
analysis queue dispatch.

Flow (per call to create_dashboard)
────────────────────────────────────
1. UIPlanner.plan(question)          → blocks + sub_questions + cache_keys
2. DashboardRepository.create()      → persist DashboardPlanModel
3. Per block:
     a. BlockCacheService.lookup()   → cache HIT  → mark CACHED, skip queue
     b. analysis_queue.enqueue()     → cache MISS → mark PENDING, dispatch
4. Return dashboard summary dict

The AnalysisWorker + ExecutionWorker pipelines are never modified.
The only change to the analysis queue is that the job document now carries
an optional ``metadata`` dict (added in Phase 5) so Phase 6 can link an
analysis back to its originating block.
"""

import logging
from typing import Any, Dict, List, Optional

from ..db.schemas import BlockPlanModel, BlockStatus, DashboardPlanModel
from ..db.dashboard_repository import DashboardRepository

logger = logging.getLogger("dashboard-orchestrator")


class DashboardOrchestrator:
    """
    Orchestrates dashboard creation end-to-end.

    Parameters
    ----------
    repo_manager
        A ``RepositoryManager`` instance.  ``repo_manager.dashboard`` must be
        a ``DashboardRepository``.
    analysis_queue
        A ``MongoAnalysisQueue`` (or compatible) instance that exposes
        ``enqueue_analysis(data: dict) -> str``.
    ui_planner
        A ``UIPlanner`` instance.
    block_cache
        A ``BlockCacheService`` instance.
    """

    def __init__(
        self,
        repo_manager: Any,
        analysis_queue: Any,
        ui_planner: Any,
        block_cache: Any,
    ) -> None:
        self.dashboard_repo: DashboardRepository = repo_manager.dashboard
        self.analysis_queue = analysis_queue
        self.ui_planner = ui_planner
        self.block_cache = block_cache

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def create_dashboard(
        self,
        question: str,
        user_id: str,
        session_id: str,
        message_id: str,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Plan, persist, and dispatch a dashboard for *question*.

        Parameters
        ----------
        question
            The original user question to decompose into blocks.
        user_id
            The requesting user's ID.
        session_id
            The chat session ID (used for SSE routing in later phases).
        message_id
            The chat message ID this dashboard is attached to.
        force_refresh
            When ``True`` the cache is bypassed for every block.

        Returns
        -------
        dict
            ``{ dashboard_id, title, subtitle, layout, blocks: [...] }``
            where each block entry includes ``status`` ("cached" or "pending")
            and ``result_data`` for cache-hit blocks.
        """

        # ── Step 1: Ask UIPlanner to decompose the question ───────────────────
        logger.info(f"🗺  Planning dashboard for: {question[:80]}…")
        plan_output = await self.ui_planner.plan(question)

        # ── Step 2: Build and persist DashboardPlanModel ──────────────────────
        block_models: List[BlockPlanModel] = [
            BlockPlanModel(
                block_id=f"b{i}",
                sequence=i,
                block_spec_id=b["blockId"],
                category=b["category"],
                title=b["title"],
                data_contract=b["dataContract"],
                sub_question=b["sub_question"],
                canonical_params=b.get("canonical_params", {}),
                cache_key=b["cache_key"],
            )
            for i, b in enumerate(plan_output["blocks"])
        ]

        dashboard = DashboardPlanModel(
            user_id=user_id,
            session_id=session_id,
            message_id=message_id,
            original_question=question,
            title=plan_output["title"],
            subtitle=plan_output["subtitle"],
            layout=plan_output["layout"],
            blocks=block_models,
            status="running",
        )

        dashboard_id = await self.dashboard_repo.create(dashboard)
        logger.info(
            f"📋 Dashboard plan persisted: {dashboard_id} "
            f"({len(block_models)} blocks)"
        )

        # ── Step 3: Cache check + dispatch per block ──────────────────────────
        block_summaries: List[Dict[str, Any]] = []

        for block in dashboard.blocks:
            cached = (
                None
                if force_refresh
                else await self.block_cache.lookup(block.cache_key)
            )

            if cached is not None:
                # ── Cache HIT: mark complete immediately, skip queue ──────────
                await self.dashboard_repo.update_block_status(
                    dashboard_id,
                    block.block_id,
                    status=BlockStatus.CACHED,
                    result_data=cached,
                )
                logger.info(
                    f"⚡ Cache HIT  — block {block.block_id} "
                    f"(key={block.cache_key})"
                )
                block_summaries.append(
                    {
                        **block.model_dump(by_alias=True),
                        "status": "cached",
                        "result_data": cached,
                    }
                )

            else:
                # ── Cache MISS: enqueue sub_question into analysis pipeline ────
                job_id = await self._enqueue_block(
                    block=block,
                    dashboard_id=dashboard_id,
                    user_id=user_id,
                    session_id=session_id,
                )
                await self.dashboard_repo.update_block_status(
                    dashboard_id,
                    block.block_id,
                    status=BlockStatus.PENDING,
                    analysis_id=job_id,
                )
                logger.info(
                    f"📥 Cache MISS — block {block.block_id} queued "
                    f"(job={job_id}, key={block.cache_key})"
                )
                block_summaries.append(
                    {
                        **block.model_dump(by_alias=True),
                        "status": "pending",
                    }
                )

        return {
            "dashboard_id": dashboard_id,
            "title": plan_output["title"],
            "subtitle": plan_output["subtitle"],
            "layout": plan_output["layout"],
            "blocks": block_summaries,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _enqueue_block(
        self,
        block: BlockPlanModel,
        dashboard_id: str,
        user_id: str,
        session_id: str,
    ) -> str:
        """
        Dispatch a single block's sub-question into the analysis queue and
        return the resulting job ID.

        The ``metadata`` dict is stored in the analysis queue job document so
        Phase 6 can correlate the completed execution back to this block:

            analysis_queue_job.metadata = {
                "dashboard_id": ...,
                "block_id":     ...,
                "cache_key":    ...,
            }

        After the AnalysisWorker acks the job, its result carries the real
        ``analysis_id`` (AnalysisModel ID).  Phase 6 can retrieve the metadata
        by calling ``analysis_queue.find_metadata_by_result_analysis_id()``.
        """
        job_id = await self.analysis_queue.enqueue_analysis(
            {
                "session_id": session_id,
                "user_question": block.sub_question,
                "user_id": user_id,
                "message_id": None,       # dashboard blocks have no chat message
                "user_message_id": None,
                "metadata": {
                    "dashboard_id": dashboard_id,
                    "block_id": block.block_id,
                    "cache_key": block.cache_key,
                },
            }
        )
        return job_id


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_dashboard_orchestrator(
    repo_manager: Any,
    analysis_queue: Any,
    ui_planner: Any,
    block_cache: Any,
) -> DashboardOrchestrator:
    """Construct a fully-wired ``DashboardOrchestrator``."""
    return DashboardOrchestrator(
        repo_manager=repo_manager,
        analysis_queue=analysis_queue,
        ui_planner=ui_planner,
        block_cache=block_cache,
    )
