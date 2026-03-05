#!/usr/bin/env python3
"""
run_all_steps — Full pipeline smoke test

Chains steps 1 → 7 in a single command, printing output after each step.
Shares one MongoDB connection and one set of services across all steps.

Steps executed inline (no subprocesses):
  Step 1 — UIPlanner.plan()                   → block plan
  Step 2 — DashboardRepository.create()       → dashboard_id
  Step 3 — BlockCacheService per block        → cache hit / miss report
  Step 4 — MongoAnalysisQueue.enqueue()       → job_ids (queued for pm2 worker)
  Wait   — reconcile_pending_blocks() loop    → polls every 5s until settled
  Step 7 — final block-status snapshot        → completion summary

Usage:
    cd backend
    python headless/steps/run_all_steps.py "How is QQQ performing over the last 6 months?"
    python headless/steps/run_all_steps.py "Compare VOO vs QQQ" --timeout 600 --pretty
    python headless/steps/run_all_steps.py "..." --force-refresh --poll-interval 3

Requirements:
    pm2 workers (analysis-queue-worker and execution-queue-worker) must be
    running to actually process the queued jobs.  Use `pm2 list` to check.

    To run fully headless without pm2, use step5_analysis.py + step6_execution.py
    per block manually, then run step7_reconcile.py.
"""

import asyncio
import json
import sys
import os
import uuid
import argparse
import time
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
logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

logger = logging.getLogger("run_all")
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[run_all] %(message)s"))
logger.addHandler(_handler)
logger.propagate = False

# ── Imports ───────────────────────────────────────────────────────────────────
from shared.db.mongodb_client import MongoDBClient
from shared.db.repositories import RepositoryManager
from shared.db.schemas import DashboardPlanModel, BlockPlanModel, BlockStatus
from shared.queue.analysis_queue import MongoAnalysisQueue
from shared.services.ui_planner import create_ui_planner
from shared.services.block_cache_service import (
    create_block_cache_service,
    compute_cache_key,
    compute_script_key,
    extract_script_params,
)
from shared.services.dashboard_orchestrator import DashboardOrchestrator


# ── Settled statuses ──────────────────────────────────────────────────────────
_PENDING = {"pending", "running", "queued"}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _banner(step: int, title: str) -> None:
    sep = "─" * 60
    print(f"\n{sep}", file=sys.stderr)
    print(f"[run_all]  STEP {step} — {title}", file=sys.stderr)
    print(sep, file=sys.stderr)


def _print_json(obj: dict, pretty: bool) -> None:
    indent = 2 if pretty else None
    print(json.dumps(obj, indent=indent, default=str))


def save_output(result: dict, label: str) -> str:
    os.makedirs(_OUTPUT, exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(_OUTPUT, f"run_all_{label}_{ts}.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return path


def _all_settled(blocks: list[dict]) -> bool:
    return all(b.get("status", "pending") not in _PENDING for b in blocks)


async def _fetch_blocks(db_client: MongoDBClient, dashboard_id: str) -> list[dict]:
    doc = await db_client.db["dashboard_plans"].find_one(
        {"dashboardId": dashboard_id}, {"_id": 0}
    )
    return doc.get("blocks", []) if doc else []


# ── Step 1 ────────────────────────────────────────────────────────────────────
async def run_step1(question: str, pretty: bool) -> dict:
    _banner(1, "UIPlanner — decompose question into blocks")
    ui_planner = create_ui_planner()
    raw = await ui_planner.plan(question)

    plan = {
        "title":    raw.get("title", ""),
        "subtitle": raw.get("subtitle", ""),
        "layout":   raw.get("layout", "grid"),
        "blocks": [
            {
                "blockId":          b.get("blockId", ""),
                "category":         b.get("category", ""),
                "title":            b.get("title", ""),
                "sub_question":     b.get("sub_question", ""),
                "canonical_params": b.get("canonical_params", {}),
                "cache_key":        b.get("cache_key", ""),
                "script_key":       b.get("script_key", ""),
                "script_params":    b.get("script_params", {}),
            }
            for b in raw.get("blocks", [])
        ],
    }

    logger.info("Plan: '%s' — %d block(s)", plan["title"], len(plan["blocks"]))
    for b in plan["blocks"]:
        logger.info("  • [%s] %s", b["blockId"], b["title"])

    out = save_output(plan, "step1")
    logger.info("Saved → %s", out)
    _print_json(plan, pretty)
    return plan


# ── Step 2 ────────────────────────────────────────────────────────────────────
async def run_step2(
    plan: dict,
    question: str,
    user_id: str,
    session_id: str,
    dashboard_repo,
    pretty: bool,
) -> str:
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
        sessionId        = session_id or None,
        messageId        = None,
        originalQuestion = question,
        title            = plan["title"],
        subtitle         = plan["subtitle"],
        layout           = plan["layout"],
        blocks           = block_models,
    )

    dashboard_id = await dashboard_repo.create(dashboard)
    logger.info("dashboard_id = %s", dashboard_id)

    result = {
        "dashboard_id": dashboard_id,
        "block_count":  len(block_models),
        "blocks": [
            {"block_id": bm.block_id, "title": bm.title, "status": "pending"}
            for bm in block_models
        ],
    }

    out = save_output(result, "step2")
    logger.info("Saved → %s", out)
    _print_json(result, pretty)
    return dashboard_id


# ── Step 3 ────────────────────────────────────────────────────────────────────
async def run_step3(plan: dict, block_cache, analysis_repo, pretty: bool) -> dict:
    _banner(3, "BlockCacheService — cache lookup per block")

    hits, misses = [], []
    for block in plan["blocks"]:
        sk = block.get("script_key", "")
        if not sk:
            misses.append(block)
            continue
        cached = await block_cache.lookup_script(sk, analysis_repo)
        if cached:
            logger.info("  HIT  script_key=%s  block=%s", sk, block["blockId"])
            hits.append({**block, "cached_analysis_id": cached.get("analysisId")})
        else:
            logger.info("  MISS script_key=%s  block=%s", sk, block["blockId"])
            misses.append(block)

    result = {
        "hit_count":  len(hits),
        "miss_count": len(misses),
        "hits":  [{"blockId": b["blockId"], "script_key": b.get("script_key"), "cached_analysis_id": b.get("cached_analysis_id")} for b in hits],
        "misses": [{"blockId": b["blockId"], "script_key": b.get("script_key")} for b in misses],
    }

    out = save_output(result, "step3")
    logger.info("Cache: %d hit(s), %d miss(es)", len(hits), len(misses))
    logger.info("Saved → %s", out)
    _print_json(result, pretty)
    return result


# ── Step 4 ────────────────────────────────────────────────────────────────────
async def run_step4(
    plan: dict,
    dashboard_id: str,
    session_id: str,
    user_id: str,
    queue: MongoAnalysisQueue,
    dashboard_repo,
    pretty: bool,
) -> list[dict]:
    _banner(4, "MongoAnalysisQueue.enqueue_analysis() — enqueue all blocks")

    enqueued = []
    for i, block in enumerate(plan["blocks"]):
        block_id = f"b{i}"
        job_id = await queue.enqueue_analysis({
            "session_id":     session_id,
            "user_question":  block["sub_question"],
            "user_id":        user_id,
            "message_id":     None,
            "user_message_id": None,
            "metadata": {
                "dashboard_id":    dashboard_id,
                "block_id":        block_id,
                "cache_key":       block.get("cache_key", ""),
                "script_key":      block.get("script_key", ""),
                "script_params":   block.get("script_params", {}),
                "canonical_params": block.get("canonical_params", {}),
            },
        })

        # Stamp the block's analysisId so the reconciler can correlate it
        await dashboard_repo.update_block_status(
            dashboard_id=dashboard_id,
            block_id=block_id,
            status=BlockStatus.PENDING,
            analysis_id=job_id,
        )

        logger.info("  Enqueued %s → job_id=%s", block_id, job_id)
        enqueued.append({
            "block_id":     block_id,
            "sub_question": block["sub_question"],
            "job_id":       job_id,
        })

    result = {"dashboard_id": dashboard_id, "enqueued": enqueued}
    out = save_output(result, "step4")
    logger.info("%d job(s) enqueued.  Saved → %s", len(enqueued), out)
    _print_json(result, pretty)
    return enqueued


# ── Step 7 / Wait loop ────────────────────────────────────────────────────────
async def run_wait(
    dashboard_id: str,
    orchestrator: DashboardOrchestrator,
    db_client: MongoDBClient,
    timeout: int,
    poll_interval: float,
    pretty: bool,
) -> dict:
    _banner(7, "Reconciler — polling until all blocks settle")
    deadline  = time.monotonic() + timeout
    pass_num  = 0
    total_rec = 0

    while True:
        pass_num += 1
        reconciled = await orchestrator.reconcile_pending_blocks(dashboard_id)
        total_rec += reconciled

        blocks = await _fetch_blocks(db_client, dashboard_id)
        settled  = _all_settled(blocks)
        complete = sum(1 for b in blocks if b.get("status") == "complete")
        failed   = sum(1 for b in blocks if b.get("status") == "failed")
        pending  = sum(1 for b in blocks if b.get("status") in _PENDING)

        logger.info(
            "Pass #%d — reconciled %d  |  complete=%d  failed=%d  pending=%d",
            pass_num, reconciled, complete, failed, pending,
        )

        if settled:
            logger.info("All blocks settled after %d pass(es).", pass_num)
            break

        if time.monotonic() >= deadline:
            logger.warning("Timeout after %ds — %d block(s) still pending.", timeout, pending)
            break

        remaining  = deadline - time.monotonic()
        sleep_for  = min(poll_interval, max(0, remaining))
        await asyncio.sleep(sleep_for)

    # Final snapshot
    blocks = await _fetch_blocks(db_client, dashboard_id)
    rows = [
        {
            "block_id":    b.get("block_id") or b.get("blockId"),
            "title":       b.get("title", ""),
            "status":      b.get("status", "unknown"),
            "analysisId":  b.get("analysisId") or b.get("analysis_id"),
            "executionId": b.get("executionId") or b.get("execution_id"),
            "has_result":  bool(b.get("resultData") or b.get("result_data")),
            "error":       b.get("error"),
        }
        for b in blocks
    ]

    result = {
        "dashboard_id":     dashboard_id,
        "passes":           pass_num,
        "total_reconciled": total_rec,
        "all_settled":      _all_settled(blocks),
        "blocks":           rows,
        "summary": {
            "total":    len(rows),
            "complete": sum(1 for r in rows if r["status"] == "complete"),
            "failed":   sum(1 for r in rows if r["status"] == "failed"),
            "pending":  sum(1 for r in rows if r["status"] in _PENDING),
        },
    }

    out = save_output(result, "step7")
    logger.info("Saved → %s", out)
    _print_json(result, pretty)
    return result


# ── Main ──────────────────────────────────────────────────────────────────────
async def main() -> None:
    parser = argparse.ArgumentParser(
        description="run_all_steps — Full dashboard pipeline smoke test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("question", nargs="?",
                        help="Question to run the full pipeline for")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Max seconds to wait for all blocks to settle (default 300)")
    parser.add_argument("--poll-interval", type=float, default=5.0, dest="poll_interval",
                        help="Seconds between reconciler polls (default 5)")
    parser.add_argument("--user-id",    dest="user_id",    default="run-all-test",
                        help="User ID stored in dashboard doc (default: run-all-test)")
    parser.add_argument("--session-id", dest="session_id", default="",
                        help="Session ID stored in dashboard doc (default: auto-generated)")
    parser.add_argument("--force-refresh", action="store_true", dest="force_refresh",
                        help="Informational flag — logged but does not change behaviour (workers always generate fresh)")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty-print JSON output after each step")
    args = parser.parse_args()

    if not args.question:
        parser.print_help(sys.stderr)
        print("ERROR: question is required", file=sys.stderr)
        sys.exit(1)

    session_id = args.session_id or f"run-all-{uuid.uuid4().hex[:8]}"
    start_wall = time.monotonic()

    logger.info("Question   : %s", args.question)
    logger.info("session_id : %s", session_id)
    logger.info("user_id    : %s", args.user_id)
    logger.info("timeout    : %ds", args.timeout)
    if args.force_refresh:
        logger.info("force_refresh flag set (note: workers always generate fresh scripts)")

    db_client = MongoDBClient()
    try:
        await db_client.connect()
        repo = RepositoryManager(db_client)
        await repo.initialize()

        queue       = MongoAnalysisQueue(db_client.db)
        block_cache = create_block_cache_service(repo.dashboard)
        ui_planner  = create_ui_planner()

        orchestrator = DashboardOrchestrator(
            repo_manager=repo,
            analysis_queue=queue,
            ui_planner=ui_planner,
            block_cache=block_cache,
        )

        # ── Step 1: Plan ─────────────────────────────────────────────────────
        plan = await run_step1(args.question, args.pretty)

        if not plan["blocks"]:
            print("ERROR: UIPlanner returned no blocks", file=sys.stderr)
            sys.exit(1)

        # ── Step 2: Persist ──────────────────────────────────────────────────
        dashboard_id = await run_step2(
            plan=plan,
            question=args.question,
            user_id=args.user_id,
            session_id=session_id,
            dashboard_repo=repo.dashboard,
            pretty=args.pretty,
        )

        # ── Step 3: Cache check ──────────────────────────────────────────────
        cache_report = await run_step3(
            plan=plan,
            block_cache=block_cache,
            analysis_repo=repo.analysis,
            pretty=args.pretty,
        )

        # ── Step 4: Enqueue all blocks ────────────────────────────────────────
        enqueued = await run_step4(
            plan=plan,
            dashboard_id=dashboard_id,
            session_id=session_id,
            user_id=args.user_id,
            queue=queue,
            dashboard_repo=repo.dashboard,
            pretty=args.pretty,
        )

        logger.info("")
        logger.info("Jobs are queued.  Waiting for pm2 workers to process them…")
        logger.info("(Use `pm2 list` to verify analysis-queue-worker + execution-queue-worker are online)")

        # ── Step 5+6: Handled by pm2 workers ─────────────────────────────────
        # ── Step 7: Poll reconciler until settled ─────────────────────────────
        final = await run_wait(
            dashboard_id=dashboard_id,
            orchestrator=orchestrator,
            db_client=db_client,
            timeout=args.timeout,
            poll_interval=args.poll_interval,
            pretty=args.pretty,
        )

        elapsed = time.monotonic() - start_wall
        summary = final["summary"]

        _banner(0, f"DONE — {summary['complete']}/{summary['total']} complete, "
                   f"{summary['failed']} failed  ({elapsed:.0f}s total)")

        # Final combined output at the end
        combined = {
            "question":     args.question,
            "dashboard_id": dashboard_id,
            "elapsed_s":    round(elapsed, 1),
            "plan_title":   plan["title"],
            "cache_hits":   cache_report["hit_count"],
            "jobs_enqueued": len(enqueued),
            "summary":      summary,
            "blocks":       final["blocks"],
        }

        out = save_output(combined, "final")
        logger.info("Final result saved → %s", out)

        sys.exit(0 if summary["failed"] == 0 and final["all_settled"] else 1)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    finally:
        await db_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
