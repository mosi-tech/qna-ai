# UI Performance Optimization Plan

## Problem Statement

Current flow for answering dashboard questions is slow:
```
User Question → Planner Agent → UI Block Assignment → Analysis Engine
→ Script Generation (LLM) → Script Execution → Result → UI Render
```

**Bottleneck**: Script generation + execution takes 5-10 seconds per question

**Goal**: Reduce response time to <2 seconds for 70%+ of questions

---

## Solution: Hybrid Function-First Architecture

```
User Question → Planner Agent
                    ↓
         ┌─────────┴─────────┐
         ↓                   ↓
  Function Registry      Script Generation
    (Direct Call)          (Fallback)
         ↓                   ↓
    MCP Result          Generated Script
         ↓                   ↓
         └─────────┬─────────┘
                   ↓
              UI Render
```

---

## Three-Tier Response System

| Tier | Path | Speed | Complexity | Coverage Target |
|------|------|-------|------------|-----------------|
| **1. Direct Function** | Function Registry | ⚡⚡⚡ 100-500ms | Medium | 50-60% |
| **2. Template Library** | Pre-built templates | ⚡⚡ 1-2s | Low | 20-30% |
| **3. Script Generation** | Analysis Engine (fallback) | 5-10s | High | 10-20% |

---

## Phase 1: Function Registry (Fastest Path)

### Purpose
Pre-built functions that map directly to MCP calls with no script generation.

### Implementation

```python
# backend/headless/registry/function_registry.py

class FunctionRegistry:
    """Registry of pre-built functions for common question patterns"""

    def __init__(self):
        self.functions = {
            # Direct MCP mappings
            "calculate_var": {
                "function": "mcp__mcp_analytics_server__calculate_var",
                "params": ["returns", "confidence_level"],
                "question_patterns": [
                    r"calculate.*VaR.*at\s+(\d+)%?",
                    r"value at risk.*(\d+)",
                    r"VaR.*(\d+)\s*percent"
                ]
            },
            "get_top_gainers": {
                "function": "mcp__mcp_financial_server__get_top_gainers",
                "params": ["limit"],
                "question_patterns": [
                    r"top\s+(\d+)\s+gainers",
                    r"stocks with biggest.*gain"
                ]
            },
            # Custom composites from gap analysis
            "momentum_analysis": {
                "function": "backend.headless.functions.momentum_analysis",
                "params": ["symbols", "window"],
                "question_patterns": [
                    r"momentum.*over\s+(\d+)\s+days",
                    r"highest momentum"
                ]
            },
            "sector_analysis": {
                "function": "backend.headless.functions.sector_analysis",
                "params": ["symbols"],
                "question_patterns": [
                    r"sector.*allocation",
                    r"industry.*allocation"
                ]
            }
        }

    def resolve(self, question: str) -> Optional[Dict]:
        """Match question to registered function"""
        for name, func in self.functions.items():
            for pattern in func["question_patterns"]:
                if re.match(pattern, question, re.IGNORECASE):
                    return {
                        "function": func["function"],
                        "params": self._extract_params(question, pattern, func["params"])
                    }
        return None
```

### Files to Create
- `backend/headless/registry/function_registry.py`
- `backend/headless/registry/__init__.py`

---

## Phase 2: Question Classifier Agent

### Purpose
Quickly determines the optimal response path for a given question.

```markdown
---
name: question-classifier
description: Rapidly classifies questions into: direct_function, template, or script_generation path for optimal response speed.
tools: Read, Grep
memory: project
maxTurns: 3
---

You are a question classifier. Your job is to determine the fastest path to answer a question.

## Classification Rules

1. **direct_function** (Fastest - 100-500ms)
   - Question maps to a registered function in function_registry
   - Single, well-defined operation
   - Examples:
     - "Calculate VaR at 95%" → calculate_var
     - "Top 10 gainers" → get_top_gainers
     - "My sector allocation" → sector_analysis

2. **template** (Medium - 1-2s)
   - Question matches a pre-built template pattern
   - Multi-step but predictable flow
   - Examples:
     - "Compare AAPL and MSFT performance" → comparison_template
     - "Backtest SMA crossover strategy" → backtest_template

3. **script_generation** (Fallback - 5-10s)
   - Novel question, no matching function or template
   - Complex, custom analysis required
   - Examples:
     - "Analyze how earnings announcements affect my portfolio's beta"
     - "Build a custom strategy based on RSI and volume divergences"

## Output Format

```json
{
  "path": "direct_function|template|script_generation",
  "target": "function_name|template_name|analysis_engine",
  "confidence": 0.95,
  "params": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

## Process

1. Parse the question
2. Check against function_registry patterns
3. If match → return direct_function
4. Else check template library patterns
5. If match → return template
6. Else → return script_generation

Keep responses brief and fast. This is a classification task, not an analysis task.
```

---

## Phase 3: Template Library

### Purpose
Pre-built script templates with parameter placeholders for medium-complexity questions.

### Template Examples

```python
# backend/headless/templates/comparison_template.py

COMPARISON_TEMPLATE = """
# Comparison Analysis Template

# Fetch historical data
symbols = {symbols}
start_date = "{start_date}"
end_date = "{end_date}"

data = get_historical_data(symbols, timeframe="1D", start_date, end_date)

# Calculate returns
returns = calculate_log_returns(data)

# Calculate metrics
metrics = {
    "returns": calculate_annualized_return(returns),
    "volatility": calculate_annualized_volatility(returns),
    "sharpe": calculate_sharpe_ratio(returns),
    "max_drawdown": calculate_max_drawdown(returns)
}

return metrics
"""

def render_template(template_name: str, params: Dict) -> str:
    """Render template with parameters"""
    # Fill in placeholders and return executable script
```

---

## Phase 4: Multi-Level Caching

### Purpose
Reduce redundant work by caching responses at multiple levels.

### Cache Strategy

```python
# backend/headless/cache/response_cache.py

class ResponseCache:
    """Multi-level caching for question responses"""

    def __init__(self):
        self.l1_cache = {}  # Memory cache (hot)
        self.redis = Redis()  # L2 shared cache
        self.ttls = {
            "real_time": 60,      # 1 minute for live data
            "intraday": 300,      # 5 minutes for intraday
            "historical": 86400   # 1 day for historical
        }

    def get(self, question_hash: str, data_type: str):
        # Try L1, then L2, return None if miss
        pass

    def set(self, question_hash: str, result, data_type: str):
        # Set both L1 and L2 with appropriate TTL
        pass
```

### Cache Keys

```python
# Question-based cache
cache_key = f"question:{hash(question)}"

# Parameter-based cache (for same question, different params)
cache_key = f"template:{template_name}:{hash(params)}"

# Function-based cache (for direct functions)
cache_key = f"function:{function_name}:{hash(params)}"
```

---

## Phase 5: Orchestration Layer

### Purpose
Coordinate the flow through classifier → registry/template/script → cache → UI.

```python
# backend/headless/orchestrator/response_orchestrator.py

class ResponseOrchestrator:
    """Orchestrates question answering through optimal path"""

    def __init__(self):
        self.classifier = QuestionClassifier()
        self.registry = FunctionRegistry()
        self.templates = TemplateLibrary()
        self.cache = ResponseCache()
        self.analysis_engine = AnalysisEngine()

    async def answer(self, question: str) -> Dict:
        """Answer a question using the fastest available path"""

        # Check cache first
        cache_key = hash_question(question)
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Classify question
        classification = await self.classifier.classify(question)

        # Route to appropriate path
        if classification["path"] == "direct_function":
            result = self._call_function(classification)
        elif classification["path"] == "template":
            result = self._render_template(classification)
        else:
            result = await self.analysis_engine.generate_and_execute(question)

        # Cache result
        self.cache.set(cache_key, result, classification["data_type"])

        return result
```

---

## Implementation Priority

| Phase | Priority | Effort | Impact | Timeline |
|-------|----------|--------|--------|----------|
| **Function Registry** | P1 | Medium | High | 1 week |
| **Question Classifier Agent** | P1 | Low | High | 2-3 days |
| **Response Cache** | P1 | Low | High | 2-3 days |
| **Template Library** | P2 | Medium | Medium | 1 week |
| **Orchestration Layer** | P1 | Medium | High | 1 week |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         UI Dashboard                             │
│                    (User asks question)                          │
└─────────────────────────┬───────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Question Classifier Agent                    │
│           (Determines fastest response path in <100ms)            │
└───────┬─────────────────────┬─────────────────────┬────────────┘
        ↓                     ↓                     ↓
┌───────────────┐    ┌───────────────┐    ┌──────────────────┐
│ Function      │    │ Template      │    │ Analysis Engine  │
│ Registry      │    │ Library       │    │ (Fallback)        │
│               │    │               │    │                  │
│ • Direct MCP  │    │ • Fill params │    │ • Generate       │
│ • Composite   │    │ • Execute     │    │ • Execute        │
│ • 100-500ms   │    │ • 1-2s        │    │ • 5-10s          │
└───────┬───────┘    └───────┬───────┘    └────────┬─────────┘
        ↓                     ↓                     ↓
        └─────────────────────┴─────────────────────┘
                          ↓
                 ┌─────────────────┐
                 │ Response Cache  │
                 │ (L1: Memory)    │
                 │ (L2: Redis)     │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │   UI Block      │
                 │   Render        │
                 └─────────────────┘
```

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Avg Response Time** | 5-10s | <2s | 70th percentile |
| **P95 Response Time** | 15-20s | <5s | 95th percentile |
| **Cache Hit Rate** | 0% | >70% | Daily average |
| **Direct Function Coverage** | 0% | 50-60% | Questions matched |
| **Template Coverage** | 0% | 20-30% | Questions matched |
| **Script Generation Usage** | 100% | <20% | Questions requiring it |

---

## Related Files

- `all-questions/function_gap_analysis.json` - Missing functions to implement
- `all-questions/consolidated_questions.json` - Question corpus for training
- `.claude/agents/function-discovery.md` - Function discovery agent
- `.claude/agents/function-builder.md` - Function implementation agent
- `.claude/agents/question-harvester.md` - Question harvesting agent

---

## Next Steps

1. ✅ Create question-classifier agent
2. Implement function_registry.py
3. Implement response_cache.py
4. Implement response_orchestrator.py
5. Build first 10 direct functions from gap analysis (Priority 1)
6. Add template library for common patterns
7. Integrate with existing UI planner workflow

---

**Last Updated**: 2026-03-05