# Mock V2: Hierarchical Question Decomposition System

## Overview

**Mock V2** (Decomposition Mode) takes a **single user question** and decomposes it into **atomic sub-questions**, then generates mock data for each sub-question independently. This contrasts with **Mock V1** (Single-Shot Mode) which plans the entire dashboard from the question in one go.

```
V1 (Single-Shot)              V2 (Decomposition)
─────────────────             ──────────────────

Question                      Question
    ↓                            ↓
UI Planner                    UI Planner Batch V2
(plan blocks from Q)          (decompose Q into sub-Qs)
    ↓                            ↓
Mock Data Generator           Mock V2 Generator
(data for all blocks)         (data per sub-Q)
    ↓                            ↓
Dashboard                     Dashboard
```

## Why V2 (Decomposition)?

- **V1 limitation**: LLM must understand all data requirements at once → longer prompts, less precise
- **V2 advantage**: Break complex question into simple, focused sub-questions → clearer intent, easier to generate targeted mock data
- **Better composability**: Each atomic sub-question can be answered independently by financial data pipeline

## Key Components

### 1. System Prompt: `system-prompt-ui-planner-batch-v2.txt`

Instructs the LLM to:
- Break questions into 2-4 **atomic** sub-questions
- Each sub-question must directly contribute to answering the original
- Map sub-questions to appropriate block types
- Extract canonical parameters (ticker, period, metric, etc.)

**Example decomposition**:
```
Original Question: "Show me my equity portfolio with holdings and daily P&L"

Decomposition:
├─ Sub-Q1: "What are my current stock holdings?"
│   Block: table, Params: {metric: holdings}
├─ Sub-Q2: "What is my portfolio value?"
│   Block: kpi-card, Params: {metric: portfolio_value}
└─ Sub-Q3: "What is my daily portfolio return?"
    Block: kpi-card, Params: {metric: return}
```

### 2. Agent: `ui_planner_batch_v2_agent.py`

**Input**: Financial question
**Output**: Decomposed sub-questions with block types and parameters

```python
{
  "original_question": "Show me my equity portfolio with holdings and daily P&L",
  "intent": "User wants to understand portfolio composition and daily performance",
  "decomposition": [
    {
      "sub_question": "What are my current stock holdings?",
      "block_type": "table",
      "title": "Portfolio Holdings",
      "description": "Shows current holdings with quantities and values",
      "canonical_params": {"metric": "holdings"}
    },
    ...
  ],
  "dashboard_title": "Portfolio Overview"
}
```

### 3. Generator: `mock_v2_generator.py`

**Input**: Decomposed sub-questions
**Output**: Mock data for each sub-question

Generates realistic mock data for 7 block types:
- `kpi-card`: Single metrics (prices, returns, volatility)
- `line-chart`: Time-series trends (price over time, P&L trends)
- `bar-chart`: Comparisons (sector performance, returns by period)
- `bar-list`: Ranked items (top holdings, sectors by momentum)
- `donut-chart`: Composition/allocation (portfolio sectors, holdings)
- `table`: Detailed rows (holdings list, sector details)
- `spark-chart`: Mini time-series (volatility trend, momentum)

```python
# Input
{
  "original_question": "...",
  "decomposition": [
    {
      "sub_question": "What are my current stock holdings?",
      "block_type": "table",
      "title": "Portfolio Holdings",
      "canonical_params": {"metric": "holdings"}
    }
  ]
}

# Output
{
  "blocks": [
    {
      "blockId": "table-01",
      "category": "tables",
      "title": "Portfolio Holdings",
      "dataContract": {...},
      "sub_question": "...",
      "canonical_params": {...}
    }
  ],
  "blocks_data": [
    {
      "blockId": "table-01",
      "data": {
        "rows": [...],
        "columns": ["symbol", "shares", "price", "value", "P&L", "P&L %"]
      }
    }
  ]
}
```

## Usage

### From Command Line

**V1 (Single-Shot)**:
```bash
python orchestrator.py --question "Show QQQ ETF price" --mock
```

**V2 (Batch Decomposition)**:
```bash
python orchestrator.py --question "Show QQQ ETF price" --mock --mock-v2
```

### From Frontend

The frontend's `buildDashboardSpec()` function can be updated to accept a `mock_v2` flag:

```typescript
const result = await runHeadlessPipeline(question, {
  useNoCode: true,
  mock: true,
  mockV2: true,  // Enable batch decomposition
  skipReuse: true
});
```

## Pipeline Flow

### V2 Full Pipeline

```
1. Question Enhancer (optional)
   ↓
   Expanded question
   ↓
2. UI Planner Batch V2
   ↓
   Decomposition (sub-questions, block types, params)
   ↓
3. Mock V2 Generator
   ↓
   Blocks + Mock data
   ↓
4. Frontend Renderer
   ↓
   Dashboard
```

## File Structure

```
backend/headless/agents/
├── ui_planner_batch_v2_agent.py        ← New: Batch decomposition
├── mock/
│   ├── mock_v2_generator.py            ← New: V2 data generation
│   ├── mock_data_generator.py          ← Existing: V1 data generation
│   └── mock_reuse_evaluator.py         ← Existing: Cache lookup
├── orchestrator.py                      ← Updated: Added v2 support
└── MOCK_V2_README.md                   ← This file

backend/shared/config/
├── system-prompt-ui-planner-batch-v2.txt  ← New: Batch decomposition prompt
└── system-prompt-ui-planner.txt         ← Existing: V1 single-shot prompt
```

## Comparison: V1 vs V2

| Aspect | V1 | V2 |
|--------|----|----|
| **Approach** | Single-shot decomposition | Batch decomposition into sub-Qs |
| **UI Planner** | `ui_planner_agent.py` | `ui_planner_batch_v2_agent.py` |
| **Data Generator** | `mock_data_generator.py` | `mock_v2_generator.py` |
| **Reuse Evaluator** | Used (ChromaDB lookup) | Not used (V2 is atomic) |
| **Best For** | Simple-to-moderate questions | Complex questions with multiple aspects |
| **Command** | `--mock` | `--mock --mock-v2` |

## Example Walkthrough

### Question
```
"Show me my equity portfolio with holdings and daily P&L"
```

### Step 1: UI Planner Batch V2
Decomposes into:
```json
{
  "decomposition": [
    {
      "sub_question": "What are my current stock holdings?",
      "block_type": "table",
      "title": "Portfolio Holdings"
    },
    {
      "sub_question": "What is my total portfolio value?",
      "block_type": "kpi-card",
      "title": "Total Value"
    },
    {
      "sub_question": "What is my daily P&L?",
      "block_type": "kpi-card",
      "title": "Daily P&L"
    }
  ]
}
```

### Step 2: Mock V2 Generator
Generates data for each sub-question independently:
```json
{
  "blocks": [
    {
      "blockId": "table-01",
      "title": "Portfolio Holdings",
      "dataContract": {"type": "table", ...}
    },
    {
      "blockId": "kpi_card-01",
      "title": "Total Value",
      "dataContract": {"type": "kpi", ...}
    },
    {
      "blockId": "kpi_card-02",
      "title": "Daily P&L",
      "dataContract": {"type": "kpi", ...}
    }
  ],
  "blocks_data": [
    {
      "blockId": "table-01",
      "data": {
        "rows": [
          {"symbol": "AAPL", "shares": 50, "price": 180.25, "value": 9012.50, "P&L": 512.50, "P&L %": 6.0},
          {"symbol": "MSFT", "shares": 30, "price": 420.00, "value": 12600.00, "P&L": -200.00, "P&L %": -1.6},
          ...
        ],
        "columns": ["symbol", "shares", "price", "value", "P&L", "P&L %"]
      }
    },
    {
      "blockId": "kpi_card-01",
      "data": {
        "metrics": [
          {
            "label": "Total Value",
            "value": "$125,450.00",
            "change": "+2.3%",
            "changeType": "positive"
          }
        ]
      }
    },
    {
      "blockId": "kpi_card-02",
      "data": {
        "metrics": [
          {
            "label": "Daily P&L",
            "value": "+$2,847.50",
            "change": "+2.3%",
            "changeType": "positive"
          }
        ]
      }
    }
  ]
}
```

### Step 3: Frontend Renders
Dashboard displays all blocks with realistic mock data.

## Integration with Frontend

### Current Frontend API

```typescript
// In frontend: dashboardAI.ts
export async function runHeadlessPipeline(
  question: string,
  options?: {
    useNoCode?: boolean;
    mock?: boolean;
    mockV2?: boolean;  // Add this
    skipReuse?: boolean;
  }
): Promise<HeadlessResult>
```

### Updated Orchestration

```typescript
// In route.ts
const args = [scriptPath, '--question', question];
if (useNoCode) args.push('--no-code');
if (mock) args.push('--mock');
if (mockV2) args.push('--mock-v2');  // Add this
if (skipReuse) args.push('--skip-reuse');
```

## Future: Real Data Integration

Currently, V2 generates **mock data**. To integrate with real financial data:

1. **Replace mock data generation** with actual financial API calls
2. **Use canonical parameters** (ticker, period, metric) to fetch real data
3. **Reuse data pipeline**: Each sub-question's `canonical_params` can be passed to the existing financial data pipeline
4. **Combine results**: Aggregate real data from all sub-questions into final dashboard

```python
# Example future enhancement
class FinancialDataGeneratorV2(AgentBase):
    """Generates REAL financial data for atomic sub-questions"""

    def generate_for_sub_question(self, sub_q, params):
        # Use canonical_params to fetch real data
        # ticker=AAPL, period=30d → fetch AAPL prices for 30 days
        # metric=holdings → fetch real portfolio holdings from Alpaca
        # etc.
        pass
```

## Testing

### Test V2 Locally

```bash
# Test ui_planner_batch_v2_agent
python backend/headless/agents/ui_planner_batch_v2_agent.py

# Test mock_v2_generator
python backend/headless/agents/mock/mock_v2_generator.py

# Test full orchestrator with v2
python backend/headless/agents/orchestrator.py \
  --question "Show me my equity portfolio with holdings and daily P&L" \
  --mock --mock-v2 --skip-enhancement
```

### Test with Frontend

```bash
# In BuilderApp.tsx, toggle the new V2 flag
const result = await runHeadlessPipeline(question, {
  mock: true,
  mockV2: true,  // Enable V2
  skipReuse: true
});
```

## Key Design Decisions

1. **Atomic sub-questions**: Each is independently answerable
2. **Batch processing**: Decompose once, generate data N times (not nested)
3. **Reusability**: Both V1 and V2 work in parallel (backward compatible)
4. **Extensibility**: Easy to add new block types and mock data generators

## Troubleshooting

### V2 not generating blocks
- Check `ui_planner_batch_v2_agent.py` LLM output
- Ensure question is clear and specific
- Look for `decomposition` field in output

### Mock data missing for some blocks
- Check `mock_v2_generator.py` block_type handling
- Verify `canonical_params` are passed correctly
- Look for block_type mismatches

### Frontend shows empty dashboard
- Check browser console for `blocks_data` array
- Ensure `blockId` matches between `blocks` and `blocks_data`
- Compare with V1 mock mode output

## References

- `ui-planner-batch-v2.md`: Original batch processing concept
- `system-prompt-ui-planner.txt`: V1 single-shot prompt (for comparison)
- `mock_data_generator.py`: V1 generator (for data generation patterns)
