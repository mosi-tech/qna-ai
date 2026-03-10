#!/usr/bin/env python3
"""
step5a_direct_function.py — Direct MCP Function Call (Fast Path)

Purpose: Execute direct MCP function calls based on LLM classification.
         This is the fastest response path (100-500ms).

Usage:
    python step5a_direct_function.py --function get_top_gainers --params '{"limit": 10}'
    python step5a_direct_function.py --mcp-call '{"mcp_server": "mcp-financial-server", "mcp_function": "get_top_gainers", "params": {"limit": 10}}'

This step bypasses:
    - LLM script generation
    - Analysis queue
    - Script execution overhead

Output: JSON with function result and metadata
"""

import asyncio
import sys
import os
import argparse
import json
from datetime import datetime
from typing import Dict, Any

# Add backend to path
_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_DIR, "..", ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(_DIR), "..", "..", "apiServer", ".env"))


class DirectFunctionExecutor:
    """Executor for direct MCP function calls"""

    def __init__(self):
        # Available MCP functions (for reference/validation)
        self.financial_functions = [
            "get_real_time_data", "get_latest_quotes", "get_latest_trades",
            "get_top_gainers", "get_top_losers", "get_most_active_stocks",
            "get_fundamentals", "get_dividends", "get_splits",
            "get_account", "get_positions", "get_portfolio_history",
            "get_historical_data", "search_symbols", "get_market_clock",
        ]
        self.analytics_functions = [
            "calculate_var", "calculate_cvar", "calculate_sma", "calculate_ema",
            "calculate_rsi", "calculate_macd", "calculate_bollinger_bands",
            "calculate_atr", "calculate_correlation", "calculate_correlation_matrix",
            "calculate_sharpe_ratio", "calculate_volatility", "calculate_returns",
        ]

    def execute(self, mcp_server: str, mcp_function: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP function directly"""
        try:
            if mcp_server == "mcp-financial-server":
                result = self._call_financial_mcp(mcp_function, params)
            elif mcp_server == "mcp-analytics-server":
                result = self._call_analytics_mcp(mcp_function, params)
            else:
                return {
                    "success": False,
                    "error": f"Unknown MCP server: {mcp_server}"
                }

            return {
                "success": True,
                "mcp_server": mcp_server,
                "mcp_function": mcp_function,
                "params": params,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": str(e),
                "error_detail": traceback.format_exc(),
                "mcp_server": mcp_server,
                "mcp_function": mcp_function,
                "params": params
            }

    def _call_financial_mcp(self, function_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call Financial MCP server functions"""
        from mcp__mcp_financial_server import (
            get_real_time_data,
            get_latest_quotes,
            get_latest_trades,
            get_top_gainers,
            get_top_losers,
            get_most_active_stocks,
            get_fundamentals,
            get_dividends,
            get_splits,
            get_account,
            get_positions,
            get_portfolio_history,
            get_historical_data,
            search_symbols,
            get_market_clock,
        )

        data_source = params.get("data_source", "alpaca")

        # Route to specific function
        if function_name == "get_real_time_data":
            symbols_list = params.get("symbols", [])
            symbols_dict = {symbol: {} for symbol in symbols_list}
            return get_real_time_data(symbols=symbols_dict, data_source=data_source)

        elif function_name == "get_latest_quotes":
            symbols_list = params.get("symbols", [])
            symbols_dict = {symbol: {} for symbol in symbols_list}
            return get_latest_quotes(symbols=symbols_dict, data_source=data_source)

        elif function_name == "get_latest_trades":
            symbols_list = params.get("symbols", [])
            symbols_dict = {symbol: {} for symbol in symbols_list}
            return get_latest_trades(symbols=symbols_dict, data_source=data_source)

        elif function_name == "get_top_gainers":
            limit = params.get("limit", 10)
            return get_top_gainers(limit=limit, data_source=data_source)

        elif function_name == "get_top_losers":
            limit = params.get("limit", 10)
            return get_top_losers(limit=limit, data_source=data_source)

        elif function_name == "get_most_active_stocks":
            limit = params.get("limit", 10)
            return get_most_active_stocks(limit=limit, data_source=data_source)

        elif function_name == "get_fundamentals":
            symbol = params.get("symbol")
            return get_fundamentals(symbol=symbol, data_source=data_source)

        elif function_name == "get_dividends":
            symbol = params.get("symbol")
            return get_dividends(symbol=symbol, data_source=data_source)

        elif function_name == "get_splits":
            symbol = params.get("symbol")
            return get_splits(symbol=symbol, data_source=data_source)

        elif function_name == "get_account":
            return get_account(data_source=data_source)

        elif function_name == "get_positions":
            return get_positions(data_source=data_source)

        elif function_name == "get_portfolio_history":
            period = params.get("period", "1M")
            timeframe = params.get("timeframe", "1D")
            end_date = params.get("end_date")
            extended_hours = params.get("extended_hours", False)
            return get_portfolio_history(
                period=period,
                timeframe=timeframe,
                end_date=end_date,
                extended_hours=extended_hours,
                data_source=data_source
            )

        elif function_name == "get_historical_data":
            symbols_list = params.get("symbols", [])
            symbols_dict = {symbol: {} for symbol in symbols_list}
            timeframe = params.get("timeframe", "1D")
            start_date = params.get("start_date")
            end_date = params.get("end_date")
            data_source_param = params.get("data_source", "alpaca")
            return get_historical_data(
                symbols=symbols_dict,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                data_source=data_source_param
            )

        elif function_name == "search_symbols":
            query = params.get("query")
            data_source_param = params.get("data_source", "alpaca")
            return search_symbols(query=query, data_source=data_source_param)

        elif function_name == "get_market_clock":
            return get_market_clock(data_source=data_source)

        else:
            raise ValueError(f"Unknown financial MCP function: {function_name}")

    def _call_analytics_mcp(self, function_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call Analytics MCP server functions"""
        from mcp__mcp_analytics_server import (
            calculate_var,
            calculate_cvar,
            calculate_sma,
            calculate_ema,
            calculate_rsi,
            calculate_macd,
            calculate_bollinger_bands,
            calculate_atr,
            calculate_correlation,
            calculate_correlation_matrix,
            calculate_sharpe_ratio,
            calculate_volatility,
            calculate_returns,
        )

        # Route to specific function
        if function_name == "calculate_var":
            returns = params.get("returns")
            confidence_level = params.get("confidence_level", 0.95)
            method = params.get("method", "historical")
            return calculate_var(returns=returns, confidence_level=confidence_level, method=method)

        elif function_name == "calculate_cvar":
            returns = params.get("returns")
            confidence_level = params.get("confidence_level", 0.95)
            return calculate_cvar(returns=returns, confidence_level=confidence_level)

        elif function_name == "calculate_sma":
            data = params.get("data")
            period = params.get("period", 20)
            return calculate_sma(data=data, period=period)

        elif function_name == "calculate_ema":
            data = params.get("data")
            period = params.get("period", 20)
            return calculate_ema(data=data, period=period)

        elif function_name == "calculate_rsi":
            data = params.get("data")
            period = params.get("period", 14)
            return calculate_rsi(data=data, period=period)

        elif function_name == "calculate_macd":
            data = params.get("data")
            fast_period = params.get("fast_period", 12)
            slow_period = params.get("slow_period", 26)
            signal_period = params.get("signal_period", 9)
            return calculate_macd(
                data=data,
                fast_period=fast_period,
                slow_period=slow_period,
                signal_period=signal_period
            )

        elif function_name == "calculate_bollinger_bands":
            data = params.get("data")
            period = params.get("period", 20)
            std_dev = params.get("std_dev", 2)
            return calculate_bollinger_bands(data=data, period=period, std_dev=std_dev)

        elif function_name == "calculate_atr":
            data = params.get("data")
            period = params.get("period", 14)
            return calculate_atr(data=data, period=period)

        elif function_name == "calculate_correlation":
            series1 = params.get("series1")
            series2 = params.get("series2")
            return calculate_correlation(series1=series1, series2=series2)

        elif function_name == "calculate_correlation_matrix":
            series_array = params.get("series_array")
            method = params.get("method", "pearson")
            return calculate_correlation_matrix(series_array=series_array, method=method)

        elif function_name == "calculate_sharpe_ratio":
            returns = params.get("returns")
            risk_free_rate = params.get("risk_free_rate", 0.0)
            return calculate_sharpe_ratio(returns=returns, risk_free_rate=risk_free_rate)

        elif function_name == "calculate_volatility":
            returns = params.get("returns")
            periods_per_year = params.get("periods_per_year", 252)
            return calculate_volatility(returns=returns, periods_per_year=periods_per_year)

        elif function_name == "calculate_returns":
            returns = params.get("returns")
            method = params.get("method", "simple")
            return calculate_returns(returns=returns, method=method)

        else:
            raise ValueError(f"Unknown analytics MCP function: {function_name}")

    def list_available_functions(self) -> Dict[str, list]:
        """List all available MCP functions"""
        return {
            "mcp-financial-server": self.financial_functions,
            "mcp-analytics-server": self.analytics_functions
        }


def save_output(result: Dict[str, Any], output_dir: str = None):
    """Save result to output directory"""
    if output_dir is None:
        output_dir = os.path.join(_DIR, "output")

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"step5a_{timestamp}.json")

    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Output saved to: {output_file}", file=sys.stderr)
    return output_file


async def main():
    parser = argparse.ArgumentParser(
        description="Execute direct MCP function calls (fast path)"
    )
    parser.add_argument("--mcp-call", help="MCP call as JSON: {mcp_server, mcp_function, params}")
    parser.add_argument("--list-functions", action="store_true", help="List available MCP functions")
    parser.add_argument("--output-dir", help="Output directory (default: ./output)")
    parser.add_argument("--pretty", action="store_true", help="Pretty print output")

    args = parser.parse_args()

    executor = DirectFunctionExecutor()
    result = None

    if args.list_functions:
        result = {
            "success": True,
            "available_functions": executor.list_available_functions()
        }

    elif args.mcp_call:
        mcp_call = json.loads(args.mcp_call)
        result = executor.execute(
            mcp_server=mcp_call.get("mcp_server"),
            mcp_function=mcp_call.get("mcp_function"),
            params=mcp_call.get("params", {})
        )

    else:
        parser.print_help()
        sys.exit(1)

    _ = save_output(result, args.output_dir)

    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))

    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    asyncio.run(main())