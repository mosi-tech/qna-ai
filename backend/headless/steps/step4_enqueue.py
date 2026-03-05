#!/usr/bin/env python3
"""
Step 4 — MongoAnalysisQueue.enqueue_analysis()

Enqueue one or more sub_questions into the analysis queue and confirm the
job documents were created correctly in MongoDB.

Two modes:
  1. Single sub_question (positional arg) — enqueues one job with fake or
     supplied dashboard/block metadata.
  2. --plan-stdin / --plan-file — reads a step1/step2 plan and enqueues
     every block's sub_question in one pass.

Usage:
    # Enqueue a single sub_question (fake metadata generated automatically)
    python step4_enqueue.py "What is QQQ's current price and daily change?"

    # With explicit metadata
    python step4_enqueue.py "What is QQQ's price?" \\
        --dashboard-id abc123 --block-id b0

    # Enqueue all blocks from a saved step1 output
    python step4_enqueue.py --plan-file output/step1_20260304_130000.json

    # Pipe from step1
    python step1_plan.py "QQQ performance" | python step4_enqueue.py --plan-stdin

    # From backend/ root:
    python headless/steps/step4_enqueue.py "What is QQQ's price?"
"""

import asyncio
import json
import sys
import os
import argparse
import uuid
from datetime import datetime

# ── Path setup ────────────────────────────────────────────────────────────────
_DIR     = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.normpath(os.path.join(_DIR, "..", ".."))
_OUTPUT  = os.path.join(_DIR, "output")
sys.path.insert(0, _BACKEND)

from dotenv import load_dotenv
load_dotenv(os.path.join(_BACKEND, "apiServer", ".env"))

# ── Imports ───────────────────────────────────────────────────────────────────
import logging
logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

logger = logging.getLogger("step4")
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[step4] %(message)s"))
logger.addHandler(_handler)
logger.propagate = False

from shared.db.mongodb_client import MongoDBClient
from shared.db.repositories import RepositoryManager
from shared.queue.analysis_queue import MongoAnalysisQueue


# ── Helpers ───────────────────────────────────────────────────────────────────
def save_output(result: dict) -> str:
    os.makedirs(_OUTPUT, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(_OUTPUT, f"step4_{ts}.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return path


def _fake_id() -> str:
    return str(uuid.uuid4())


def _build_job_input(
    sub_question: str,
    dashboard_id: str,
    block_id: str,
    block: dict | None = None,
    user_id: str = "test",
    session_id: str = "test-session",
) -> dict:
    """Construct the analysis_data dict expected by enqueue_analysis()."""
    metadata: dict = {
        "dashboard_id":   dashboard_id,
        "block_id":       block_id,
        "source":         "step4_enqueue",
    }
    if block:
        metadata["cache_key"]       = block.get("cache_key", "")
        metadata["script_key"]      = block.get("script_key", "")
        metadata["script_params"]   = block.get("script_params", {})
        metadata["canonical_params"] = block.get("canonical_params", {})

    return {
        "user_question":   sub_question,
        "user_message_id": _fake_id(),
        "session_id":      session_id,
        "message_id":      _fake_id(),
        "metadata":        metadata,
    }


async def _read_back_job(queue: MongoAnalysisQueue, job_id: str) -> dict | None:
    """Read a job document directly from the collection (non-destructive)."""
    try:
        doc = await queue.collection.find_one({"job_id": job_id})
        return doc
    except Exception as e:
        logger.warning("Could not read back job %s: %s", job_id, e)
        return None


# ── Core enqueue logic ────────────────────────────────────────────────────────
async def enqueue_jobs(
    jobs: list[dict],
    db_raw,
    pretty: bool,
) -> dict:
    """
    Enqueue a list of job dicts and return a summary result.

    Each item in ``jobs`` must have keys:
        sub_question, dashboard_id, block_id, block (optional)
    """
    queue = MongoAnalysisQueue(db_raw)

    enqueued = []
    for item in jobs:
        analysis_data = _build_job_input(
            sub_question  = item["sub_question"],
            dashboard_id  = item["dashboard_id"],
            block_id      = item["block_id"],
            block         = item.get("block"),
        )

        job_id = await queue.enqueue_analysis(analysis_data)
        logger.info("Enqueued job_id=%s  block_id=%s", job_id, item["block_id"])

        # Non-destructive read-back
        doc = await _read_back_job(queue, job_id)

        entry = {
            "job_id":       job_id,
            "sub_question": item["sub_question"],
            "dashboard_id": item["dashboard_id"],
            "block_id":     item["block_id"],
            "status":       doc.get("status") if doc else None,
            "created_at":   str(doc.get("created_at", "")) if doc else None,
            "metadata":     doc.get("metadata") if doc else None,
        }
        enqueued.append(entry)

    return {"enqueued": enqueued, "count": len(enqueued)}


# ── Main ──────────────────────────────────────────────────────────────────────
async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Step 4 — Enqueue sub_questions into the analysis queue",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "sub_question", nargs="?",
        help="Sub-question to enqueue (single job mode)",
    )
    parser.add_argument("--dashboard-id", dest="dashboard_id", default=None,
                        help="dashboard_id for metadata (auto-generated if omitted)")
    parser.add_argument("--block-id",     dest="block_id",     default=None,
                        help="block_id for metadata (auto-generated if omitted)")
    parser.add_argument("--plan-stdin",   action="store_true",
                        help="Read plan JSON from stdin (pipe from step1/step2)")
    parser.add_argument("--plan-file",    dest="plan_file",    default=None,
                        help="Path to a saved step1/step2 JSON output file")
    parser.add_argument("--pretty",       action="store_true",
                        help="Pretty-print JSON output")
    args = parser.parse_args()

    # ── Determine what to enqueue ─────────────────────────────────────────────
    jobs: list[dict] = []

    if args.plan_stdin or args.plan_file:
        # Bulk enqueue from plan
        if args.plan_stdin:
            logger.info("Reading plan from stdin…")
            raw = sys.stdin.read()
        else:
            logger.info("Reading plan from %s…", args.plan_file)
            with open(args.plan_file) as f:
                raw = f.read()

        try:
            plan = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"ERROR: invalid plan JSON: {e}", file=sys.stderr)
            sys.exit(1)

        dashboard_id = args.dashboard_id or _fake_id()
        blocks = plan.get("blocks", [])
        if not blocks:
            print("ERROR: plan has no blocks", file=sys.stderr)
            sys.exit(1)

        for i, block in enumerate(blocks):
            sub_q = block.get("sub_question", "")
            if not sub_q:
                logger.warning("Block %d has no sub_question, skipping", i)
                continue
            jobs.append({
                "sub_question": sub_q,
                "dashboard_id": dashboard_id,
                "block_id":     block.get("block_id", f"b{i}"),
                "block":        block,
            })

    elif args.sub_question:
        jobs.append({
            "sub_question": args.sub_question,
            "dashboard_id": args.dashboard_id or _fake_id(),
            "block_id":     args.block_id     or "b0",
            "block":        None,
        })

    else:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # ── Connect and enqueue ───────────────────────────────────────────────────
    db_client = MongoDBClient()
    try:
        await db_client.connect()
        repo = RepositoryManager(db_client)
        await repo.initialize()

        # MongoAnalysisQueue expects the raw motor database (db_client.db),
        # not the MongoDBClient wrapper — matching how analysis_worker.py does it.
        result = await enqueue_jobs(jobs, db_client.db, args.pretty)

        out_path = save_output(result)
        logger.info(
            "Enqueued %d job(s). Saved → %s",
            result["count"],
            out_path,
        )

        if args.pretty:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(json.dumps(result, default=str))

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await db_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
