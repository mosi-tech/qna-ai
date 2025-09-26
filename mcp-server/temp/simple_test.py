def simple_test():
    """Simple test without external dependencies"""
    try:
        # Basic test that should always work
        result = {
            "status": "success",
            "message": "Script execution working",
            "python_version": "available",
            "globals_available": len([k for k in globals().keys() if not k.startswith('__')])
        }
        return result
    except Exception as e:
        return {"error": str(e), "status": "failed"}