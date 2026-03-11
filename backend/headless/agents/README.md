# Headless Agents

This directory contains scripts for running various headless agents to process financial questions and build dashboards.

## run_ui_planner_agent.py

Runs the ui-planner-system agent on the consolidated questions file, sending one question at a time to the LLM to generate dashboard structures with blocks, sub-questions, and data contracts.

### Installation

Requires the Anthropic SDK:

```bash
pip install anthropic
```

### Usage

```bash
# Process all questions
python backend/headless/agents/run_ui_planner_agent.py

# Process a range of questions
python backend/headless/agents/run_ui_planner_agent.py --start 1 --end 50

# Process with custom input/output
python backend/headless/agents/run_ui_planner_agent.py \
    --input all-questions/consolidated_questions.json \
    --output all-questions/sub_questions_ui_planner_system.json
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input` | Input JSON file with questions | `all-questions/consolidated_questions.json` |
| `--output` | Output JSON file for results | `all-questions/sub_questions_ui_planner_system.json` |
| `--start` | Start from question N (1-indexed) | `1` |
| `--end` | End at question N (1-indexed, inclusive) | Process all |
| `--agent-file` | Path to the ui-planner-system agent file | `.claude/agents/ui-planner-system.md` |
| `--model` | Claude model to use | `glm-4.7:cloud` |

### Output Format

Each question generates a dashboard structure:

```json
{
  "question_id": 1,
  "original_question": "What is my portfolio performance?",
  "title": "Portfolio Performance Dashboard",
  "subtitle": "Key metrics and trends for your investment portfolio",
  "layout": "grid",
  "blocks": [
    {
      "blockId": "kpi-card-01",
      "category": "kpi-cards",
      "title": "Portfolio Summary",
      "dataContract": {
        "type": "kpi",
        "description": "Total value, returns, and risk metrics",
        "points": 4
      },
      "sub_question": "What are my portfolio key performance metrics: total value, 30-day return, YTD return, and Sharpe ratio?",
      "canonical_params": {
        "metric": "performance_summary",
        "period": "30d"
      }
    },
    {
      "blockId": "line-chart-01",
      "category": "line-charts",
      "title": "Portfolio Value Over Time",
      "dataContract": {
        "type": "timeseries",
        "description": "Portfolio value history",
        "xAxis": "date",
        "yAxis": "value"
      },
      "sub_question": "Show my portfolio value history over the last year with monthly granularity",
      "canonical_params": {
        "period": "1y"
      }
    }
  ]
}
```

### Checkpointing

The script saves checkpoints every 10 questions to `sub_questions_ui_planner_system_checkpoint_N.json`, allowing you to resume progress if interrupted.

---

## run_function_planner_agent.py

Runs the function-planner agent on batches of financial questions to create a function registry and question-to-function mappings.

### Installation

Requires the Claude Agent SDK:

```bash
pip install claude-agent-sdk
```

### Usage

```bash
# Basic usage - process questions from sub_questions file in batches of 20
python backend/headless/agents/run_function_planner_agent.py

# Custom input file
python backend/headless/agents/run_function_planner_agent.py --input all-questions/my_questions.json

# Custom batch size
python backend/headless/agents/run_function_planner_agent.py --batch-size 50

# Custom output directory
python backend/headless/agents/run_function_planner_agent.py --output-dir all-questions/output

# All options
python backend/headless/agents/run_function_planner_agent.py \
    --input all-questions/sub_questions_ui_planner_system_v2.json \
    --batch-size 20 \
    --output-dir all-questions \
    --question-field original_question \
    --agent-file .claude/agents/function-planner.md
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input` | Input JSON file with questions | `all-questions/sub_questions_ui_planner_system_v2.json` |
| `--batch-size` | Number of questions per batch | `20` |
| `--output-dir` | Output directory for results | `all-questions` |
| `--question-field` | JSON path to question field | `original_question` |
| `--agent-file` | Path to the function-planner agent file | `.claude/agents/function-planner.md` |
| `--help` | Show help message | - |

### Input Format

The input file should be a JSON array where each item has a `question` or `original_question` field:

```json
[
  {
    "question_id": 1,
    "original_question": "What is AAPL's P/E ratio?",
    "blocks": [...]
  },
  {
    "question_id": 2,
    "original_question": "What is MSFT's market cap?",
    "blocks": [...]
  }
]
```

Or a simple array of question strings:

```json
[
  "What is AAPL's P/E ratio?",
  "What is MSFT's market cap?",
  "Show QQQ price history for 1 year"
]
```

### Output Files

The script generates two types of output files:

#### Per-Batch Files
- `function_registry_batch_N.json` - Custom functions created for batch N
- `question_function_mapping_batch_N.json` - Question mappings for batch N

#### Consolidated Files
- `function_registry.json` - Merged registry of all custom functions
- `question_function_mapping.json` - Merged mapping of all questions to functions

#### Example Output

**function_registry.json:**
```json
{
  "custom_functions": {
    "stock_fundamental": {
      "name": "get_stock_fundamental",
      "description": "Retrieve fundamental metrics for a stock",
      "parameters": {...},
      "implementation": {...},
      "questions": [1, 2, 5, 8]
    },
    "compare_stocks": {
      "name": "compare_stocks",
      "description": "Compare performance of multiple stocks",
      "parameters": {...},
      "implementation": {...},
      "questions": [3, 7]
    }
  },
  "metadata": {
    "total_custom_functions": 2,
    "total_questions": 10,
    "created_at": "..."
  }
}
```

**question_function_mapping.json:**
```json
{
  "mappings": [
    {
      "question": "What is AAPL's P/E ratio?",
      "mapping_type": "CUSTOM_REUSE",
      "custom_function": "stock_fundamental",
      "parameters": {"symbol": "AAPL", "metric": "pe_ratio"}
    },
    {
      "question": "What is MSFT's market cap?",
      "mapping_type": "CUSTOM_REUSE",
      "custom_function": "stock_fundamental",
      "parameters": {"symbol": "MSFT", "metric": "market_cap"}
    }
  ],
  "metadata": {
    "total_mappings": 10,
    "total_questions": 10
  }
}
```

### Summary Report

After processing all batches, the script displays a summary report:

```
============================================================
FINAL SUMMARY REPORT
============================================================
Total questions processed: 100
Total batches processed: 5
Batch size: 20

Mapping Type Breakdown:
  MCP_DIRECT: 15 (15.0%)
  MCP_PARAMETERIZED: 25 (25.0%)
  CUSTOM_REUSE: 60 (60.0%)

Unique Custom Functions Created: 8
Reusability Rate: 60.0%
Average Questions per Function: 12.5

Output Files:
  - all-questions/function_registry.json
  - all-questions/question_function_mapping.json
============================================================
```

### Agent Integration

The script uses the `function-planner` agent defined in `.claude/agents/function-planner.md`. The agent:

1. Analyzes each question to determine if it can be answered by an existing MCP function
2. Creates reusable custom functions when patterns emerge
3. Maps each question to the appropriate function or MCP call
4. Tracks reusability across all questions

### Troubleshooting

**Import Error: claude_agent_sdk not found**
```bash
pip install claude-agent-sdk
```

**Input file not found**
Check that the input file path is correct relative to the project root.

**Agent file not found**
Check that the `.claude/agents/function-planner.md` file exists in your project root.

### Future Agents

Additional agent runners can be added to this directory following the same pattern:

- `run_ui_planner_agent.py` - Run UI planner agent for dashboard generation
- `run_recipe_extractor_agent.py` - Extract reusable recipes from sub-questions
- `run_cache_key_generator_agent.py` - Generate cache keys for function calls