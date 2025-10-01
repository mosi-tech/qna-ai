#!/usr/bin/env python3
"""
Portfolio Correlation Analysis
Generated with fast-track MCP validation - Parameterized Version

This script calculates the pairwise correlation matrix of portfolio asset returns.
It accepts historical price data for the portfolio assets, converts the prices to returns
(using the MCP `prices_to_returns` function), and then computes the correlation matrix
(using `calculate_correlation_matrix`).

The script is fully parameterized: you can provide a CSV file path containing the
historical prices (one column per asset, dates as the index) or supply the data
directly via the `historical_prices` argument.

Author: MCP Script Generator
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ------------------------------------------------------------
# Helper for MCP function calls with fail‑fast error handling
# ------------------------------------------------------------

def safe_mcp_call(function_name: str, params: Dict[str, Any]) -> Any:
    """Wraps call_mcp_function with validation and clear error messages.

    Args:
        function_name: Name of the MCP function to call.
        params: Dictionary of parameters to pass.

    Returns:
        Result from the MCP function.

    Raises:
        Exception: If the MCP function returns None or an empty dict, or if the
        call itself raises an exception.
    """
    try:
        result = call_mcp_function(function_name, params)
    except Exception as e:
        raise Exception(f"MCP call '{function_name}' failed with error: {e}")
    if result is None:
        raise Exception(f"MCP call '{function_name}' returned None – function may not be implemented")
    if isinstance(result, dict) and not result:
        raise Exception(f"MCP call '{function_name}' returned empty dict – check parameters: {params}")
    return result

# ------------------------------------------------------------
# Core analysis function
# ------------------------------------------------------------

def analyze_portfolio_correlations(
    historical_prices: pd.DataFrame,
    mock: bool = False,
) -> Dict[str, Any]:
    """Calculate portfolio correlation matrix.

    Args:
        historical_prices: DataFrame with dates as index and one column per asset.
        mock: If True, the function will skip real MCP calls and use mock
            data for validation purposes.

    Returns:
        Dictionary containing the correlation matrix and metadata.
    """
    logging.info("Starting correlation analysis")

    # Validate input DataFrame
    if historical_prices.empty:
        raise ValueError("Input historical_prices DataFrame is empty")
    if not isinstance(historical_prices.index, pd.DatetimeIndex):
        try:
            historical_prices.index = pd.to_datetime(historical_prices.index)
        except Exception as e:
            raise ValueError(f"Failed to parse index as datetime: {e}")

    # Convert prices to returns using MCP function
    return_series_list = []
    for symbol in historical_prices.columns:
        prices_series = historical_prices[symbol].dropna()
        if prices_series.empty:
            raise ValueError(f"Price series for {symbol} is empty after dropping NaN")
        if mock:
            # For mock mode, create simple returns using pct_change
            returns_series = prices_series.pct_change().dropna()
        else:
            returns_series = safe_mcp_call(
                "prices_to_returns",
                {"prices": prices_series, "method": "simple"},
            )
        return_series_list.append(returns_series)

    # Ensure all series are aligned to common dates
    aligned_returns = pd.concat(return_series_list, axis=1, join="inner")
    aligned_returns.columns = historical_prices.columns

    # Calculate correlation matrix via MCP
    if mock:
        corr_matrix = aligned_returns.corr(method="pearson")
    else:
        corr_matrix = safe_mcp_call(
            "calculate_correlation_matrix",
            {"series_array": aligned_returns.to_dict(orient="list")},
        )
        # MCP returns a DataFrame; convert to pandas if needed
        if not isinstance(corr_matrix, pd.DataFrame):
            corr_matrix = pd.DataFrame(corr_matrix)

    # Prepare output as list of lists for JSON serialization
    output = {
        "correlation_matrix": corr_matrix.values.tolist(),
        "symbols": list(corr_matrix.columns),
        "analysis_completed": True,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "MCP Financial + Analytics Servers",
            "mock_mode": mock,
        },
    }
    return output

# ------------------------------------------------------------
# Main entry point for HTTP execution
# ------------------------------------------------------------

def main(mock: bool = False, **kwargs) -> Dict[str, Any]:
    """Main function for parameterized execution.

    Extracts all user‑supplied parameters from **kwargs and forwards them to
    :func:`analyze_portfolio_correlations`.
    """
    # Extract parameters
    historical_prices_file: Optional[str] = kwargs.get("historical_prices_file")
    historical_prices_json: Optional[str] = kwargs.get("historical_prices_json")
    historical_prices: Optional[pd.DataFrame] = None

    if historical_prices_file:
        if not os.path.exists(historical_prices_file):
            raise FileNotFoundError(f"Historical prices file not found: {historical_prices_file}")
        historical_prices = pd.read_csv(historical_prices_file, index_col=0, parse_dates=True)
    elif historical_prices_json:
        # Expect a JSON string representing a dict of lists indexed by date
        try:
            data = json.loads(historical_prices_json)
            historical_prices = pd.DataFrame(data)
        except Exception as e:
            raise ValueError(f"Failed to parse historical_prices_json: {e}")
    else:
        raise ValueError("Either 'historical_prices_file' or 'historical_prices_json' must be provided")

    # Delegate to core analysis
    return analyze_portfolio_correlations(
        historical_prices=historical_prices,
        mock=mock,
        **kwargs,  # Pass through any extra arguments
    )

# ------------------------------------------------------------
# CLI support for local testing
# ------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Portfolio Correlation Analysis")
    parser.add_argument("--historical_prices_file", type=str, help="Path to CSV file containing historical prices")
    parser.add_argument("--historical_prices_json", type=str, help="JSON string of historical prices data")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no MCP calls) for validation")

    args = parser.parse_args()
    try:
        results = main(
            historical_prices_file=args.historical_prices_file,
            historical_prices_json=args.historical_prices_json,
            mock=args.mock,
        )
        print(json.dumps(results, indent=2, default=str))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)
"