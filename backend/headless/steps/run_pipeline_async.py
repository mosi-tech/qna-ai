#!/usr/bin/env python3
"""
Async Dashboard Pipeline - MongoDB + Inline Analysis, No PM2 Workers

Chains steps 1 → 4 inline using async, with MongoDB persistence:
  Step 1 — UIPlanner.plan()                   → block plan
  Step 2 — DashboardRepository.create()       → dashboard_id
  Step 3 — (Optional cache check, can skip)
  Step 4 — Inline analysis per block           → results directly
  Step 5 — Return final dashboard with results

Usage:
    cd backend
    python headless/steps/run_pipeline_async.py "How is QQQ performing?"
"""

import asyncio
import json
import sys
import os
import uuid
from datetime import datetime

# ── Path setup ────────────────────────────────────────────────────────────────
_DIR     = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.normpath(os.path.join(_DIR, "..", ".."))
_OUTPUT  = os.path.join(_DIR, "output")
sys.path.insert(0, _BACKEND)

from dotenv import load_dotenv
load_dotenv(os.path.join(_BACKEND, "apiServer", ".env"))

# ── Logging ───────────────────────────────────────────────────────────────────
import logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)

logger = logging.getLogger("async-pipeline")
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[async-pipeline] %(message)s"))
logger.addHandler(_handler)
logger.propagate = False

# ── Imports ───────────────────────────────────────────────────────────────────
from shared.db.mongodb_client import MongoDBClient
from shared.db.repositories import RepositoryManager
from shared.db.schemas import DashboardPlanModel, BlockPlanModel, BlockStatus
from shared.services.ui_planner import create_ui_planner, UIPlanner
from shared.llm import LLMConfig, create_llm_service


# ── Helpers ───────────────────────────────────────────────────────────────────
def _banner(step: int, title: str) -> None:
    sep = "─" * 60
    print(f"\n{sep}", file=sys.stderr)
    print(f"[async-pipeline]  STEP {step} — {title}", file=sys.stderr)
    print(sep, file=sys.stderr)


def save_output(result: dict, label: str) -> str:
    os.makedirs(_OUTPUT, exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(_OUTPUT, f"async_{label}_{ts}.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return path


# ── Inline Analyzer ─────────────────────────────────────────────────────────
class InlineBlockAnalyzer:
    """Analyze block sub-questions inline using async LLM calls"""

    def __init__(self):
        # Use analysis config
        config = LLMConfig.for_task("ANALYSIS")
        config.service_name = "analysis"
        config.max_tokens = 4000
        config.base_url = os.getenv("OLLAMA_BASE_URL", "https://ollama.com/api")
        # Explicitly set API key from env
        config.api_key = os.environ.get("OLLAMA_API_KEY") or os.environ.get("ANALYSIS_LLM_API_KEY")
        self.llm = create_llm_service(config=config)

    async def analyze_block(self, sub_question: str, block_id: str) -> dict:
        """Analyze a single block's sub-question"""
        try:
            logger.info(f"  [{block_id}] Analyzing: {sub_question[:60]}...")

            response = await self.llm.simple_completion(
                prompt=sub_question,
                max_tokens=1000,
            )

            if not response.get("success"):
                return {
                    "status": "failed",
                    "error": response.get("error", "Unknown error"),
                }

            content = response.get("content", "")

            # Try to parse as JSON, otherwise return as text
            try:
                result_data = json.loads(content)
            except json.JSONDecodeError:
                result_data = {"text": content}

            return {
                "status": "complete",
                "resultData": result_data,
            }

        except Exception as e:
            logger.error(f"  [{block_id}] Analysis failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
            }


# ── Main Pipeline ────────────────────────────────────────────────────────────
async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline_async.py \"your question here\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]
    user_id = sys.argv.get("user_id", "async-user")
    session_id = sys.argv.get("session_id", f"async-{uuid.uuid4().hex[:8]}")
    start_time = time.monotonic()

    logger.info("=" * 60)
    logger.info(f"Question: {question}")
    logger.info(f"session_id: {session_id}")
    logger.info("=" * 60)

    # Initialize database and services
    db_client = MongoDBClient()
    try:
        await db_client.connect()
        repo = RepositoryManager(db_client)
        await repo.initialize()

        # ── Step 1: UIPlanner ─────────────────────────────────────────────────
        _banner(1, "UIPlanner — decompose question into blocks")
        ui_config = LLMConfig.for_task("UI_PLANNER")
        ui_config.service_name = "ui-planner"
        ui_config.max_tokens = 4000
        ui_config.base_url = os.getenv("OLLAMA_BASE_URL", "https://ollama.com/api")
        ui_config.api_key = os.environ.get("OLLAMA_API_KEY") or os.environ.get("UI_PLANNER_LLM_API_KEY")
        ui_llm = create_llm_service(config=ui_config)

        ui_planner = UIPlanner(llm_service=ui_llm)
        raw_plan = await ui_planner.plan(question)

        plan = {
            "title": raw_plan.get("title", ""),
            "subtitle": raw_plan.get("subtitle", ""),
            "layout": raw_plan.get("layout", "grid"),
            "blocks": raw_plan.get("blocks", []),
        }

        logger.info(f"✅ Plan: '{plan['title']}' — {len(plan['blocks'])} block(s)")

        # ── Step 2: Persist to MongoDB ─────────────────────────────────────────
        _banner(2, "DashboardRepository.create() — persist plan to MongoDB")

        block_models = [
            BlockPlanModel(
                block_id      = f"b{i}",
                sequence      = i,
                block_spec_id = b.get("blockId", f"block-{i}"),
                category      = b.get("category", ""),
                title         = b.get("title", ""),
                dataContract  = b.get("dataContract", {}),
                sub_question  = b.get("sub_question", ""),
                canonical_params = b.get("canonical_params", {}),
                cache_key     = b.get("cache_key", ""),
                script_key    = b.get("script_key") or None,
                script_params = b.get("script_params") or None,
            )
            for i, b in enumerate(plan["blocks"])
        ]

        dashboard = DashboardPlanModel(
            userId           = user_id,
            sessionId        = session_id,
            messageId        = None,
            originalQuestion = question,
            title            = plan["title"],
            subtitle         = plan["subtitle"],
            layout           = plan["layout"],
            blocks           = block_models,
        )

        dashboard_id = await repo.dashboard.create(dashboard)
        logger.info(f"✅ dashboard_id = {dashboard_id}")

        # ── Step 3: Inline Analysis (skip queue/PM2) ───────────────────────
        _banner(3, "Inline Analysis — analyze blocks directly (no queue)")

        analyzer = InlineBlockAnalyzer()

        for i, block in enumerate(plan["blocks"]):
            block_id = f"b{i}"
            sub_question = block.get("sub_question", "")

            # Update block status to running
            await repo.dashboard.update_block_status(
                dashboard_id=dashboard_id,
                block_id=block_id,
                status=BlockStatus.RUNNING,
            )

            # Analyze the block
            analysis_result = await analyzer.analyze_block(sub_question, block_id)

            # Update block status and result
            if analysis_result.get("status") == "complete":
                await repo.dashboard.update_block_status(
                    dashboard_id=dashboard_id,
                    block_id=block_id,
                    status=BlockStatus.COMPLETE,
                    result_data=analysis_result.get("resultData"),
                )
                logger.info(f"  ✅ [{block_id}] Complete")
            else:
                await repo.dashboard.update_block_status(
                    dashboard_id=dashboard_id,
                    block_id=block_id,
                    status=BlockStatus.FAILED,
                    error=analysis_result.get("error"),
                )
                logger.warning(f"  ❌ [{block_id}] Failed: {analysis_result.get('error')}")

        # ── Fetch final results from MongoDB ─────────────────────────────────
        _banner(4, "Fetch Results — retrieve final dashboard from MongoDB")

        doc = await db_client.db["dashboard_plans"].find_one(
            {"dashboardId": dashboard_id}, {"_id": 0}
        )

        blocks = doc.get("blocks", [])
        final_blocks = [
            {
                "block_id": b.get("block_id"),
                "title": b.get("title"),
                "category": b.get("category"),
                "status": b.get("status"),
                "has_result": bool(b.get("result_data")),
                "resultData": b.get("result_data"),
                "error": b.get("error"),
            }
            for b in blocks
        ]

        elapsed = time.monotonic() - start_time
        complete = sum(1 for b in final_blocks if b["status"] == "complete")
        failed = sum(1 for b in final_blocks if b["status"] == "failed")

        # ── Final Result ───────────────────────────────────────────────────────
        result = {
            "question": question,
            "dashboard_id": dashboard_id,
            "elapsed_s": round(elapsed, 1),
            "plan_title": plan["title"],
            "cache_hits": 0,  # No cache check in this version
            "jobs_enqueued": len(plan["blocks"]),
            "summary": {
                "total": len(plan["blocks"]),
                "complete": complete,
                "failed": failed,
                "pending": 0,
            },
            "blocks": final_blocks,
        }

        out = save_output(result, "final")
        logger.info(f"Final result saved → {out}")

        _banner(0, f"DONE — {complete}/{len(plan['blocks'])} complete ({elapsed:.1f}s)")

        # Output final result as JSON (for API to parse)
        print(json.dumps(result, indent=2, default=str))

        sys.exit(0 if failed == 0 else 1)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    finally:
        await db_client.disconnect()


# Need to import time
import time

if __name__ == "__main__":
    asyncio.run(main())