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
            "type": metadata.get("analysis_type") or metadata.get("query_type", "Financial Analysis"),
            "results": {},
            "execution": {
                "status": "completed",
                "progress": None,
                "logs": [],
                "error": None,
            },
            "parameters": {},
            "confidence": metadata.get("confidence"),
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
                # Now we need to extract the "results" field from that
                result_data = execution_data["results"]
                
                if isinstance(result_data, dict) and "results" in result_data:
                    execution_results = result_data["results"]
                    ui_data["results"] = execution_results
                else:
                    # Fallback: if result_data is already the results
                    ui_data["results"] = result_data
            
            # Get parameters from execution  
            ui_data["parameters"] = execution_data.get("parameters", {})
        elif execution_id and self.db_client:
            # Fallback to individual DB call if no pre-populated data
            try:
                execution = await self.db_client.get_execution(execution_id)
                if execution:
                    # Update execution status
                    execution_status = execution.status.value if hasattr(execution.status, 'value') else str(execution.status)
                    execution_error = execution.error
                    
                    # Get execution results directly from results field
                    if execution.result:
                        ui_data["results"] = extract_key_findings_from_execution(execution.result)
                    
                    # Get parameters from execution
                    ui_data["parameters"] = execution.parameters or {}
            except Exception as e:
                logger.warning(f"Failed to fetch execution {execution_id}: {e}")
        
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
            analysis_type = analysis_data["llm_response"].get("analysis_type") or analysis_data["llm_response"].get("query_type")
            if analysis_type:
                ui_data["type"] = analysis_type
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
                    analysis_type = analysis.llm_response.get("analysis_type") or analysis.llm_response.get("query_type")
                    if analysis_type:
                        ui_data["type"] = analysis_type
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
        analysis_type = metadata.get("analysis_type", "") or metadata.get("response_type", "") #Backward compatible
        execution_id = msg.get("executionId")
        
        # Normalize analysis types for UI - analysis results should all be "script_generation"  
        if analysis_type in ["reuse_decision", "cache_hit", "analysis", "script_generation"]:
            analysis_type = "script_generation"
        
        # Base message structure with essential fields
        clean_msg = {
            "id": msg.get("messageId"),
            "role": msg.get("role"),
            "timestamp": msg.get("timestamp"),
            "analysisId": msg.get("analysisId"),
            "executionId": execution_id,
            "analysis_type": analysis_type,  # Normalized analysis type for UI
        }
        
        if analysis_type == "script_generation":
            # For analysis: Use the improved transform_analysis_data_to_ui for complete status handling
            execution_data = msg.get("execution")
            analysis_data = msg.get("analysis") 
            
            
            # Get complete UI data with combined status from both metadata and execution
            ui_data = await self.transform_analysis_data_to_ui(
                metadata=metadata,
                analysis_id=msg.get("analysisId"),
                execution_id=execution_id,
                execution_data=execution_data,
                analysis_data=analysis_data
            )
            
            # Handle markdown from execution results if available
            if execution_data and execution_data.get("results"):
                # Extract markdown from pre-populated execution data
                markdown = execution_data["results"].get("markdown")
                if markdown:
                    ui_data["markdown"] = markdown
            elif execution_id and self.db_client:
                # Fallback to individual DB call for markdown
                try:
                    execution = await self.db_client.get_execution(execution_id)
                    if execution and execution.result:
                        markdown = execution.result.get("markdown")
                        if markdown:
                            ui_data["markdown"] = markdown
                except Exception as e:
                    logger.warning(f"Failed to fetch execution markdown for {execution_id}: {e}")
            
            clean_msg.update({
                "content": msg.get("content", ""),
                "uiData": ui_data,  # Complete UI data with status information
            })
            
        elif analysis_type == "clarification":
            # For clarification: different structure with original/expanded queries
            clean_msg.update({
                "type": "clarification",
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
                "type": analysis_type or msg.get("role", "assistant"),
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


def generate_analysis_summary(analysis_type: str, key_findings: list) -> str:
    """Generate user-friendly summary text"""
    if not key_findings:
        return f"{analysis_type} completed successfully."
    
    if "weekday" in analysis_type.lower() or "performance" in analysis_type.lower():
        best_day_finding = next((f for f in key_findings if "day" in f["label"].lower()), None)
        return_finding = next((f for f in key_findings if "return" in f["label"].lower()), None)
        
        if best_day_finding and return_finding:
            return f"Analysis shows {best_day_finding['value']} performs best with {return_finding['value']} average return."
    
    return f"{analysis_type} completed with {len(key_findings)} key finding{'s' if len(key_findings) != 1 else ''}."