# Mock V2 Architecture Diagram

## System Overview

```
                              USER QUESTION
                                    |
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
            [MOCK MODE]                    [NORMAL MODE]
                    |                               |
        ┌───────────┴────────┐            [Code Generation Path]
        ▼                    ▼
    [V1: Single-Shot]  [V2: Batch]
        |                    |
        ├─ UI Planner        ├─ UI Planner Batch V2
        │                    │   (decompose)
        ├─ Mock Reuse        ├─ Mock V2 Generator
        │  Evaluator         │   (generate per sub-Q)
        │                    │
        └─ Mock Data         └─ [Skip reuse/regen]
           Generator

        [Both produce same output format]
                    |
                    ▼
            Blocks + Mock Data
                    |
                    ▼
            Frontend Dashboard
```

## V2 Detailed Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER QUESTION                                   │
│          "Show me my equity portfolio with holdings and daily P&L"      │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │ Question Enhancer? │  (optional)
                    └────────────┬───────┘
                                 │
                                 ▼
                    ┌────────────────────────────────┐
                    │ UI Planner Batch V2 Agent      │
                    │                                │
                    │ Input: Question                │
                    │ Output: Decomposition          │
                    └────────────┬───────────────────┘
                                 │
        ┌────────────────────────┴──────────────────────────┐
        ▼                        ▼                          ▼
    [Sub-Q1]              [Sub-Q2]                  [Sub-Q3]
    ─────────              ──────────                ────────
    "What are my       "What is my            "What is my
    current stock      portfolio value?"      daily P&L?"
    holdings?"
    │                  │                      │
    Block: table       Block: kpi-card        Block: kpi-card
    │                  │                      │
    Params:            Params:                Params:
    metric=holdings    metric=value           metric=return
    │                  │                      │
    └──────────────────┴──────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Mock V2 Generator               │
        │                                  │
        │  Generate mock data for:         │
        │  ├─ Sub-Q1 → Table data          │
        │  ├─ Sub-Q2 → KPI data            │
        │  └─ Sub-Q3 → KPI data            │
        └────────────┬─────────────────────┘
                     │
        ┌────────────┴──────────────────┐
        ▼                               ▼
    Blocks Schema              Blocks Data
    ──────────────              ────────────
    [                          [
      {                          {
        blockId: table-01,         blockId: table-01,
        title: Holdings,           data: {
        dataContract: {...}          rows: [...],
      },                             columns: [...]
      {                            }
        blockId: kpi-01,          },
        title: Total Value,        {
        dataContract: {...}          blockId: kpi-01,
      },                             data: {metrics: [...]}
      {                            }
        blockId: kpi-02,          ]
        title: Daily P&L,
        dataContract: {...}
      }
    ]
        │                               │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Frontend HeadlessResult      │
        │                               │
        │   {                           │
        │     success: true,            │
        │     action: "mock_generated", │
        │     blocks: [...],            │
        │     blocks_data: [...]        │
        │   }                           │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   BlockShell Renderer          │
        │                               │
        │   For each block:             │
        │   1. Get blockId              │
        │   2. Find matching data       │
        │   3. Render with block type   │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Dashboard with 3 Blocks     │
        │                               │
        │   ┌─────────────────────────┐ │
        │   │ Portfolio Holdings (T)  │ │
        │   │ AAPL  50  180.25  9012  │ │
        │   │ MSFT  30  420.00 12600  │ │
        │   └─────────────────────────┘ │
        │                               │
        │   ┌───────────────────────┐   │
        │   │ Total Value     │ KPI │   │
        │   │ $125,450.00     │     │   │
        │   │ +2.3%           │     │   │
        │   └───────────────────────┘   │
        │                               │
        │   ┌───────────────────────┐   │
        │   │ Daily P&L       │ KPI │   │
        │   │ +$2,847.50      │     │   │
        │   │ +2.3%           │     │   │
        │   └───────────────────────┘   │
        │                               │
        └───────────────────────────────┘
```

## Component Diagram

```
                     ┌─────────────────────────┐
                     │   Orchestrator.py       │
                     │                         │
                     │ if mock_v2_mode:        │
                     │   - Skip UI Planner v1  │
                     │   - Use Batch V2 flow   │
                     └────────────┬────────────┘
                                  │
                  ┌───────────────┼───────────────┐
                  ▼               ▼               ▼
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │   Question   │  │ UI Planner   │  │  Mock V2     │
            │  Enhancer    │  │  Batch V2    │  │  Generator   │
            │              │  │              │  │              │
            │ (optional)   │  │ Decomposes   │  │ Generates    │
            │              │  │ into sub-Qs  │  │ mock data    │
            │ Expands      │  │              │  │              │
            │ question     │  │ Uses:        │  │ Uses:        │
            │              │  │ - system-    │  │ - Block type │
            │ Returns:     │  │   prompt-    │  │ - Params     │
            │ Enhanced     │  │   ui-plan-   │  │ - Period     │
            │ question     │  │   ner-batch- │  │              │
            │              │  │   v2.txt     │  │ Generates:   │
            │              │  │              │  │ - Realistic  │
            │              │  │ Returns:     │  │   data       │
            │              │  │ - original_  │  │ - Returns:   │
            │              │  │   question   │  │ - Blocks     │
            │              │  │ - intent     │  │ - BlocksData │
            │              │  │ - decomp     │  │              │
            │              │  │   -osition   │  │              │
            │              │  │ - dashboard_ │  │              │
            │              │  │   title      │  │              │
            └──────────────┘  └──────────────┘  └──────────────┘
                  │                  │                  │
                  └──────────────────┼──────────────────┘
                                     │
                                     ▼
                           ┌──────────────────┐
                           │  Frontend        │
                           │  HeadlessResult  │
                           └──────────────────┘
```

## Data Flow Through Stack

```
BACKEND                          FRONTEND
────────────────────────────────────────────────────

┌─────────────────────┐
│ Orchestrator        │
├─────────────────────┤
│ Input:              │
│ - question          │
│ - mock_v2_mode      │
│                     │
│ Process:            │
│ 1. Decompose        │
│ 2. Generate data    │
│                     │
│ Output:             │
│ - blocks[]          │         ┌───────────────┐
│ - blocks_data[]     │────────▶│ /api/headless │
│ - title             │         │ /run (POST)   │
│ - total_time        │         └───────┬───────┘
│ - steps             │                 │
└─────────────────────┘                 ▼
                              ┌──────────────────┐
                              │ route.ts         │
                              │                  │
                              │ Parse JSON       │
                              │ Create           │
                              │ HeadlessResult   │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ BuilderApp.tsx   │
                              │                  │
                              │ setBlockStates() │
                              │ setSpec()        │
                              │ setMessages()    │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ DashboardCanvas  │
                              │                  │
                              │ Render each      │
                              │ BlockState       │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ BlockShell       │
                              │                  │
                              │ Match blockId    │
                              │ Find data        │
                              │ Render block     │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Block Component  │
                              │ (e.g., Table01)  │
                              │                  │
                              │ Display UI       │
                              └──────────────────┘
```

## Comparison: V1 vs V2 Side by Side

```
V1 (Single-Shot)                    V2 (Batch)
─────────────────────────────────────────────────

Question                            Question
  │                                   │
  ├─ "Show portfolio with           ├─ "Show portfolio with
  │   holdings and P&L"             │   holdings and P&L"
  │                                 │
  ▼                                 ▼
UI Planner                    UI Planner Batch V2
  │                                 │
  └─ Generates all blocks      └─ Decomposes:
    in one shot                   ├─ Sub-Q1: Holdings
    (may miss details)            ├─ Sub-Q2: Value
                                  ├─ Sub-Q3: P&L

  ▼                                 ▼
Mock Data Generator           Mock V2 Generator
  │                                 │
  └─ One prompt for all       └─ One prompt per
    block data                   sub-question
    (complex)                     (simpler)

  ▼                                 ▼
  ├─ blocks[]                       ├─ blocks[]
  ├─ blocks_data[]                  ├─ blocks_data[]
  ├─ title                          ├─ title
  ├─ total_time                     ├─ total_time
  └─ steps                          └─ steps

  ▼                                 ▼
Dashboard (same format in both!)
  ├─ Table: Holdings
  ├─ KPI: Total Value
  └─ KPI: Daily P&L
```

## File Dependencies

```
┌──────────────────────────────────────┐
│ backend/headless/agents/             │
│ orchestrator.py                      │
│ (MAIN ORCHESTRATOR)                  │
└────────────┬──────────────────────────┘
             │
    ┌────────┼────────────────────────────┐
    │        │                            │
    ▼        ▼                            ▼
   [V1]   [V2 NEW]                    [EXISTING]
    │        │                            │
    ├────────┤                            │
    │        │                            ├─ question_enhancer_agent.py
    │        ├─ ui_planner_batch_v2_agent.py
    │        │   └─ system-prompt-ui-planner-batch-v2.txt
    │        │
    │        └─ mock/mock_v2_generator.py
    │
    ├─ ui_planner_agent.py
    │   └─ system-prompt-ui-planner.txt
    │
    ├─ mock/
    │   ├─ mock_data_generator.py (V1)
    │   └─ mock_reuse_evaluator.py
    │
    ├─ reuse_evaluator_agent.py
    ├─ code_prompt_builder_agent.py
    ├─ code_script_generator_agent.py
    ├─ script_validator_agent.py
    ├─ verification_agent.py
    ├─ script_executor_agent.py
    └─ mcp_direct_agent.py
```

## Command-Line Flow

```
Entry: orchestrator.py --question "..." --mock --mock-v2

Parse Arguments:
  ├─ question: "..."
  ├─ mock: true
  ├─ mock_v2: true ◄── Enables V2 mode
  └─ other flags...

Create Orchestrator:
  └─ AnalysisOrchestrator(mock_v2_mode=True)
       ├─ Initialize V2 agents if mock_v2_mode
       │   ├─ self.ui_planner_batch_v2
       │   └─ self.mock_v2_generator
       └─ Initialize V1 agents (always)
           ├─ self.ui_planner
           ├─ self.mock_reuse_evaluator
           └─ self.mock_data_generator

Process Question:
  └─ if mock_mode and mock_v2_mode:
       ├─ Step 1: Question Enhancer (optional)
       ├─ Step 2: UI Planner Batch V2 ◄── Different from V1
       ├─ Step 3: Mock V2 Generator ◄── Different from V1
       └─ Return combined result
     else if mock_mode:
       └─ Use V1 flow (original)
     else:
       └─ Use code generation flow

Output: JSON with blocks + blocks_data
```

## Integration Points

```
┌─────────────────────────────────────────┐
│ Frontend (TypeScript)                   │
│                                         │
│ route.ts                                │
│  ├─ POST /api/headless/run              │
│  ├─ Parse: mockV2 from request body     │
│  ├─ Add: --mock-v2 to Python args       │
│  └─ Execute orchestrator.py             │
│                                         │
└────────────────┬────────────────────────┘
                 │
                 │ Python subprocess
                 │
┌────────────────▼────────────────────────┐
│ Backend (Python)                        │
│                                         │
│ orchestrator.py                         │
│  ├─ Parse: --mock-v2 argument           │
│  ├─ Set: self.mock_v2_mode = True       │
│  └─ Route to V2 flow                    │
│                                         │
└────────────────┬────────────────────────┘
                 │
                 │ JSON to stdout
                 │
┌────────────────▼────────────────────────┐
│ Frontend (TypeScript)                   │
│                                         │
│ route.ts                                │
│  ├─ Parse JSON from orchestrator        │
│  ├─ Create HeadlessResult               │
│  ├─ Return to BuilderApp.tsx            │
│                                         │
│ BuilderApp.tsx                          │
│  ├─ Receive HeadlessResult              │
│  ├─ setSpec(dashSpec)                   │
│  ├─ setBlockStates(blocks_data)         │
│  └─ Trigger re-render                   │
│                                         │
│ DashboardCanvas → BlockShell → Block    │
│  └─ Render dashboard                    │
│                                         │
└─────────────────────────────────────────┘
```

---

## Key Takeaway

**V2 = Decompose First, Generate Per Sub-Question**
- Breaks complex questions into simpler pieces
- Each piece gets its own data generation
- Same output format as V1
- Zero breaking changes to existing V1 code
