# Dashboard Builder — Full Implementation Plan

**Objective:** Replace the current single-question → single-result flow with a presentation-first
dashboard system. A top-level question is decomposed into atomic sub-questions, each mapped to a
specific base-ui block. Sub-questions execute in parallel through the existing pipeline. Blocks paint
progressively as results arrive. Executed sub-questions are cached by a canonical fingerprint and
reused across future dashboards.

---

## Architecture in One Sentence

> **UIPlanner** decomposes a question into a `DashboardSpec` (N blocks with sub-questions) →
> each block's sub-question enters the **existing** AnalysisWorker → ExecutionWorker pipeline →
> results stream back via SSE `block_update` events → **DashboardCanvas** (from `@ui-gen/base-ui`)
> renders base-ui blocks progressively.

---

## Existing Assets — What Is Already Built

| Asset | Location | Role in new system |
|-------|----------|--------------------|
| 40+ production base-ui blocks | `apps/base-ui/src/blocks/` | All dashboard rendering |
| `BLOCK_CATALOG.json` | `apps/base-ui/src/blocks/BLOCK_CATALOG.json` | UIPlanner system prompt source |
| `blockSelector.ts` + `BLOCK_METADATA.json` | `apps/base-ui/src/blocks/` | Block selection & layout rules |
| `DashboardSpec` / `BlockSpec` types | `apps/ai-builder/services/dashboardAI.ts` | Canonical spec shape |
| `DashboardCanvas.tsx` | `apps/ai-builder/components/` | Progressive block renderer |
| `BlockShell.tsx` | `apps/ai-builder/components/` | Per-block loading / error / render |
| `BuilderApp.tsx` | `apps/ai-builder/components/` | Chat → spec → canvas flow |
| `AnalysisModel` + `ExecutionModel` | `backend/shared/db/schemas.py` | Sub-question results |
| AnalysisWorker + ExecutionWorker | `backend/shared/queue/` | Unchanged pipeline |
| `progress_service.py` + SSE | `backend/shared/services/` | Event delivery |
| `execution_service.py` | `backend/apiServer/services/` | Execution orchestration |

---

## What Changes vs. What Is Retired

| Component | Status |
|-----------|--------|
| `apps/qna-ai/src/components/insights/` (all 14 files) | **Retired** — replaced by base-ui blocks |
| `UIConfigurationRenderer.tsx` | **Retired** |
| `UIResultFormatter` (backend) | **Retired** — replaced by UIPlanner |
| `system-prompt-ui-formatter.txt` | **Retired** |
| `DashboardCanvas.tsx` (ai-builder) | **Moved → base-ui** |
| `BlockShell.tsx` (ai-builder) | **Moved → base-ui** |
| `DashboardSpec` / `BlockSpec` types (ai-builder) | **Moved → base-ui** |
| `apps/ai-builder` | **Unchanged** — continues working with mock data |
| Existing analysis / execution pipeline | **Unchanged** |

---

## Phase Overview

```
Phase 1  — Shared types & canvas moved to base-ui                [Frontend, zero risk]
Phase 2  — UIPlanner backend service                             [Backend, new only]
Phase 3  — DashboardPlan + BlockPlan DB models                   [Backend, additive]
Phase 4  — Block cache service                                   [Backend, read-only]
Phase 5  — Dashboard orchestrator                                [Backend, new only]
Phase 6  — Pipeline hookback (block_update SSE)                  [Backend, +12 lines]
Phase 7  — New API routes: /api/dashboard/*                      [Backend, additive]
Phase 8  — qna-ai: DashboardResultSection + useBlockUpdates      [Frontend, new only]
Phase 9  — qna-ai: retire UIConfigurationRenderer + insights     [Frontend, cleanup]
Phase 10 — ai-builder: wire real data (optional upgrade)         [Frontend, opt-in]
```

---

## Phase 1 — Move Shared Types and Canvas to `@ui-gen/base-ui`

**Goal:** Make `DashboardSpec`, `BlockSpec`, `DashboardCanvas`, and `BlockShell` available to all
apps via the shared package instead of living only in `ai-builder`.

### 1.1 — New file: `apps/base-ui/src/blocks/types.ts`

Extract and re-export types from `ai-builder/services/dashboardAI.ts`.
No logic moves — types only.

```typescript
// apps/base-ui/src/blocks/types.ts

export type BlockCategory =
    | 'kpi-cards'  | 'line-charts'  | 'bar-charts'
    | 'bar-lists'  | 'donut-charts' | 'spark-charts'
    | 'tables'     | 'status-monitoring' | 'treemaps' | 'heatmaps';

export type DataContractType =
    | 'kpi' | 'timeseries' | 'categorical'
    | 'ranked-list' | 'table-rows' | 'spark' | 'tracker';

export interface DataContract {
    type: DataContractType;
    description: string;
    points?: number;
    categories?: string[];
}

export interface BlockSpec {
    blockId: string;          // matches BLOCK_CATALOG.json id
    category: BlockCategory;
    title: string;
    dataContract: DataContract;
    // Sub-question extensions (populated when coming from UIPlanner)
    sub_question?: string;
    canonical_params?: Record<string, string>;
    cache_key?: string;
}

export interface DashboardSpec {
    dashboard_id?: string;    // set after backend persists
    title: string;
    subtitle: string;
    layout: 'wide' | 'grid';
    blocks: BlockSpec[];
}

export type BlockLoadState = 'loading' | 'loaded' | 'error' | 'cached';

export interface BlockState {
    spec: BlockSpec;
    loadState: BlockLoadState;
    data?: Record<string, unknown>;
    error?: string;
}
```

### 1.2 — Move `DashboardCanvas.tsx` → `apps/base-ui/src/blocks/DashboardCanvas.tsx`

Copy current `ai-builder/components/DashboardCanvas.tsx`. Update the import:
```typescript
// Before (ai-builder internal)
import type { DashboardSpec, BlockSpec } from '@/services/dashboardAI';
import type { BlockLoadState } from './BlockShell';

// After (from base-ui types)
import type { DashboardSpec, BlockState } from './types';
```

### 1.3 — Move `BlockShell.tsx` → `apps/base-ui/src/blocks/BlockShell.tsx`

Copy current `ai-builder/components/BlockShell.tsx`. Update the import:
```typescript
// Before
import type { BlockSpec } from '@/services/dashboardAI';

// After
import type { BlockSpec } from './types';
```
All base-ui component imports (`@ui-gen/base-ui`) already resolve correctly.

### 1.4 — Export from `apps/base-ui/src/blocks/index.ts`

```typescript
// Add to existing exports
export * from './types';
export { default as DashboardCanvas } from './DashboardCanvas';
export { default as BlockShell } from './BlockShell';
```

### 1.5 — Update `ai-builder` imports

Update `ai-builder/components/DashboardCanvas.tsx` and `BlockShell.tsx` to re-export from base-ui
so `ai-builder` internals break no further:
```typescript
// ai-builder/components/DashboardCanvas.tsx
export { DashboardCanvas as default } from '@ui-gen/base-ui';
```
```typescript
// ai-builder/components/BlockShell.tsx
export { BlockShell as default } from '@ui-gen/base-ui';
```

Update `ai-builder/services/dashboardAI.ts` to import types from base-ui:
```typescript
import type { DashboardSpec, BlockSpec, BlockCategory, DataContractType, DataContract } from '@ui-gen/base-ui';
```

### 1.6 — Verify

```bash
cd frontend && npm run type-check   # all apps
```

**Risk:** Zero. No logic changes. `ai-builder` behaviour is identical.

---

## Phase 2 — UIPlanner Backend Service

**Goal:** Given a user question, produce a `DashboardSpec` (the same JSON shape from Phase 1 types)
with 3–6 blocks, each carrying a `sub_question`, `canonical_params`, and `cache_key`.

### 2.1 — New file: `backend/shared/services/ui_planner.py`

Extends `BaseService` (same pattern as `UIResultFormatter`).

```python
class UIPlanner(BaseService):
    """
    Decomposes a user question into a DashboardSpec:
    - Selects 3–6 base-ui blocks from BLOCK_CATALOG.json
    - Assigns an atomic sub_question per block
    - Emits canonical_params for cache fingerprinting
    """

    def _create_default_llm(self) -> LLMService:
        return create_ui_planner_llm()           # fast/cheap model — planning only

    def _get_system_prompt_filename(self) -> str:
        return "system-prompt-ui-planner.txt"

    async def plan(self, question: str) -> DashboardPlanOutput:
        system_prompt = await self.get_system_prompt()
        user_message  = self._build_user_message(question)
        response      = await self.llm_service.make_request(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            max_tokens=1500,
            temperature=0.1,
        )
        raw = safe_json_loads(response["content"])
        return self._validate_and_enrich(raw, question)     # adds cache_key per block

    def _compute_cache_key(self, canonical_params: dict) -> str:
        import hashlib, json
        normalised = json.dumps(canonical_params, sort_keys=True)
        return hashlib.sha256(normalised.encode()).hexdigest()[:16]
```

### 2.2 — New file: `backend/shared/config/system-prompt-ui-planner.txt`

Full system prompt fed to the LLM. Key sections:

**Section A — Available blocks** (injected from `BLOCK_CATALOG.json` at service init time):
Includes `id`, `category`, `bestFor`, `avoidWhen`, `dataShape`, `requiredProps` for each block.

**Section B — Rules:**
```
- Respond ONLY with valid JSON. No prose, no markdown fences.
- Select 3–6 blocks. Always start with a kpi-cards block.
- Each block must have: blockId, category, title, dataContract, sub_question, canonical_params.
- sub_question: a standalone atomic question whose answer directly populates this block.
  It must be self-contained (no pronouns referencing other blocks).
- canonical_params: a flat object with keys from: ticker, tickers[], metric, period,
  benchmark, strategy, sector, exchange. Omit keys that don't apply.
- Layout: use "grid" unless the question produces primarily time-series content.
- Do NOT invent data. sub_question must be answerable by the existing financial data pipeline.
```

**Section C — Output schema:**
```json
{
  "title": "string",
  "subtitle": "string",
  "layout": "grid | wide",
  "blocks": [
    {
      "blockId": "kpi-card-01",
      "category": "kpi-cards",
      "title": "string",
      "dataContract": { "type": "kpi", "description": "...", "points": 4 },
      "sub_question": "What are QQQ's key performance metrics over the past 30 days?",
      "canonical_params": { "ticker": "QQQ", "metric": "performance_summary", "period": "30d" }
    }
  ]
}
```

### 2.3 — New file: `backend/shared/llm/__init__.py` addition

```python
def create_ui_planner_llm() -> LLMService:
    """Fast/cheap LLM for planning — not execution analysis"""
    return LLMService(provider_type="anthropic", model="claude-3-haiku-20240307")
```

### 2.4 — Factory function

```python
# bottom of ui_planner.py
def create_ui_planner(llm_service=None) -> UIPlanner:
    return UIPlanner(llm_service=llm_service)
```

**Risk:** Zero — isolated new file, nothing calls it yet.

---

## Phase 3 — DashboardPlan + BlockPlan DB Models

**Goal:** Persist the plan and track per-block execution status.

### 3.1 — Add to `backend/shared/db/schemas.py`

```python
class BlockStatus(str, Enum):
    PENDING  = "pending"
    RUNNING  = "running"
    COMPLETE = "complete"
    FAILED   = "failed"
    CACHED   = "cached"      # result served from an existing execution


class BlockPlanModel(BaseMongoModel):
    """One block within a DashboardPlan"""
    block_id:         str                    # "b1", "b2" ... stable within dashboard
    sequence:         int                    # render order (0-indexed)
    # --- BlockSpec fields (mirrors frontend types.ts) ---
    block_spec_id:    str                    # matches BLOCK_CATALOG.json id, e.g. "kpi-card-01"
    category:         str                    # "kpi-cards", "line-charts" ...
    title:            str
    data_contract:    Dict[str, Any] = Field(alias='dataContract')
    # --- Sub-question & cache ---
    sub_question:     str
    canonical_params: Dict[str, str]
    cache_key:        str                    # sha256[:16] of canonical_params
    # --- Execution linkage ---
    analysis_id:      Optional[str] = Field(None, alias='analysisId')
    execution_id:     Optional[str] = Field(None, alias='executionId')
    status:           BlockStatus = BlockStatus.PENDING
    result_data:      Optional[Dict[str, Any]] = Field(None, alias='resultData')
    error:            Optional[str] = None
    updated_at:       datetime = Field(default_factory=datetime.utcnow, alias='updatedAt')


class DashboardPlanModel(BaseMongoModel):
    """Top-level dashboard plan — one per user question"""
    dashboard_id:      str = Field(default_factory=lambda: str(uuid.uuid4()), alias='dashboardId')
    user_id:           str = Field(..., alias='userId')
    session_id:        Optional[str] = Field(None, alias='sessionId')
    message_id:        Optional[str] = Field(None, alias='messageId')
    original_question: str = Field(..., alias='originalQuestion')
    title:             str
    subtitle:          str
    layout:            str                   # "grid" | "wide"
    blocks:            List[BlockPlanModel]
    status:            str = "planning"      # planning | running | complete | partial | failed
    created_at:        datetime = Field(default_factory=datetime.utcnow, alias='createdAt')
    updated_at:        datetime = Field(default_factory=datetime.utcnow, alias='updatedAt')

    class Config:
        collection = "dashboard_plans"
        indexes = [
            {"fields": [("userId", 1), ("createdAt", -1)]},
            {"fields": [("messageId",  1)]},
            {"fields": [("sessionId",  1)]},
            {"fields": [("blocks.cache_key", 1)]},        # cache lookups
            {"fields": [("blocks.status",    1)]},
        ]
```

### 3.2 — New repository: `backend/shared/db/dashboard_repository.py`

```python
class DashboardRepository:
    async def create(plan: DashboardPlanModel) -> str              # returns dashboard_id
    async def get_by_id(dashboard_id) -> Optional[dict]
    async def get_by_message_id(message_id) -> Optional[dict]
    async def update_block_status(dashboard_id, block_id, status, **fields)
    async def find_cached_block(cache_key, max_age_hours=24) -> Optional[dict]
    # find_cached_block searches blocks.cache_key across ALL dashboard_plans for
    # any block with status=COMPLETE and updatedAt within max_age_hours
```

### 3.3 — Register in `RepositoryManager`

```python
# backend/shared/db/repositories.py
class RepositoryManager:
    def __init__(self, ...):
        ...
        self.dashboard = DashboardRepository(client)   # ← add this line
```

**Risk:** Zero — additive schema + new collection. Existing collections untouched.

---

## Phase 4 — Block Cache Service

**Goal:** Before dispatching a block's sub-question, check if an identical answered block exists.

### 4.1 — New file: `backend/shared/services/block_cache_service.py`

```python
class BlockCacheService:
    """
    Checks whether a block's canonical_params have already been answered
    recently enough to reuse.
    """

    def __init__(self, dashboard_repo: DashboardRepository, ttl_hours: int = 24):
        self.repo = dashboard_repo
        self.ttl_hours = ttl_hours

    async def lookup(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Returns result_data if a matching completed block exists within TTL.
        Returns None (cache miss) otherwise.
        """
        return await self.repo.find_cached_block(cache_key, self.ttl_hours)

    async def is_stale(self, cache_key: str) -> bool:
        """True if the cached block is older than TTL"""
        cached = await self.repo.find_cached_block(cache_key, self.ttl_hours)
        return cached is None
```

**Cache key computation** (canonical params → sha256[:16]):
```python
import hashlib, json

def compute_cache_key(canonical_params: dict) -> str:
    normalised = json.dumps(canonical_params, sort_keys=True)
    return hashlib.sha256(normalised.encode()).hexdigest()[:16]
```

Cache invalidation strategies:
- **Default:** TTL-based (24h for daily market data, configurable per `metric` type)
- **Force refresh:** `force_refresh=True` flag on `/api/dashboard/create` skips cache
- **Manual bust:** `POST /api/dashboard/{id}/blocks/{block_id}/refresh`

**Risk:** Zero — read-only lookups only.

---

## Phase 5 — Dashboard Orchestrator

**Goal:** Thin glue that wires UIPlanner → DB → cache lookup → pipeline dispatch.

### 5.1 — New file: `backend/shared/services/dashboard_orchestrator.py`

```python
class DashboardOrchestrator:

    def __init__(self, repo_manager, analysis_queue_service, ui_planner, block_cache):
        self.dashboard_repo    = repo_manager.dashboard
        self.analysis_queue    = analysis_queue_service
        self.ui_planner        = ui_planner
        self.block_cache       = block_cache

    async def create_dashboard(
        self,
        question:      str,
        user_id:       str,
        session_id:    str,
        message_id:    str,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:

        # ── Step 1: UIPlanner ──────────────────────────────────────────────────
        plan_output = await self.ui_planner.plan(question)

        # ── Step 2: Persist DashboardPlan ─────────────────────────────────────
        dashboard = DashboardPlanModel(
            user_id=user_id, session_id=session_id, message_id=message_id,
            original_question=question,
            title=plan_output["title"],  subtitle=plan_output["subtitle"],
            layout=plan_output["layout"],
            blocks=[BlockPlanModel(block_id=f"b{i}", sequence=i, **b)
                    for i, b in enumerate(plan_output["blocks"])],
            status="running",
        )
        dashboard_id = await self.dashboard_repo.create(dashboard)

        # ── Step 3: Cache check + dispatch per block ───────────────────────────
        block_summaries = []
        for block in dashboard.blocks:
            cached = None if force_refresh else await self.block_cache.lookup(block.cache_key)

            if cached:
                # ── Cache HIT: mark complete, no queue entry ─────────────────
                await self.dashboard_repo.update_block_status(
                    dashboard_id, block.block_id,
                    status=BlockStatus.CACHED, result_data=cached,
                )
                block_summaries.append({**block.dict(), "status": "cached", "result_data": cached})
            else:
                # ── Cache MISS: enqueue sub_question into existing pipeline ───
                analysis_id = await self.analysis_queue.enqueue_question(
                    question=block.sub_question,
                    user_id=user_id,
                    session_id=session_id,
                    metadata={
                        "dashboard_id": dashboard_id,
                        "block_id":     block.block_id,
                        "cache_key":    block.cache_key,
                    },
                )
                await self.dashboard_repo.update_block_status(
                    dashboard_id, block.block_id,
                    status=BlockStatus.PENDING, analysis_id=analysis_id,
                )
                block_summaries.append({**block.dict(), "status": "pending"})

        return {
            "dashboard_id": dashboard_id,
            "title":        plan_output["title"],
            "subtitle":     plan_output["subtitle"],
            "layout":       plan_output["layout"],
            "blocks":       block_summaries,
        }
```

**Risk:** Low. No existing code paths touch this. The `enqueue_question` call is the same as a regular
chat message entering the pipeline — the only difference is the `metadata` dict carrying
`dashboard_id` + `block_id`.

---

## Phase 6 — Pipeline Hookback (block_update SSE)

**Goal:** When an execution completes, if it originated from a dashboard block, emit a
`block_update` SSE event and update the `DashboardPlan`.

### 6.1 — Edit `backend/apiServer/services/execution_service.py`

Locate the end of `execute_analysis()`, after `result_data` is built and saved. Add **~15 lines**:

```python
# ── Dashboard block hookback ────────────────────────────────────────────────
analysis_metadata = analysis.get("metadata", {})
dashboard_id  = analysis_metadata.get("dashboard_id")
block_id      = analysis_metadata.get("block_id")
cache_key     = analysis_metadata.get("cache_key")

if dashboard_id and block_id:
    from shared.db.dashboard_repository import DashboardRepository
    dashboard_repo = DashboardRepository(self.repo.client)

    await dashboard_repo.update_block_status(
        dashboard_id, block_id,
        status="complete",
        result_data=result_data,
        execution_id=execution_id,
    )

    # ── SSE event: block_update ────────────────────────────────────────────
    # Uses the SAME send_progress_event() that already exists
    if session_id:
        await send_progress_event(session_id, {
            "type":         "block_update",
            "dashboard_id": dashboard_id,
            "block_id":     block_id,
            "status":       "complete",
            "result_data":  result_data,
        })

    self.logger.info(f"✅ Block update emitted: dashboard={dashboard_id} block={block_id}")
```

Add a matching failure branch in the error path ~10 lines above (same shape but `"status": "failed"`).

### 6.2 — No changes to AnalysisWorker or ExecutionWorker

They remain fully unaware of dashboards. The hookback lives entirely in `execution_service.py`.

**Risk:** Very low. Guarded by `if dashboard_id and block_id:` — does nothing for normal executions.

---

## Phase 7 — New API Routes: `/api/dashboard/*`

**Goal:** Expose dashboard creation and status to the frontend.

### 7.1 — New file: `backend/apiServer/api/dashboard_routes.py`

```
POST   /api/dashboard/create
    Body:  { question, sessionId, messageId, forceRefresh? }
    Auth:  required
    Returns: DashboardPlan (all blocks with initial status — pending or cached)
    Action: runs UIPlanner + orchestrator, returns immediately

GET    /api/dashboard/{dashboard_id}
    Auth:  required
    Returns: full DashboardPlanModel with current block statuses + any result_data

GET    /api/dashboard/{dashboard_id}/blocks/{block_id}
    Returns: single BlockPlanModel (status + result_data)

POST   /api/dashboard/{dashboard_id}/blocks/{block_id}/refresh
    Forces cache bypass, re-runs sub_question through pipeline

GET    /api/dashboard/session/{session_id}
    Returns all dashboards in a session (for chat history)
```

### 7.2 — Register in `backend/apiServer/api/routes.py`

```python
from .dashboard_routes import router as dashboard_router
app.include_router(dashboard_router)
```

### 7.3 — Wire orchestrator into app startup

```python
# backend/apiServer/main.py (or wherever app.state is set)
from shared.services.ui_planner import create_ui_planner
from shared.services.block_cache_service import BlockCacheService
from shared.services.dashboard_orchestrator import DashboardOrchestrator

app.state.ui_planner     = create_ui_planner()
app.state.block_cache    = BlockCacheService(repo_manager.dashboard)
app.state.dashboard_orch = DashboardOrchestrator(
    repo_manager, execution_queue_service, app.state.ui_planner, app.state.block_cache
)
```

**Risk:** Low — additive routes. No existing route is modified.

---

## Phase 8 — qna-ai Frontend: DashboardResultSection + useBlockUpdates

**Goal:** In `qna-ai`, render a live dashboard instead of the old single-result view when the
API returns a `dashboard_id`.

### 8.1 — New hook: `apps/qna-ai/src/hooks/useBlockUpdates.ts`

```typescript
import { useEffect } from 'react';
import type { BlockState } from '@ui-gen/base-ui';

/**
 * Subscribes to the existing SSE stream (same EventSource already used for
 * execution_status events) and calls onBlockUpdate whenever a block_update
 * event arrives for this dashboardId.
 */
export function useBlockUpdates(
    sessionId: string,
    dashboardId: string,
    onBlockUpdate: (blockId: string, resultData: Record<string, unknown>) => void,
) {
    useEffect(() => {
        // The SSE EventSource is already open for this session — attach a listener
        // to the existing event bus / context rather than opening a new connection.
        const handler = (event: CustomEvent) => {
            const data = event.detail;
            if (data.type === 'block_update' && data.dashboard_id === dashboardId) {
                onBlockUpdate(data.block_id, data.result_data);
            }
        };
        window.addEventListener('sse_event', handler as EventListener);
        return () => window.removeEventListener('sse_event', handler as EventListener);
    }, [sessionId, dashboardId, onBlockUpdate]);
}
```

### 8.2 — New component: `apps/qna-ai/src/components/dashboard/DashboardResultSection.tsx`

```tsx
'use client';

import React, { useState, useCallback } from 'react';
import { DashboardCanvas, type BlockState, type DashboardSpec } from '@ui-gen/base-ui';
import { useBlockUpdates } from '@/hooks/useBlockUpdates';

interface Props {
    dashboardId: string;
    initialPlan: DashboardSpec & { blocks: Array<{ block_id: string; status: string; result_data?: any }> };
    sessionId: string;
}

export default function DashboardResultSection({ dashboardId, initialPlan, sessionId }: Props) {

    const [blockStates, setBlockStates] = useState<BlockState[]>(() =>
        initialPlan.blocks.map((b) => ({
            spec: b,
            loadState: (b.status === 'cached' || b.status === 'complete') ? 'loaded' : 'loading',
            data: b.result_data ?? undefined,
        }))
    );

    const handleBlockUpdate = useCallback((blockId: string, resultData: Record<string, unknown>) => {
        setBlockStates((prev) =>
            prev.map((bs) =>
                bs.spec.block_id === blockId
                    ? { ...bs, loadState: 'loaded', data: resultData }
                    : bs,
            )
        );
    }, []);

    useBlockUpdates(sessionId, dashboardId, handleBlockUpdate);

    return (
        <DashboardCanvas
            spec={initialPlan}
            blockStates={blockStates}
            specLoading={false}
        />
    );
}
```

### 8.3 — Wire into the chat message render path

In the component that currently renders `AnalysisResultSection`, add a branch:

```tsx
// Existing: analysis_id → AnalysisResultSection (unchanged)
// New:      dashboard_id → DashboardResultSection

const content = message.content;

if (content?.dashboard_id) {
    return (
        <DashboardResultSection
            dashboardId={content.dashboard_id}
            initialPlan={content}
            sessionId={sessionId}
        />
    );
}

// Existing single-analysis view remains as the fallback
return <AnalysisResultSection results={content} ... />;
```

### 8.4 — Wire the API call (chat submit path)

```typescript
// In the function that calls POST /analyze or equivalent:

// New: if backend returns dashboard_id, treat as dashboard
const response = await api.post('/api/dashboard/create', {
    question, sessionId, messageId,
});
// response.dashboard_id is set → 8.3 branch handles rendering
```

**Risk:** Low. The existing single-question path is the `else` fallback — untouched.

---

## Phase 9 — Retire `UIConfigurationRenderer` and Insight Components

**Goal:** Clean up `apps/qna-ai/src/components/insights/` once Phase 8 is stable.

### 9.1 — Verify zero remaining imports

```bash
cd frontend
grep -r "UIConfigurationRenderer\|from.*insights/" apps/qna-ai/src --include="*.tsx" --include="*.ts"
```

### 9.2 — Delete the entire insights directory

```
apps/qna-ai/src/components/insights/   ← DELETE (all 14 block files + UIConfigurationRenderer)
```

### 9.3 — Remove UIResultFormatter from backend

```
backend/shared/services/ui_result_formatter.py        ← DELETE
backend/shared/config/system-prompt-ui-formatter.txt  ← DELETE
```

Remove `create_shared_result_formatter` import and call from `execution_service.py`.

### 9.4 — Remove `AnalysisResultSection` references to `UIConfigurationRenderer`

The `AnalysisResultSection` component itself can stay (handles the single-execution fallback path)
but remove the `UIConfigurationRenderer` import and its rendering branch.

**Risk:** Low — only after Phase 8 is confirmed working end-to-end.

---

## Phase 10 — ai-builder: Wire Real Data (Optional Upgrade)

**Goal:** Allow `ai-builder` to optionally use the real execution pipeline instead of
`mockDataService.ts`. Keeps `ai-builder` as a standalone showcase that can also run against
real data.

### 10.1 — Add env toggle to `ai-builder`

```bash
# apps/ai-builder/.env.local
NEXT_PUBLIC_REAL_DATA=false    # flip to true to use qna-ai API
```

### 10.2 — New service: `apps/ai-builder/services/realDataService.ts`

```typescript
export async function fetchRealData(spec: BlockSpec): Promise<Record<string, unknown>> {
    const res = await fetch('/api/execute-block', {
        method: 'POST',
        body: JSON.stringify({ sub_question: spec.sub_question, canonical_params: spec.canonical_params }),
    });
    return res.json();
}
```

### 10.3 — Switch in `BuilderApp.tsx`

```typescript
const fetchFn = process.env.NEXT_PUBLIC_REAL_DATA === 'true' ? fetchRealData : fetchMockData;
// Replace fetchMockData(block) call with fetchFn(block)
```

**Risk:** Zero — opt-in via env flag. Mock data path unchanged.

---

## Data Flow — End to End

```
User types question in qna-ai chat
        │
        ▼
POST /api/dashboard/create
        │
        ▼
DashboardOrchestrator
  ├─ UIPlanner.plan(question)
  │     └─ LLM → DashboardSpec JSON (3–6 blocks + sub_questions)
  ├─ DashboardRepository.create(plan)
  └─ per block:
       ├─ BlockCacheService.lookup(cache_key)
       │    ├─ HIT  → status=CACHED, result_data ready  ──────────────┐
       │    └─ MISS → enqueue sub_question into AnalysisQueue          │
        │                                                              │
        ▼                                                              │
API returns DashboardPlan immediately                                  │
(cached blocks have result_data, pending blocks have status=pending)   │
        │                                                              │
        ▼                                                              │
DashboardResultSection renders DashboardCanvas                        │
  - Cached blocks: loadState='loaded' (paint immediately) ◄───────────┘
  - Pending blocks: loadState='loading' (skeleton shimmer)
        │
        │  (in parallel, for each MISS block:)
        ▼
AnalysisWorker picks up sub_question
        │
        ▼
ExecutionWorker runs script
        │
        ▼
execution_service.py
  └─ DashboardRepository.update_block(status=COMPLETE, result_data)
  └─ send_progress_event(session_id, { type: "block_update", block_id, result_data })
        │
        ▼ (SSE)
useBlockUpdates hook receives event
        │
        ▼
setBlockStates → loadState='loaded', data=result_data
        │
        ▼
DashboardCanvas re-renders block with real data (base-ui BlockShell)
```

---

## File Change Summary

### New files (backend)
```
backend/shared/services/ui_planner.py
backend/shared/services/block_cache_service.py
backend/shared/services/dashboard_orchestrator.py
backend/shared/db/dashboard_repository.py
backend/shared/config/system-prompt-ui-planner.txt
backend/apiServer/api/dashboard_routes.py
```

### Modified files (backend)
```
backend/shared/db/schemas.py                    (+BlockPlanModel, +DashboardPlanModel)
backend/shared/db/repositories.py              (+DashboardRepository registration)
backend/apiServer/services/execution_service.py (+15 lines hookback)
backend/apiServer/api/routes.py                 (+dashboard_router)
backend/apiServer/main.py                       (+orchestrator wiring)
```

### Deleted files (backend)
```
backend/shared/services/ui_result_formatter.py
backend/shared/config/system-prompt-ui-formatter.txt
```

### New files (frontend)
```
apps/base-ui/src/blocks/types.ts
apps/base-ui/src/blocks/DashboardCanvas.tsx     (moved from ai-builder)
apps/base-ui/src/blocks/BlockShell.tsx          (moved from ai-builder)
apps/qna-ai/src/hooks/useBlockUpdates.ts
apps/qna-ai/src/components/dashboard/DashboardResultSection.tsx
```

### Modified files (frontend)
```
apps/base-ui/src/blocks/index.ts                (+exports)
apps/ai-builder/services/dashboardAI.ts         (import types from base-ui)
apps/ai-builder/components/DashboardCanvas.tsx  (re-export from base-ui)
apps/ai-builder/components/BlockShell.tsx       (re-export from base-ui)
apps/qna-ai/src/components/AnalysisResultSection.tsx  (+dashboard_id branch)
```

### Deleted files (frontend — Phase 9)
```
apps/qna-ai/src/components/insights/           (entire directory — 16 files)
```

---

## Risk Register

| Risk | Mitigation |
|------|-----------|
| UIPlanner emits bad JSON | `safe_json_loads` + fallback to 1-block plan |
| Sub-question too vague for pipeline | UIPlanner prompt requires self-contained questions; can add a validation pass |
| Cache key collision (different questions → same params) | sha256 of sorted canonical_params is deterministic; review canonical_params keys for uniqueness |
| SSE event lost (client reconnect) | `GET /api/dashboard/{id}` provides full state on reconnect; frontend re-hydrates from it |
| Execution failure mid-dashboard | Failed blocks show error state in `BlockShell`; rest of dashboard renders normally |
| Phase 9 cleanup breaks existing sessions | Phase 9 runs after Phase 8 is confirmed; old sessions use `AnalysisResultSection` fallback |
| ai-builder breakage | Phase 1 makes ai-builder import types from base-ui — verified at type-check step |

---

## Acceptance Criteria per Phase

| Phase | Done when |
|-------|-----------|
| 1 | `npm run type-check` passes for all three apps; ai-builder renders identically |
| 2 | `UIPlanner.plan("How is QQQ doing?")` returns valid DashboardSpec with 3+ blocks |
| 3 | `DashboardPlanModel` round-trips to/from MongoDB; `find_cached_block` returns correct results |
| 4 | Cache HIT returns result within 5ms; MISS returns None |
| 5 | `create_dashboard` persists plan, dispatches N sub-questions to analysis queue |
| 6 | `execution_status=complete` for a sub-question triggers `block_update` SSE + DB update |
| 7 | `POST /api/dashboard/create` returns plan in <2s (UIPlanner latency only); blocks arrive via SSE |
| 8 | Dashboard renders skeleton immediately; cached blocks paint <100ms; executed blocks paint as SSE arrives |
| 9 | Zero references to `UIConfigurationRenderer` or `insights/` in qna-ai; `UIResultFormatter` gone |
| 10 | `NEXT_PUBLIC_REAL_DATA=true` in ai-builder uses real pipeline; mock path unchanged |
