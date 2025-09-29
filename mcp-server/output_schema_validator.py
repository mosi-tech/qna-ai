#!/usr/bin/env python3
"""
Output Schema Validator

Validates script output structure without exposing actual data.
Returns only schema compliance status to validation server.
"""

def validate_output_schema(output_data: dict, expected_schema: str = "server_display") -> dict:
    """
    Validate output data structure for different consumption patterns
    
    Args:
        output_data: The actual script output
        expected_schema: Expected schema type
        
    Returns:
        dict: Validation result with schema compliance only
    """
    
    if expected_schema == "server_display":
        return validate_server_display_schema(output_data)
    elif expected_schema == "json_output":
        return validate_json_output_schema(output_data)
    else:
        return {"valid": False, "error": f"Unknown schema type: {expected_schema}"}

def validate_server_display_schema(output_data: dict) -> dict:
    """Validate schema for server-side display format"""
    
    required_fields = ["question", "analysis_completed"]
    missing_fields = []
    
    for field in required_fields:
        if field not in output_data:
            missing_fields.append(field)
    
    if missing_fields:
        return {
            "valid": False,
            "error": f"Missing required fields: {missing_fields}",
            "schema_type": "server_display"
        }
    
    # Check analysis completion
    if not output_data.get("analysis_completed", False):
        if "error" not in output_data:
            return {
                "valid": False,
                "error": "Analysis failed but no error field provided",
                "schema_type": "server_display"
            }
        # Failed analysis with error is valid
        return {
            "valid": True,
            "schema_type": "server_display",
            "analysis_status": "failed_with_error"
        }
    
    return {
        "valid": True,
        "schema_type": "server_display", 
        "analysis_status": "completed",
        "metadata_present": "metadata" in output_data
    }

def validate_display_field_structure(field_name: str, field_data) -> dict:
    """Validate specific display field structure"""
    
    if field_name == "outperforming_etfs":
        if not isinstance(field_data, list):
            return {"present": True, "valid": False, "error": "Should be a list"}
        
        if len(field_data) > 0:
            # Check first item structure
            first_item = field_data[0]
            required_keys = ["symbol", "total_return_pct", "outperformance_vs_spy_pct", "outperformance_vs_qqq_pct"]
            missing_keys = [key for key in required_keys if key not in first_item]
            
            if missing_keys:
                return {"present": True, "valid": False, "error": f"ETF items missing keys: {missing_keys}"}
        
        return {"present": True, "valid": True, "count": len(field_data)}
    
    elif field_name == "benchmarks":
        if not isinstance(field_data, dict):
            return {"present": True, "valid": False, "error": "Should be a dict"}
        
        required_benchmarks = ["SPY", "QQQ"]
        missing_benchmarks = [b for b in required_benchmarks if b not in field_data]
        
        if missing_benchmarks:
            return {"present": True, "valid": False, "error": f"Missing benchmarks: {missing_benchmarks}"}
        
        return {"present": True, "valid": True, "benchmark_count": len(field_data)}
    
    elif field_name == "summary":
        if not isinstance(field_data, dict):
            return {"present": True, "valid": False, "error": "Should be a dict"}
        
        expected_keys = ["total_etfs_analyzed", "outperformers_count", "outperformance_rate"]
        present_keys = [key for key in expected_keys if key in field_data]
        
        return {"present": True, "valid": True, "summary_keys_present": len(present_keys)}
    
    return {"present": True, "valid": True, "type": type(field_data).__name__}

def validate_json_output_schema(output_data: dict) -> dict:
    """Validate schema for JSON output format (experimental/approved)"""
    
    required_fields = ["description", "body"]
    missing_fields = []
    
    for field in required_fields:
        if field not in output_data:
            missing_fields.append(field)
    
    if missing_fields:
        return {
            "valid": False,
            "error": f"Missing required JSON output fields: {missing_fields}",
            "schema_type": "json_output"
        }
    
    # Validate body structure
    body = output_data["body"]
    if not isinstance(body, list):
        return {
            "valid": False,
            "error": "Body field must be a list",
            "schema_type": "json_output"
        }
    
    # Check body items
    if len(body) > 0:
        first_item = body[0]
        required_item_keys = ["key", "value", "description"]
        missing_item_keys = [key for key in required_item_keys if key not in first_item]
        
        if missing_item_keys:
            return {
                "valid": False,
                "error": f"Body items missing keys: {missing_item_keys}",
                "schema_type": "json_output"
            }
    
    return {
        "valid": True,
        "schema_type": "json_output",
        "body_item_count": len(body),
        "description_present": isinstance(output_data.get("description"), str)
    }