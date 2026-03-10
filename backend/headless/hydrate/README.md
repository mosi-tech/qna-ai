# Cache Hydration Pipeline

> Location: `backend/headless/hydrate/`
> Purpose: Discover and warm generic question templates for high cache hit rates.

## Overview

The hydration pipeline iteratively discovers **generic question templates** that enable
script reuse across different tickers, periods, and parameters.

```
Specific Question: "What is QQQ's current price?"
                         │
                         ▼ Genericize (block-aware)
                         │
Generic Template: "What is {{ticker}}'s current price?"
                         │
                         ▼ Cache key
                         │
hash(template + block_type) → cached script
```

**Same generic template → same cached script → any ticker.**

## Files

```
backend/headless/hydrate/
  hydrate_pipeline.py    — Main pipeline script
  prompts.py             — LLM prompts for question generation and genericization
  output/                — Auto-created; hydration reports saved here
```

## Usage

```bash
# Quick test without LLM (uses fallback questions)
python hydrate_pipeline.py --max-iterations 500

# With LLM for realistic question generation
python hydrate_pipeline.py --use-llm --warm-cache 500

# Full pipeline with UIPlanner
python hydrate_pipeline.py --use-planner --use-llm --max-iterations 1000

# Run until 95% hit rate
python hydrate_pipeline.py --target 0.95 --max-iterations 5000
```

## Pipeline Flow

```
┌───────────────────────┐
│ QuestionGenerator     │  LLM generates 100s of realistic questions
│ (or fallback)         │  in a single call
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ UIPlanner             │  Decomposes each question into blocks
│ (or mock)             │  Each block: sub_question + block_type + dataContract
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ GenericQuestionGen    │  Converts specific → generic template
│                       │  "What is QQQ's price?" → "What is {{ticker}}'s price?"
│                       │  Block-aware: output must fit block's data contract
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ CacheSimulator        │  Tracks hit rate
│                       │  generic_key = hash(template + block_type)
└───────────────────────┘

Repeat until 95% hit rate or max iterations
```

## Generic Question Format

```python
{
    "template": "What is {{ticker}}'s current price?",
    "params": ["ticker"],
    "block_type": "kpi-cards",
    "output_shape": "single scalar value",
    "block_contract": {"type": "kpi", "points": 1},
    "generic_key": "80b2a854886ead9c"
}
```

## Block-Aware Genericization

The generic question must produce output that the block can render:

| Block Type | Expects | Generic Form Example |
|------------|---------|---------------------|
| kpi-cards | 1-6 scalar values | "What is {{ticker}}'s price?" |
| line-chart | time series | "What is {{ticker}}'s price history over {{period}}?" |
| comparison-chart | 2+ series | "Compare {{ticker1}} and {{ticker2}} performance" |
| table | rows/columns | "What are {{ticker}}'s top holdings?" |

Same question + different block → different generic template:

```
"QQQ price trend" + kpi-cards  → "What are {{ticker}}'s key price metrics?"
"QQQ price trend" + line-chart → "What is {{ticker}}'s price history?"
```

## Output

After running, a report is saved to `output/hydrate_<timestamp>.json`:

```json
{
  "stats": {
    "total_questions": 500,
    "cache_hits": 425,
    "cache_misses": 75,
    "unique_generic_questions": 42
  },
  "hit_rate": "85.0%",
  "top_generic_questions": [
    {"template": "What is {{ticker}}'s current price?", "hit_count": 25},
    ...
  ],
  "block_type_coverage": {
    "kpi-cards": 250,
    "line-chart": 150,
    ...
  }
}
```

## Prompts

See `prompts.py` for:

- `QUESTION_GENERATOR_PROMPT` — Generates realistic user questions
- `GENERIC_QUESTION_PROMPT` — Converts specific → generic (block-aware)
- `BLOCK_CONTEXT_PROMPT` — Determines block type for a question