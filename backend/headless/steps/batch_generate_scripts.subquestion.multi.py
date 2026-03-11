#!/usr/bin/env python3
"""
Batch Process: Generate Scripts for All Sub-Questions (Full Analysis Pipeline)

Processes all sub-questions from the UI planner output using the full
analysis and validation pipeline (CacheService, SearchService, VerificationService,
ReuseEvaluator, etc.).

Usage:
    python batch_generate_scripts.py
    python batch_generate_scripts.py --input all-questions/sub_questions_ui_planner_system.json
    python batch_generate_scripts.py --start 1 --end 50  # Process subset
"""

import asyncio
import json
import sys
import os
import argparse
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# ── Path setup ────────────────────────────────────────────────────────────────
_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.normpath(os.path.join(_DIR, "..", ".."))
sys.path.insert(0, _BACKEND)

from dotenv import load_dotenv
load_dotenv(os.path.join(_BACKEND, "apiServer", ".env"))

# ── Imports ───────────────────────────────────────────────────────────────────
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("batch_generate")

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


# ── Cache Key Generation ───────────────────────────────────────────────────
def generate_cache_key(question: str) -> str:
    """Generate a cache key for a question."""
    return hashlib.md5(question.encode()).hexdigest()


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
            logger.info("Verification service ready (%d/%d LLMs)", available, len(svc.llm_services))
            return svc
        logger.warning("Verification service: no LLM services available — skipping verification")
        return None
    except Exception as e:
        logger.warning("Verification service init failed (%s) — continuing without it", e)
        return None


# ── Build Analysis Pipeline ─────────────────────────────────────────────────
async def _build_pipeline(repo: RepositoryManager):
    """Construct the full AnalysisPipelineService."""
    logger.info("Initialising services…")

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

    logger.info("Pipeline ready")
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
        logger.warning(f"Cache check failed: {e}")
        return None


# ── Run Analysis Pipeline ────────────────────────────────────────────────────
async def run_analysis_pipeline(pipeline, question: str, user_id: str, timeout: int = 300) -> Dict[str, Any]:
    """Run the full analysis pipeline for a question."""
    session_id = f"batch-{uuid.uuid4().hex[:8]}"
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


# ── Extract Sub-Questions from Dashboard JSON ──────────────────────────────
def extract_sub_questions(input_file: str) -> List[Dict[str, Any]]:
    """Extract all sub-questions from dashboard JSON."""
    with open(input_file, "r") as f:
        dashboards = json.load(f)

    sub_questions = []

    for idx, dashboard in enumerate(dashboards):
        for block in dashboard.get("blocks", []):
            sub_question = block.get("sub_question")
            if not sub_question:
                continue

            sub_questions.append({
                "question": sub_question,
                "dashboard_id": idx + 1,  # Use 1-indexed array position
                "dashboard_title": dashboard.get("title"),
                "block_id": block.get("blockId"),
                "block_category": block.get("category"),
                "output_format": block.get("output_format", {}),
                "canonical_params": block.get("canonical_params", {})
            })

    return sub_questions


# ── Main Batch Processing ───────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(
        description="Batch process sub-questions to generate cached scripts using full analysis pipeline"
    )
    parser.add_argument("--input", default="all-questions/sub_questions_ui_planner_system.json",
                        help="Input JSON file with sub-questions")
    parser.add_argument("--start", type=int, default=1,
                        help="Start processing from question N (1-indexed)")
    parser.add_argument("--end", type=int,
                        help="End processing at question N (inclusive)")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Max seconds per question (default 300)")
    parser.add_argument("--user-id", dest="user_id", default="batch_process",
                        help="user_id for batch generated scripts (default: batch_process)")
    parser.add_argument("--output", default="batch_results.json",
                        help="Output file with results summary")
    args = parser.parse_args()

    # Connect to MongoDB and build pipeline
    db_client = MongoDBClient()
    await db_client.connect()

    repo = RepositoryManager(db_client)
    await repo.initialize()

    pipeline = await _build_pipeline(repo)

    # Extract sub-questions
    print(f"Loading sub-questions from {args.input}...")
    sub_questions = extract_sub_questions(args.input)

    # Apply start/end filters
    if args.start > 1:
        sub_questions = [sq for sq in sub_questions if sq["dashboard_id"] >= args.start]
    if args.end:
        sub_questions = [sq for sq in sub_questions if sq["dashboard_id"] <= args.end]

    print(f"Found {len(sub_questions)} sub-questions to process")

    # Process each sub-question
    results = {
        "timestamp": datetime.now().isoformat(),
        "input_file": args.input,
        "total_questions": len(sub_questions),
        "processed": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "successful": 0,
        "failed": 0,
        "results": []
    }

    start_time = datetime.now()

    for i, sq in enumerate(sub_questions):
        cache_key = generate_cache_key(sq["question"])

        print(f"\n[{i+1}/{len(sub_questions)}] Q{sq['dashboard_id']}-{sq['block_id']}")
        print(f"  Question: {sq['question'][:60]}...")
        print(f"  Cache key: {cache_key[:8]}...")

        # Check cache
        existing_id = await is_script_cached(db_client, cache_key)

        if existing_id:
            print(f"  ✓ Cache HIT (analysis_id: {existing_id[:8]}...)")
            results["cache_hits"] += 1
            results["results"].append({
                **sq,
                "cache_key": cache_key,
                "status": "cached",
                "analysis_id": existing_id,
                "elapsed_s": 0
            })
        else:
            print(f"  ✗ Cache MISS - running full analysis pipeline...")
            results["cache_misses"] += 1

            # Run full analysis pipeline
            loop_start = datetime.now()
            pipeline_result = await run_analysis_pipeline(
                pipeline,
                sq["question"],
                args.user_id,
                timeout=args.timeout
            )
            elapsed = (datetime.now() - loop_start).total_seconds()

            if pipeline_result["success"]:
                analysis_id = pipeline_result.get("analysis_id")
                if analysis_id:
                    print(f"    ✓ Completed in {elapsed:.1f}s (analysis_id: {analysis_id[:8]}...)")

                    # Update MongoDB with cache_key if not already set
                    try:
                        col = db_client.db["analyses"]
                        await col.update_one(
                            {"analysisId": analysis_id},
                            {"$set": {"cacheKey": cache_key}}
                        )
                    except Exception as e:
                        logger.warning(f"Failed to update cacheKey: {e}")
                else:
                    print(f"    ✓ Completed in {elapsed:.1f}s (no analysis_id)")
                results["successful"] += 1
            else:
                print(f"    ✗ Failed: {pipeline_result.get('error')}")
                results["failed"] += 1

            results["results"].append({
                **sq,
                "cache_key": cache_key,
                "status": "generated" if pipeline_result["success"] else "failed",
                "analysis_id": pipeline_result.get("analysis_id"),
                "elapsed_s": elapsed,
                "error": pipeline_result.get("error")
            })

        results["processed"] += 1

    elapsed = (datetime.now() - start_time).total_seconds()

    # Summary
    print(f"\n{'='*60}")
    print("BATCH PROCESS SUMMARY")
    print(f"{'='*60}")
    print(f"Total questions: {results['total_questions']}")
    print(f"Processed: {results['processed']}")
    print(f"Cache hits: {results['cache_hits']} ({results['cache_hits']/results['processed']*100 if results['processed'] > 0 else 0:.1f}%)")
    print(f"Cache misses: {results['cache_misses']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"Total time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    if results['cache_misses'] > 0:
        avg_gen_time = elapsed / results['cache_misses']
        print(f"Average per generated question: {avg_gen_time:.1f}s")
    print(f"{'='*60}\n")

    # Save results
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to: {args.output}")

    # Disconnect MongoDB
    await db_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())