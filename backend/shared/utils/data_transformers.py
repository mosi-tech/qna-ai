"""
Data Transformation Utilities
Shared logic for transforming raw database data into UI-safe formats
"""

import logging
from typing import Dict, Any, Optional
from shared.constants import MessageStatus
from shared.db.schemas import ExecutionStatus

logger = logging.getLogger("data-transformers")


class DataTransformer:
    """Data transformation utility class that encapsulates database operations"""
    
    def __init__(self, db_client=None):
        self.db_client = db_client
    
    async def transform_analysis_data_to_ui(
        self, 
        metadata: Dict[str, Any], 
        analysis_id: Optional[str] = None, 
        execution_id: Optional[str] = None,
        execution_data: Optional[Dict[str, Any]] = None,
        analysis_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Transform analysis data to UI-safe format
        
        Args:
            metadata: Raw metadata from message or analysis
            analysis_id: Optional analysis ID to fetch additional data
            execution_id: Optional execution ID to fetch results
            execution_data: Optional execution data from aggregation
            analysis_data: Optional analysis data from aggregation
        
        Returns:
            UI-safe data structure for frontend consumption with combined status information
        """
        
        # Default response structure
        ui_data = {
            "results": {},
            "execution": {
                "status": "pending",
                "progress": None,
                "logs": [],
                "error": None,
            },
            "canRerun": True,
            "canExport": True,
        }
        
        # Step 1: Extract execution status and data
        execution_status = "unknown"
        execution_error = None
        
        if execution_data:
            # Use pre-populated data from aggregation
            execution_status = execution_data.get("status", "unknown")
            execution_error = execution_data.get("error")
            
            # Get execution results - aggregation already extracts execution.result into "results"
            if execution_data.get("results"):
                # aggregation pipeline puts execution.result into execution_data["results"]
                ui_config = execution_data["results"].get("ui_config")
                if ui_config:
                    ui_data["results"]["ui_config"] = ui_config
            
            # Get parameters from execution  
            ui_data["results"]["parameters"] = execution_data.get("parameters", {})
        
        # Step 2: Extract metadata status information using MessageStatus constants
        metadata_status = metadata.get("status")  # Using MessageStatus constants
        metadata_error = metadata.get("error")
        
        # Step 3: Determine overall status and error state for UI
        # Priority: execution status > metadata status (execution success overrides stale metadata)
        # This ensures successful executions are shown as completed even if metadata is stale
        
        overall_status = "completed"  # Default
        overall_error = None
        
        if MessageStatus.is_execution_success_state(execution_status):
            # Execution succeeded - this is the highest priority (overrides any stale metadata)
            overall_status = "completed"
        elif MessageStatus.is_execution_failed_state(execution_status):
            # Execution failed - second highest priority
            overall_status = "failed"
            overall_error = execution_error or "Execution failed"
        elif MessageStatus.is_execution_pending_state(execution_status):
            # Execution is in progress - third priority
            overall_status = execution_status
        elif MessageStatus.is_failed_state(metadata_status):
            # Analysis pipeline failed (only if no execution status available)
            overall_status = "failed"
            overall_error = metadata_error or "Analysis failed to complete"
        elif MessageStatus.is_pending_state(metadata_status):
            # Analysis is still in progress (only if no execution status available)
            overall_status = "pending"
        else:
            # Unknown status - default to completed unless there's a metadata error
            overall_status = "completed" if not metadata_error else "failed"
            if metadata_error:
                overall_error = metadata_error
        
        # Step 4: Update UI data with combined status
        ui_data["execution"]["status"] = overall_status
        ui_data["execution"]["error"] = overall_error
        
        # Add top-level status for easier UI access
        ui_data["status"] = overall_status
        ui_data["error"] = overall_error
        
        # Step 5: Handle analysis data for parameters and type
        if analysis_data and analysis_data.get("llm_response"):
            # Use pre-populated data from aggregation
            llm_params = analysis_data["llm_response"].get("parameters", {})
            if llm_params:
                ui_data["parameters"].update(llm_params)
            
            # Update analysis type if available
            response_type = analysis_data["llm_response"].get("response_type") or analysis_data["llm_response"].get("query_type")
            if response_type:
                ui_data["type"] = response_type
        elif analysis_id and self.db_client:
            # Fallback to individual DB call if no pre-populated data
            try:
                analysis = await self.db_client.get_analysis(analysis_id)
                if analysis and analysis.llm_response:
                    # Extract parameters from LLM response
                    llm_params = analysis.llm_response.get("parameters", {})
                    if llm_params:
                        ui_data["parameters"].update(llm_params)
                    
                    # Update analysis type if available
                    response_type = analysis.llm_response.get("response_type") or analysis.llm_response.get("query_type")
                    if response_type:
                        ui_data["type"] = response_type
            except Exception as e:
                logger.warning(f"Failed to fetch analysis {analysis_id}: {e}")
        
        # Step 6: Adjust UI controls based on status
        if overall_status in ["pending", "queued", "running"]:
            ui_data["canRerun"] = False
            ui_data["canExport"] = False
        elif overall_status == "failed":
            ui_data["canRerun"] = True
            ui_data["canExport"] = False
        
        
        return ui_data
    
    async def transform_message_to_ui_data(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """Transform message to complete UI-safe data - includes all essential fields"""
        metadata = msg.get("metadata", {})
        response_type = metadata.get("response_type", "")
        execution_id = msg.get("executionId")
        
        # Normalize analysis types for UI - analysis results should all be "script_generation"  
        if response_type in ["reuse_decision", "cache_hit", "analysis", "script_generation"]:
            response_type = "script_generation"
        
        # Base message structure with essential fields
        clean_msg = {
            "id": msg.get("messageId"),
            "sessionId": msg.get("sessionId"),
            "role": msg.get("role"),
            "timestamp": msg.get("timestamp"),
            "analysisId": msg.get("analysisId"),
            "executionId": execution_id,
            "response_type": response_type, 
        }
        
        execution_data = msg.get("execution")  
        # Handle cases where   response_type in empty and execution was successful
        if response_type == "script_generation" or (execution_data and execution_data.get("status", "unknonw") == "success"):
            # For analysis: Use the improved transform_analysis_data_to_ui for complete status handling
            
            analysis_data = msg.get("analysis") 
            
            # Get complete UI data with combined status from both metadata and execution
            ui_data = await self.transform_analysis_data_to_ui(
                metadata=metadata,
                analysis_id=msg.get("analysisId"),
                execution_id=execution_id,
                execution_data=execution_data,
                analysis_data=analysis_data
            )
            
            clean_msg.update({
                "content": msg.get("content", ""),
                **ui_data,  # Flatten UI data properties directly into clean_msg
            })
            
            # Add logs for pending/running messages so frontend can display progress history
            if ui_data.get("status") in ["pending", "running", "queued"]:
                logs = msg.get("logs", [])
                if logs:
                    # Clean logs - keep only essential fields for frontend
                    clean_logs = []
                    for log in logs:
                        clean_log = {
                            "message": log.get("message"),
                            "timestamp": log.get("timestamp"),
                            "level": log.get("level", "info")
                        }
                        clean_logs.append(clean_log)
                    clean_msg["logs"] = clean_logs
            
        elif response_type == "clarification":
            # For clarification: different structure with original/expanded queries
            clean_msg.update({
                "response_type": "clarification",
                "content": msg.get("content", ""),
                "originalQuery": metadata.get("original_query", ""),
                "expandedQuery": metadata.get("expanded_query", ""),
                "suggestions": metadata.get("suggestions", []),
                "confidence": metadata.get("confidence"),
            })
        
        else:
            # For regular messages (user or assistant): just content
            clean_msg.update({
                "content": msg.get("content", ""),
                "response_type": response_type,
            })
        
        return clean_msg



def extract_key_findings_from_execution(execution_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract the key findings from execution result
    Returns execution_result.results field which contains the actual analysis results
    
    Args:
        execution_result: Full execution result from database
        
    Returns:
        Just the results portion that contains actual analysis data
    """
    if not execution_result:
        return {}
    
    # Extract the nested results field which contains the actual analysis results
    return execution_result.get("results", {})


def transform_clarification_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Transform clarification metadata to UI-safe format"""
    return {
        "type": "clarification",
        "originalQuery": metadata.get("original_query", ""),
        "expandedQuery": metadata.get("expanded_query", ""),
        "suggestions": metadata.get("suggestions", []),
        "confidence": metadata.get("confidence"),
        "canExport": False,
        "canRerun": False,
    }


def generate_analysis_summary(response_type: str, key_findings: list) -> str:
    """Generate user-friendly summary text"""
    if not key_findings:
        return f"{response_type} completed successfully."
    
    if "weekday" in response_type.lower() or "performance" in response_type.lower():
        best_day_finding = next((f for f in key_findings if "day" in f["label"].lower()), None)
        return_finding = next((f for f in key_findings if "return" in f["label"].lower()), None)
        
        if best_day_finding and return_finding:
            return f"Analysis shows {best_day_finding['value']} performs best with {return_finding['value']} average return."
    
    return f"{response_type} completed with {len(key_findings)} key finding{'s' if len(key_findings) != 1 else ''}."