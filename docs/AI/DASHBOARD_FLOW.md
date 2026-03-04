# Dashboard Pipeline — End-to-End Flow

> Last updated: 2026-03-04  
> Source of truth for the headless step-scripts and integration tests.

---

## Overview

A user question enters the system and fans out into one independent block per
data need.  Each block travels through a five-step async pipeline and settles
to `complete` or `failed`.  Cached blocks skip the async steps entirely and
return data in the initial API response.

```
Client  ──POST /api/dashboard/create──►  DashboardOrchestrator
                                                │
                                         ① UIPlanner.plan()
                                                │
                                         ② DashboardRepository.create()
                                                │
                                    ┌───────────┴───────────┐
                                 cache HIT             cache MISS
                                    │                       │
                             block → "cached"        ③ analysis_queue.enqueue()
                             result_data now          block → "pending"
                                    │                       │
                                    │               AnalysisWorker (pm2)
                                    │               ④ write + validate script
                                    │               AnalysisModel → db.analyses
                                    │                       │
                                    │               ExecutionWorker (pm2)
                                    │               ⑤ run script → MCP data
                                    │               Execution → db.executions
                                    │                       │
                                    │               ⑥ reconcile_pending_blocks()
                                    │               (polls every 2 s)
                                    │               block → "complete" / "failed"
                                    │                       │
                                    └───────────┬───────────┘
                                          final blocks
```

---

## Steps in Detail

### Step 1 — UIPlanner  
**File:** `backend/shared/services/ui_planner.py`  
**Input:** `question: str`  
**Output:**
```json
{
  "title": "...",
  "subtitle": "...",
  "layout": "grid",
  "blocks": [
    {
      "blockId": "line-chart-02",
      "category": "line-charts",
      "title": "...",
      "dataContract": { "type": "time_series", "description": "...", "points": 30 },
      "sub_question": "...",
      "canonical_params": { "ticker": "QQQ", "metric": "price", "period": "30d" },
      "cache_key": "b8eef5ce56a7f593"
    }
  ]
}
```
**What it does:** LLM decomposes the question into 2–5 focused blocks.  
Each block picks a component from the BLOCK_CATALOG and sets canonical_params
used for cache keying.

---

### Step 2 — DB Persist  
**File:** `backend/shared/db/dashboard_repository.py`  
**Input:** `DashboardPlanModel` (blocks at status `pending`)  
**Output:** `dashboard_id: str` (MongoDB ObjectId string)  
**What it does:** Writes the full plan to `db.dashboards`.  
Block statuses start as `pending`; result_data is `null`.

---

### Step 3 — Cache Check (BlockCacheService)  
**File:** `backend/shared/services/block_cache_service.py`  
**Input:** `cache_key: str` (16-char hex, deterministic hash of canonical_params)  
**Output:** `result_data: dict | None`  
**What it does:** Looks up `db.block_cache` by key.  
- HIT → block marked `cached`, `result_data` populated, queue skipped  
- MISS → proceed to step 4

Cache key formula: `sha256(json.dumps(canonical_params, sort_keys=True))[:16]`

---

### Step 4 — Analysis Queue Enqueue  
**File:** `backend/shared/queue/analysis_queue.py` (`MongoAnalysisQueue`)  
**Input:** job payload with `sub_question`, `session_id`, `metadata: { dashboard_id, block_id, cache_key }`  
**Output:** `job_id: str`  
**What it does:** Inserts a document into `db.analysis_queue` with `status: "pending"`.  
`block.analysisId` is set to this job_id for later reconciliation.

---

### Step 5 — AnalysisWorker (async, pm2: analysis-queue-worker)  
**File:** `backend/shared/queue/analysis_worker.py`  
**Entry:** `backend/executionServer/analysis/run_worker.py`  
**Input:** dequeuen job from `db.analysis_queue`  
**Output:** `AnalysisModel` doc in `db.analyses`; job result carries `analysis_id`  
**Sub-steps:**
1. Context search / query expansion (`context_aware.py`)
2. Script reuse check — find an existing analysis that answers the same question
3. If no reuse: LLM writes Python script (tools: MCP data servers)
4. `write_and_validate` loop — up to 4 attempts; script is run and output is checked
5. On success: `AnalysisModel` created; job `status → "completed"`, `result.analysis_id` set
6. On failure: job `status → "failed"`, `error` field set

---

### Step 6 — ExecutionWorker (async, pm2: execution-queue-worker)  
**File:** `backend/shared/queue/execution_worker.py`  
**Entry:** `backend/executionServer/execution/run_worker.py`  
**Input:** dequeued execution from `db.execution_queue`  
**Output:** `Execution` doc in `db.executions` with `status: "success" | "failed"`, `result: {...}`  
**What it does:** Runs the validated Python script against live MCP data servers
(market data, financial APIs, etc.).  
Result is the raw JSON from the script — no LLM post-processing (UIResultFormatter removed).

---

### Step 7 — Reconciler  
**File:** `backend/shared/services/dashboard_orchestrator.py` → `reconcile_pending_blocks()`  
**Input:** `dashboard_id: str`  
**Output:** `int` (number of blocks settled in this pass)  
**What it does:** For each `pending` block:
1. Look up `db.analysis_queue` job by `block.analysisId`
2. If job `status == "failed"` → block → `failed` (immediate)
3. Else read `job.result.analysis_id` → look up `db.executions`
4. If execution `status == "success"` → block → `complete` + `result_data`
5. If execution `status == "failed"` → block → `failed` + `error`

Called every 2 s by the headless polling loop.

---

## Key Files

| Layer | File |
|-------|------|
| API route | `backend/apiServer/api/dashboard_routes.py` |
| Orchestrator | `backend/shared/services/dashboard_orchestrator.py` |
| UIPlanner | `backend/shared/services/ui_planner.py` |
| Block cache | `backend/shared/services/block_cache_service.py` |
| Dashboard DB | `backend/shared/db/dashboard_repository.py` |
| Analysis queue | `backend/shared/queue/analysis_queue.py` |
| Analysis pipeline | `backend/shared/analyze/services/analysis_pipeline.py` |
| Analysis worker | `backend/shared/queue/analysis_worker.py` |
| Execution worker | `backend/shared/queue/execution_worker.py` |
| Full headless run | `backend/infrastructure/headless/run_dashboard_headless.py` |
| Monitored run | `backend/infrastructure/headless/run_headless_monitored.py` |
| Step scripts (to build) | `backend/infrastructure/headless/steps/` |

---

## Data Contracts (MongoDB)

### `db.dashboards` (DashboardPlanModel)
```json
{
  "dashboardId": "uuid",
  "userId": "...",
  "sessionId": "...",
  "messageId": "...",
  "originalQuestion": "...",
  "title": "...",
  "subtitle": "...",
  "layout": "grid",
  "status": "running | complete | failed",
  "blocks": [
    {
      "block_id": "b0",
      "sequence": 0,
      "block_spec_id": "line-chart-02",
      "category": "line-charts",
      "title": "...",
      "sub_question": "...",
      "canonical_params": {},
      "cache_key": "...",
      "analysisId": "job_id or null",
      "executionId": "uuid or null",
      "status": "pending | cached | complete | failed",
      "resultData": null,
      "error": null
    }
  ]
}
```

### `db.analysis_queue` (job)
```json
{
  "job_id": "uuid",
  "status": "pending | processing | completed | failed",
  "data": { "user_question": "...", "session_id": "...", "metadata": { "dashboard_id": "...", "block_id": "b0" } },
  "result": { "analysisId": "...", "analysis_id": "..." },
  "error": null
}
```

### `db.executions`
```json
{
  "executionId": "uuid",
  "analysisId": "uuid",
  "status": "success | failed",
  "result": { "question": "...", "results": {}, "analysis_completed": true },
  "error": null
}
```
