def inspect_raw_data():
    """Inspect the raw data structure from MCP calls"""
    
    result = {
        "context_data_structure": {},
        "positions_inspection": {},
        "bars_inspection": {}
    }
    
    # Inspect context_data structure
    for key in context_data.keys():
        value = context_data[key]
        result["context_data_structure"][key] = {
            "type": str(type(value)),
            "length": len(value) if hasattr(value, '__len__') else "no length",
            "sample": str(value)[:200] if value else "empty"
        }
    
    # Inspect positions data
    if "positions_data" in context_data:
        pos_data = context_data["positions_data"]
        result["positions_inspection"] = {
            "type": str(type(pos_data)),
            "content": str(pos_data)[:300] if pos_data else "empty"
        }
    
    # Inspect bars data  
    if "bars_data" in context_data:
        bars = context_data["bars_data"]
        result["bars_inspection"] = {
            "type": str(type(bars)),
            "keys": list(bars.keys()) if hasattr(bars, 'keys') else "no keys",
            "content_sample": str(bars)[:300] if bars else "empty"
        }
    
    return result