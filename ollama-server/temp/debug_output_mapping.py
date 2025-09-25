def debug_output_mapping():
    """Debug what the output mapping extracted"""
    
    result = {
        "all_context_keys": list(context_data.keys()),
        "positions_data": {
            "type": str(type(context_data.get("positions_data"))),
            "value": context_data.get("positions_data"),
            "length": len(context_data.get("positions_data", [])) if context_data.get("positions_data") else 0
        },
        "position_symbols": {
            "type": str(type(context_data.get("position_symbols"))),
            "value": context_data.get("position_symbols"),
            "length": len(context_data.get("position_symbols", [])) if context_data.get("position_symbols") else 0
        },
        "bars_data": {
            "type": str(type(context_data.get("bars_data"))),
            "value": str(context_data.get("bars_data"))[:200] if context_data.get("bars_data") else None,
            "is_none": context_data.get("bars_data") is None
        }
    }
    
    return result