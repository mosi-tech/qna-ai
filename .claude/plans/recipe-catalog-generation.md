# Recipe Catalog Generation Plan

## Overview

Extract reusable recipe patterns from user questions by decomposing questions into sub-questions and clustering similar patterns.

## Architecture

```
consolidated_questions.json (1,813 questions)
    ↓
UI Planner Agent (3-6 sub-questions per question)
    ↓
sub_questions.json (~6,000 sub-questions)
    ↓
Recipe Extractor Agent (cluster & extract)
    ↓
recipe_catalog.json (~50-100 recipes)
```

## Agents Created

### 1. UI Planner Agent
- Location: `.claude/agents/ui-planner.md`
- Purpose: Decompose user questions into dashboard blocks with sub-questions
- Input: User question(s)
- Output: JSON with blocks containing sub_question and canonical_params

### 2. Recipe Extractor Agent
- Location: `.claude/agents/recipe-extractor.md`
- Purpose: Analyze sub-questions, cluster similar patterns, extract function sequences
- Input: sub_questions.json
- Output: recipe_catalog.json

## Implementation Steps

### Step 1: Run UI Planner Agent on Question Bank
- Process `all-questions/consolidated_questions.json`
- Generate `all-questions/sub_questions.json`

### Step 2: Test with Sample (Do First)
- Test UI Planner on 10-20 sample questions
- Test Recipe Extractor on output from Step 2
- Verify approach works end-to-end

### Step 3: Run Full Pipeline
- Run UI Planner on full question bank
- Run Recipe Extractor on full output
- Generate recipe_catalog.json

### Step 4: Review and Refine
- Review recipe catalog
- Identify gaps and low-confidence recipes
- Update agents if needed

## Output Files

- `all-questions/sub_questions.json` - All sub-questions from UI Planner
- `all-questions/recipe_catalog.json` - Final recipe catalog

## Recipe Structure

```json
{
  "id": "portfolio_performance_kpi",
  "name": "Portfolio Performance KPI",
  "sub_question_patterns": ["What are my portfolio key performance metrics?"],
  "frequency": 234,
  "function_sequence": [
    "get_portfolio_history",
    "calculate_annualized_return",
    "calculate_sharpe_ratio"
  ],
  "path": "direct_mcp"
}
```

## Status

- [x] Create UI Planner agent (.claude/agents/ui-planner-batch.md)
- [x] Create Recipe Extractor agent (.claude/agents/recipe-extractor.md)
- [x] Test with sample (v1 - generic sub-questions, needs improvement)
- [x] Run UI Planner on question bank (v1 - 1,813 → 11,708 generic sub-questions)
- [x] Run Recipe Extractor on sub-questions (v1 - 25 recipes from generic patterns)
- [x] Create improved UI Planner agent (.claude/agents/ui-planner-batch-v2.md) → v3 output
- [x] Test improved agent (v3 - 20 questions with context-specific sub-questions)
- [x] Create Block Mapper agent (.claude/agents/ui-planner-block-mapper.md)
- [x] Test Block Mapper (20 questions → dashboard_plans.json)
- [ ] Improve Block Mapper to extract canonical_params (ticker, period, metric)
- [ ] Run improved agents on full question bank (1,813 questions)
- [ ] Run Recipe Extractor on final output
- [ ] Review recipe catalog (pending)

## Block Mapper Status

**Tested on**: 20 questions
**Blocks generated**: 180 (9 blocks/question)
**Issues found**:
- ✓ blockId mapping to catalog (kpi-card-01, line-chart-01, etc.)
- ✓ category matching (kpi-cards, line-charts, donut-charts, etc.)
- ✓ dataContract type (kpi, timeseries, pie, etc.)
- ✓ context-specific sub-questions
- ✗ canonical_params empty - need to extract ticker, period, metric from sub-questions

**Example**:
```json
{
  "blockId": "kpi-card-01",
  "category": "kpi-cards",
  "dataContract": {"type": "kpi", "fields": [...]},
  "sub_question": "Which position has the highest unrealized gain?",
  "canonical_params": {}  ← Should extract entities
}
```

**Should be**:
```json
{
  "canonical_params": {"metric": "unrealized_gain", "limit": 1}
}
```

## Issues Found and Fixed

**v1 Issue**: Sub-questions were generic and didn't address original question
- Example: Question about drawdown → Sub-questions about "total portfolio value"
- Impact: Recipes extracted from generic patterns, not useful

**v3 Fix**: All sub-questions must directly address original question
- Example: Question about drawdown → Sub-questions about intraday drawdown
- Impact: Recipes will be context-specific and useful