#!/usr/bin/env python3
"""
Generate Single Script Per Dashboard

Instead of one script per sub-question, this generates ONE script per dashboard
that can output multiple formats (KPI, table, bar-list, donut chart, etc.).

Usage:
    python run_single_script_per_dashboard.py "What is QQQ?"
    python run_single_script_per_dashboard.py "What is QQQ?" --timeout 300
"""

import asyncio
import json
import sys
import os
import argparse
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# ── Path setup ────────────────────────────────────────────────────────────────
_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.normpath(os.path.join(_DIR, "..", ".."))
sys.path.insert(0, _BACKEND)

from dotenv import load_dotenv
load_dotenv(os.path.join(_BACKEND, "apiServer", ".env"))

# ── Imports ───────────────────────────────────────────────────────────────────
import logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("single-script")

from shared.db.mongodb_client import MongoDBClient
from shared.db.repositories import RepositoryManager
from shared.analyze import AnalysisService, AnalysisPersistenceService
from shared.analyze import ReuseEvaluator as ReuseEvaluatorService
from shared.analyze import CodePromptBuilderService
from shared.analyze.services.analysis_pipeline import create_analysis_pipeline
from shared.analyze.services.verification.verification_service import StandaloneVerificationService
from shared.services.search import SearchService
from shared.services.chat_service import ChatHistoryService
from shared.services.cache_service import CacheService
from shared.services.audit_service import AuditService
from shared.services.session_manager import SessionManager
from shared.services.ui_planner import create_ui_planner


# ── Verification Service Initialization ────────────────────────────────────
def _init_verification_service():
    """Mirror AnalysisQueueWorker._initialize_verification_service()."""
    try:
        prompt_template = (
            "Before we proceed, I need to verify something important:\n\n"
            "**Question**: {question}\n\n"
            "Please check if the script correctly answers the question."
        )
        svc = StandaloneVerificationService(prompt_template)
        available = len([s for s in svc.llm_services if s is not None])
        if available > 0:
            logger.info("✓ Verification service ready (%d/%d LLMs)", available, len(svc.llm_services))
            return svc
        logger.warning("⚠ Verification service: no LLM services available — skipping verification")
        return None
    except Exception as e:
        logger.warning("⚠ Verification service init failed (%s) — continuing without it", e)
        return None


# ── Build Analysis Pipeline ─────────────────────────────────────────────────
async def _build_pipeline(repo: RepositoryManager):
    """Construct the full AnalysisPipelineService."""
    logger.info("🔧 Initialising services…")

    chat_history_service       = ChatHistoryService(repo)
    cache_service              = CacheService(repo)
    analysis_persistence_svc  = AnalysisPersistenceService(repo)

    # Redis for session manager — optional, fall back gracefully
    redis_client = None
    try:
        from shared.services.redis_client import get_redis_client
        redis_client = await get_redis_client()
    except Exception:
        pass

    session_manager = SessionManager(
        chat_history_service=chat_history_service,
        redis_client=redis_client,
    )

    pipeline = create_analysis_pipeline(
        analysis_service              = AnalysisService(),
        search_service                = SearchService(),
        chat_history_service          = chat_history_service,
        cache_service                 = cache_service,
        analysis_persistence_service  = analysis_persistence_svc,
        reuse_evaluator               = ReuseEvaluatorService(),
        code_prompt_builder           = CodePromptBuilderService(),
        session_manager               = session_manager,
        audit_service                 = AuditService(repo),
        verification_service          = _init_verification_service(),
    )

    logger.info("✓ Pipeline ready")
    return pipeline


# ── MongoDB Cache Check ─────────────────────────────────────────────────────
async def is_script_cached(db_client, cache_key: str) -> Optional[str]:
    """Check if a script is already cached in MongoDB."""
    try:
        col = db_client.db["analyses"]
        doc = await col.find_one({"cacheKey": cache_key})
        if doc:
            return doc.get("analysisId")
        return None
    except Exception as e:
        logger.warning(f"⚠ Cache check failed: {e}")
        return None


# ── Build Output Spec from Plan ────────────────────────────────────────────────
def build_output_spec_from_plan(plan: Dict[str, Any]) -> str:
    """Build output specification from dashboard plan blocks."""
    blocks = plan.get("blocks", [])
    specs = []

    for block in blocks:
        category = block.get("category", "")
        data_contract = block.get("dataContract", {})
        data_type = data_contract.get("type", "")

        # Map category to output format type
        type_map = {
            "kpi-cards": "kpi",
            "tables": "table",
            "bar-lists": "bar_list",
            "bar-charts": "bar",
            "donut-charts": "pie",
            "pie-charts": "pie",
            "line-charts": "line",
        }
        output_type = type_map.get(category, data_type)

        # Build spec based on type
        if output_type == "kpi":
            points = data_contract.get("points", 0)
            if points > 0:
                specs.append(f"  - KPI metrics: {points} key indicators for {block.get('title', 'the asset')}")
            else:
                specs.append(f"  - KPI metrics: price, change, volume for {block.get('title', 'the asset')}")
        elif output_type == "table":
            specs.append(f"  - Table data: detailed rows and columns for {block.get('title', 'this section')}")
        elif output_type == "bar_list":
            specs.append(f"  - Bar list data: label and value pairs for {block.get('title', ' rankings')}")
        elif output_type == "bar":
            specs.append(f"  - Bar chart data: x-axis labels and y-axis values for {block.get('title', ' comparison')}")
        elif output_type == "line":
            specs.append(f"  - Line chart data: time series data (dates and values) for {block.get('title', 'trend')}")
        elif output_type in ["pie", "donut"]:
            specs.append(f"  - Pie/donut chart data: category labels and values for {block.get('title', 'distribution')}")
        else:
            specs.append(f"  - {block.get('title', 'data block')}: {data_type or 'structured data'}")

    return "\n".join(specs) if specs else "  - Full detailed data for dashboard"


# ── Run Analysis Pipeline ────────────────────────────────────────────────────
async def run_analysis_pipeline(pipeline, question: str, user_id: str, timeout: int = 300) -> Dict[str, Any]:
    """Run the full analysis pipeline for a question."""
    session_id = f"single-{hashlib.md5(question.encode()).hexdigest()[:8]}"
    message_id = None

    request_data = {
        "question": question,
        "session_id": session_id,
        "message_id": message_id,
        "user_id": user_id,
        "enable_caching": False,  # We handle caching separately
        "auto_expand": True,
        "model": None,
    }

    try:
        logger.info(f"📊 Running analysis pipeline (timeout: {timeout}s)...")
        pipeline_result = await asyncio.wait_for(
            pipeline.analyze_question(request_data),
            timeout=timeout,
        )

        success = getattr(pipeline_result, "success", True)
        pipeline_data = getattr(pipeline_result, "data", {}) or {}
        if not isinstance(pipeline_data, dict):
            pipeline_data = {}

        return {
            "success": success,
            "analysis_id": pipeline_data.get("analysis_id") or pipeline_data.get("analysisId"),
            "execution_id": pipeline_data.get("execution_id") or pipeline_data.get("executionId"),
            "response_type": pipeline_data.get("response_type", "unknown"),
            "error": getattr(pipeline_result, "error", None) if not success else None,
            "pipeline_data": pipeline_data,
        }

    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": f"Pipeline timed out after {timeout}s",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# ── Main ──────────────────────────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(
        description="Generate single script per dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
    python run_single_script_per_dashboard.py "What is QQQ?"
    python run_single_script_per_dashboard.py "Compare VOO vs QQQ" --timeout 600
""",
    )
    parser.add_argument("question", help="Question to generate script for")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Max seconds for analysis (default 300)")
    parser.add_argument("--user-id", dest="user_id", default="single-script-user",
                        help="User ID for generated script (default: single-script-user)")
    parser.add_argument("--output", "-o",
                        help="Output file for results (optional)")
    parser.add_argument("--skip-cache", action="store_true",
                        help="Skip cache check and force regeneration")
    args = parser.parse_args()

    if not args.question:
        parser.print_help(sys.stderr)
        print("ERROR: question is required", file=sys.stderr)
        sys.exit(1)

    start_time = datetime.now()

    # Connect to MongoDB
    logger.info("📡 Connecting to MongoDB...")
    db_client = MongoDBClient()
    await db_client.connect()

    repo = RepositoryManager(db_client)
    await repo.initialize()

    # ── Step 1: Get dashboard plan ───────────────────────────────────────
    logger.info("=" * 60)
    logger.info("STEP 1: Planning dashboard...")
    logger.info("=" * 60)

    ui_planner = create_ui_planner()
    plan = await ui_planner.plan(args.question)

    if not plan.get("blocks"):
        logger.error("❌ UIPlanner returned no blocks")
        sys.exit(1)

    logger.info(f"✓ Plan: '{plan['title']}' with {len(plan['blocks'])} blocks")
    for i, block in enumerate(plan["blocks"]):
        logger.info(f"  [{i+1}] {block.get('blockId')}: {block.get('title')} ({block.get('category')})")

    # ── Step 2: Build enhanced question ───────────────────────────────────
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: Building enhanced question...")
    logger.info("=" * 60)

    output_spec = build_output_spec_from_plan(plan)

    enhanced_question = f"""{args.question}

Please structure your output to support these visualization types:
{output_spec}

Return all the data needed for these visualizations in the results dict.""".strip()

    logger.info(f"✓ Enhanced question ({len(enhanced_question)} chars)")

    # ── Step 3: Check cache ───────────────────────────────────────────────
    cache_key = hashlib.md5(enhanced_question.encode()).hexdigest()

    logger.info("\n" + "=" * 60)
    logger.info("STEP 3: Checking cache...")
    logger.info("=" * 60)

    if not args.skip_cache:
        existing_id = await is_script_cached(db_client, cache_key)
        if existing_id:
            logger.info(f"✓ Cache HIT (analysis_id: {existing_id[:8]}...)")

            # Build blocks array from plan for frontend compatibility
            blocks_array = []
            for block in plan["blocks"]:
                blocks_array.append({
                    "block_id": block.get("blockId"),
                    "title": block.get("title"),
                    "status": "complete",
                    "has_result": True,
                })

            result = {
                "question": args.question,
                "cache_key": cache_key,
                "status": "cached",
                "analysis_id": existing_id,
                "elapsed_s": 0,
                "total_elapsed_s": 0,
                "blocks": len(plan["blocks"]),
                "blocks_data": blocks_array,
                "dashboard_id": cache_key[:16],
                "plan_title": plan.get("title"),
            }
            if args.output:
                with open(args.output, "w") as f:
                    json.dump(result, f, indent=2, default=str)
                logger.info(f"✓ Results saved to: {args.output}")
            print(json.dumps(result, indent=2, default=str))
            sys.exit(0)
        else:
            logger.info(f"✗ Cache MISS (key: {cache_key[:8]}...)")
    else:
        logger.info("⚠ Cache skipped (--skip-cache)")

    # ── Step 4: Run analysis pipeline ───────────────────────────────────────
    logger.info("\n" + "=" * 60)
    logger.info("STEP 4: Running analysis pipeline...")
    logger.info("=" * 60)

    # Build pipeline
    pipeline = await _build_pipeline(repo)

    # Run pipeline
    loop_start = datetime.now()
    pipeline_result = await run_analysis_pipeline(
        pipeline,
        enhanced_question,
        args.user_id,
        timeout=args.timeout
    )
    elapsed = (datetime.now() - loop_start).total_seconds()

    # ── Step 5: Update cache key ──────────────────────────────────────────
    if pipeline_result["success"]:
        analysis_id = pipeline_result.get("analysis_id")
        if analysis_id:
            try:
                col = db_client.db["analyses"]
                await col.update_one(
                    {"analysisId": analysis_id},
                    {"$set": {"cacheKey": cache_key}}
                )
                logger.info(f"✓ Cache key set (key: {cache_key[:8]}...)")
            except Exception as e:
                logger.warning(f"⚠ Failed to update cacheKey: {e}")

    # ── Final Result ────────────────────────────────────────────────────────
    total_elapsed = (datetime.now() - start_time).total_seconds()

    # Build blocks array from plan for frontend compatibility
    blocks_array = []
    for block in plan["blocks"]:
        blocks_array.append({
            "block_id": block.get("blockId"),
            "title": block.get("title"),
            "status": "complete" if pipeline_result["success"] else "failed",
            "has_result": pipeline_result["success"],
            "error": pipeline_result.get("error"),
        })

    result = {
        "question": args.question,
        "cache_key": cache_key,
        "status": "generated" if pipeline_result["success"] else "failed",
        "analysis_id": pipeline_result.get("analysis_id"),
        "execution_id": pipeline_result.get("execution_id"),
        "elapsed_s": round(elapsed, 1),
        "total_elapsed_s": round(total_elapsed, 1),
        "blocks": len(plan["blocks"]),
        "blocks_data": blocks_array,
        "dashboard_id": cache_key[:16],
        "plan_title": plan.get("title"),
        "error": pipeline_result.get("error"),
        "response_type": pipeline_result.get("response_type"),
    }

    logger.info("\n" + "=" * 60)
    if pipeline_result["success"]:
        logger.info(f"✓ SUCCESS - Generated in {elapsed:.1f}s")
        if pipeline_result.get("analysis_id"):
            logger.info(f"  Analysis ID: {pipeline_result['analysis_id'][:8]}...")
        if pipeline_result.get("execution_id"):
            logger.info(f"  Execution ID: {pipeline_result['execution_id'][:8]}...")
    else:
        logger.error(f"✗ FAILED - {pipeline_result.get('error')}")
    logger.info("=" * 60)

    # Save results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"✓ Results saved to: {args.output}")

    # Output result
    print(json.dumps(result, indent=2, default=str))

    # Cleanup
    await db_client.disconnect()

    # Exit code
    sys.exit(0 if pipeline_result["success"] else 1)


if __name__ == "__main__":
    asyncio.run(main())