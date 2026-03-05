#!/usr/bin/env python3
"""
Step 3 — BlockCacheService (script cache)

Three sub-commands:

    key     — Compute cache_key, script_key, and script_params from canonical_params.
               Purely local; no MongoDB needed.

    lookup  — Find an AnalysisModel tagged with a given script_key.
               Returns the matching doc or reports a MISS.

    write   — Tag an existing AnalysisModel with a script_key so future
               lookups can find and reuse its generated script.

Usage:
    # Compute keys from params (order-independent; no DB needed)
    python step3_cache.py key --params '{"ticker":"QQQ","metric":"price","period":"6m"}'
    python step3_cache.py key --params '{"metric":"price","ticker":"SPY","period":"1y"}'

    # Look up a cached script by script_key
    python step3_cache.py lookup --key 8a789f21fa4b5af6

    # Tag an AnalysisModel (--analysis-id) with a script_key
    python step3_cache.py write --analysis-id <uuid> --key 8a789f21fa4b5af6

    # From backend/ root:
    python headless/steps/step3_cache.py key --params '{"ticker":"QQQ","metric":"price"}'
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

logger = logging.getLogger("step3")
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[step3] %(message)s"))
logger.addHandler(_handler)
logger.propagate = False

from shared.db.mongodb_client import MongoDBClient
from shared.db.repositories import RepositoryManager
from shared.services.block_cache_service import (
    compute_cache_key,
    compute_script_key,
    extract_script_params,
    create_block_cache_service,
)


# ── Helpers ───────────────────────────────────────────────────────────────────
def save_output(result: dict, label: str = "step3") -> str:
    """Persist result JSON to output/ and return the saved file path."""
    os.makedirs(_OUTPUT, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(_OUTPUT, f"step3_{label}_{ts}.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return path


def _emit(result: dict, pretty: bool) -> None:
    if pretty:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(json.dumps(result, default=str))


# ── Sub-command: key ──────────────────────────────────────────────────────────
def cmd_key(params: dict, pretty: bool) -> None:
    """
    Compute cache_key, script_key, and script_params from canonical_params.

    Demonstrates the three-way split:
        canonical_params  — full identity (block-level)
        cache_key         — hash of full params (block fingerprint)
        script_key        — hash of params minus runtime args (function identity)
        script_params     — runtime args only (injected at execution time)
    """
    ck = compute_cache_key(params)
    sk = compute_script_key(params)
    sp = extract_script_params(params)

    result = {
        "canonical_params": params,
        "cache_key":    ck,
        "script_key":   sk,
        "script_params": sp,
        "_note": (
            "cache_key  = hash(full params)           — block identity\n"
            "script_key = hash(params - runtime args) — function identity\n"
            "script_params = runtime args only        — injected at run time"
        ),
    }

    out_path = save_output(result, "key")
    logger.info("cache_key  : %s", ck)
    logger.info("script_key : %s", sk)
    logger.info("script_params: %s", json.dumps(sp))
    logger.info("Saved → %s", out_path)
    _emit(result, pretty)


# ── Sub-command: lookup ───────────────────────────────────────────────────────
async def cmd_lookup(script_key: str, pretty: bool) -> None:
    """Find the most-recent AnalysisModel tagged with script_key."""
    db = MongoDBClient()
    try:
        await db.connect()
        repo = RepositoryManager(db)
        await repo.initialize()

        block_cache = create_block_cache_service(repo.dashboard)
        doc = await block_cache.lookup_script(script_key, repo.analysis)

        if doc:
            result = {
                "hit":         True,
                "script_key":  script_key,
                "analysis_id": doc.get("analysisId"),
                "created_at":  str(doc.get("createdAt", "")),
                "script_url":  doc.get("scriptUrl"),
                "sub_question": doc.get("subQuestion"),
                "status":      doc.get("status"),
            }
            logger.info("HIT — analysis_id=%s", doc.get("analysisId"))
        else:
            result = {
                "hit":        False,
                "script_key": script_key,
            }
            logger.info("MISS — no analysis tagged with key=%s", script_key)

        out_path = save_output(result, "lookup")
        logger.info("Saved → %s", out_path)
        _emit(result, pretty)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await db.disconnect()


# ── Sub-command: write ────────────────────────────────────────────────────────
async def cmd_write(script_key: str, analysis_id: str, pretty: bool) -> None:
    """
    Tag an existing AnalysisModel with script_key, then read it back to confirm.
    """
    db = MongoDBClient()
    try:
        await db.connect()
        repo = RepositoryManager(db)
        await repo.initialize()

        block_cache = create_block_cache_service(repo.dashboard)

        # Write
        await block_cache.store_script(script_key, analysis_id, repo.analysis)
        logger.info("Tagged analysis_id=%s with script_key=%s", analysis_id, script_key)

        # Read-back to confirm
        doc = await block_cache.lookup_script(script_key, repo.analysis)
        confirmed = doc is not None and doc.get("analysisId") == analysis_id

        result = {
            "written":     True,
            "script_key":  script_key,
            "analysis_id": analysis_id,
            "read_back_ok": confirmed,
        }
        if not confirmed:
            logger.warning(
                "Read-back mismatch: expected %s, got %s",
                analysis_id,
                doc.get("analysisId") if doc else None,
            )

        out_path = save_output(result, "write")
        logger.info("Saved → %s", out_path)
        _emit(result, pretty)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await db.disconnect()


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Step 3 — BlockCacheService (script cache)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # ── key ─────────────────────────────────────────────────────────────
    p_key = sub.add_parser("key", help="Compute cache_key / script_key / script_params from params")
    p_key.add_argument(
        "--params", required=True,
        help='Canonical params JSON, e.g. \'{"ticker":"QQQ","metric":"price","period":"6m"}\'',
    )
    p_key.add_argument("--pretty", action="store_true")

    # ── lookup ───────────────────────────────────────────────────────────
    p_lookup = sub.add_parser("lookup", help="Look up an analysis by script_key")
    p_lookup.add_argument("--key", required=True, help="16-char hex script_key")
    p_lookup.add_argument("--pretty", action="store_true")

    # ── write ────────────────────────────────────────────────────────────
    p_write = sub.add_parser("write", help="Tag an AnalysisModel with a script_key")
    p_write.add_argument("--key",         required=True, help="16-char hex script_key")
    p_write.add_argument("--analysis-id", required=True, dest="analysis_id",
                         help="UUID of the AnalysisModel to tag")
    p_write.add_argument("--pretty", action="store_true")

    args = parser.parse_args()

    if args.cmd == "key":
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as e:
            print(f"ERROR: invalid --params JSON: {e}", file=sys.stderr)
            sys.exit(1)
        cmd_key(params, args.pretty)

    elif args.cmd == "lookup":
        asyncio.run(cmd_lookup(args.key, args.pretty))

    elif args.cmd == "write":
        asyncio.run(cmd_write(args.key, args.analysis_id, args.pretty))


if __name__ == "__main__":
    main()
