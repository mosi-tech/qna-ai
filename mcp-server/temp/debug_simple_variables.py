def debug_simple_variables():
    """Debug what simple variables are available in context"""
    
    result = {
        "all_context_keys": list(context_data.keys()),
        "positions_data": {
            "available": "positions_data" in context_data,
            "type": str(type(context_data.get("positions_data"))),
            "value": context_data.get("positions_data"),
            "is_none": context_data.get("positions_data") is None
        },
        "bars_data": {
            "available": "bars_data" in context_data, 
            "type": str(type(context_data.get("bars_data"))),
            "value": str(context_data.get("bars_data"))[:200] if context_data.get("bars_data") else None,
            "is_none": context_data.get("bars_data") is None
        },
        "position_symbols": {
            "available": "position_symbols" in context_data,
            "type": str(type(context_data.get("position_symbols"))),
            "value": context_data.get("position_symbols"),
            "is_none": context_data.get("position_symbols") is None
        }
    }
    
    return result