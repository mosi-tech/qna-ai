#!/usr/bin/env python3
"""
Compare step5_analysis.py (script generation) vs step5_mcp.py (direct MCP)

Runs both approaches for the same sub-questions and compares:
- Success rate
- Execution time
- Result quality

Usage:
    python compare_step5_approaches.py
"""

import asyncio
import json
import sys
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path


# ── Path setup ────────────────────────────────────────────────────────────────
_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.normpath(os.path.join(_DIR, "..", ".."))
_OUTPUT = os.path.join(_DIR, "output")
sys.path.insert(0, _BACKEND)


# ── Test Questions from "Positions Near 52-Week High" dashboard ──────────────
TEST_QUESTIONS = [
    {
        "id": "q40_kpi",
        "block": "kpi-card-01",
        "question": "What is the count and total market value of positions within 2% of their 52-week high?",
        "output_format": "kpi",
    },
    {
        "id": "q40_table",
        "block": "table-01",
        "question": "What are the positions within 2% of their 52-week high, showing ticker, current price, 52-week high, and percentage gap?",
        "output_format": "table",
    },
    {
        "id": "q40_barlist",
        "block": "bar-list-01",
        "question": "Rank the positions within 2% of their 52-week high by the smallest percentage difference to the high.",
        "output_format": "bar_list",
    },
    {
        "id": "q40_donut",
        "block": "donut-chart-01",
        "question": "What is the market value breakdown by ticker for positions within 2% of their 52-week high?",
        "output_format": "pie",
    },
]


def run_step5_analysis(question: str, timeout: int = 300) -> dict:
    """Run step5_analysis.py for a question."""
    script = os.path.join(_DIR, "step5_analysis.py")

    try:
        result = subprocess.run(
            [sys.executable, script, question, "--timeout", str(timeout)],
            capture_output=True,
            text=True,
            timeout=timeout + 10,
            cwd=_DIR
        )

        output = result.stdout.strip()
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                # Output might be plain text
                return {"success": result.returncode == 0, "output": output}

        return {
            "success": result.returncode == 0,
            "error": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"timeout after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def run_step5_mcp(question: str, timeout: int = 300) -> dict:
    """Run step5_mcp.py for a question."""
    script = os.path.join(_DIR, "step5_mcp.py")

    try:
        result = await asyncio.create_subprocess_exec(
            sys.executable, script, question, "--timeout", str(timeout),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=_DIR
        )

        stdout, stderr = await asyncio.wait_for(
            result.communicate(),
            timeout=timeout + 10
        )

        output = stdout.decode().strip()
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return {"success": result.returncode == 0, "output": output}

        return {
            "success": result.returncode == 0,
            "error": stderr.decode(),
            "returncode": result.returncode
        }
    except asyncio.TimeoutError:
        return {"success": False, "error": f"timeout after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def compare_approach(question: dict) -> dict:
    """Run both approaches for a single question."""
    print(f"\n{'='*60}")
    print(f"Question: {question['id']} ({question['block']})")
    print(f"{'='*60}")
    print(f"Text: {question['question'][:80]}...")

    # Run analysis pipeline
    print(f"\n[1/2] Running step5_analysis.py...")
    start_analysis = time.time()
    analysis_result = run_step5_analysis(question["question"])
    analysis_elapsed = time.time() - start_analysis
    analysis_result["elapsed_s"] = analysis_elapsed

    print(f"  → Success: {analysis_result.get('success', False)}")
    print(f"  → Time: {analysis_elapsed:.1f}s")
    if not analysis_result.get("success"):
        print(f"  → Error: {analysis_result.get('error', 'unknown')}")

    # Run MCP direct
    print(f"\n[2/2] Running step5_mcp.py...")
    start_mcp = time.time()
    mcp_result = await run_step5_mcp(question["question"])
    mcp_elapsed = time.time() - start_mcp
    mcp_result["elapsed_s"] = mcp_elapsed

    print(f"  → Success: {mcp_result.get('success', False)}")
    print(f"  → Time: {mcp_elapsed:.1f}s")
    if not mcp_result.get("success"):
        print(f"  → Error: {mcp_result.get('error', 'unknown')}")

    # Compare
    print(f"\n--- Comparison ---")
    speedup = analysis_elapsed / mcp_elapsed if mcp_elapsed > 0 else 0
    print(f"Speedup (MCP vs Analysis): {speedup:.1f}x")

    return {
        "question_id": question["id"],
        "block": question["block"],
        "question": question["question"],
        "output_format": question["output_format"],
        "analysis": {
            "success": analysis_result.get("success", False),
            "elapsed_s": round(analysis_elapsed, 1),
            "error": analysis_result.get("error"),
            "analysis_id": analysis_result.get("analysis_id"),
            "execution_id": analysis_result.get("execution_id"),
        },
        "mcp": {
            "success": mcp_result.get("success", False),
            "elapsed_s": round(mcp_elapsed, 1),
            "error": mcp_result.get("error"),
            "tool_call_count": mcp_result.get("tool_call_count", 0),
        },
        "speedup": round(speedup, 1),
    }


async def main():
    print("="*60)
    print("STEP5 COMPARISON: Analysis Pipeline vs Direct MCP")
    print("="*60)
    print(f"Test questions: {len(TEST_QUESTIONS)}")
    print(f"Output directory: {_OUTPUT}")

    results = []

    for question in TEST_QUESTIONS:
        result = await compare_approach(question)
        results.append(result)

    # Summary report
    print(f"\n{'='*60}")
    print("SUMMARY REPORT")
    print(f"{'='*60}")

    # Success rates
    analysis_success = sum(1 for r in results if r["analysis"]["success"])
    mcp_success = sum(1 for r in results if r["mcp"]["success"])

    print(f"\nSuccess Rate:")
    print(f"  Analysis Pipeline: {analysis_success}/{len(results)} ({analysis_success/len(results)*100:.0f}%)")
    print(f"  MCP Direct:        {mcp_success}/{len(results)} ({mcp_success/len(results)*100:.0f}%)")

    # Average times
    analysis_times = [r["analysis"]["elapsed_s"] for r in results if r["analysis"]["elapsed_s"]]
    mcp_times = [r["mcp"]["elapsed_s"] for r in results if r["mcp"]["elapsed_s"]]

    print(f"\nAverage Execution Time:")
    if analysis_times:
        print(f"  Analysis Pipeline: {sum(analysis_times)/len(analysis_times):.1f}s")
    if mcp_times:
        print(f"  MCP Direct:        {sum(mcp_times)/len(mcp_times):.1f}s")

    # Speedup
    speedups = [r["speedup"] for r in results if r["speedup"] > 0]
    if speedups:
        print(f"\nSpeedup (MCP vs Analysis):")
        print(f"  Average: {sum(speedups)/len(speedups):.1f}x")
        print(f"  Best:    {max(speedups):.1f}x")
        print(f"  Worst:   {min(speedups):.1f}x")

    # Save results
    os.makedirs(_OUTPUT, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(_OUTPUT, f"step5_comparison_{ts}.json")

    report = {
        "timestamp": datetime.now().isoformat(),
        "test_questions": len(TEST_QUESTIONS),
        "summary": {
            "analysis_success_rate": analysis_success / len(results),
            "mcp_success_rate": mcp_success / len(results),
            "analysis_avg_time": sum(analysis_times) / len(analysis_times) if analysis_times else None,
            "mcp_avg_time": sum(mcp_times) / len(mcp_times) if mcp_times else None,
            "avg_speedup": sum(speedups) / len(speedups) if speedups else None,
        },
        "results": results,
    }

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\nReport saved: {report_path}")

    # Individual question breakdown
    print(f"\n{'='*60}")
    print("QUESTION BREAKDOWN")
    print(f"{'='*60}")
    print(f"{'ID':<12} {'Block':<15} {'Analysis':<12} {'MCP':<12} {'Speedup':<10}")
    print(f"{'-'*60}")
    for r in results:
        analysis_status = "✓" if r["analysis"]["success"] else "✗"
        mcp_status = "✓" if r["mcp"]["success"] else "✗"
        speedup_str = f"{r['speedup']}x" if r["speedup"] > 0 else "-"
        print(f"{r['question_id']:<12} {r['block']:<15} {analysis_status:>8}{r['analysis']['elapsed_s']:>5.1f}s  {mcp_status:>8}{r['mcp']['elapsed_s']:>5.1f}s  {speedup_str:>10}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())