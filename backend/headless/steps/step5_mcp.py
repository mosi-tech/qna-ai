#!/usr/bin/env python3
"""
Step 5 — MCP Direct (answer sub_questions using MCP functions directly)

Uses Anthropic SDK with direct function calling (simulating MCP tools) to answer
questions without script generation. This is the fast path for questions that
can be answered by available MCP functions.

Note: Uses Anthropic SDK directly (not Agent SDK) because Agent SDK requires
spawning CLI subprocesses, which is not suitable for headless batch processing.

Usage:
    python step5_mcp.py "What is QQQ's current price and daily change?"
    python step5_mcp.py "..." --show-details        # show tool calls
    python step5_mcp.py "..." --timeout 180        # max seconds (default 300)

    # From backend/ root:
    python headless/steps/step5_mcp.py "What is QQQ's daily price range?"

What to check:
    - success: true
    - elapsed_s shows how fast MCP is vs script generation
    - If failing: look at the "error" field
"""

import asyncio
import json
import sys
import os
import argparse
import time
from datetime import datetime
from pathlib import Path


# ── Path setup ────────────────────────────────────────────────────────────────
_DIR     = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.normpath(os.path.join(_DIR, "..", ".."))
_OUTPUT  = os.path.join(_DIR, "output")
sys.path.insert(0, _BACKEND)

from dotenv import load_dotenv
load_dotenv(os.path.join(_BACKEND, "apiServer", ".env"))

# ── Imports (after path/env setup) ───────────────────────────────────────────
import logging
logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

logger = logging.getLogger("step5_mcp")
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[step5_mcp] %(message)s"))
logger.addHandler(_handler)
logger.propagate = False


# ── Helpers ───────────────────────────────────────────────────────────────────
def save_output(result: dict) -> str:
    os.makedirs(_OUTPUT, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(_OUTPUT, f"step5_mcp_{ts}.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return path


# ── Anthropic SDK Setup ───────────────────────────────────────────────────────
try:
    from anthropic import Anthropic
except ImportError:
    print("Error: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Step 5 — Answer sub_question using MCP directly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("question", nargs="?", help="Sub-question to answer via MCP")
    parser.add_argument("--show-details", action="store_true",
                        help="Include tool call details in output")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Max seconds to wait (default 300)")
    parser.add_argument("--model", default=None,
                        help="Claude model to use (default: from MODEL env var)")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty-print JSON output")
    args = parser.parse_args()

    if not args.question:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Get API key
    api_key = os.getenv("ANTHROPIC_AUTH_TOKEN") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Build system prompt
    system_prompt = """You are a financial data analyst. Answer the user's question using the available MCP tools.

Available tools come from two servers:
- mcp-financial-server: Fetch market data, fundamentals, portfolio info
- mcp-analytics-server: Calculate financial metrics and indicators

You have access to financial tools including:
- get_real_time_data: Get current market data
- get_historical_data: Get historical price data
- get_positions: Get portfolio positions
- get_fundamentals: Get company fundamentals
- calculate_*: Various financial calculations (returns, volatility, correlations, etc.)

Return ONLY the structured data answer as JSON, no markdown code blocks, no backticks, no explanations."""

    # Build query with format specification
    # Try to infer format from question
    question_lower = args.question.lower()
    format_hint = ""
    if "table" in question_lower or "list" in question_lower:
        format_hint = "\n\nReturn results as a table with rows and columns."
    elif "breakdown" in question_lower or "allocation" in question_lower:
        format_hint = "\n\nReturn results with labels and values for each category."
    elif "count" in question_lower:
        format_hint = "\n\nReturn results as key-value pairs (count, total_value, etc)."
    else:
        format_hint = "\n\nReturn results as key-value pairs for metrics."

    user_message = f"{args.question}{format_hint}"

    # Set model
    model = args.model or os.getenv("MODEL", "glm-4.7:cloud")

    logger.info("Querying via MCP (Anthropic SDK): %s", args.question[:100])

    # Create client
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    if base_url and "ollama.com" in base_url:
        import httpx
        client = Anthropic(
            api_key=api_key,
            base_url=base_url,
            http_client=httpx.Client(
                headers={"Authorization": f"Bearer {api_key}"},
                verify=False
            )
        )
    elif base_url:
        client = Anthropic(api_key=api_key, base_url=base_url)
    else:
        client = Anthropic(api_key=api_key)

    start = time.time()

    try:
        response = client.messages.create(
            model=model,
            max_tokens=8192,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        # Extract response
        result_text = ""
        tool_calls = []

        for block in response.content:
            if hasattr(block, 'type'):
                if block.type == 'text':
                    result_text += block.text
                elif block.type == 'tool_use':
                    tool_calls.append({
                        "name": block.name,
                        "input": block.input
                    })

    except Exception as e:
        elapsed = time.time() - start
        print(f"ERROR: Query failed after {elapsed:.1f}s: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    elapsed = time.time() - start

    # Try to parse JSON from result
    result_data = None
    try:
        # Find JSON in response
        import re
        json_pattern = r'\{[\s\S]*\}'
        json_matches = re.findall(json_pattern, result_text)
        if json_matches:
            result_data = json.loads(max(json_matches, key=len))
        else:
            # Try array pattern
            array_pattern = r'\[[\s\S]*\]'
            array_matches = re.findall(array_pattern, result_text)
            if array_matches:
                result_data = json.loads(max(array_matches, key=len))
    except Exception as e:
        logger.debug("JSON parse failed: %s", e)
        result_data = None

    # Build result
    result: dict = {
        "success": True if result_text else False,
        "elapsed_s": round(elapsed, 1),
        "question": args.question,
        "answer_text": result_text,
        "parsed_data": result_data,
        "tool_call_count": len(tool_calls),
    }

    if args.show_details and tool_calls:
        result["tool_calls"] = tool_calls

    if not result_text:
        result["success"] = False
        result["error"] = "No response from LLM"

    logger.info("MCP completed in %.1fs", elapsed)

    out_path = save_output(result)
    logger.info("Saved → %s", out_path)

    if args.pretty:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(json.dumps(result, default=str))

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()