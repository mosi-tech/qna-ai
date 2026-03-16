# Headless Agents Architecture

## Overview

Break down the monolithic analysis pipeline into independent, testable agents for rapid iteration and improvement.

## Directory Structure

```
backend/headless/agents/
├── ui_planner_agent.py          # Plans dashboard blocks from user question
├── question_enhancer_agent.py    # Enhances question with data requirements
├── reuse_evaluator_agent.py      # Finds reusable analyses in cache
├── code_prompt_builder_agent.py  # Analyzes question, selects MCP functions, builds enriched prompt
├── code_script_generator_agent.py # Generates Python scripts from enriched prompts
├── script_validator_agent.py     # Validates syntax and execution
├── verification_agent.py         # Multi-model verification of scripts
├── script_executor_agent.py      # Executes scripts and captures results
├── result_formatter_agent.py     # Formats output for dashboard rendering
├── agent_base.py                 # Base class with common agent functionality
├── run_single_agent.py           # Generic runner: run any agent standalone
├── orchestrator.py               # Chains agents together (when needed)
└── AGENTS.md                     # This file
```

## Key Design Principles

1. **Independent Contracts**: Each agent has clear JSON input/output
2. **Self-Contained Prompts**: Each agent has its own prompt file in `backend/shared/config/agents/`
3. **Testable in Isolation**: `run_single_agent.py` can run any agent with test data
4. **Composable**: `orchestrator.py` chains them when needed
5. **Versioned Prompts**: Keep prompt history for A/B testing

## Agent Contracts

### ui_planner_agent.py
**Input:**
```json
{
  "question": "Show QQQ ETF price and YTD return"
}
```

**Output:**
```json
{
  "title": "QQQ ETF Performance Dashboard",
  "blocks": [
    {"blockId": "kpi-card-01", "title": "QQQ Price", "category": "kpi-cards", "dataContract": {...}},
    ...
  ],
  "metadata": {"question_hash": "...", "timestamp": "..."}
}
```

### question_enhancer_agent.py
**Input:**
```json
{
  "question": "Show QQQ ETF price",
  "blocks": [...],  // From ui_planner
  "original_question": "Show QQQ ETF price and YTD return"
}
```

**Output:**
```json
{
  "enhanced_question": "Show QQQ ETF price and YTD return. Provide current price, daily change, 1-year history...",
  "data_requirements": [...],
  "metadata": {}
}
```

### reuse_evaluator_agent.py
**Input:**
```json
{
  "question": "Show QQQ ETF price",
  "existing_analyses": [...]
}
```

**Output:**
```json
{
  "should_reuse": true,
  "analysis_id": "xxx",
  "script_name": "qqq_performance_analysis.py",
  "similarity": 0.89,
  "reason": "..."
}
```

### code_prompt_builder_agent.py
**Input:**
```json
{
  "question": "Show QQQ ETF price",
  "blocks": [...],
  "context": {}
}
```

**Output:**
```json
{
  "enriched_prompt": "Analyze QQQ ETF and prepare data for comprehensive dashboard...",
  "selected_functions": ["financial_data__get_real_time_data", "financial_data__get_historical_data"],
  "analysis_type": "Single asset price analysis",
  "suggested_workflow": "Step 1: Fetch data. Step 2: Calculate metrics. Step 3: Return results.",
  "metadata": {...}
}
```

### code_script_generator_agent.py
**Input:**
```json
{
  "question": "Show QQQ ETF price",
  "enriched_prompt": "...",
  "selected_functions": [...],
  "context": {
    "validation_feedback": [
      {"attempt": 1, "errors": [...], "valid": false}
    ]
  }
}
```

**Output:**
```json
{
  "script": "#!/usr/bin/env python3\n...",
  "script_name": "show_qqq_etf_price_20260316_132526.py",
  "metadata": {...}
}
```

### script_validator_agent.py
**Input:**
```json
{
  "script": "#!/usr/bin/env python3\n..."
}
```

**Output:**
```json
{
  "valid": true,
  "syntax_valid": true,
  "execution_valid": true,
  "errors": [],
  "warnings": []
}
```

### verification_agent.py
**Input:**
```json
{
  "question": "Show QQQ ETF price",
  "script": "#!/usr/bin/env python3\n...",
  "context": {...}
}
```

**Output:**
```json
{
  "approved": true,
  "confidence": 0.92,
  "issues": [],
  "model_votes": {"glm-4.6": "approve", "gpt-oss:120b": "approve"}
}
```

### script_executor_agent.py
**Input:**
```json
{
  "script_path": "/path/to/script.py",
  "parameters": {"symbol": "QQQ"}
}
```

**Output:**
```json
{
  "success": true,
  "results": {...},
  "execution_time": 2.3,
  "error": null
}
```

### result_formatter_agent.py
**Input:**
```json
{
  "question": "Show QQQ ETF price",
  "script_results": {...},
  "blocks": [...]
}
```

**Output:**
```json
{
  "dashboard_data": {
    "kpi_metrics": {...},
    "charts": {...},
    "tables": {...}
  },
  "blocks_status": [...],
  "metadata": {}
}
```

## Running Agents

### Run Single Agent (Isolated Testing)
```bash
# UI Planner
python headless/agents/run_single_agent.py ui_planner \
    --input '{"question": "Show QQQ ETF price and YTD return"}'

# With custom prompt
python headless/agents/run_single_agent.py ui_planner \
    --input '{"question": "Show QQQ ETF price"}' \
    --prompt-file shared/config/agents/ui_planner_v2.txt

# With test data from file
python headless/agents/run_single_agent.py code_generator \
    --input-file test_data/code_gen_input.json \
    --output-file output/code_gen_output.json
```

### Run Orchestrator (Full Pipeline)
```bash
# Full pipeline (with enhancement, verification, execution)
python headless/agents/orchestrator.py \
    --question "Show QQQ ETF price and YTD return"

# Skip enhancement (for testing with well-formed questions)
python headless/agents/orchestrator.py \
    --question "Show QQQ ETF price and YTD return" \
    --skip-enhancement

# Skip verification (faster testing)
python headless/agents/orchestrator.py \
    --question "Show QQQ ETF price and YTD return" \
    --skip-verification

# Skip execution (generate and validate only)
python headless/agents/orchestrator.py \
    --question "Show QQQ ETF price and YTD return" \
    --skip-execution

# Combine skip flags for fastest testing
python headless/agents/orchestrator.py \
    --question "Show QQQ ETF price" \
    --skip-enhancement --skip-verification --skip-execution

# Configure retry behavior
python headless/agents/orchestrator.py \
    --question "Show QQQ ETF price" \
    --max-generation-attempts 5
```

**Pipeline Steps:**
1. `question_enhancer` - Expand short questions (skipped via `--skip-enhancement`)
2. `ui_planner` - Plan dashboard layout
3. `reuse_evaluator` - Check for reusable analyses
4. `code_prompt_builder` - Select MCP functions, build enriched prompt
5. `code_script_generator` - Generate Python script
6. `script_validator` - Validate script (with retry, max 3 attempts)
7. `verification_agent` - Multi-model verification (skipped via `--skip-verification`)
8. `script_executor` - Execute script (skipped via `--skip-execution`)

**Note:** Generated scripts should return data matching UI planner block contracts. No separate result formatter needed.

## Benefits

✅ **Iterate Fast**: Work on one agent without running full pipeline
✅ **A/B Test Prompts**: Swap prompt files easily
✅ **Parallel Development**: Different agents can be improved independently
✅ **Clear Fail Points**: Know exactly which agent failed
✅ **Performance Profile**: Time each agent independently

## Implementation Status

- [x] Create AGENTS.md (this file)
- [x] agent_base.py - Base class with LLM service, input/output validation, metrics
- [x] run_single_agent.py - Generic runner for any agent
- [x] ui_planner_agent.py - First working agent ✅
- [x] question_enhancer_agent.py - Expands short questions (runs before ui_planner) ✅
- [x] reuse_evaluator_agent.py - Checks for reusable analyses ✅
- [x] code_prompt_builder_agent.py - Analyzes question, selects MCP functions ✅
- [x] code_script_generator_agent.py - Generates scripts from enriched prompts ✅
- [x] script_validator_agent.py - AST-based validation with retry ✅
- [x] verification_agent.py - Multi-model verification (glm-4.7:cloud, gpt-oss:120b) ✅
- [x] script_executor_agent.py - Executes scripts ✅
- [x] orchestrator.py - Full pipeline with skip flags and retry mechanism ✅
- [x] result_formatter_agent.py - Removed (scripts should return UI-ready data)

## Two-Stage Code Generation

The code generation uses a two-stage approach:

1. **code_prompt_builder**:
   - Analyzes the financial question
   - Selects 3-6 relevant MCP functions
   - Builds enriched prompt with analysis type and workflow

2. **code_script_generator**:
   - Takes enriched prompt and selected functions
   - Generates Python script using `call_mcp_function()`
   - Includes validation feedback for retry attempts

## Unified Retry Loop

The orchestrator uses a unified retry loop for code generation:

```python
for gen_attempt in range(max_generation_attempts):
    # 1. Generate script (with feedback from previous failures)
    script = code_script_generator.execute({
        "enriched_prompt": enriched_prompt,
        "selected_functions": selected_functions,
        "question": question,
        "context": {
            "blocks": blocks,
            "validation_feedback": all_validation_messages,   # From previous validation failures
            "verification_feedback": all_verification_messages # From previous verification failures
        }
    })

    # 2. Validate script
    if not validation.valid:
        continue  # Retry generation with validation feedback

    # 3. Verify script (if not skipped)
    if not verification.approved:
        continue  # Retry generation with verification feedback

    # Both passed - done
    break
```

**Key points:**
- Generation is the restart point for ALL failures
- Validation failures → retry generation with `validation_feedback`
- Verification failures → retry generation with `verification_feedback`
- Configurable: `--max-generation-attempts` (default: 3)
- Feedback accumulates across attempts

## Step Output Saving

Each step's input and output are saved to `backend/headless/output/<question_name>/`:

```
backend/headless/output/show_qqq_etf_price/
├── question_enhancer.json  # Only if not skipped
├── ui_planner.json
├── reuse_evaluator.json
├── code_prompt_builder.json
├── code_script_generator.json
├── script_validator.json
├── verification.json       # Only if not skipped
├── script_executor.json     # Only if not skipped
└── final_result.json
```

Each JSON contains:
- `input`: Data passed to the agent
- `output`: Agent result
- `duration`: Execution time in seconds
- `timestamp`: ISO timestamp

## Prompt File Location

All agent prompts should be in: `backend/shared/config/agents/`

## Model Configuration

Agents use task-based model configuration via environment variables. See [MODEL_CONFIGURATION.md](MODEL_CONFIGURATION.md) for details on:
- Task-specific model configuration
- Verification model configuration
- Provider configuration
- Example .env files