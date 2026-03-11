#!/usr/bin/env python3
"""
Step 5 — Analysis Agent (direct code generation via Claude)

Uses Anthropic SDK directly with a focused agent to generate, validate,
and execute Python code using MCP functions. This bypasses the full
analysis pipeline infrastructure to measure baseline performance.

Usage:
    python step5_analysis_agent.py "What is QQQ's current price?"
    python step5_analysis_agent.py "..." --show-code       # print generated code
    python step5_analysis_agent.py "..." --timeout 180     # max seconds (default 300)

What to check:
    - success: true
    - elapsed_s - compare with step5_analysis.py
    - code_preview - shows the generated Python code
"""

import asyncio
import json
import sys
import os
import argparse
import time
from datetime import datetime
from pathlib import Path


# ── Path setup ────────────────────────────────────────────────────────────────
_DIR     = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.normpath(os.path.join(_DIR, "..", ".."))
_OUTPUT  = os.path.join(_DIR, "output")
sys.path.insert(0, _BACKEND)

from dotenv import load_dotenv
load_dotenv(os.path.join(_BACKEND, "apiServer", ".env"))

# ── Imports (after path/env setup) ───────────────────────────────────────────
import logging
logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

logger = logging.getLogger("step5_agent")
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[step5_agent] %(message)s"))
logger.addHandler(_handler)
logger.propagate = False


# ── Helpers ───────────────────────────────────────────────────────────────────
def save_output(result: dict) -> str:
    os.makedirs(_OUTPUT, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(_OUTPUT, f"step5_agent_{ts}.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return path


# ── Agent Prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a financial data analyst who writes Python code to answer financial questions using MCP functions.

## Available MCP Functions

You have access to financial MCP tools through these servers:

### mcp-financial-server
- `get_real_time_data(symbols)`: Get current market data (quotes, trades, daily bars)
- `get_historical_data(symbols, start_date, end_date, timeframe)`: Get historical price data
- `get_latest_quotes(symbols)`: Get best bid/ask prices
- `get_latest_trades(symbols)`: Get recent trades
- `get_fundamentals(symbol)`: Get company fundamentals (P/E, market cap, etc)
- `get_dividends(symbol, start_date, end_date)`: Get dividend history
- `get_splits(symbol, start_date, end_date)`: Get stock split history
- `get_positions()`: Get current portfolio positions
- `get_portfolio_history(period, timeframe)`: Get portfolio value history
- `get_market_clock()`: Check if market is open
- `search_symbols(query)`: Search for stocks/ETFs
- And more...

### mcp-analytics-server
- `calculate_returns(prices, method)`: Calculate returns (simple or log)
- `calculate_cumulative_returns(returns)`: Calculate cumulative returns
- `calculate_annualized_return(prices, periods)`: Calculate annualized return
- `calculate_annualized_volatility(returns, periods_per_year)`: Calculate volatility
- `calculate_sharpe_ratio(returns, risk_free_rate)`: Calculate Sharpe ratio
- `calculate_beta(stock_returns, market_returns)`: Calculate beta
- `calculate_correlation(series1, series2)`: Calculate correlation
- `calculate_drawdown_analysis(returns)`: Analyze drawdowns
- `calculate_rolling_volatility(returns, window)`: Calculate rolling volatility
- `calculate_rsi(data, period)`: Calculate RSI
- `calculate_macd(data, fast_period, slow_period, signal_period)`: Calculate MACD
- `calculate_bollinger_bands(data, period, std_dev)`: Calculate Bollinger Bands
- `calculate_sma(data, period)`: Calculate Simple Moving Average
- `calculate_ema(data, period)`: Calculate Exponential Moving Average
- And many more...

## Important Notes

1. **Use `financial_lib.` prefix** for financial functions (e.g., `financial_lib.get_real_time_data(...)`)
2. **Use `analytics_lib.` prefix** for analytics functions (e.g., `analytics_lib.calculate_returns(...)`)

3. **Add a `main()` block** that calls `analyze_question()` and prints the result.

4. **Handle errors gracefully** with try/except blocks.

5. **Return structured data** - not just printed output.

## Important Notes

1. **DO NOT import MCP functions** - they are available as built-in functions in the execution environment.
2. Use `financial_lib.` prefix for financial functions and `analytics_lib.` prefix for analytics functions.
3. Define an `analyze_question()` function that takes no arguments and returns the result as a dictionary or JSON-serializable object.
4. Add a `main()` block that calls `analyze_question()` and prints the result.
5. Handle errors gracefully with try/except blocks.
6. Return structured data - not just printed output.

## Example Code Structure

```python
import json
from datetime import datetime, timedelta

def analyze_question():
    # Get data
    data = financial_lib.get_real_time_data(symbols={"QQQ": "QQQ"})
    prices = data.get("QQQ", {}).get("close", [])

    # Calculate metrics
    returns = analytics_lib.calculate_returns(prices=prices, method="simple")
    volatility = analytics_lib.calculate_annualized_volatility(returns=returns, periods_per_year=252)

    return {
        "symbol": "QQQ",
        "current_price": prices[-1] if prices else None,
        "volatility": volatility,
        "num_data_points": len(prices)
    }

if __name__ == "__main__":
    result = analyze_question()
    print(json.dumps(result, indent=2))
```

## Output Format

Return ONLY the Python code, no markdown fences, no backticks, no explanations.
"""

USER_PROMPT_TEMPLATE = """Write Python code to answer this question:

{question}

The code should:
1. Use available MCP functions from mcp-financial-server (use `financial_lib.` prefix) and mcp-analytics-server (use `analytics_lib.` prefix)
2. Define an `analyze_question()` function that returns the result
3. Include a main block that prints the result as JSON
4. Handle errors gracefully
5. Return structured data (dict with keys/values)

Example:
- financial_lib.get_real_time_data(symbols={{"QQQ": "QQQ"}})
- financial_lib.get_historical_data(symbols="QQQ", start_date="2024-01-01", end_date="2024-12-31")
- analytics_lib.calculate_returns(prices=prices, method="simple")
- analytics_lib.calculate_volatility(returns=returns, periods_per_year=252)

Return ONLY the Python code, no markdown fences, no backticks, no explanations."""


# ── Validation and Execution ─────────────────────────────────────────────────
async def validate_and_execute_code(code: str, timeout: int = 60) -> dict:
    """
    Validate and execute the generated Python code using shared execution module.
    """
    logger.info("Validating and executing code...")

    try:
        from shared.execution import execute_script

        execution_result = execute_script(
            script_content=code,
            mock_mode=False,  # Use real MCP calls
            timeout=timeout
        )

        return execution_result

    except Exception as e:
        logger.warning(f"Execution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


# ── Main ──────────────────────────────────────────────────────────────────────
async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Step 5 — Direct agent for analysis code generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("question", nargs="?", help="Question to analyze")
    parser.add_argument("--show-code", action="store_true",
                        help="Include the generated code in output")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Max seconds for generation + execution (default 300)")
    parser.add_argument("--model", default=None,
                        help="Claude model to use (default: from MODEL env var)")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty-print JSON output")
    args = parser.parse_args()

    if not args.question:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Get API key
    api_key = os.getenv("ANTHROPIC_AUTH_TOKEN") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Set model
    model = args.model or os.getenv("MODEL", "glm-4.7:cloud")

    # Build user message
    user_message = USER_PROMPT_TEMPLATE.format(question=args.question)

    logger.info("Generating code for: %s", args.question[:100])

    # Create Anthropic client
    from anthropic import Anthropic
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    if base_url and "ollama.com" in base_url:
        import httpx
        client = Anthropic(
            api_key=api_key,
            base_url=base_url,
            http_client=httpx.Client(
                headers={"Authorization": f"Bearer {api_key}"},
                verify=False
            )
        )
    elif base_url:
        client = Anthropic(api_key=api_key, base_url=base_url)
    else:
        client = Anthropic(api_key=api_key)

    # Phase 1: Generate code
    generation_start = time.time()
    try:
        response = client.messages.create(
            model=model,
            max_tokens=8192,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}]
        )

        # Extract code from response
        generated_code = ""
        for block in response.content:
            if hasattr(block, 'type'):
                if block.type == 'text' and hasattr(block, 'text') and block.text:
                    generated_code += block.text

        # Clean up - remove markdown fences if present
        generated_code = generated_code.strip()
        if generated_code.startswith("```python"):
            generated_code = generated_code[9:]
        if generated_code.startswith("```"):
            generated_code = generated_code[3:]
        if generated_code.endswith("```"):
            generated_code = generated_code[:-3]
        generated_code = generated_code.strip()

    except Exception as e:
        print(f"ERROR: Code generation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    generation_elapsed = time.time() - generation_start

    if not generated_code:
        print("ERROR: No code generated", file=sys.stderr)
        sys.exit(1)

    logger.info("Code generated in %.1fs (%d chars)", generation_elapsed, len(generated_code))

    # Phase 2: Validate and execute
    execution_start = time.time()
    try:
        execution_result = await validate_and_execute_code(generated_code, timeout=args.timeout - int(generation_elapsed))
    except Exception as e:
        print(f"ERROR: Code execution failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    execution_elapsed = time.time() - execution_start
    total_elapsed = generation_elapsed + execution_elapsed

    # Build result
    result: dict = {
        "success": execution_result.get("success", False),
        "question": args.question,
        "elapsed_s": round(total_elapsed, 1),
        "generation_elapsed_s": round(generation_elapsed, 1),
        "execution_elapsed_s": round(execution_elapsed, 1),
        "code_length": len(generated_code),
        "code_preview": (generated_code[:500] + "...") if len(generated_code) > 500 else generated_code,
    }

    if args.show_code:
        result["code_full"] = generated_code

    if execution_result.get("success"):
        if "result" in execution_result:
            result["answer"] = execution_result["result"]
        if "output" in execution_result:
            result["output"] = execution_result["output"]
        logger.info("SUCCESS - generated in %.1fs, executed in %.1fs", generation_elapsed, execution_elapsed)
    else:
        result["error"] = execution_result.get("error", "Unknown error")
        if "error_traceback" in execution_result:
            result["error_traceback"] = execution_result["error_traceback"]
        logger.error("FAILED - %s", result["error"])

    out_path = save_output(result)
    logger.info("Saved → %s", out_path)

    if args.pretty:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(json.dumps(result, default=str))

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    asyncio.run(main())