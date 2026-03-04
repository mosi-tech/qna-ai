# Headless Step Scripts — Plan

> Location: `backend/infrastructure/headless/steps/`  
> Purpose: Run and test each stage of the dashboard pipeline in **isolation**,
> without needing the full pm2 stack, the FastAPI server, or a live browser.

Each script is self-contained: bootstraps only the services it needs, runs one
step, prints structured output, and exits.  They can be run in sequence to
simulate a full pipeline, or individually to debug a specific stage.

---

## Directory Layout

```
backend/infrastructure/headless/steps/
  step1_plan.py          — Run UIPlanner for a question → print block plan
  step2_persist.py       — Persist a dashboard plan to MongoDB → print dashboard_id
  step3_cache.py         — Check / write BlockCache for given canonical_params
  step4_enqueue.py       — Enqueue sub_questions into analysis_queue → print job_ids
  step5_analysis.py      — Run the full analysis pipeline for ONE sub_question
  step6_execution.py     — Run the execution worker for a given analysis_id
  step7_reconcile.py     — Run reconciler once for a dashboard_id → print block statuses
  run_all_steps.py       — Chain all steps end-to-end (replaces run_dashboard_headless.py logic)
  README.md              — Usage reference
```

---

## Steps Specification

### `step1_plan.py` — UIPlanner
**Purpose:** Test whether UIPlanner decomposes a question sensibly.  
**Usage:**
```bash
python step1_plan.py "How is QQQ performing over the last 6 months?"
python step1_plan.py "What is the current price of AAPL?" --pretty
```
**Behaviour:**
- Bootstraps: `LLMService`, `UIPlanner`
- Calls `UIPlanner.plan(question)`
- Prints JSON: `{ title, subtitle, layout, blocks[] }` with each block's
  `blockId`, `category`, `sub_question`, `canonical_params`, `cache_key`
- Exit 0 on success, non-zero on failure

**What to check:**
- Correct number of blocks (2–5)
- `sub_question` is focused and answerable
- `canonical_params` are clean (no extraneous keys)
- `cache_key` is 16 hex chars

---

### `step2_persist.py` — DB Persist
**Purpose:** Write a plan to MongoDB and confirm it round-trips correctly.  
**Usage:**
```bash
python step2_persist.py --plan '{"title":"...", "blocks":[...]}'
# or pipe from step1:
python step1_plan.py "QQQ current price" | python step2_persist.py --stdin
```
**Behaviour:**
- Bootstraps: `MongoDBClient`, `DashboardRepository`
- Accepts plan JSON via `--plan` or `--stdin`
- Calls `DashboardRepository.create(DashboardPlanModel(...))`
- Reads back the created document and prints it
- Prints: `dashboard_id`, block count, all block statuses (all should be `pending`)

**What to check:**
- `dashboard_id` is a valid UUID
- All blocks present with `status: pending`, `resultData: null`
- `analysisId` and `executionId` are null

---

### `step3_cache.py` — BlockCacheService
**Purpose:** Test cache lookup and write-back in isolation.  
**Usage:**
```bash
# Lookup
python step3_cache.py lookup --key b8eef5ce56a7f593

# Write (insert test data)
python step3_cache.py write --key b8eef5ce56a7f593 --data '{"price": 105.67}'

# Compute key from canonical_params
python step3_cache.py key --params '{"ticker":"QQQ","metric":"price","period":"30d"}'
```
**Behaviour:**
- Bootstraps: `MongoDBClient`, `BlockCacheService`
- `lookup`: prints cached data or `MISS`
- `write`: stores data and confirms with a read-back
- `key`: deterministically computes + prints the 16-char hex key

**What to check:**
- Key is order-independent (same key regardless of param dict ordering)
- HIT returns original stored structure
- TTL / expiry behaviour (if any)

---

### `step4_enqueue.py` — Analysis Queue
**Purpose:** Enqueue sub_questions and confirm job docs are created correctly.  
**Usage:**
```bash
python step4_enqueue.py "What is QQQ's current price, daily change, and 52-week high/low?"
python step4_enqueue.py --plan-file plan.json   # enqueue all blocks from a plan
```
**Behaviour:**
- Bootstraps: `MongoDBClient`, `MongoAnalysisQueue`
- Enqueues the sub_question(s) with fake `dashboard_id`/`block_id` metadata
- Prints resulting `job_id(s)` and the full job document as stored in MongoDB

**What to check:**
- Status is `pending`
- `metadata.dashboard_id` and `metadata.block_id` are present
- `dequeue()` returns the same job (smoke-test round-trip)

---

### `step5_analysis.py` — Analysis Pipeline
**Purpose:** Run the full analysis pipeline end-to-end for a single sub_question.  
This is the slowest and most failure-prone step — isolating it makes debugging
script generation issues much faster.  
**Usage:**
```bash
python step5_analysis.py "What is QQQ's current price, daily change, and 52-week high/low?"
python step5_analysis.py "..." --show-script    # also print the generated Python script
python step5_analysis.py "..." --timeout 120
```
**Behaviour:**
- Bootstraps: full `AnalysisPipeline` stack (LLM, MCP script server, analysis worker services)
- Runs the pipeline directly (bypasses the queue worker)
- On success: prints `analysis_id`, generated script, and raw result JSON
- On failure: prints the error and which attempt failed

**What to check:**
- Script generation converges within 4 attempts
- `analysis_id` is a valid UUID in `db.analyses`
- No `NoneType` subscript errors or `'bs'` key errors in the generated script

---

### `step6_execution.py` — Execution
**Purpose:** Run the execution step for a known `analysis_id`.  
Use this to test the script runner and MCP data connections without re-running
the expensive analysis generation.  
**Usage:**
```bash
python step6_execution.py --analysis-id <uuid>
python step6_execution.py --analysis-id <uuid> --show-output   # full result JSON
```
**Behaviour:**
- Bootstraps: `execute_script`, `AuditService`, `MongoDBClient`
- Looks up the `AnalysisModel` by `analysis_id` → retrieves the script
- Runs the script against live MCP data servers
- Saves result to `db.executions`
- Prints: `execution_id`, `status`, summary of `result` keys

**What to check:**
- Script runs without Python errors
- Result contains a `results` key with actual data (not empty)
- `execution_id` is present in `db.executions` with `status: "success"`

---

### `step7_reconcile.py` — Reconciler
**Purpose:** Run one reconciler pass for a specific dashboard and print current block statuses.  
**Usage:**
```bash
python step7_reconcile.py --dashboard-id <uuid>
python step7_reconcile.py --dashboard-id <uuid> --watch   # poll every 3s until all settled
```
**Behaviour:**
- Bootstraps: `MongoDBClient`, `DashboardOrchestrator` (minimal — only needs repos + queue)
- Calls `reconcile_pending_blocks(dashboard_id)` once (or in a loop with `--watch`)
- Prints a table: `block_id | status | analysisId | executionId | error`

**What to check:**
- Pending blocks advance to `complete` or `failed` after analysis+execution finish
- `resultData` is non-null for completed blocks
- Error messages are informative for failed blocks

---

### `run_all_steps.py` — End-to-end chain
**Purpose:** Chain steps 1–7 with a single command for smoke-testing the full pipeline.  
Equivalent to `run_dashboard_headless.py` but structured as explicit step calls
with output printed between each.  
**Usage:**
```bash
python run_all_steps.py "How is QQQ performing over the last 6 months?" --timeout 300
```
**Behaviour:**
- Runs step 1 → prints plan
- Runs step 2 → prints dashboard_id
- Runs step 3 (cache check per block) → skips queue for cache hits
- Runs step 4 → prints job_ids for cache misses
- Waits for steps 5+6 via step 7 `--watch` logic (polls reconciler)
- Prints final dashboard JSON when all blocks settled or timeout reached

---

## Common Bootstrap Pattern

Each script follows this pattern:
```python
#!/usr/bin/env python3
import asyncio, sys, os, argparse
_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_DIR, "..", "..", ".."))   # → backend/

from dotenv import load_dotenv
load_dotenv(os.path.join(_DIR, "..", "..", "..", "apiServer", ".env"))

from shared.db import MongoDBClient, RepositoryManager
# ... other imports

async def main():
    db = MongoDBClient()
    await db.connect()
    repo = RepositoryManager(db)
    await repo.initialize()
    # ... step-specific logic

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Implementation Status

| Script | Status |
|--------|--------|
| `step1_plan.py` | ⬜ not built |
| `step2_persist.py` | ⬜ not built |
| `step3_cache.py` | ⬜ not built |
| `step4_enqueue.py` | ⬜ not built |
| `step5_analysis.py` | ⬜ not built |
| `step6_execution.py` | ⬜ not built |
| `step7_reconcile.py` | ⬜ not built |
| `run_all_steps.py` | ⬜ not built |
| `README.md` | ⬜ not built |

Use the **`headless_steps_builder`** agent to implement any of these.
