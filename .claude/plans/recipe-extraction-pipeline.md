# Recipe Extraction Pipeline Plan

## Overview

Extract reusable recipe patterns from UI Planner sub-questions to create a catalog of dashboard building blocks.

## Goal

Create a recipe catalog where each recipe represents:
- A reusable sub-question pattern
- The atomic MCP function sequence to answer it
- Standardized input/output schemas
- Frequency tracking across the question bank

## Architecture

```
consolidated_questions.json (1,813 questions)
    ↓
UI Planner Agent (decompose into blocks with sub-questions)
    ↓
sub_questions.json (~6,000 sub-questions, 3-6 per question)
    ↓
Recipe Extractor Agent (cluster similar patterns)
    ↓
recipe_catalog.json (~50-100 unique recipes)
    ↓
Dashboard Components (built from recipes)
```

## Components

### 1. UI Planner Agent (`.claude/agents/ui-planner.md`)
- Decomposes user questions into dashboard blocks
- Each block has a `sub_question` field - the atomic question to answer
- Uses `system-prompt-ui-planner.txt` prompt
- Outputs JSON with blocks, canonical_params, and block categories

### 2. Recipe Extractor Agent (`.claude/agents/recipe-extractor.md`)
- Analyzes all sub-questions from UI Planner output
- Normalizes sub-questions (extracts patterns, replaces entities with placeholders)
- Clusters similar sub-questions by semantic similarity and params
- Extracts MCP function sequences for each cluster
- Generates recipe catalog with frequency, complexity, and path metadata

## Recipe Structure

```json
{
  "id": "portfolio_performance_kpi",
  "name": "Portfolio Performance KPI",
  "description": "Calculate key portfolio performance metrics",
  "sub_question_patterns": ["What are my portfolio key performance metrics?"],
  "canonical_params": ["period", "benchmark"],
  "frequency": 234,
  "function_sequence": [
    {"step": 1, "function": "get_portfolio_history"},
    {"step": 2, "function": "calculate_annualized_return"},
    {"step": 3, "function": "calculate_sharpe_ratio"}
  ],
  "input_schema": {...},
  "output_schema": {...},
  "path": "direct_mcp",
  "dashboard_components": ["kpi-cards", "sparkline"]
}
```

## Common Recipe Types

- **Portfolio Analysis**: performance summary, sector allocation, position ranking
- **Market Analysis**: security performance, sector comparison, top gainers/losers
- **Technical Analysis**: indicator values, signal detection, pattern recognition
- **Fundamental Analysis**: fundamentals summary, financial ratios, valuation metrics

## Implementation Steps

### Phase 1: UI Planner (Test)
- [x] Create UI Planner agent
- [ ] Run UI Planner on sample questions (10-20)
- [ ] Verify output format and sub-question quality
- [ ] Run on full question bank if test passes

### Phase 2: Recipe Extractor (Test)
- [x] Create Recipe Extractor agent
- [ ] Run on UI Planner output from Phase 1
- [ ] Verify clustering and function extraction
- [ ] Review recipe catalog for accuracy

### Phase 3: Full Pipeline
- [ ] Run UI Planner on full question bank (1,813 questions)
- [ ] Run Recipe Extractor on all sub-questions
- [ ] Generate final recipe catalog
- [ ] Identify gaps (sub-questions requiring script_generation)

### Phase 4: Integration
- [ ] Map recipes to dashboard components
- [ ] Create recipe execution layer
- [ ] Integrate with dashboard builder

## Expected Outputs

| File | Content |
|------|---------|
| `all-questions/sub_questions.json` | All sub-questions from UI Planner |
| `all-questions/recipe_catalog.json` | Catalog of reusable recipes |
| `all-questions/unmatched_patterns.json` | Sub-questions not covered by recipes |

## Success Metrics

- **Recipe coverage**: % of sub-questions covered by recipes (target: >70%)
- **Recipe diversity**: Number of unique recipes (expected: 50-100)
- **Direct MCP coverage**: % of recipes using direct_mcp path (target: >60%)
- **Reduction**: % of questions that can be answered using only recipe combinations

## Notes

- Recipes are larger units than atomic functions
- Recipes represent the "glue" logic between atomic functions
- Sub-questions are the interface between questions and recipes
- The question_classifier agent should potentially also check against recipes