#!/usr/bin/env python3
"""
Monitored headless dashboard runner.

Runs run_dashboard_headless.py as a subprocess while concurrently tailing
the analysis-worker and execution-worker error logs. Errors are surfaced
immediately with context rather than discovered only after a timeout.

Usage:
    cd backend
    python infrastructure/headless/run_headless_monitored.py "How is QQQ doing?"
    python infrastructure/headless/run_headless_monitored.py "Compare VOO vs QQQ" --timeout 180
    python infrastructure/headless/run_headless_monitored.py "How is QQQ doing?" --verbose
"""
import argparse
import asyncio
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

# ── ANSI colours ───────────────────────────────────────────────────────────────
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_DIM    = "\033[2m"
_RED    = "\033[91m"
_YELLOW = "\033[93m"
_GREEN  = "\033[92m"
_CYAN   = "\033[96m"
_BLUE   = "\033[94m"
_WHITE  = "\033[97m"


def _c(color: str, text: str) -> str:
    """Wrap text in ANSI color codes (no-op if not a tty)."""
    if not sys.stdout.isatty():
        return text
    return f"{color}{text}{_RESET}"


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


# ── Log-file paths ─────────────────────────────────────────────────────────────
_SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
_EXEC_SERVER  = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", "..", "..", "backend", "executionServer"))

# Fallback: relative from backend/
_EXEC_SERVER_ALT = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", "..", "executionServer"))

WORKER_LOGS = {
    "analysis":  "logs/analysis-worker/err.log",
    "execution": "logs/execution-worker/err.log",
}

# ── Error pattern classifier ───────────────────────────────────────────────────
_ERROR_RE   = re.compile(r"\bERROR\b|\b❌\b")
_WARN_RE    = re.compile(r"\bWARNING\b|\b⚠️\b")
_SUCCESS_RE = re.compile(r"\b✅\b|\bINFO\b.*(?:complete|success|settled|initialized)", re.IGNORECASE)

# Patterns that are informational noise — suppress unless --verbose
_NOISE_RE = re.compile(
    r"Progress event stored|HTTP Request: GET|HTTP Request: POST|"
    r"Timing|⏱️|📝|httpx|uvicorn",
    re.IGNORECASE,
)

# ── Error context buffer ───────────────────────────────────────────────────────
class ErrorTracker:
    def __init__(self):
        self.errors: list[dict] = []       # {"worker", "line", "ts"}
        self.warnings: list[dict] = []

    def record(self, worker: str, line: str):
        entry = {"worker": worker, "line": line.strip(), "ts": _ts()}
        if _ERROR_RE.search(line):
            self.errors.append(entry)
        elif _WARN_RE.search(line):
            self.warnings.append(entry)

    def summary(self) -> str:
        lines = []
        if self.errors:
            lines.append(_c(_RED + _BOLD, f"\n{'─'*60}"))
            lines.append(_c(_RED + _BOLD, f"  {len(self.errors)} ERROR(S) captured during run:"))
            lines.append(_c(_RED, f"{'─'*60}"))
            for e in self.errors:
                lines.append(_c(_RED, f"  [{e['ts']}] [{e['worker']}] {e['line']}"))
        if self.warnings:
            lines.append(_c(_YELLOW + _BOLD, f"\n  {len(self.warnings)} WARNING(S):"))
            for w in self.warnings:
                lines.append(_c(_YELLOW, f"  [{w['ts']}] [{w['worker']}] {w['line']}"))
        if not self.errors and not self.warnings:
            lines.append(_c(_GREEN, "\n  ✅  No errors or warnings during run."))
        return "\n".join(lines)


# ── Tail a log file continuously ───────────────────────────────────────────────
async def tail_worker_log(
    worker_name: str,
    log_path: str,
    tracker: ErrorTracker,
    stop_event: asyncio.Event,
    verbose: bool,
):
    """Seek to EOF then stream new lines as they appear."""
    if not os.path.exists(log_path):
        print(_c(_YELLOW, f"  [monitor] Log not found, skipping: {log_path}"), flush=True)
        return

    label = _c(_BLUE, f"[{worker_name}]")

    try:
        with open(log_path, "r", errors="replace") as fh:
            # Jump to end — only capture lines written during this run
            fh.seek(0, 2)

            while not stop_event.is_set():
                line = fh.readline()
                if not line:
                    await asyncio.sleep(0.2)
                    continue

                # Strip pm2 timestamp prefix: "6|analysis | 2026-03-04T10:08:54: "
                clean = re.sub(r"^\d+\|[^|]+\|\s+[\d\-T:.]+:\s*", "", line).rstrip()
                if not clean:
                    continue

                tracker.record(worker_name, clean)

                # Decide whether to print
                is_error   = bool(_ERROR_RE.search(clean))
                is_warning = bool(_WARN_RE.search(clean))
                is_noise   = bool(_NOISE_RE.search(clean))

                if is_error:
                    print(f"  {label} {_c(_RED,    '● ERROR  ')} {clean}", flush=True)
                elif is_warning:
                    print(f"  {label} {_c(_YELLOW, '◆ WARN   ')} {clean}", flush=True)
                elif verbose and not is_noise:
                    print(f"  {label} {_c(_DIM,    '  INFO   ')} {clean}", flush=True)
    except Exception as exc:
        print(_c(_YELLOW, f"  [monitor] Log reader error ({worker_name}): {exc}"), flush=True)


# ── Main ───────────────────────────────────────────────────────────────────────
async def main(question: str, timeout: int, verbose: bool, pretty: bool):
    tracker    = ErrorTracker()
    stop_event = asyncio.Event()

    # Resolve executionServer directory
    exec_server = _EXEC_SERVER if os.path.isdir(_EXEC_SERVER) else _EXEC_SERVER_ALT

    print(_c(_CYAN + _BOLD, f"\n{'═'*62}"), flush=True)
    print(_c(_CYAN + _BOLD, f"  🚀  Dashboard headless run — monitored"), flush=True)
    print(_c(_CYAN,         f"  Question : {question}"), flush=True)
    print(_c(_CYAN,         f"  Timeout  : {timeout}s"), flush=True)
    print(_c(_CYAN + _BOLD, f"{'═'*62}\n"), flush=True)

    # ── Start log-tail coroutines ──────────────────────────────────────────
    tail_tasks = []
    for worker_name, rel_path in WORKER_LOGS.items():
        log_path = os.path.join(exec_server, rel_path)
        task = asyncio.create_task(
            tail_worker_log(worker_name, log_path, tracker, stop_event, verbose)
        )
        tail_tasks.append(task)

    # ── Spawn headless runner as subprocess ────────────────────────────────
    headless_script = os.path.join(_SCRIPT_DIR, "run_dashboard_headless.py")
    cmd = [sys.executable, headless_script, question, "--timeout", str(timeout)]
    if pretty:
        cmd.append("--pretty")

    print(_c(_WHITE, f"  [runner] Launching subprocess…"), flush=True)
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,   # merge stderr into stdout
    )

    # ── Stream runner output ───────────────────────────────────────────────
    runner_label = _c(_GREEN, "[runner]")
    result_lines: list[str] = []
    capturing_json = False

    assert proc.stdout is not None
    async for raw in proc.stdout:
        line = raw.decode(errors="replace").rstrip()

        # Detect start of JSON output (begins with '{' or '[')
        if re.match(r"^\s*[\[{]", line):
            capturing_json = True

        if capturing_json:
            result_lines.append(line)
        else:
            # Colour runner log lines
            if "ERROR" in line or "❌" in line:
                print(f"  {runner_label} {_c(_RED, line)}", flush=True)
            elif "TIMEOUT" in line:
                print(f"  {runner_label} {_c(_YELLOW, line)}", flush=True)
            elif "settled" in line or "created" in line:
                print(f"  {runner_label} {_c(_GREEN, line)}", flush=True)
            else:
                print(f"  {runner_label} {line}", flush=True)

    await proc.wait()
    exit_code = proc.returncode

    # ── Stop log watchers ──────────────────────────────────────────────────
    stop_event.set()
    for t in tail_tasks:
        try:
            await asyncio.wait_for(t, timeout=1.0)
        except asyncio.TimeoutError:
            t.cancel()

    # ── Final output ───────────────────────────────────────────────────────
    print(_c(_CYAN + _BOLD, f"\n{'═'*62}"), flush=True)
    print(_c(_CYAN + _BOLD,  "  📊  RESULT"), flush=True)
    print(_c(_CYAN + _BOLD, f"{'═'*62}"), flush=True)

    if result_lines:
        print("\n".join(result_lines), flush=True)
    else:
        print(_c(_YELLOW, "  (no JSON result captured — see errors above)"), flush=True)

    # ── Error/warning summary ──────────────────────────────────────────────
    print(tracker.summary(), flush=True)

    print(_c(_CYAN + _BOLD, f"\n{'═'*62}"), flush=True)
    status_str = _c(_GREEN, "SUCCESS") if exit_code == 0 else _c(_RED, f"FAILED (exit {exit_code})")
    print(_c(_BOLD, f"  Run complete — {status_str}"), flush=True)
    print(_c(_CYAN + _BOLD, f"{'═'*62}\n"), flush=True)

    sys.exit(exit_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run headless dashboard with live log monitoring."
    )
    parser.add_argument("question", help="Question to build a dashboard for.")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Max seconds to wait for all blocks to complete.")
    parser.add_argument("--verbose", action="store_true",
                        help="Show all INFO log lines from workers (not just errors/warnings).")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty-print the final JSON result.")
    args = parser.parse_args()

    asyncio.run(main(args.question, args.timeout, args.verbose, args.pretty))
