# @ui-gen/base-ui

Base UI Block-level Components for investment and trading dashboards.

## Purpose

This package contains **block-level components** — financial semantic blocks built on base primitives.

## What This Package Does NOT Contain

- ❌ No primitives (Card, Grid, Chart, Table, etc.)
- ❌ No adapters to visual libraries (Tremor, Carbon, etc.)
- ❌ No references to base-ui-legacy

## What This Package Contains

Block-level components represent:
- Financial concepts (performance, risk, portfolio, strategy)
- Semantic aggregations of base primitives
- Reusable patterns for LLM-driven UI generation

## Structure

```
src/
  blocks/          # Block-level components
  index.ts         # Public exports (currently empty)
```

## Build

```bash
npm run build
```

## Design Principles

1. **Semantically stable** — Components represent financial concepts, not visual whims
2. **Reusable** — Each component applies across 10+ unrelated questions
3. **Orthogonal** — No component duplicates another's intent
4. **Deterministic** — Components map cleanly to base primitives