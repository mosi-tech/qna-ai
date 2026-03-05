#!/usr/bin/env python3
"""
Step 6 — Script Execution (run a script directly from an analysis_id)

Looks up an existing AnalysisModel by analysis_id, loads its script from
storage, executes it against the live MCP data servers, saves the execution
result via AuditService, and prints a summary.

Use this to re-run or debug a specific analysis without going through the
full pipeline or the execution queue worker.

Usage:
    python step6_execution.py --analysis-id <uuid>
    python step6_execution.py --analysis-id <uuid> --show-output    # full result JSON
    python step6_execution.py --analysis-id <uuid> --timeout 120

    # From backend/ root:
    python headless/steps/step6_execution.py --analysis-id <uuid>

What to check:
    - status: "success"
    - execution_id is present in db.executions
    - result_keys includes "results" or "data" (not just empty)
    - If failing: re-run with --show-output to inspect raw execution output
"""

import asyncio
import json
import sys
import os
import uuid
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

logger = logging.getLogger("step6")
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[step6] %(message)s"))
logger.addHandler(_handler)
logger.propagate = False

from shared.db.mongodb_client import MongoDBClient
from shared.db.repositories import RepositoryManager
from shared.services.audit_service import AuditService
from shared.execution import execute_script
from shared.storage import get_storage


# ── Helpers ───────────────────────────────────────────────────────────────────
def save_output(result: dict) -> str:
    os.makedirs(_OUTPUT, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(_OUTPUT, f"step6_{ts}.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return path


async def _lookup_analysis(db_client: MongoDBClient, analysis_id: str) -> dict | None:
    """Find an AnalysisModel doc by analysisId."""
    col = db_client.db["analyses"]
    doc = await col.find_one({"analysisId": analysis_id})
    return doc


async def _lookup_execution(db_client: MongoDBClient, execution_id: str) -> dict | None:
    """Find an ExecutionModel doc by executionId."""
    col = db_client.db["executions"]
    doc = await col.find_one({"executionId": execution_id})
    return doc


# ── Main ──────────────────────────────────────────────────────────────────────
async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Step 6 — Execute a script from an existing analysis_id",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--analysis-id",  dest="analysis_id",  default=None,
                        help="UUID of an existing AnalysisModel whose script to run")
    parser.add_argument("--execution-id", dest="execution_id", default=None,
                        help="UUID of an existing ExecutionModel to inspect (read-only)")
    parser.add_argument("--show-output",  action="store_true",
                        help="Include the full raw execution output in the result JSON")
    parser.add_argument("--timeout",      type=int, default=120,
                        help="Script execution timeout in seconds (default 120)")
    parser.add_argument("--pretty",       action="store_true",
                        help="Pretty-print JSON output")
    args = parser.parse_args()

    if not args.analysis_id and not args.execution_id:
        parser.print_help(sys.stderr)
        sys.exit(1)

    db_client = MongoDBClient()
    try:
        await db_client.connect()
        repo = RepositoryManager(db_client)
        await repo.initialize()
        audit = AuditService(repo)

        # ── Inspect-only mode (existing execution_id) ─────────────────────
        if args.execution_id and not args.analysis_id:
            logger.info("Inspect mode — loading execution_id=%s", args.execution_id)
            edoc = await _lookup_execution(db_client, args.execution_id)
            if not edoc:
                print(f"ERROR: execution_id {args.execution_id!r} not found in db.executions",
                      file=sys.stderr)
                sys.exit(1)

            raw_result = edoc.get("result") or {}
            result_keys = list(raw_result.keys()) if isinstance(raw_result, dict) else []

            result = {
                "mode":          "inspect",
                "execution_id":  args.execution_id,
                "analysis_id":   edoc.get("analysisId"),
                "status":        edoc.get("status"),
                "created_at":    str(edoc.get("createdAt", "")),
                "completed_at":  str(edoc.get("completedAt", "")),
                "execution_time_ms": edoc.get("executionTimeMs"),
                "result_keys":   result_keys,
            }
            if args.show_output:
                result["result_full"] = raw_result

            out_path = save_output(result)
            logger.info("Saved → %s", out_path)
            if args.pretty:
                print(json.dumps(result, indent=2, default=str))
            else:
                print(json.dumps(result, default=str))
            return

        # ── Execute mode ──────────────────────────────────────────────────
        logger.info("Looking up analysis_id=%s", args.analysis_id)
        adoc = await _lookup_analysis(db_client, args.analysis_id)
        if not adoc:
            print(f"ERROR: analysis_id {args.analysis_id!r} not found in db.analyses",
                  file=sys.stderr)
            sys.exit(1)

        script_name = adoc.get("scriptUrl") or adoc.get("script_name")
        execution_params_raw = adoc.get("executionParams") or adoc.get("execution") or {}
        parameters = execution_params_raw.get("parameters", {}) if isinstance(execution_params_raw, dict) else {}
        question   = adoc.get("question", "")
        user_id    = adoc.get("userId", "headless-step6")

        if not script_name:
            print(f"ERROR: AnalysisModel {args.analysis_id!r} has no scriptUrl/script_name",
                  file=sys.stderr)
            sys.exit(1)

        logger.info("Script: %s", script_name)
        logger.info("Parameters: %s", json.dumps(parameters, default=str))

        # Load script content from storage
        storage = get_storage()
        try:
            script_content = await storage.read_script(script_name)
        except FileNotFoundError:
            print(f"ERROR: Script file not found in storage: {script_name}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: failed to read script {script_name!r}: {e}", file=sys.stderr)
            sys.exit(1)

        # Create the execution doc in DB (log_execution_start)
        execution_id = await audit.log_execution_start(
            user_id       = user_id,
            analysis_id   = args.analysis_id,
            question      = question,
            generated_script = script_content,
            execution_params = execution_params_raw if isinstance(execution_params_raw, dict) else {},
            session_id    = f"step6-{uuid.uuid4().hex[:8]}",
        )
        logger.info("Execution doc created: execution_id=%s", execution_id)

        # Run the script synchronously (execute_script is blocking/subprocess)
        start = datetime.utcnow()
        logger.info("Running script (timeout=%ds)…", args.timeout)

        raw = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: execute_script(
                script_content=script_content,
                mock_mode=True,         # matches what execution_worker uses
                timeout=args.timeout,
                parameters=parameters,
            ),
        )

        elapsed_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
        success = raw.get("success", False)
        output  = raw.get("output", {})
        error   = raw.get("error")

        # Persist result via AuditService
        await audit.log_execution_complete(
            execution_id     = execution_id,
            result           = output if isinstance(output, dict) else {"raw": str(output)},
            execution_time_ms = elapsed_ms,
            success          = success,
            error            = error,
        )

        # Build output for step6
        result_keys = list(output.keys()) if isinstance(output, dict) else []
        result: dict = {
            "execution_id":   execution_id,
            "analysis_id":    args.analysis_id,
            "script_name":    script_name,
            "status":         "success" if success else "failed",
            "elapsed_ms":     elapsed_ms,
            "result_keys":    result_keys,
        }

        if not success:
            result["error"] = error

        if args.show_output:
            result["result_full"] = output

        if success:
            logger.info("SUCCESS  execution_id=%s  elapsed=%dms", execution_id, elapsed_ms)
        else:
            logger.error("FAILED   error=%s", error)

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
