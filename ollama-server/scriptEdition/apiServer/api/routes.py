"""
FastAPI Routes for Financial Analysis Server
"""

import json
import logging
from datetime import datetime
from fastapi import HTTPException
from typing import Dict, Any

from api.models import QuestionRequest, AnalysisResponse
from services.llm import UnifiedLLMService

logger = logging.getLogger("api-routes")


class APIRoutes:
    """Handles all API route logic"""
    
    def __init__(self, llm_service: UnifiedLLMService):
        self.llm_service = llm_service
    
    async def analyze_question(self, request: QuestionRequest) -> AnalysisResponse:
        """
        Analyze a financial question and generate tool calls without execution
        """
        try:
            logger.info(f"📝 Received question: {request.question[:100]}...")
            
            # Use the specified model or default
            model = request.model or self.llm_service.default_model
            logger.info(f"🤖 Using model: {model}")
            
            # Analyze the question
            result = await self.llm_service.analyze_question(request.question, model, request.enable_caching)
            
            if result["success"]:
                return AnalysisResponse(
                    success=True,
                    data=result["data"],
                    timestamp=datetime.now().isoformat()
                )
            else:
                return AnalysisResponse(
                    success=False,
                    error=result["error"],
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            logger.error(f"❌ Analysis endpoint error: {e}")
            return AnalysisResponse(
                success=False,
                error=f"Internal server error: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "provider": self.llm_service.provider_type,
            "model": self.llm_service.default_model,
            "mcp_initialized": self.llm_service.mcp_initialized,
            "caching_supported": self.llm_service.provider.supports_caching(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def debug_mcp_tools(self) -> Dict[str, Any]:
        """Debug endpoint to check MCP tools"""
        try:
            await self.llm_service.ensure_mcp_initialized()
            
            if not self.llm_service.mcp_client:
                return {
                    "error": "MCP client not initialized",
                    "tools_count": 0,
                    "tools": []
                }
            
            tools = self.llm_service.get_mcp_tools()
            
            return {
                "mcp_initialized": self.llm_service.mcp_initialized,
                "tools_count": len(tools),
                "tools": [
                    {
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"][:100] + "..." if len(tool["function"]["description"]) > 100 else tool["function"]["description"]
                    }
                    for tool in tools[:10]  # Limit to first 10 for readability
                ],
                "total_available": len(tools)
            }
            
        except Exception as e:
            logger.error(f"❌ MCP debug error: {e}")
            return {
                "error": str(e),
                "tools_count": 0
            }
    
    async def debug_system_prompt(self) -> Dict[str, Any]:
        """Debug endpoint to check system prompt"""
        try:
            system_prompt = await self.llm_service.get_system_prompt()
            
            return {
                "system_prompt_length": len(system_prompt),
                "system_prompt_preview": system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt,
                "system_prompt_path": self.llm_service.system_prompt_path
            }
            
        except Exception as e:
            logger.error(f"❌ System prompt debug error: {e}")
            return {
                "error": str(e)
            }
    
    async def test_tool_result_processing(self) -> Dict[str, Any]:
        """Test endpoint to verify tool result processing pipeline"""
        try:
            # Simulate tool calls that would be processed
            mock_tool_calls = [
                {
                    "function": {
                        "name": "mcp__mcp-validation-server__get_validation_capabilities",
                        "arguments": {}
                    }
                }
            ]
            
            # Process through the validation pipeline
            validation = self.llm_service.mcp_integration.validate_mcp_functions(mock_tool_calls)
            
            if validation["all_valid"]:
                # Test actual tool execution
                tool_results = await self.llm_service.mcp_integration.generate_tool_calls_only(mock_tool_calls)
                
                return {
                    "validation_passed": True,
                    "tool_execution": tool_results["success"],
                    "tool_results_count": len(tool_results.get("tool_results", [])),
                    "sample_result": tool_results.get("tool_results", [{}])[0] if tool_results.get("tool_results") else None,
                    "error_traceback_included": "error_traceback" in str(tool_results) if tool_results.get("tool_results") else False
                }
            else:
                return {
                    "validation_passed": False,
                    "validation_results": validation
                }
                
        except Exception as e:
            logger.error(f"❌ Tool result processing test error: {e}")
            return {
                "error": str(e),
                "validation_passed": False
            }
    
    async def list_models(self) -> Dict[str, Any]:
        """List available models for the current provider"""
        try:
            if self.llm_service.provider_type == "anthropic":
                models = [
                    "claude-3-5-haiku-20241022",
                    "claude-3-5-sonnet-20241022", 
                    "claude-sonnet-4-5-20250929"
                ]
                return {
                    "provider": "anthropic",
                    "current_model": self.llm_service.default_model,
                    "available_models": models
                }
            elif self.llm_service.provider_type == "openai":
                models = [
                    "gpt-4-turbo-preview",
                    "gpt-4-turbo",
                    "gpt-4o",
                    "gpt-4o-mini"
                ]
                return {
                    "provider": "openai",
                    "current_model": self.llm_service.default_model,
                    "available_models": models
                }
            else:
                # For other providers like Ollama
                return {
                    "provider": self.llm_service.provider_type,
                    "current_model": self.llm_service.default_model,
                    "available_models": [self.llm_service.default_model],
                    "note": f"Model list not implemented for {self.llm_service.provider_type}"
                }
        except Exception as e:
            return {"error": str(e)}