# Data Rendering Debug Guide

## Quick Test: Data Flow Tracing

We've added comprehensive logging to trace where data is lost. Follow these steps:

### 1. Start the Frontend Dev Server
```bash
cd frontend/apps/ai-builder
npm run dev
```

### 2. Open Browser Console
- Open DevTools (F12 or Cmd+Option+I)
- Go to **Console** tab
- Keep it visible while testing

### 3. Make a Request with Logging
1. In the UI, enter question: `Show me my equity portfolio with holdings, daily P&L, sector allocation and YTD performance`
2. Toggle: **Mock Mode ON** + **Skip Cache ON**
3. Press Enter

### 4. Check Logs at Each Stage

#### Frontend Console (Browser DevTools)
```
[BuilderApp] Result received: {
  status: "mock_generated",
  ui_blocks_count: 3,
  blocks_data_count: 3,
  blocks_data_sample: {
    block_id: "kpi-card-01",
    has_data: true,
    data_keys: ["metrics", "cols"]
  }
}

[BuilderApp] Matching blocks to data:
  dashSpec.blocks: ["kpi-card-01", "donut-chart-04", "table-action-01"]
  blocksData: ["kpi-card-01", "donut-chart-04", "table-action-01"]

[BuilderApp] ✓ Matched kpi-card-01 with data
[BuilderApp] ✓ Matched donut-chart-04 with data
[BuilderApp] ✓ Matched table-action-01 with data
```

If you see **"No data found for block"** warnings, that's the issue.

#### Next.js Server Logs
Look for timestamps and block counts:
```
[2026-03-18T20:17:47.877195Z] [headless/run] POST received: {
  question: "Show me my equity portfolio...",
  useNoCode: true,
  mock: true,
  skipReuse: true
}

[2026-03-18T20:17:47.877195Z] [headless/run] Process exited with code: 0
[2026-03-18T20:17:47.877195Z] [headless/run] ✅ Parsed orchestrator result: {
  success: true,
  action: "mock_generated",
  blocks: 3,
  blocks_data: 3
}

[2026-03-18T20:17:47.877195Z] [headless/run] ✅ Returning HeadlessResult: {
  status: "mock_generated",
  blocks: 3,
  blocks_data_count: 3,
  elapsed_s: 92.03
}
```

#### Backend Output File
Check the orchestrator's debug info:
```bash
cat backend/headless/output/show_me_my_equity_portfolio_with_holdings,_daily_p/final_result.json | jq '._debug'
```

Should show:
```json
{
  "blocks_count": 3,
  "blocks_data_count": 3,
  "blocks_ids": ["kpi-card-01", "donut-chart-04", "table-action-01"],
  "blocks_data_ids": ["kpi-card-01", "donut-chart-04", "table-action-01"],
  "success": true,
  "action": "mock_generated"
}
```

## Data Flow Checklist

✅ **Orchestrator**: Returns blocks + blocks_data with matching blockIds
✅ **route.ts**: Transforms blockId → block_id, matches with block titles
✅ **Frontend received**: blocks_data array with correct block_id values
✅ **Frontend matching**: Finds matching data for each block by block_id

If any step fails, the issue is at that stage.

## Common Issues & Fixes

### Issue: No data shows on UI
**Symptoms**: Blocks render but no data visible

**Checklist**:
1. Browser console shows `blocks_data_count: 0`?
   → Problem in route.ts transformation
2. Browser console shows matching failures for some blocks?
   → blockIds don't match (see blocks vs blocksData arrays)
3. Server logs show process exit code != 0?
   → Orchestrator crashed, check stderr logs

### Issue: "Skip Cache" button doesn't work
**Symptoms**: Still shows cached data even after clicking skip cache

**Checklist**:
1. Check server logs for: `[headless/run] ⚠️  SKIP CACHE ENABLED`
   → If missing, button click didn't pass flag
2. Check orchestrator logs for: `🧪 Mock mode enabled (skip_reuse=True)`
   → If False, flag wasn't passed to orchestrator
3. Check if reused data blockIds match current UI layout
   → If not matching, should generate fresh data

### Issue: Table shows 1 row instead of 5+
**Symptoms**: Table renders but only partial data

**Checklist**:
1. Check final_result.json blocks_data for table block
2. Count rows in `table.data.rows` array
3. If < 5 rows, issue is in mock_data_generator

## File Locations for Debugging

```
Backend output:
  /backend/headless/output/{question_id}/
    ├── final_result.json       ← Full orchestrator output with _debug
    ├── ui_planner.json         ← UI layout (blocks)
    ├── mock_data_generator.json ← Mock data generation details
    └── _debug.log              ← Timestamp log of each step

Frontend request/response:
  Browser DevTools → Network → /api/headless/run
  → See full request/response JSON

Server logs:
  Next.js console where you ran `npm run dev`
  Search for: `[headless/run]` prefix
```

## How to Share Logs for Debugging

When reporting "no data rendered":

1. **Browser console** (copy-paste entire [BuilderApp] section)
2. **Server logs** (last 50 lines from dev server)
3. **Backend output** (curl):
   ```bash
   cat backend/headless/output/show_me_my_equity_portfolio_with_holdings,_daily_p/final_result.json | jq '{success, action, blocks: (.blocks | length), blocks_data: (.blocks_data | length), _debug}'
   ```

This will show exactly where the data flow breaks.
