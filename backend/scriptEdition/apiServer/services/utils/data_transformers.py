"""
Data Transformation Utilities
Shared logic for transforming raw database data into UI-safe formats
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("data-transformers")


class DataTransformer:
    """Data transformation utility class that encapsulates database operations"""
    
    def __init__(self, db_client=None):
        self.db_client = db_client
    
    async def transform_analysis_data_to_ui(
        self, 
        metadata: Dict[str, Any], 
        analysis_id: Optional[str] = None, 
        execution_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transform analysis data to UI-safe format
        
        Args:
            metadata: Raw metadata from message or analysis
            analysis_id: Optional analysis ID to fetch additional data
            execution_id: Optional execution ID to fetch results
        
        Returns:
            UI-safe data structure for frontend consumption
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
        
        # Fetch execution results if execution_id exists
        if execution_id and self.db_client:
            try:
                execution = await self.db_client.get_execution(execution_id)
                if execution:
                    # Update execution status
                    ui_data["execution"]["status"] = execution.status.value if hasattr(execution.status, 'value') else str(execution.status)
                    ui_data["execution"]["error"] = execution.error
                    
                    # Get execution results directly from results field
                    if execution.result:
                        ui_data["results"] = extract_key_findings_from_execution(execution.result)
                    
                    # Get parameters from execution
                    ui_data["parameters"] = execution.parameters or {}
            except Exception as e:
                logger.warning(f"Failed to fetch execution {execution_id}: {e}")
        
        # Fetch analysis parameters if analysis_id exists
        if analysis_id and self.db_client:
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
        
        return ui_data
    
    async def transform_message_to_ui_data(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """Transform message to complete UI-safe data - includes all essential fields"""
        metadata = msg.get("metadata", {})
        response_type = metadata.get("response_type", "")
        execution_id = msg.get("executionId")
        
        # Base message structure with essential fields
        clean_msg = {
            "id": msg.get("messageId"),
            "role": msg.get("role"),
            "timestamp": msg.get("timestamp"),
            "analysisId": msg.get("analysisId"),
            "executionId": execution_id,
        }
        
        if response_type == "analysis":
            # For analysis: content + uiData with results (consistent with AnalysisResponse)
            ui_data = {
                "results": {},  # Will be populated from execution if available
            }
            
            # Fetch execution results if available
            if execution_id and self.db_client:
                try:
                    execution = await self.db_client.get_execution(execution_id)
                    if execution and execution.result:
                        # Extract only the nested results field (execution.result.results)
                        execution_results = execution.result.get("results", {})
                        if execution_results:
                            ui_data["results"] = execution_results
                except Exception as e:
                    logger.warning(f"Failed to fetch execution results for {execution_id}: {e}")
            
            clean_msg.update({
                "content": msg.get("content", ""),
                "uiData": ui_data,  # Nested under uiData for consistency
            })
            
        elif response_type == "clarification":
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
                "type": response_type or msg.get("role", "assistant"),
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