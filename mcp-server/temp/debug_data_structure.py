def debug_data_structure():
    """Debug what data structure we're receiving"""
    import json
    
    result = {
        "context_data_keys": list(context_data.keys()) if 'context_data' in globals() else "context_data not found",
        "position_symbols_type": str(type(position_symbols)) if 'position_symbols' in globals() else "position_symbols not found",
        "position_symbols_value": position_symbols if 'position_symbols' in globals() else None,
        "bars_data_type": str(type(bars_data)) if 'bars_data' in globals() else "bars_data not found",
        "bars_data_keys": list(bars_data.keys()) if 'bars_data' in globals() and hasattr(bars_data, 'keys') else "bars_data no keys",
        "sample_data": str(context_data)[:500] if 'context_data' in globals() else "no context_data"
    }
    
    return result