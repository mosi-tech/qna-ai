def debug_bars_data():
    """Debug what bars data looks like"""
    
    result = {
        "available_keys": list(context_data.keys()),
        "aapl_bars": {
            "available": "aapl_bars" in context_data,
            "type": str(type(context_data.get("aapl_bars"))),
            "is_none": context_data.get("aapl_bars") is None,
            "value_preview": str(context_data.get("aapl_bars"))[:200] if context_data.get("aapl_bars") else None
        },
        "spy_bars": {
            "available": "spy_bars" in context_data,
            "type": str(type(context_data.get("spy_bars"))),
            "is_none": context_data.get("spy_bars") is None,
            "value_preview": str(context_data.get("spy_bars"))[:200] if context_data.get("spy_bars") else None
        }
    }
    
    # Show raw tool results too
    for key in context_data.keys():
        if key.startswith("tool_result_"):
            tool_result = context_data[key]
            if isinstance(tool_result, dict) and "tool" in tool_result and "bars" in tool_result["tool"]:
                result[f"{key}_details"] = {
                    "tool": tool_result.get("tool"),
                    "success": tool_result.get("success"),
                    "has_result": "result" in tool_result,
                    "result_structure": str(tool_result.get("result", {}))[:300] if "result" in tool_result else None
                }
    
    return result