# Headless Step Scripts — Plan

> Location: `backend/headless/steps/`  
> Purpose: Run and test each stage of the dashboard pipeline in **isolation**,
> without needing the full pm2 stack, the FastAPI server, or a live browser.

Each script is self-contained: bootstraps only the services it needs, runs one
step, prints structured output, exits, and **saves its JSON result to the
`output/` folder** for later inspection or piping into the next step.

---

## Directory Layout

```
backend/headless/steps/
  step1_plan.py          — Run UIPlanner for a question → print block plan
  step2_persist.py       — Persist a dashboard plan to MongoDB → print dashboard_id
  step3_cache.py         — Check / write BlockCache for given canonical_params
  step4_enqueue.py       — Enqueue sub_questions into analysis_queue → print job_ids
  step5_analysis.py      — Run the full analysis pipeline for ONE sub_question
  step6_execution.py     — Run the execution worker for a given analysis_id
  step7_reconcile.py     — Run reconciler once for a dashboard_id → print block statuses
  run_all_steps.py       — Chain all steps end-to-end (replaces run_dashboard_headless.py logic)
  README.md              — Usage reference
  output/                — Auto-created; each run saves stepN_<timestamp>.json here
```

### Output folder convention

Every script automatically saves its JSON result to:
```
backend/headless/steps/output/stepN_<YYYYMMDD_HHMMSS>.json
```
- The folder is created on first use (no manual setup needed).
- The path of the saved file is printed to **stderr** so stdout stays clean JSON.
- `output/` is git-ignored — add `backend/headless/steps/output/` to `.gitignore`.

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
- Prints JSON to **stdout**: `{ title, subtitle, layout, blocks[] }` with each block's
  `blockId`, `category`, `sub_question`, `canonical_params`, `cache_key`
- Saves output to `output/step1_<timestamp>.json`
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
# or load previous step1 output:
python step2_persist.py --plan-file output/step1_20260304_120000.json
```
**Behaviour:**
- Bootstraps: `MongoDBClient`, `DashboardRepository`
- Accepts plan JSON via `--plan`, `--stdin`, or `--plan-file`
- Calls `DashboardRepository.create(DashboardPlanModel(...))`
- Reads back the created document and prints it
- Prints: `dashboard_id`, block count, all block statuses (all should be `pending`)
- Saves output to `output/step2_<timestamp>.json`

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

## Related: Cache Hydration Pipeline

> See `backend/headless/hydrate/` for the cache hydration pipeline.

The hydration pipeline discovers **generic question templates** for script caching:

```
Specific: "What is QQQ's current price?"
    ↓ Genericize (block-aware)
Generic: "What is {{ticker}}'s current price?"
    ↓ Cache key
hash(template + block_type) → cached script
```

**Key concept:** Same generic template → same cached script → any ticker.

See `backend/headless/hydrate/README.md` for details.

---

## UI Performance Optimization — Fast Path Routing

> Goal: Reduce 5-10s response time to <2s for 70%+ of questions
> See `ARCHITECTURE.md` for detailed architecture

### `step3_cache_enhanced.py` — LLM Classification + Cache + Routing
**Purpose:** Classify questions into optimal response paths (direct_mcp, template, or script_generation), check cache, and route accordingly.
**Usage:**
```bash
# Classify single question
python step3_cache_enhanced.py --question "What is QQQ's current price?" --pretty

# Process multiple sub-questions from JSON string
python step3_cache_enhanced.py --sub-questions '[{"block_id": "1", "sub_question": "..."}]'

# Process sub-questions from file
python step3_cache_enhanced.py --sub-questions-file sub_questions.json
```
**Behaviour:**
- Bootstraps: `LLMService` (if API key available), `QuestionClassifier`, `CacheService`
- Classifies each question using:
  1. LLM-based classification (if ANTHROPIC_API_KEY set)
  2. Regex pattern fallback (if LLM unavailable)
- Checks cache based on classification
- Returns routing decisions: `path`, `target`, `mcp_server`, `confidence`, `params`, `route_to`
- Saves output to `output/step3_routing_<timestamp>.json`

**What to check:**
- Classification accuracy (simple questions → direct_mcp)
- Cache hit detection
- Parameter extraction (symbols, limits, etc.)

### `step5a_direct_function.py` — Direct MCP Calls (Fast Path)
**Purpose:** Execute single MCP function calls without script generation.
**Usage:**
```bash
# Call specific function
python step5a_direct_function.py --function get_top_gainers --params '{"limit": 10}'

# Process routing decisions from step3
python step5a_direct_function.py --routing-file output/step3_routing.json
```
**Behaviour:**
- Bootstraps: MCP servers (financial, analytics)
- Calls the specified function directly (no script generation)
- Executes and returns result
- Caches result to memory cache
- Saves output to `output/step5a_<timestamp>.json`

**Supported Functions:**
- `get_real_time_data`, `get_latest_quotes`, `get_latest_trades`
- `get_top_gainers`, `get_top_losers`, `get_most_active_stocks`
- `get_fundamentals`, `get_dividends`, `get_splits`
- `get_account`, `get_positions`
- `calculate_var`, `calculate_sma`, `calculate_rsi`, `calculate_macd`
- `calculate_correlation`, `calculate_risk_metrics`
- And more...

### `test_routing.py` — Question Classification Test
**Purpose:** Test question classification coverage on consolidated questions.
**Usage:**
```bash
# Test with sample of questions
python test_routing.py --questions /path/to/consolidated_questions.json --sample 100

# Test with all questions
python test_routing.py --questions /path/to/consolidated_questions.json

# Save report to specific file
python test_routing.py --questions /path/to/consolidated_questions.json --output report.json
```
**Behaviour:**
- Loads questions from JSON file
- Classifies each question using `QuestionClassifier`
- Generates coverage report:
  - Direct MCP (fast path) percentage
  - Template (medium path) percentage
  - Script generation (slow path) percentage
  - Top identified MCP functions
  - Sample questions by path
  - Performance estimate (speedup)
- Saves JSON report to `output/routing_test_<timestamp>.json`

**Current Results (Regex Fallback, 1,813 questions):**
- Direct MCP: 44.5%
- Template: 7.9%
- Script Generation: 47.5%
- Estimated Speedup: 2.0x

### `test_classification.py` — Classification Coverage Test
**Purpose:** Test how questions are routed through the new architecture.
**Usage:**
```bash
# Test with default consolidated questions
python test_classification.py

# Test with sample
python test_classification.py --sample 50

# Test with custom questions file
python test_classification.py --questions-file /path/to/questions.json
```

---

## Updated Implementation Status

| Script | Status |
|--------|--------|
| `step1_plan.py` | ✅ done |
| `step2_persist.py` | ✅ done |
| `step3_cache.py` | ✅ done |
| `step3_cache_enhanced.py` | ✅ done (LLM + regex classification) |
| `step4_enqueue.py` | ✅ done |
| `step5_analysis.py` | ✅ done |
| `step5a_direct_function.py` | ✅ done (fast path) |
| `step6_execution.py` | ✅ done |
| `step7_reconcile.py` | ✅ done |
| `run_all_steps.py` | ✅ done |
| `test_routing.py` | ✅ done |
| `test_classification.py` | ✅ done |
| `README.md` | ⬜ not built |

### `cache_coverage_pipeline.py` — Generic Question Discovery
**Purpose:** Iteratively discover and warm generic question templates for high cache hit rates.
**Usage:**
```bash
# Run with mock blocks (no UIPlanner needed)
python cache_coverage_pipeline.py --target 0.95 --max-iterations 1000

# Run with real UIPlanner
python cache_coverage_pipeline.py --use-planner --target 0.95

# Run and save report
python cache_coverage_pipeline.py --output coverage_report.json
```
**Behaviour:**
1. Generates diverse financial questions from templates
2. Sends each to UIPlanner to get block decompositions
3. Genericizes each sub-question (block-aware)
4. Tracks cache hits/misses and unique generic questions
5. Repeats until target hit rate (default 95%) or max iterations

**Key Concepts:**

#### Generic Questions
Instead of caching specific questions like:
- "What is QQQ's current price?"
- "What is AAPL's current price?"
- "What is SPY's current price?"

We cache **parametric templates**:
- `"What is {{ticker}}'s current price?"` (same cache key for all tickers)

#### Block-Aware Genericization
The generic question must fit the block that will render it:
```
Question: "What is QQQ's price trend?"
Block: kpi-cards (expects scalar values)
→ Generic: "What are {{ticker}}'s key price metrics?"

Question: "What is QQQ's price trend?"
Block: line-chart (expects time series)
→ Generic: "What is {{ticker}}'s price history?"
```

#### Cache Key Derivation
```python
cache_key = hash(template + block_type)
# Same template + same block = same cache key
# Same template + different block = different cache key
```

**Output:**
- JSON report with all discovered generic questions
- Hit rate statistics
- Coverage by block type
- Top questions by hit count

---

### `test_cache_coverage.py` — Test Suite
**Purpose:** Validate the cache coverage pipeline logic without LLM dependencies.
**Usage:**
```bash
python test_cache_coverage.py
```
**Tests:**
- Question bank generation
- Cache simulator (hits/misses)
- Cache key determinism
- Pipeline dry run (mock mode)

---

## Architecture: Generic Question Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ User Question: "How is QQQ performing?"                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ UIPlanner.plan()                                                            │
│   → Block 1: sub_question = "What is QQQ's current price?"                  │
│              block_type = "kpi-cards"                                       │
│              data_contract = {type: "kpi", points: 1}                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GenericQuestionGenerator.genericize()                                       │
│   Input: sub_question + block_type + data_contract                          │
│   Output: generic_question = "What is {{ticker}}'s current price?"          │
│           params = ["ticker"]                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Cache Lookup                                                                 │
│   generic_key = hash("What is {{ticker}}'s current price?" + "kpi-cards")   │
│                                                                             │
│   cache.get(generic_key) → HIT?                                             │
│     YES → return cached_script.render(ticker="QQQ")                         │
│     NO  → Analysis LLM generates script, cache it, execute                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Updated Implementation Status

| Script | Status |
|--------|--------|
| `step1_plan.py` | ✅ done |
| `step2_persist.py` | ✅ done |
| `step3_cache.py` | ✅ done |
| `step4_enqueue.py` | ✅ done |
| `step5_analysis.py` | ✅ done |
| `step6_execution.py` | ✅ done |
| `step7_reconcile.py` | ✅ done |
| `run_all_steps.py` | ✅ done |
| `cache_coverage_pipeline.py` | ✅ done |
| `test_cache_coverage.py` | ✅ done |
| `README.md` | ⬜ not built |
