# UI Performance Optimization Plan — Integrated with Headless Steps

> Reference: `backend/headless/steps/PLAN.md`
> Goal: Reduce 5-10s response time to <2s for 70%+ of questions

---

## Current Flow (Bottleneck Analysis)

```
step1_plan.py → UIPlanner (decomposes question → blocks with sub_questions)
step2_persist.py → Persist plan to DB
step3_cache.py → Check cache for canonical_params
step4_enqueue.py → Enqueue sub_questions (ALL go here)
step5_analysis.py → Run analysis pipeline (script generation + execution)  ← BOTTLENECK (5-10s)
step6_execution.py → Execute script
step7_reconcile.py → Reconcile results
```

**Problem**: Every sub_question goes through `step5_analysis.py` (script generation), even for simple questions.

---

## Simplified Optimized Flow

```
step1_plan.py → UIPlanner (decomposes question → blocks with sub_questions)
step2_persist.py → Persist plan to DB
step3_cache.py → ENHANCED: LLM classification + cache + route
                      │
                      ├─→ cache HIT → return result
                      │
                      ├─→ Single MCP function → step5a_direct_function.py (FAST: 100-500ms)
                      │
                      └─→ Multi-step/complex → step4_enqueue.py → step5_analysis.py (SLOW: 5-10s)
```

**Key Insight**: Simple questions use direct MCP calls; complex questions use existing script generation pipeline.

---

## Proposed Changes

### 1. New: `step3_cache_enhanced.py`

Replaces/enhances `step3_cache.py` to add classification and routing.

**Purpose:**
- Classify each sub_question into: `direct_function`, `template`, or `script_generation`
- Check appropriate cache based on classification
- Route to fast path or queue accordingly

**Usage:**
```bash
python step3_cache_enhanced.py --dashboard-id <uuid>
# Output: JSON with routing decisions for each block
```

**Output Structure:**
```json
{
  "dashboard_id": "uuid",
  "routing_decisions": [
    {
      "block_id": "block-1",
      "sub_question": "What is QQQ's current price?",
      "classification": "direct_function",
      "function_name": "get_real_time_data",
      "cache_hit": false,
      "route_to": "step5a_direct_function",
      "params": {"symbols": ["QQQ"], "data_source": "alpaca"}
    },
    {
      "block_id": "block-2",
      "sub_question": "Top 10 gainers today",
      "classification": "direct_function",
      "function_name": "get_top_gainers",
      "cache_hit": false,
      "route_to": "step5a_direct_function",
      "params": {"limit": 10, "data_source": "alpaca"}
    },
    {
      "block_id": "block-3",
      "sub_question": "Compare AAPL vs MSFT performance",
      "classification": "template",
      "template_name": "comparison_template",
      "cache_hit": false,
      "route_to": "step5b_template",
      "params": {"symbols": ["AAPL", "MSFT"], "period": "30d"}
    },
    {
      "block_id": "block-4",
      "sub_question": "Analyze earnings impact on my portfolio",
      "classification": "script_generation",
      "cache_hit": false,
      "route_to": "step4_enqueue",
      "params": {}
    }
  ]
}
```

---

### 2. New: `step5a_direct_function.py`

**Purpose:** Execute direct MCP function calls (fastest path).

**Usage:**
```bash
python step5a_direct_function.py --function get_top_gainers --params '{"limit": 10}'
# Or from routing decisions:
python step5a_direct_function.py --routing-file output/step3_routing.json
```

**Behaviour:**
- Bootstraps: MCP servers (financial, analytics)
- Calls function directly (no script generation)
- Executes and returns result
- Caches result to BlockCache
- Saves output to `output/step5a_<timestamp>.json`

**Functions to Implement (from function_gap_analysis.json):**

| Function Name | MCP Call | Input | Output |
|---------------|----------|-------|--------|
| `get_real_time_data` | `get_real_time_data` | symbols, timeframe | OHLCV data |
| `get_top_gainers` | `get_top_gainers` | limit | [{symbol, change, ...}] |
| `get_top_losers` | `get_top_losers` | limit | [{symbol, change, ...}] |
| `get_most_active_stocks` | `get_most_active_stocks` | limit | [{symbol, volume, ...}] |
| `calculate_var` | `calculate_var` | returns, confidence | var_value |
| `calculate_sharpe` | `calculate_risk_metrics` | returns, risk_free | sharpe_ratio |
| `get_fundamentals` | `get_fundamentals` | symbol | {pe, pb, ...} |
| `get_dividends` | `get_dividends` | symbol | [{amount, date, ...}] |

---

### 3. New: `step5b_template.py`

**Purpose:** Render and execute pre-built script templates (medium path).

**Usage:**
```bash
python step5b_template.py --template comparison --params '{"symbols": ["AAPL", "MSFT"]}'
# Or from routing decisions:
python step5b_template.py --routing-file output/step3_routing.json
```

**Templates to Implement:**

| Template Name | Use Case | Params |
|---------------|----------|--------|
| `comparison_template` | Compare N assets | symbols, period, metrics |
| `performance_template` | Performance metrics | symbols, period |
| `risk_template` | Risk analysis | symbols, confidence |
| `backtest_template` | Backtest strategy | strategy, symbols, params |
| `correlation_template` | Correlation matrix | symbols, period |

**Behaviour:**
- Load template file
- Fill in parameters
- Execute (no LLM script generation)
- Return result
- Cache result

---

### 4. New: `registry/function_registry.py`

**Purpose:** Registry of direct functions with question pattern matching.

```python
# backend/headless/registry/function_registry.py

class FunctionRegistry:
    """Registry of pre-built functions for common question patterns"""

    def __init__(self):
        self.functions = {
            # Direct MCP mappings
            "get_real_time_data": {
                "mcp_server": "mcp-financial-server",
                "mcp_function": "get_real_time_data",
                "question_patterns": [
                    r"current price of (.+)",
                    r"what is (.+) trading at",
                    r"(.+) quote"
                ]
            },
            "get_top_gainers": {
                "mcp_server": "mcp-financial-server",
                "mcp_function": "get_top_gainers",
                "question_patterns": [
                    r"top (\d+)\s+gainers",
                    r"biggest gainers",
                    r"best performers"
                ]
            },
            "get_top_losers": {
                "mcp_server": "mcp-financial-server",
                "mcp_function": "get_top_losers",
                "question_patterns": [
                    r"top (\d+)\s+losers",
                    r"worst performers",
                    r"biggest drop"
                ]
            },
            "calculate_var": {
                "mcp_server": "mcp-analytics-server",
                "mcp_function": "calculate_var",
                "question_patterns": [
                    r"VaR at (\d+)%",
                    r"value at risk.*(\d+)%",
                    r"calculate var"
                ]
            },
            "get_fundamentals": {
                "mcp_server": "mcp-financial-server",
                "mcp_function": "get_fundamentals",
                "question_patterns": [
                    r"(?:P\/E|PE) ratio",
                    r"fundamentals of (.+)",
                    r"(?:valuation|metrics) for (.+)"
                ]
            }
        }

    def classify(self, question: str) -> Optional[Dict]:
        """Classify question and return function mapping if match"""
        import re

        for func_name, func_info in self.functions.items():
            for pattern in func_info["question_patterns"]:
                match = re.search(pattern, question, re.IGNORECASE)
                if match:
                    return {
                        "function_name": func_name,
                        "mcp_server": func_info["mcp_server"],
                        "mcp_function": func_info["mcp_function"],
                        "params": self._extract_params(question, match, pattern)
                    }
        return None

    def _extract_params(self, question: str, match, pattern) -> Dict:
        """Extract parameters from question based on pattern match"""
        params = {}
        # Extract captured groups
        groups = match.groups()
        if groups:
            if "symbols" in pattern.lower():
                params["symbols"] = groups[0].upper().split(",")
            elif "limit" in pattern.lower():
                params["limit"] = int(groups[0])
            elif "confidence" in pattern.lower():
                params["confidence_level"] = float(groups[0]) / 100
        return params
```

---

### 5. New: `templates/template_library.py`

**Purpose:** Library of pre-built script templates.

```python
# backend/headless/templates/template_library.py

class TemplateLibrary:
    """Library of pre-built script templates for common question patterns"""

    def __init__(self):
        self.templates = {
            "comparison_template": """
# Compare performance of multiple symbols

symbols = {symbols}
start_date = "{start_date}"
end_date = "{end_date}"

# Fetch historical data
data = get_historical_data(symbols, timeframe="1D", start_date=start_date, end_date=end_date)

# Calculate returns
returns = calculate_log_returns(data)

# Calculate metrics
result = {{
    "symbols": symbols,
    "returns": calculate_annualized_return(returns),
    "volatility": calculate_annualized_volatility(returns),
    "sharpe": calculate_sharpe_ratio(returns),
    "max_drawdown": calculate_max_drawdown(returns),
    "total_return": calculate_total_return(returns)
}}

return result
""",
            "performance_template": """
# Get performance metrics for a symbol

symbol = "{symbol}"
period = "{period}"

# Fetch data
data = get_historical_data([symbol], timeframe="1D", period=period)

# Calculate metrics
returns = calculate_log_returns(data)
result = {{
    "symbol": symbol,
    "period": period,
    "current_price": data["close"].iloc[-1],
    "total_return": calculate_total_return(returns),
    "annualized_return": calculate_annualized_return(returns),
    "volatility": calculate_annualized_volatility(returns),
    "sharpe_ratio": calculate_sharpe_ratio(returns),
    "max_drawdown": calculate_max_drawdown(returns).min()
}}

return result
"""
        }

    def get_template(self, name: str) -> Optional[str]:
        return self.templates.get(name)

    def classify(self, question: str) -> Optional[Dict]:
        """Classify question and return template mapping if match"""
        import re

        # Comparison pattern
        if re.search(r"compare|vs|versus", question, re.IGNORECASE):
            symbols = self._extract_symbols(question)
            return {
                "template_name": "comparison_template",
                "params": {"symbols": symbols, "period": "30d"}
            }

        # Performance pattern
        if re.search(r"performance|metrics|how.*doing", question, re.IGNORECASE):
            symbol = self._extract_single_symbol(question)
            return {
                "template_name": "performance_template",
                "params": {"symbol": symbol, "period": "30d"}
            }

        return None

    def _extract_symbols(self, question: str) -> List[str]:
        """Extract stock symbols from question"""
        # Simple extraction - in production, use a more sophisticated parser
        import re
        matches = re.findall(r"\b[A-Z]{2,5}\b", question)
        return matches

    def _extract_single_symbol(self, question: str) -> str:
        symbols = self._extract_symbols(question)
        return symbols[0] if symbols else "QQQ"
```

---

### 6. Updated: `run_all_steps.py`

```python
# Enhanced run_all_steps.py with routing

async def run_all_optimized(question: str, timeout: int = 300):
    """Run all steps with optimized routing"""

    # Step 1: Plan
    plan = run_step1(question)

    # Step 2: Persist
    dashboard_id = run_step2(plan)

    # Step 3: Enhanced Cache + Classification + Routing
    routing = run_step3_enhanced(dashboard_id)

    # Process each block based on routing
    results = []
    for decision in routing["routing_decisions"]:
        if decision["cache_hit"]:
            results.append(decision["cached_result"])
        elif decision["route_to"] == "step5a_direct_function":
            result = run_step5a_direct_function(decision)
            results.append(result)
        elif decision["route_to"] == "step5b_template":
            result = run_step5b_template(decision)
            results.append(result)
        elif decision["route_to"] == "step4_enqueue":
            # Slow path - enqueue and wait
            job_ids = run_step4_enqueue([decision])
            run_step5_analysis(job_ids)
            run_step6_execution(job_ids)
            results.append(get_results(job_ids))

    # Step 7: Reconcile
    run_step7(dashboard_id)

    return {"dashboard_id": dashboard_id, "results": results}
```

---

## Directory Structure (Simplified)

```
backend/headless/
  steps/
    step3_cache_enhanced.py    ← LLM classification + cache + route
    step5a_direct_function.py  ← Direct MCP calls (fast path)
    step5_analysis.py          ← Script generation (slow path, multi-step)
    step4_enqueue.py          ← Queue for slow path
    step6_execution.py          ← Script execution
  .claude/agents/
    question-classifier.md    ← LLM-based question classifier
    function-discovery.md      ← Gap analysis agent
    function-builder.md        ← Function implementation agent
    question-harvester.md      ← Question consolidation agent
```

---

## Implementation Priority

| Phase | Change | Effort | Impact | Timeline |
|-------|--------|--------|--------|----------|
| **1** | `function_registry.py` | Low | High | 2-3 days |
| **2** | `step5a_direct_function.py` | Low | High | 2-3 days |
| **3** | `step3_cache_enhanced.py` | Medium | High | 3-5 days |
| **4** | `template_library.py` | Low | Medium | 2-3 days |
| **5** | `step5b_template.py` | Low | Medium | 2-3 days |
| **6** | Update `run_all_steps.py` | Low | High | 1-2 days |

**Total**: ~2 weeks

---

## Success Metrics

| Metric | Current | Target | When |
|--------|---------|--------|------|
| Direct Function Path | 0% | 50-60% | After Phase 1-2 |
| Template Path | 0% | 20-30% | After Phase 4-5 |
| Script Generation | 100% | <20% | After Phase 3-6 |
| Avg Response Time | 5-10s | <2s | After Phase 3-6 |
| P95 Response Time | 15-20s | <5s | After Phase 3-6 |

---

## Related Files

- `all-questions/function_gap_analysis.json` - Missing functions to implement
- `.claude/agents/function-discovery.md` - Function discovery agent
- `.claude/agents/function-builder.md` - Function implementation agent
- `.claude/agents/question-classifier.md` - Question classification agent (to be created)
- `backend/headless/steps/PLAN.md` - Existing headless steps plan
- `backend/headless/hydrate/` - Cache hydration pipeline

---

## Next Steps

1. Create `question-classifier` agent (for classification logic)
2. Implement `function_registry.py` with pattern matching
3. Implement `step5a_direct_function.py` with top 10 functions
4. Implement `step3_cache_enhanced.py` with routing logic
5. Test with sample questions and measure speedup

---

**Last Updated**: 2026-03-05