#!/usr/bin/env python3
"""
Headless dashboard runner — no browser required.

Runs the complete dashboard pipeline (UIPlanner → DashboardOrchestrator →
block execution) and prints the final JSON result to stdout.

Usage:
    cd backend
    python infrastructure/headless/run_dashboard_headless.py "How is QQQ performing?"
    python infrastructure/headless/run_dashboard_headless.py "Compare VOO vs QQQ" --timeout 180 --pretty
"""
import argparse
import asyncio
import json
import os
import sys
import time

from dotenv import load_dotenv

# Ensure the monorepo backend root is on sys.path
# Script lives at backend/infrastructure/headless/ → two levels up reaches backend/
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_SCRIPT_DIR, "..", ".."))

# Load .env from backend/apiServer/ (same level as server.py)
load_dotenv(os.path.join(_SCRIPT_DIR, "..", "..", "apiServer", ".env"))

from shared.db.mongodb_client import MongoDBClient
from shared.db.repositories import RepositoryManager
from shared.queue.analysis_queue import get_analysis_queue, initialize_analysis_queue
from shared.services.block_cache_service import create_block_cache_service
from shared.services.dashboard_orchestrator import create_dashboard_orchestrator
from shared.services.ui_planner import create_ui_planner


async def run(question: str, timeout: int, pretty: bool) -> None:
    # ── Wire up services ────────────────────────────────────────────────────
    client = MongoDBClient()
    repo_manager = RepositoryManager(client)
    await repo_manager.initialize()

    # Analysis queue must be initialized before it can be used
    initialize_analysis_queue(client.db)

    ui_planner   = create_ui_planner()
    block_cache  = create_block_cache_service(repo_manager.dashboard)
    orchestrator = create_dashboard_orchestrator(
        repo_manager=repo_manager,
        analysis_queue=get_analysis_queue(),
        ui_planner=ui_planner,
        block_cache=block_cache,
    )

    # ── Plan and dispatch ────────────────────────────────────────────────────
    print(f"[headless] Planning dashboard for: {question!r}", flush=True)
    plan = await orchestrator.create_dashboard(
        question=question,
        user_id="headless",
        session_id="",       # no SSE session — block_update events are silently skipped
        message_id="headless",
        force_refresh=False,
    )

    dashboard_id  = plan["dashboard_id"]
    block_count   = len(plan.get("blocks", []))
    print(f"[headless] Dashboard created: {dashboard_id} ({block_count} blocks)", flush=True)

    # ── Poll until all blocks settle ─────────────────────────────────────────
    current  = plan
    deadline = time.time() + timeout

    while time.time() < deadline:
        statuses = {b["status"] for b in current.get("blocks", [])}
        pending  = [b["block_id"] for b in current.get("blocks", [])
                    if b["status"] not in ("complete", "cached", "failed")]

        if not pending:
            print("[headless] All blocks settled.", flush=True)
            break

        print(f"[headless] Waiting… pending blocks: {pending}", flush=True)

        # Reconcile: check if any executions have completed and update block statuses
        reconciled = await orchestrator.reconcile_pending_blocks(dashboard_id)
        if reconciled:
            print(f"[headless] Reconciled {reconciled} block(s).", flush=True)

        await asyncio.sleep(2)

        current = await repo_manager.dashboard.get_by_id(dashboard_id)
    else:
        print("[headless] TIMEOUT — returning partial results.", flush=True)

    indent = 2 if pretty else None
    print(json.dumps(current, indent=indent, default=str))

    await repo_manager.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a dashboard pipeline headlessly and print the result."
    )
    parser.add_argument("question", help="The question to decompose into a dashboard.")
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Maximum seconds to wait for all blocks to complete (default: 120).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output.",
    )
    args = parser.parse_args()
    asyncio.run(run(args.question, args.timeout, args.pretty))
