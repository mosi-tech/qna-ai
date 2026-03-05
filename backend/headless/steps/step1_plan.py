#!/usr/bin/env python3
"""
Step 1 — UIPlanner

Decomposes a question into a dashboard block plan (title, subtitle, layout,
blocks with sub_question / canonical_params / cache_key).

Does NOT need MongoDB — UIPlanner only calls the LLM.

Usage:
    cd backend/headless/steps
    python step1_plan.py "How is QQQ performing over the last 6 months?"
    python step1_plan.py "Compare VOO vs QQQ" --pretty

    cd backend
    python headless/steps/step1_plan.py "What is the current price of AAPL?" --pretty

Pipe to step2:
    python step1_plan.py "QQQ 6-month trend" | python step2_persist.py --stdin
"""

import asyncio
import json
import sys
import os
import argparse
from datetime import datetime

# ── Path setup ────────────────────────────────────────────────────────────────
# Script lives at  backend/headless/steps/
# Go up 2 levels:  steps/ → headless/ → backend/
_DIR     = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.normpath(os.path.join(_DIR, "..", ".."))
_OUTPUT  = os.path.join(_DIR, "output")
sys.path.insert(0, _BACKEND)

from dotenv import load_dotenv
load_dotenv(os.path.join(_BACKEND, "apiServer", ".env"))

# ── Imports ───────────────────────────────────────────────────────────────────
import logging
logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

logger = logging.getLogger("step1")
logger.setLevel(logging.INFO)

# Handler that writes to stderr (so stdout stays clean JSON)
_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[step1] %(message)s"))
logger.addHandler(_handler)
logger.propagate = False

from shared.services.ui_planner import create_ui_planner


# ── Helpers ───────────────────────────────────────────────────────────────────
def save_output(result: dict) -> str:
    """Persist result JSON to output/ and return the saved file path."""
    os.makedirs(_OUTPUT, exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(_OUTPUT, f"step1_{ts}.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return path


# ── Main ──────────────────────────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(
        description="Step 1 — Run UIPlanner for a question and print the block plan."
    )
    parser.add_argument("question", nargs="?", help="Question to plan a dashboard for")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    question = args.question
    if not question:
        parser.print_help(sys.stderr)
        print("ERROR: question is required", file=sys.stderr)
        sys.exit(1)

    logger.info(f"Planning dashboard for: {question!r}")

    try:
        ui_planner = create_ui_planner()
        plan = await ui_planner.plan(question)

        # Ensure cache_key is present on every block (UIPlanner computes it internally)
        blocks = plan.get("blocks", [])
        logger.info(
            f"Plan ready: '{plan.get('title')}' — {len(blocks)} block(s)"
        )

        # Validate acceptance criteria
        issues = []
        for i, block in enumerate(blocks):
            ck = block.get("cache_key", "")
            if len(ck) != 16:
                issues.append(f"Block {i} cache_key is {len(ck)} chars (expected 16): {ck!r}")
        if issues:
            for issue in issues:
                logger.warning(issue)

        result = {
            "title":    plan.get("title", ""),
            "subtitle": plan.get("subtitle", ""),
            "layout":   plan.get("layout", "grid"),
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
                for b in blocks
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


if __name__ == "__main__":
    asyncio.run(main())
