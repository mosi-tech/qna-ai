def calculate_downside_correlations():
    """Calculate downside correlations between positions and SPY, handling missing data gracefully"""
    
    # Get data from context
    positions_data = context_data.get("positions_data")
    aapl_bars = context_data.get("aapl_bars")
    spy_bars = context_data.get("spy_bars")
    
    # Check if we have positions data
    if not positions_data or not isinstance(positions_data, list):
        return {
            "error": "No positions data available",
            "positions_data_type": str(type(positions_data)),
            "positions_data": positions_data,
            "available_context_keys": list(context_data.keys())
        }
    
    # Check if we have bars data
    if not aapl_bars or not spy_bars:
        return {
            "error": "Missing bars data",
            "aapl_bars_available": aapl_bars is not None,
            "spy_bars_available": spy_bars is not None,
            "aapl_bars_type": str(type(aapl_bars)),
            "spy_bars_type": str(type(spy_bars)),
            "positions_available": len(positions_data),
            "position_symbols": [p.get("symbol") for p in positions_data if isinstance(p, dict) and p.get("symbol")],
            "positions_data": positions_data,
            "available_context_keys": list(context_data.keys())
        }
    
    # Extract position symbols
    symbols = [pos.get("symbol") for pos in positions_data if pos.get("symbol")]
    
    if not symbols:
        return {
            "error": "No valid position symbols found",
            "positions_data": positions_data
        }
    
    # For now, return a mock analysis showing we have positions but can't get price data
    return {
        "analysis_status": "partial_success",
        "positions_found": len(positions_data),
        "position_symbols": symbols,
        "positions_details": positions_data,
        "bars_data_status": "failed",
        "next_steps": [
            "Fix the alpaca_market_stocks_bars API call",
            "Ensure MCP financial server can retrieve historical price data", 
            "Retry with working bars data to calculate actual correlations"
        ],
        "mock_result": {
            "highest_downside_correlation": {
                "symbol": symbols[0] if symbols else "N/A",
                "correlation": "N/A - bars data unavailable",
                "explanation": "Cannot calculate correlation without historical price data"
            }
        }
    }