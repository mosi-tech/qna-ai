#!/usr/bin/env python3
"""
Step 2 — DashboardRepository.create()

Persists a dashboard plan (from step1 or inline JSON) to MongoDB and reads
it back to verify round-trip integrity.

Usage:
    # From a plan JSON string:
    python step2_persist.py --plan '{"title":"...", "blocks":[...]}'

    # Pipe from step1 (original question passed via --question):
    python step1_plan.py "How is QQQ performing?" | python step2_persist.py --stdin --question "How is QQQ performing?"

    # Load a saved step1 output file:
    python step2_persist.py --plan-file output/step1_20260304_120000.json

    # With custom user/session:
    python step2_persist.py --plan-file output/step1_20260304_120000.json --user-id alice --session-id sess123

    cd backend
    python headless/steps/step2_persist.py --plan-file headless/steps/output/step1_20260304_120000.json --pretty
"""

import asyncio
import json
import sys
import os
import argparse
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

logger = logging.getLogger("step2")
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[step2] %(message)s"))
logger.addHandler(_handler)
logger.propagate = False

from shared.db.mongodb_client import MongoDBClient
from shared.db.repositories import RepositoryManager
from shared.db.schemas import DashboardPlanModel, BlockPlanModel


# ── Helpers ───────────────────────────────────────────────────────────────────
def save_output(result: dict) -> str:
    """Persist result JSON to output/ and return the saved file path."""
    os.makedirs(_OUTPUT, exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(_OUTPUT, f"step2_{ts}.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return path


def plan_from_args(args) -> dict:
    """Load the plan JSON from --plan, --stdin, or --plan-file."""
    if args.stdin:
        raw = sys.stdin.read().strip()
        if not raw:
            raise ValueError("--stdin: no data received on stdin")
        return json.loads(raw)
    if args.plan_file:
        with open(args.plan_file) as f:
            return json.load(f)
    if args.plan:
        return json.loads(args.plan)
    raise ValueError("Provide one of --plan, --stdin, or --plan-file")


def build_dashboard_model(
    plan: dict,
    user_id: str,
    session_id: str,
    question: str,
) -> DashboardPlanModel:
    """Convert a step1 plan dict into a DashboardPlanModel ready for insertion."""

    raw_blocks = plan.get("blocks", [])
    if not raw_blocks:
        raise ValueError("Plan has no blocks")

    block_models = []
    for i, b in enumerate(raw_blocks):
        block_models.append(
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
        )

    return DashboardPlanModel(
        userId           = user_id,
        sessionId        = session_id or None,
        messageId        = None,
        originalQuestion = question or plan.get("title", ""),
        title            = plan.get("title", ""),
        subtitle         = plan.get("subtitle", ""),
        layout           = plan.get("layout", "grid"),
        blocks           = block_models,
    )


# ── Main ──────────────────────────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(
        description="Step 2 — Persist a dashboard plan to MongoDB."
    )

    source = parser.add_mutually_exclusive_group()
    source.add_argument("--plan",      help="Plan JSON as a string")
    source.add_argument("--stdin",     action="store_true", help="Read plan JSON from stdin (pipe from step1)")
    source.add_argument("--plan-file", metavar="PATH", help="Path to a step1 output JSON file")

    parser.add_argument("--question",   default="",    help="Original question (used as originalQuestion in DB)")
    parser.add_argument("--user-id",    default="test", help="userId to store (default: test)")
    parser.add_argument("--session-id", default="",    help="sessionId to store (default: empty)")
    parser.add_argument("--pretty",     action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    # ── Load plan ─────────────────────────────────────────────────────────────
    try:
        plan = plan_from_args(args)
    except Exception as e:
        print(f"ERROR loading plan: {e}", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)

    logger.info(f"Plan loaded: '{plan.get('title')}' — {len(plan.get('blocks', []))} block(s)")

    db = MongoDBClient()
    try:
        await db.connect()
        repo = RepositoryManager(db)
        await repo.initialize()

        # ── Build model ───────────────────────────────────────────────────────
        try:
            model = build_dashboard_model(
                plan,
                user_id    = args.user_id,
                session_id = args.session_id,
                question   = args.question or plan.get("title", ""),
            )
        except Exception as e:
            print(f"ERROR building model: {e}", file=sys.stderr)
            sys.exit(1)

        logger.info(f"Persisting dashboard_id={model.dashboard_id} …")

        # ── Insert ────────────────────────────────────────────────────────────
        await repo.dashboard.create(model)

        # ── Read back to verify ───────────────────────────────────────────────
        doc = await repo.dashboard.get_by_id(model.dashboard_id)
        if not doc:
            raise RuntimeError(f"Read-back failed: dashboard_id={model.dashboard_id} not found after insert")

        blocks_back = doc.get("blocks", [])
        logger.info(f"Read-back OK — {len(blocks_back)} block(s) in DB")

        # ── Build result ──────────────────────────────────────────────────────
        result = {
            "dashboard_id": model.dashboard_id,
            "block_count":  len(blocks_back),
            "user_id":      doc.get("userId", args.user_id),
            "session_id":   doc.get("sessionId", ""),
            "original_question": doc.get("originalQuestion", ""),
            "blocks": [
                {
                    "block_id":     b.get("block_id", b.get("blockId", "")),
                    "status":       b.get("status", "pending"),
                    "cache_key":    b.get("cache_key", b.get("cacheKey", "")),
                    "script_key":   b.get("script_key", b.get("scriptKey")),
                    "script_params": b.get("script_params", b.get("scriptParams")),
                    "analysisId":   b.get("analysisId"),
                    "executionId":  b.get("executionId"),
                    "resultData":   b.get("resultData"),
                }
                for b in blocks_back
            ],
        }

        out_path = save_output(result)
        logger.info(f"Saved → {out_path}")

        if args.pretty:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(json.dumps(result, default=str))

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
