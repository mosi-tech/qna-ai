#!/usr/bin/env python3
"""
Step 5 — AnalysisPipeline (full script-generation pipeline for one sub_question)

Runs the complete analysis pipeline for a single sub_question directly —
no queue, no pm2 worker needed.  This is the most expensive step (LLM call)
and the most common source of failures, so isolating it here makes debugging
fast: script generation, validation, and persistence all in one shot.

Usage:
    python step5_analysis.py "What is QQQ's current price and daily change?"
    python step5_analysis.py "..." --show-script        # print generated script
    python step5_analysis.py "..." --timeout 180        # max seconds (default 300)

    # From backend/ root:
    python headless/steps/step5_analysis.py "What is QQQ's daily price range?"

What to check:
    - analysis_id present in output → verify in db.analyses
    - success: true
    - attempts ≤ 4
    - script_preview non-empty
    - If failing: look at the "error" field and re-run with --show-script
"""

import asyncio
import json
import sys
import os
import uuid
import argparse
import signal
from datetime import datetime


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

logger = logging.getLogger("step5")
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[step5] %(message)s"))
logger.addHandler(_handler)
logger.propagate = False

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


# ── Helpers ───────────────────────────────────────────────────────────────────
def save_output(result: dict) -> str:
    os.makedirs(_OUTPUT, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(_OUTPUT, f"step5_{ts}.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return path


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


async def _build_pipeline(repo: RepositoryManager):
    """Construct the full AnalysisPipelineService — mirrors worker _initialize_services()."""
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


# ── Main ──────────────────────────────────────────────────────────────────────
async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Step 5 — Run full analysis pipeline for one sub_question",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("question", nargs="?", help="Sub-question to analyse")
    parser.add_argument("--show-script", action="store_true",
                        help="Include the full generated Python script in output")
    parser.add_argument("--timeout",  type=int, default=300,
                        help="Max seconds to wait for pipeline (default 300)")
    parser.add_argument("--user-id",  dest="user_id",  default="headless-step5",
                        help="user_id passed to pipeline (default: headless-step5)")
    parser.add_argument("--pretty",   action="store_true",
                        help="Pretty-print JSON output")
    args = parser.parse_args()

    if not args.question:
        parser.print_help(sys.stderr)
        sys.exit(1)

    session_id  = f"step5-{uuid.uuid4().hex[:8]}"
    # Do NOT pass message_id — the pipeline already has a headless branch in
    # _update_message_only() that silently skips chat-message persistence when
    # message_id is None.  Passing a fake ID causes the conversation store to
    # fail trying to find a message that was never inserted.
    message_id  = None

    request_data = {
        "question":       args.question,
        "session_id":     session_id,
        "message_id":     message_id,
        "user_id":        args.user_id,
        "enable_caching": False,   # headless debug — always run fresh
        "auto_expand":    True,
        "model":          None,
    }

    db_client = MongoDBClient()
    try:
        await db_client.connect()
        repo = RepositoryManager(db_client)
        await repo.initialize()

        pipeline = await _build_pipeline(repo)

        logger.info("Running pipeline for: %s", args.question[:100])
        logger.info("session_id=%s  message_id=%s", session_id, message_id)

        start = asyncio.get_event_loop().time()
        try:
            pipeline_result = await asyncio.wait_for(
                pipeline.analyze_question(request_data),
                timeout=args.timeout,
            )
        except asyncio.TimeoutError:
            print(f"ERROR: pipeline timed out after {args.timeout}s", file=sys.stderr)
            sys.exit(1)

        elapsed = asyncio.get_event_loop().time() - start
        success = getattr(pipeline_result, "success", True)

        # ------------------------------------------------------------------
        # Unpack result
        # ------------------------------------------------------------------
        pipeline_data = getattr(pipeline_result, "data", {}) or {}
        if not isinstance(pipeline_data, dict):
            pipeline_data = {}

        analysis_id  = pipeline_data.get("analysis_id") or pipeline_data.get("analysisId")
        execution_id = pipeline_data.get("execution_id") or pipeline_data.get("executionId")
        script_text  = pipeline_data.get("script") or pipeline_data.get("script_url") or ""

        # Try to resolve script text from DB if pipeline only gave a path/id
        if analysis_id and not script_text:
            try:
                col = db_client.db["analyses"]
                adoc = await col.find_one({"analysisId": analysis_id})
                if adoc:
                    script_text = adoc.get("scriptUrl", "") or adoc.get("script", "")
            except Exception:
                pass

        result: dict = {
            "success":      success,
            "analysis_id":  analysis_id,
            "execution_id": execution_id,
            "elapsed_s":    round(elapsed, 1),
            "response_type": pipeline_data.get("response_type", "unknown"),
            "result_keys":  list(pipeline_data.keys()),
            "script_preview": (script_text[:800] + "…") if script_text and len(script_text) > 800 else script_text,
        }

        if not success:
            result["error"]          = getattr(pipeline_result, "error", "unknown")
            result["internal_error"] = getattr(pipeline_result, "internal_error", "")

        if args.show_script:
            result["script_full"] = script_text

        if success:
            logger.info("SUCCESS  analysis_id=%s  elapsed=%.1fs", analysis_id, elapsed)
        else:
            logger.error("FAILED   error=%s", result.get("error"))

        out_path = save_output(result)
        logger.info("Saved → %s", out_path)

        if args.pretty:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(json.dumps(result, default=str))

        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    finally:
        await db_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
