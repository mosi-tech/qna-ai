#!/usr/bin/env python3
"""
Compare step5_analysis.py (script generation) vs step5_mcp.py (direct MCP)

Runs both approaches for the same sub-questions and compares:
- Success rate
- Execution time
- Result quality

Usage:
    python compare_step5_approaches_simple.py
"""

import subprocess
import json
import sys
import time
from datetime import datetime


# ── Test Questions ──────────────────────────────────────────────────────────
# Questions that can be answered with available MCP tools (no portfolio data required)
TEST_QUESTIONS = [
    {
        "id": "qqq_price",
        "question": "What is QQQ's current price?",
        "category": "simple_metric",
    },
    {
        "id": "qqq_volatility",
        "question": "What is QQQ's 30-day volatility?",
        "category": "calculated_metric",
    },
    {
        "id": "spy_qqq_compare",
        "question": "Compare QQQ vs VOO performance for the last year",
        "category": "comparison",
    },
]


def run_analysis(question: str, timeout: int = 120) -> dict:
    """Run step5_analysis.py for a question."""
    script = "backend/headless/steps/step5_analysis.py"

    try:
        result = subprocess.run(
            [sys.executable, script, question, "--timeout", str(timeout)],
            capture_output=True,
            text=True,
            timeout=timeout + 10,
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


def run_mcp(question: str, timeout: int = 60) -> dict:
    """Run step5_mcp.py for a question."""
    script = "backend/headless/steps/step5_mcp.py"

    try:
        result = subprocess.run(
            [sys.executable, script, question, "--timeout", str(timeout)],
            capture_output=True,
            text=True,
            timeout=timeout + 10,
        )

        output = result.stdout.strip()
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
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


def compare_approach(question: dict) -> dict:
    """Run both approaches for a single question."""
    print(f"\n{'='*60}")
    print(f"Question: {question['id']} ({question['category']})")
    print(f"{'='*60}")
    print(f"Text: {question['question']}")

    # Run MCP direct (faster approach)
    print(f"\n[1/2] Running step5_mcp.py...")
    start = time.time()
    mcp_result = run_mcp(question["question"])
    mcp_elapsed = time.time() - start
    mcp_result["elapsed_s"] = mcp_elapsed

    print(f"  → Success: {mcp_result.get('success', False)}")
    print(f"  → Time: {mcp_elapsed:.1f}s")
    if not mcp_result.get("success"):
        print(f"  → Error: {mcp_result.get('error', 'unknown')}")
    else:
        print(f"  → Has parsed data: {mcp_result.get('parsed_data') is not None}")

    # Run analysis pipeline
    print(f"\n[2/2] Running step5_analysis.py...")
    start = time.time()
    analysis_result = run_analysis(question["question"])
    analysis_elapsed = time.time() - start
    analysis_result["elapsed_s"] = analysis_elapsed

    print(f"  → Success: {analysis_result.get('success', False)}")
    print(f"  → Time: {analysis_elapsed:.1f}s")
    if not analysis_result.get("success"):
        print(f"  → Error: {analysis_result.get('error', 'unknown')}")
    else:
        print(f"  → Has analysis_id: {analysis_result.get('analysis_id') is not None}")
        print(f"  → Response type: {analysis_result.get('response_type', 'unknown')}")

    # Compare
    print(f"\n--- Comparison ---")
    speedup = analysis_elapsed / mcp_elapsed if mcp_elapsed > 0 else 0
    print(f"Speedup (MCP vs Analysis): {speedup:.1f}x")
    print(f"MCP is faster by: {analysis_elapsed - mcp_elapsed:.1f}s ({(1 - mcp_elapsed/analysis_elapsed)*100:.0f}%)")

    return {
        "question_id": question["id"],
        "category": question["category"],
        "question": question["question"],
        "analysis": {
            "success": analysis_result.get("success", False),
            "elapsed_s": round(analysis_elapsed, 1),
            "error": analysis_result.get("error"),
            "analysis_id": analysis_result.get("analysis_id"),
            "response_type": analysis_result.get("response_type"),
        },
        "mcp": {
            "success": mcp_result.get("success", False),
            "elapsed_s": round(mcp_elapsed, 1),
            "error": mcp_result.get("error"),
            "has_parsed_data": mcp_result.get("parsed_data") is not None,
        },
        "speedup": round(speedup, 1),
        "time_saved": round(analysis_elapsed - mcp_elapsed, 1),
    }


def main():
    print("="*60)
    print("STEP5 COMPARISON: Analysis Pipeline vs Direct MCP")
    print("="*60)
    print(f"Test questions: {len(TEST_QUESTIONS)}")

    results = []

    for question in TEST_QUESTIONS:
        result = compare_approach(question)
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

    # Time saved per question
    time_saved = [r["time_saved"] for r in results if r["time_saved"] > 0]
    if time_saved:
        print(f"\nTime Saved (per question):")
        print(f"  Average: {sum(time_saved)/len(time_saved):.1f}s")
        print(f"  Total for {len(TEST_QUESTIONS)} questions: {sum(time_saved):.1f}s")

    # Save results
    import os
    output_dir = "backend/headless/steps/output"
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"{output_dir}/step5_comparison_{ts}.json"

    report = {
        "timestamp": datetime.now().isoformat(),
        "test_questions": len(TEST_QUESTIONS),
        "summary": {
            "analysis_success_rate": analysis_success / len(results),
            "mcp_success_rate": mcp_success / len(results),
            "analysis_avg_time": sum(analysis_times) / len(analysis_times) if analysis_times else None,
            "mcp_avg_time": sum(mcp_times) / len(mcp_times) if mcp_times else None,
            "avg_speedup": sum(speedups) / len(speedups) if speedups else None,
            "total_time_saved": sum(time_saved) if time_saved else None,
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
    print(f"{'ID':<15} {'Category':<15} {'Analysis':<12} {'MCP':<12} {'Speedup':<10} {'Saved':<10}")
    print(f"{'-'*75}")
    for r in results:
        analysis_status = "✓" if r["analysis"]["success"] else "✗"
        mcp_status = "✓" if r["mcp"]["success"] else "✗"
        speedup_str = f"{r['speedup']}x" if r["speedup"] > 0 else "-"
        saved_str = f"{r['time_saved']}s" if r["time_saved"] > 0 else "-"
        print(f"{r['question_id']:<15} {r['category']:<15} {analysis_status:>8}{r['analysis']['elapsed_s']:>5.1f}s  {mcp_status:>8}{r['mcp']['elapsed_s']:>5.1f}s  {speedup_str:>10} {saved_str:>10}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()