#!/usr/bin/env python3
"""
Step 7 — Reconciler

Runs one (or more) reconciliation passes for a specific dashboard and prints
the current block statuses.  Useful for checking whether pending blocks have
advanced to complete/failed after the analysis+execution workers have finished.

Usage:
    python step7_reconcile.py --dashboard-id <uuid>
    python step7_reconcile.py --dashboard-id <uuid> --watch         # poll every 3s
    python step7_reconcile.py --dashboard-id <uuid> --watch --timeout 120

    # From backend/ root:
    python headless/steps/step7_reconcile.py --dashboard-id <uuid>

What to check:
    - Pending blocks advance to "complete" or "failed" after workers finish
    - resultData is non-null for completed blocks
    - Error messages are informative for failed blocks
    - With --watch, exits cleanly when all blocks are settled (or timeout)
"""

import asyncio
import json
import sys
import os
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

# ── Imports ───────────────────────────────────────────────────────────────────
import logging
logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

logger = logging.getLogger("step7")
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[step7] %(message)s"))
logger.addHandler(_handler)
logger.propagate = False

from shared.db.mongodb_client import MongoDBClient
from shared.db.repositories import RepositoryManager
from shared.queue.analysis_queue import MongoAnalysisQueue
from shared.services.block_cache_service import create_block_cache_service
from shared.services.dashboard_orchestrator import DashboardOrchestrator

# ── Settled statuses ──────────────────────────────────────────────────────────
_PENDING_STATUSES = {"pending", "running", "queued"}

# ── Helpers ───────────────────────────────────────────────────────────────────

def save_output(result: dict) -> str:
    os.makedirs(_OUTPUT, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(_OUTPUT, f"step7_{ts}.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return path


async def fetch_block_statuses(db_client: MongoDBClient, dashboard_id: str) -> list[dict]:
    """Return the blocks array from the dashboard document."""
    doc = await db_client.db["dashboard_plans"].find_one(
        {"dashboardId": dashboard_id}, {"_id": 0}
    )
    if not doc:
        return []
    return doc.get("blocks", [])


def _block_row(b: dict) -> dict:
    """Extract a clean summary row for a block."""
    return {
        "block_id":    b.get("block_id") or b.get("blockId"),
        "title":       b.get("title", ""),
        "status":      b.get("status", "unknown"),
        "analysisId":  b.get("analysisId") or b.get("analysis_id"),
        "executionId": b.get("executionId") or b.get("execution_id"),
        "has_result":  bool(b.get("resultData") or b.get("result_data")),
        "error":       b.get("error"),
    }


def _print_table(blocks: list[dict], pass_num: int, reconciled: int) -> None:
    """Print a human-readable block status table to stderr."""
    print(
        f"\n[step7] Pass #{pass_num}  — reconciled {reconciled} block(s) this pass",
        file=sys.stderr,
    )
    header = f"  {'block_id':<12}  {'status':<10}  {'analysisId':<36}  {'executionId':<36}  result  error"
    print(header, file=sys.stderr)
    print("  " + "-" * (len(header) - 2), file=sys.stderr)
    for b in blocks:
        row = _block_row(b)
        print(
            f"  {str(row['block_id']):<12}  "
            f"{str(row['status']):<10}  "
            f"{str(row['analysisId'] or ''):<36}  "
            f"{str(row['executionId'] or ''):<36}  "
            f"{'yes' if row['has_result'] else 'no ':<6}  "
            f"{row['error'] or ''}",
            file=sys.stderr,
        )


def _all_settled(blocks: list[dict]) -> bool:
    return all(
        b.get("status", "pending") not in _PENDING_STATUSES for b in blocks
    )


# ── Main ──────────────────────────────────────────────────────────────────────
async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Step 7 — Reconcile pending dashboard blocks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--dashboard-id", dest="dashboard_id", required=True,
                        help="UUID of the dashboard to reconcile")
    parser.add_argument("--watch", action="store_true",
                        help="Poll every 3s until all blocks are settled")
    parser.add_argument("--interval", type=float, default=3.0,
                        help="Seconds between poll passes when --watch is set (default 3)")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Max seconds to wait in --watch mode (default 300)")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty-print JSON output")
    args = parser.parse_args()

    db_client = MongoDBClient()
    try:
        await db_client.connect()
        repo = RepositoryManager(db_client)
        await repo.initialize()

        # Build lightweight orchestrator — ui_planner not needed for reconciliation
        queue      = MongoAnalysisQueue(db_client.db)
        block_cache = create_block_cache_service(repo.dashboard)

        orchestrator = DashboardOrchestrator(
            repo_manager=repo,
            analysis_queue=queue,
            ui_planner=None,   # not needed for reconcile
            block_cache=block_cache,
        )

        deadline    = time.monotonic() + args.timeout
        pass_num    = 0
        total_reconciled = 0

        while True:
            pass_num += 1
            logger.info("Pass #%d — calling reconcile_pending_blocks …", pass_num)

            try:
                reconciled = await orchestrator.reconcile_pending_blocks(args.dashboard_id)
            except Exception as exc:
                print(f"ERROR during reconcile pass #{pass_num}: {exc}", file=sys.stderr)
                sys.exit(1)

            total_reconciled += reconciled

            # Fetch fresh block statuses for display
            blocks = await fetch_block_statuses(db_client, args.dashboard_id)
            if not blocks:
                print(f"ERROR: Dashboard '{args.dashboard_id}' not found.", file=sys.stderr)
                sys.exit(1)

            _print_table(blocks, pass_num, reconciled)

            settled = _all_settled(blocks)

            if settled:
                logger.info("All blocks settled after %d pass(es).", pass_num)
                break

            if not args.watch:
                # Single pass — report whatever state we have
                break

            if time.monotonic() >= deadline:
                print(
                    f"\n[step7] Timeout after {args.timeout}s — "
                    f"{sum(1 for b in blocks if b.get('status') in _PENDING_STATUSES)} "
                    f"block(s) still pending.",
                    file=sys.stderr,
                )
                break

            remaining = deadline - time.monotonic()
            sleep_for = min(args.interval, max(0, remaining))
            logger.info("Sleeping %.1fs …", sleep_for)
            await asyncio.sleep(sleep_for)

        # ── Build output JSON ────────────────────────────────────────────────
        blocks = await fetch_block_statuses(db_client, args.dashboard_id)
        rows   = [_block_row(b) for b in blocks]

        result = {
            "dashboard_id":      args.dashboard_id,
            "passes":            pass_num,
            "total_reconciled":  total_reconciled,
            "all_settled":       _all_settled(blocks),
            "blocks":            rows,
            "summary": {
                "total":    len(rows),
                "complete": sum(1 for r in rows if r["status"] == "complete"),
                "failed":   sum(1 for r in rows if r["status"] == "failed"),
                "pending":  sum(1 for r in rows if r["status"] in _PENDING_STATUSES),
            },
        }

        out_path = save_output(result)
        logger.info("Saved → %s", out_path)

        indent = 2 if args.pretty else None
        print(json.dumps(result, indent=indent, default=str))

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    finally:
        await db_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
