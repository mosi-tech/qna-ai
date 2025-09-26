def debug_context_data():
    """
    Debug function to inspect what's available in context_data
    """
    import json
    
    # Get data from context_data (set by execution engine)
    step_data = context_data
    
    debug_info = {
        "context_keys": list(step_data.keys()),
        "context_types": {k: str(type(v)) for k, v in step_data.items()},
        "context_sample": {}
    }
    
    # Sample some data for debugging
    for key, value in step_data.items():
        if isinstance(value, dict):
            debug_info["context_sample"][key] = {
                "type": str(type(value)),
                "keys": list(value.keys()) if isinstance(value, dict) else "not_dict",
                "sample": str(value)[:500] if len(str(value)) > 500 else str(value)
            }
        else:
            debug_info["context_sample"][key] = {
                "type": str(type(value)),
                "value": str(value)[:200] if len(str(value)) > 200 else str(value)
            }
    
    return debug_info