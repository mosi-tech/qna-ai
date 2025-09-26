def debug_tool_results():
    """Debug the raw tool results to see MCP response structure"""
    
    result = {
        "tool_result_keys": [k for k in context_data.keys() if k.startswith("tool_result_")],
        "tool_result_0_structure": {},
        "tool_result_1_structure": {}
    }
    
    if "tool_result_0" in context_data:
        tr0 = context_data["tool_result_0"]
        result["tool_result_0_structure"] = {
            "type": str(type(tr0)),
            "keys": list(tr0.keys()) if isinstance(tr0, dict) else "not_dict",
            "result_key_exists": "result" in tr0 if isinstance(tr0, dict) else False,
            "full_structure": str(tr0)[:500]
        }
        
        if isinstance(tr0, dict) and "result" in tr0:
            mcp_result = tr0["result"]
            result["tool_result_0_structure"]["mcp_result"] = {
                "type": str(type(mcp_result)),
                "keys": list(mcp_result.keys()) if isinstance(mcp_result, dict) else "not_dict",
                "content_exists": "content" in mcp_result if isinstance(mcp_result, dict) else False,
                "full_mcp_result": str(mcp_result)[:300]
            }
    
    if "tool_result_1" in context_data:
        tr1 = context_data["tool_result_1"]
        result["tool_result_1_structure"] = {
            "type": str(type(tr1)),
            "keys": list(tr1.keys()) if isinstance(tr1, dict) else "not_dict",
            "result_key_exists": "result" in tr1 if isinstance(tr1, dict) else False,
            "full_structure": str(tr1)[:500]
        }
    
    return result