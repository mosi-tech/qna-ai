# MCP Integration Prompt

## CRITICAL MCP INTEGRATION RULE:
- ALWAYS use existing MCP functions from the /mcp/ directory structure
- NEVER create custom mock data or duplicate existing functionality  
- BEFORE writing any financial analysis code, FIRST explore the MCP directory with LS and Read tools
- Import financial data functions from: mcp.financial.functions_mock
- Import analytics functions from: mcp.analytics.[module].metrics  
- Import utility functions from: mcp.analytics.utils.data_utils
- If MCP function imports fail, immediately investigate the correct import paths rather than falling back to custom implementations
- All workflow scripts must demonstrate real MCP function usage with proper error handling
- Include "✅ Successfully imported MCP functions" confirmation in every script
- List actual MCP functions used in results summary as "🔧 MCP Functions Used:"

## WORKFLOW PATTERN:
1. Import MCP functions (financial server + analytics + utils)
2. Call MCP financial functions for data retrieval  
3. Use MCP utility functions for data processing
4. Call MCP analytics functions for calculations
5. Present results with MCP function attribution

## FORBIDDEN:
- Creating hardcoded price data arrays
- Implementing custom calculation functions that duplicate MCP functionality
- Using fallback mock implementations instead of investigating real MCP imports
- Writing financial analysis without confirming MCP function availability first

## Example Usage:
```python
# CORRECT: Always start by importing MCP functions
try:
    from mcp.financial.functions_mock import alpaca_market_stocks_bars
    from mcp.analytics.performance.metrics import calculate_returns_metrics
    from mcp.analytics.utils.data_utils import prices_to_returns
    print("✅ Successfully imported MCP functions")
except ImportError as e:
    print(f"❌ Failed to import MCP functions: {e}")
    return {"workflow_success": False, "error": str(e)}

# CORRECT: Use MCP financial server for data
price_data = alpaca_market_stocks_bars(symbols="ARKK,QQQ", timeframe="1Day", start="2024-01-01", end="2024-09-21")

# CORRECT: Use MCP utilities for processing
prices = [bar["c"] for bar in price_data["bars"]["ARKK"]]
returns = prices_to_returns(prices, method="simple")

# CORRECT: Use MCP analytics for calculations
metrics = calculate_returns_metrics(returns.tolist())

# CORRECT: Attribution in results
print("🔧 MCP Functions Used:")
print("   ✅ alpaca_market_stocks_bars - Retrieved price data from MCP financial server")
print("   ✅ prices_to_returns - Converted prices to returns via MCP utils")
print("   ✅ calculate_returns_metrics - Calculated metrics via MCP analytics")
```

## WRONG Examples:
```python
# WRONG: Creating custom mock data
arkk_prices = [100.0, 98.5, 99.2, 101.1, ...]

# WRONG: Custom calculation functions
def calculate_returns_from_prices(prices):
    returns = []
    for i in range(1, len(prices)):
        returns.append((prices[i] - prices[i-1]) / prices[i-1])
    return returns

# WRONG: Fallback implementations
except ImportError:
    def alpaca_market_stocks_bars(symbols, timeframe, start, end):
        return {"bars": {"ARKK": [...]}}
```

This prompt ensures that all financial analysis leverages the existing MCP infrastructure and maintains consistency across all workflow implementations.