# Mock V2 Testing & Validation Checklist

## Pre-Flight Check

### Code Structure
- [ ] `backend/shared/config/system-prompt-ui-planner-batch-v2.txt` exists
- [ ] `backend/headless/agents/ui_planner_batch_v2_agent.py` exists
- [ ] `backend/headless/agents/mock/mock_v2_generator.py` exists
- [ ] `backend/headless/agents/orchestrator.py` updated with V2 support
- [ ] All new files have correct imports
- [ ] No syntax errors in Python files

### Import Chain
```python
# orchestrator.py should have:
from ui_planner_batch_v2_agent import create_ui_planner_batch_v2
from mock.mock_v2_generator import create_mock_v2_generator

# ui_planner_batch_v2_agent.py should have:
from agent_base import AgentBase, AgentResult

# mock_v2_generator.py should have:
from agent_base import AgentBase, AgentResult
```

- [ ] All imports can be resolved
- [ ] No circular dependencies

## Unit Tests

### Test UI Planner Batch V2 Agent

```bash
cd backend/headless/agents
python ui_planner_batch_v2_agent.py
```

**Expected Output**:
```json
{
  "data": {
    "original_question": "...",
    "intent": "...",
    "decomposition": [
      {
        "sub_question": "...",
        "block_type": "...",
        "title": "...",
        "description": "...",
        "canonical_params": {...}
      }
    ],
    "dashboard_title": "..."
  },
  "success": true
}
```

- [ ] Success flag is `true`
- [ ] Decomposition array has 2-4 items
- [ ] Each sub_question is unique
- [ ] Block types are valid (kpi-card, line-chart, bar-chart, bar-list, donut-chart, table, spark-chart)
- [ ] Canonical params are reasonable

### Test Mock V2 Generator

```bash
cd backend/headless/agents
python mock/mock_v2_generator.py
```

**Expected Output**:
```json
{
  "data": {
    "blocks": [...],
    "blocks_data": [...]
  },
  "success": true
}
```

- [ ] Success flag is `true`
- [ ] Blocks array has entries
- [ ] Blocks_data array matches block count
- [ ] Each block has blockId, category, title, dataContract
- [ ] Each block_data has blockId and data payload
- [ ] Data payloads are reasonable (not null, not empty)

## Integration Tests

### Test V2 End-to-End

**Simple Question**:
```bash
python backend/headless/agents/orchestrator.py \
  --question "What is the QQQ ETF price?" \
  --mock --mock-v2 --skip-enhancement
```

**Expected**:
- [ ] Returns `"success": true`
- [ ] `"action": "mock_generated"`
- [ ] Blocks count matches decomposition count
- [ ] Blocks_data count matches blocks count
- [ ] Total time < 5 seconds
- [ ] All steps completed successfully

**Complex Question**:
```bash
python backend/headless/agents/orchestrator.py \
  --question "Show me my equity portfolio with holdings and daily P&L" \
  --mock --mock-v2 --skip-enhancement
```

**Expected**:
- [ ] Returns `"success": true`
- [ ] Decomposed into 3+ sub-questions
- [ ] Each sub-question has appropriate block type
- [ ] Mock data is realistic
  - [ ] Prices in reasonable range ($50-$500)
  - [ ] Percentages reasonable (-20% to +50%)
  - [ ] Table has actual rows
  - [ ] All data fields populated

### Test V1 Still Works

```bash
python backend/headless/agents/orchestrator.py \
  --question "What is the QQQ ETF price?" \
  --mock --skip-enhancement
```

**Expected**:
- [ ] Returns `"success": true`
- [ ] `"action": "mock_generated"`
- [ ] Uses old UI Planner (not Batch V2)
- [ ] Results match previous V1 behavior
- [ ] No regression

### Test Output File Structure

```bash
python backend/headless/agents/orchestrator.py \
  --question "Show QQQ price" \
  --mock --mock-v2 --skip-enhancement \
  --output-dir "./test_output"
```

**Check directory structure**:
```
test_output/
└── show_qqq_price/
    ├── final_result.json          ✓ Contains full result
    ├── _debug.log                 ✓ Contains step logs
    ├── ui_planner_batch_v2.json  ✓ Decomposition step
    └── mock_v2_generator.json    ✓ Generation step
```

- [ ] final_result.json valid JSON
- [ ] final_result.json has all expected fields
- [ ] All step files exist
- [ ] All step files are valid JSON

## Frontend Integration Tests

### Verify API Compatibility

In `frontend/apps/ai-builder/app/api/headless/run/route.ts`:

```typescript
// Verify these are handled:
const { question, useNoCode, mock, skipReuse, mockV2 } = body;

// Check args construction:
if (mockV2) {
  args.push('--mock-v2');
}
```

- [ ] mockV2 parameter parsed from request
- [ ] --mock-v2 flag passed to Python
- [ ] Route still works without mockV2
- [ ] Route works with mockV2

### Verify Service Integration

In `frontend/apps/ai-builder/services/dashboardAI.ts`:

```typescript
export async function runHeadlessPipeline(
  question: string,
  options?: {
    useNoCode?: boolean;
    mock?: boolean;
    mockV2?: boolean;
    skipReuse?: boolean;
  }
): Promise<HeadlessResult>
```

- [ ] Function signature accepts mockV2
- [ ] Passes mockV2 to API route
- [ ] Works without mockV2 (backward compatible)

### Test Full Flow (Manual)

1. Start frontend dev server:
```bash
cd frontend/apps/ai-builder
npm run dev
```

2. Test with V2 disabled (should use V1):
```javascript
// In browser console or update BuilderApp temporarily
const result = await runHeadlessPipeline(
  "Show me my equity portfolio with holdings and daily P&L",
  { mock: true, skipReuse: true }
);
console.log(result);
```

- [ ] Dashboard renders
- [ ] All blocks show
- [ ] Data appears in tables/charts
- [ ] No errors in console

3. Test with V2 enabled:
```javascript
// If frontend updated to accept V2 flag
const result = await runHeadlessPipeline(
  "Show me my equity portfolio with holdings and daily P&L",
  { mock: true, mockV2: true, skipReuse: true }
);
console.log(result);
```

- [ ] Dashboard renders
- [ ] All blocks show
- [ ] Data appears in tables/charts
- [ ] No errors in console
- [ ] Performance similar to V1

## Data Validation Tests

### Check Block Data Consistency

```python
import json

with open('test_output/show_qqq_price/final_result.json') as f:
    result = json.load(f)

blocks = result['blocks']
blocks_data = result['blocks_data']

# Check 1: Same count
assert len(blocks) == len(blocks_data), "Block count mismatch"

# Check 2: Same IDs in same order
for block, data in zip(blocks, blocks_data):
    assert block['blockId'] == data['blockId'], \
        f"ID mismatch: {block['blockId']} vs {data['blockId']}"
    assert data.get('data') is not None, \
        f"No data for {data['blockId']}"

# Check 3: Data matches schema
for data in blocks_data:
    block_id = data['blockId']
    block_type = block_id.split('-')[0]  # e.g., "table" from "table-01"

    if block_type == 'table':
        assert 'rows' in data['data'], "Table missing rows"
        assert 'columns' in data['data'], "Table missing columns"
        assert len(data['data']['rows']) > 0, "Table empty"
    elif 'kpi' in block_type:
        assert 'metrics' in data['data'], "KPI missing metrics"
        assert len(data['data']['metrics']) > 0, "KPI empty"

print("✓ All data validation checks passed!")
```

- [ ] Run validation script successfully
- [ ] No assertion errors
- [ ] Block counts match
- [ ] Data is populated
- [ ] Data structures are correct

## Performance Tests

### Measure Execution Time

```bash
# V1
time python backend/headless/agents/orchestrator.py \
  --question "Show me my equity portfolio" --mock --skip-enhancement

# V2
time python backend/headless/agents/orchestrator.py \
  --question "Show me my equity portfolio" --mock --mock-v2 --skip-enhancement
```

- [ ] V1 execution time < 5s
- [ ] V2 execution time < 5s
- [ ] V2 not significantly slower than V1

### Memory Usage

```bash
# Monitor memory during execution
python -m memory_profiler backend/headless/agents/orchestrator.py \
  --question "Show me my equity portfolio" --mock --mock-v2 --skip-enhancement
```

- [ ] Memory usage reasonable (< 500MB)
- [ ] No memory leaks (check with repeated runs)

## Error Handling Tests

### Test Invalid Inputs

```bash
# No decomposition
python backend/headless/agents/orchestrator.py \
  --question "" --mock --mock-v2

# Very long question
python backend/headless/agents/orchestrator.py \
  --question "$(python -c 'print("a" * 10000)')" \
  --mock --mock-v2
```

- [ ] Handles empty question gracefully
- [ ] Handles very long input
- [ ] Returns proper error messages
- [ ] Doesn't crash

### Test Missing Files

```bash
# Rename prompt file temporarily
mv backend/shared/config/system-prompt-ui-planner-batch-v2.txt \
   backend/shared/config/system-prompt-ui-planner-batch-v2.txt.bak

# Try to run
python backend/headless/agents/orchestrator.py \
  --question "Show QQQ" --mock --mock-v2

# Restore
mv backend/shared/config/system-prompt-ui-planner-batch-v2.txt.bak \
   backend/shared/config/system-prompt-ui-planner-batch-v2.txt
```

- [ ] Returns proper error message
- [ ] Doesn't crash with traceback
- [ ] Suggests what's missing

## Regression Tests

### Ensure V1 Not Affected

```bash
# Run same question with V1 multiple times
python backend/headless/agents/orchestrator.py \
  --question "Show QQQ price" --mock --skip-enhancement

python backend/headless/agents/orchestrator.py \
  --question "Show QQQ price" --mock --skip-enhancement

python backend/headless/agents/orchestrator.py \
  --question "Show QQQ price" --mock --skip-enhancement
```

- [ ] All runs succeed
- [ ] Results are consistent
- [ ] No degradation

### Ensure Normal Code Path Not Affected

```bash
# Try non-mock, non-v2 mode
python backend/headless/agents/orchestrator.py \
  --question "Show QQQ price" --no-code --skip-enhancement
```

- [ ] Succeeds
- [ ] Uses MCP direct mode
- [ ] No regression

## Documentation Tests

### Verify Examples Work

From `MOCK_V2_README.md`:

```bash
# Example 1: Portfolio Overview
python backend/headless/agents/orchestrator.py \
  --question "Show me my equity portfolio with holdings and daily P&L" \
  --mock --mock-v2 --skip-enhancement

# Example 2: QQQ Analysis
python backend/headless/agents/orchestrator.py \
  --question "What is the QQQ ETF price and how is it performing this month?" \
  --mock --mock-v2 --skip-enhancement

# Example 3: Sector Performance
python backend/headless/agents/orchestrator.py \
  --question "Which sectors in my portfolio are performing best?" \
  --mock --mock-v2 --skip-enhancement
```

- [ ] All examples produce valid results
- [ ] Output matches expected format
- [ ] Documentation is accurate

## Sign-Off Checklist

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] V1 compatibility verified
- [ ] Performance acceptable
- [ ] Error handling works
- [ ] Documentation is accurate
- [ ] Code is committed
- [ ] No warnings or errors in logs

## Known Issues & Workarounds

### Issue: LLM Returns Empty Decomposition
**Symptom**: `decomposition: []`
**Cause**: LLM model or prompt issue
**Fix**:
- Check LLM model is available
- Verify prompt file is readable
- Check question is clear enough

### Issue: Mock Data Too Simple
**Symptom**: All values same or pattern is obvious
**Cause**: Random generation uses fixed seeds
**Fix**: V2 generator can be enhanced with more realistic distributions

### Issue: Frontend Cache Stale
**Symptom**: Frontend shows old results after changing code
**Cause**: Browser cache
**Fix**: Clear browser cache, do hard refresh (Cmd+Shift+R)

## Success Criteria

✅ **Core Functionality**:
- [ ] V2 mode produces valid output
- [ ] Output matches frontend expectations
- [ ] All blocks render properly

✅ **Backward Compatibility**:
- [ ] V1 mode still works
- [ ] Normal code path unaffected
- [ ] No breaking changes

✅ **Performance**:
- [ ] V2 comparable to V1 speed
- [ ] Memory usage reasonable
- [ ] No resource leaks

✅ **Robustness**:
- [ ] Handles errors gracefully
- [ ] Validates inputs
- [ ] Logs properly

✅ **Documentation**:
- [ ] All files documented
- [ ] Examples accurate
- [ ] API clear
