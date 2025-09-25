def debug_pandas():
    """Debug pandas availability and data structure"""
    try:
        result = {
            "pandas_available": "PANDAS_AVAILABLE" in globals() and PANDAS_AVAILABLE,
            "pd_type": str(type(pd)),
            "np_type": str(type(np)),
            "context_data_keys": list(context_data.keys()),
            "position_symbols": position_symbols,
            "bars_data_keys": list(bars_data.keys()),
            "spy_bars_length": len(bars_data.get('SPY', [])) if 'SPY' in bars_data else 0
        }
        return result
    except Exception as e:
        return {"error": str(e), "exception_type": str(type(e))}