# Mock V2 (Decomposition) System Setup & Quick Start

## What Was Created

### 1. New Components
- **`backend/shared/config/system-prompt-ui-planner-batch-v2.txt`**
  - LLM prompt for hierarchical question decomposition
  - Instructs LLM to break one question into 2-4 atomic sub-questions

- **`backend/headless/agents/ui_planner_batch_v2_agent.py`**
  - Decomposes questions into atomic sub-questions
  - Returns decomposition with block types and parameters

- **`backend/headless/agents/mock/mock_v2_generator.py`**
  - Generates realistic mock data for each sub-question
  - Handles 7 block types: kpi-card, line-chart, bar-chart, bar-list, donut-chart, table, spark-chart

- **`backend/headless/agents/orchestrator.py`** (Updated)
  - Added `mock_v2_mode` parameter
  - Added `--mock-v2` command-line flag
  - V2 flow: Skip normal UI planner, use batch decomposition instead

- **`backend/headless/agents/MOCK_V2_README.md`**
  - Comprehensive documentation on V2 architecture
  - Comparison with V1
  - Usage examples and troubleshooting

### 2. Backward Compatibility
- **V1 still works fully**: `--mock` alone uses single-shot mode
- **V2 is opt-in**: Requires both `--mock` and `--mock-v2` flags
- **No existing code changed**: Only additions and new flags

## Quick Start

### Test V2 from Command Line

```bash
# Simple test
python backend/headless/agents/orchestrator.py \
  --question "Show me my equity portfolio with holdings and daily P&L" \
  --mock --mock-v2 --skip-enhancement

# With all options
python backend/headless/agents/orchestrator.py \
  --question "Which sectors are performing best?" \
  --mock --mock-v2 --skip-enhancement --skip-reuse -v
```

### Test Individual V2 Components

```bash
# Test UI Planner Batch V2
python backend/headless/agents/ui_planner_batch_v2_agent.py
# Output: Decomposed sub-questions

# Test Mock V2 Generator
python backend/headless/agents/mock/mock_v2_generator.py
# Output: Mock data for 3 sample blocks
```

### Update Frontend (Optional)

In `frontend/apps/ai-builder/app/api/headless/run/route.ts`:

```typescript
// Add mockV2 to the request body parsing
const { question, useNoCode, mock, skipReuse, mockV2 } = body;

// Add to args
if (mockV2) {
  args.push('--mock-v2');
}
```

In `frontend/apps/ai-builder/services/dashboardAI.ts`:

```typescript
export async function runHeadlessPipeline(
  question: string,
  options?: {
    useNoCode?: boolean;
    mock?: boolean;
    mockV2?: boolean;      // Add this
    skipReuse?: boolean;
  }
): Promise<HeadlessResult> {
  // ... existing code
  body.mockV2 = options?.mockV2 ?? false;
}
```

In `frontend/apps/ai-builder/components/BuilderApp.tsx`:

```typescript
// Add toggle for V2 mode
const [mockV2Mode, setMockV2Mode] = useState(false);

// Update handleSend call
headlessResult = await runHeadlessPipeline(text, {
  useNoCode: true,
  mock: mockMode,
  mockV2: mockV2Mode,    // Add this
  skipReuse
});
```

## Architecture Comparison

### V1 (Single-Shot)
```
Question → UI Planner → Blocks → Mock Data Generator → Blocks + Data
```
- Plan dashboard blocks directly from question
- Generate all data together
- Good for simple/focused questions

### V2 (Decomposition)
```
Question → Decompose into Sub-Qs → Mock V2 Generator → Blocks + Data
```
- Decompose question into atomic sub-questions first
- Generate data per sub-question independently
- Better for complex multi-aspect questions

## Key Features of V2 (Decomposition)

✅ **Atomic Sub-Questions**: Each stands alone, answerable independently
✅ **Hierarchical**: Decompose once, generate data per sub-question
✅ **Type-Specific Mock Data**: Tailored to each block type
✅ **Realistic Data**: Random but sensible values (stock prices, P&L %, etc.)
✅ **Backward Compatible**: V1 still fully functional
✅ **Extensible**: Easy to add new block types or integrate real data

## Expected Output Structure

Both V1 and V2 return the same format:
```json
{
  "success": true,
  "action": "mock_generated",
  "title": "Portfolio Overview",
  "blocks": [
    {
      "blockId": "table-01",
      "category": "tables",
      "title": "Portfolio Holdings",
      "dataContract": {...}
    },
    ...
  ],
  "blocks_data": [
    {
      "blockId": "table-01",
      "data": {
        "rows": [...],
        "columns": [...]
      }
    },
    ...
  ],
  "total_time": 2.34,
  "steps": [...]
}
```

## File Locations Summary

```
✓ Created:
  backend/shared/config/system-prompt-ui-planner-batch-v2.txt
  backend/headless/agents/ui_planner_batch_v2_agent.py
  backend/headless/agents/mock/mock_v2_generator.py
  backend/headless/agents/MOCK_V2_README.md
  MOCK_V2_SETUP.md (this file)

✓ Updated:
  backend/headless/agents/orchestrator.py
    - Added mock_v2_mode parameter
    - Added --mock-v2 flag
    - Added V2 pipeline logic
    - Added imports for V2 components

✓ Still working (V1):
  backend/headless/agents/mock/mock_data_generator.py
  backend/headless/agents/mock/mock_reuse_evaluator.py
  backend/shared/config/system-prompt-ui-planner.txt
  All existing code paths
```

## Testing Checklist

- [ ] Test V1 still works: `--mock` without `--mock-v2`
- [ ] Test V2 basic: `--mock --mock-v2` with simple question
- [ ] Test V2 complex: `--mock --mock-v2` with multi-aspect question
- [ ] Check blocks_data matches blocks structure
- [ ] Verify mock data is realistic (prices, percentages, etc.)
- [ ] Test with `--skip-enhancement` flag
- [ ] Test with `--skip-reuse` flag
- [ ] Check output file saves correctly

## Troubleshooting

**V2 agent not found error?**
- Ensure `ui_planner_batch_v2_agent.py` is in `backend/headless/agents/`
- Check import in orchestrator.py: `from ui_planner_batch_v2_agent import create_ui_planner_batch_v2`

**Empty decomposition?**
- Check LLM response in `ui_planner_batch_v2_agent.py`
- Verify question is clear (not too vague)
- Check system prompt file exists

**No mock data generated?**
- Check `mock_v2_generator.py` is called
- Verify `mock_v2_mode` is set to True
- Check block_type handling for your blocks

**Frontend still shows old data?**
- Clear browser cache
- Restart frontend dev server
- Check `--skip-reuse` flag is used

## Next Steps

1. **Test V2 locally** from command line with sample questions
2. **Verify output** matches expected structure
3. **Update frontend** with V2 flag (optional but recommended for testing)
4. **Integrate real data** (future enhancement)
5. **Add V2 UI toggle** in dashboard builder (optional)

## References

- Full documentation: `backend/headless/agents/MOCK_V2_README.md`
- Batch concept: `.claude/agents/ui-planner-batch-v2.md`
- V1 comparison: `backend/shared/config/system-prompt-ui-planner.txt`
