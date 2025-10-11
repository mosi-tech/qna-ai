"""
FastAPI Routes for Financial Analysis Server
"""

import json
import logging
from datetime import datetime
from fastapi import HTTPException
from typing import Dict, Any

from api.models import QuestionRequest, AnalysisResponse
from services.analysis_simplified import AnalysisService
from services.search import SearchService
from dialogue import search_with_context, initialize_dialogue_factory, get_session_manager

logger = logging.getLogger("api-routes")


class APIRoutes:
    """Handles all API route logic"""
    
    def __init__(self, analysis_service: AnalysisService, search_service: SearchService):
        self.analysis_service = analysis_service
        self.search_service = search_service
        
        # Initialize dialogue factory using search service's library
        try:
            analysis_library = search_service._get_library_client()
        except Exception:
            analysis_library = None
        
        initialize_dialogue_factory(analysis_library=analysis_library)
    
    async def analyze_question(self, request: QuestionRequest) -> AnalysisResponse:
        """
        Analyze a financial question with conversation context support
        """
        try:
            logger.info(f"📝 Received question: {request.question[:100]}...")
            
            # Step 1: Use conversation-aware search to handle contextual queries
            context_result = await search_with_context(
                query=request.question,
                session_id=request.session_id,
                auto_expand=request.auto_expand
            )
            
            if not context_result["success"]:
                return AnalysisResponse(
                    success=False,
                    error=f"Context analysis failed: {context_result.get('error')}",
                    timestamp=datetime.now().isoformat()
                )
            
            # Get the final query to analyze (expanded if contextual)
            final_query = context_result.get("expanded_query", request.question)
            session_id = context_result["session_id"]
            
            logger.info(f"🔍 Query type: {context_result.get('query_type', 'unknown')}")
            if final_query != request.question:
                logger.info(f"🔄 Expanded to: {final_query[:100]}...")
            
            # Step 2: Check if we need confirmation for low-confidence expansions
            if context_result.get("needs_confirmation") or context_result.get("needs_clarification"):
                return AnalysisResponse(
                    success=True,
                    data={
                        "needs_user_input": True,
                        "session_id": session_id,
                        "context_result": context_result,
                        "message": context_result.get("message"),
                        "options": context_result.get("options"),
                        "suggestion": context_result.get("suggestion")
                    },
                    timestamp=datetime.now().isoformat()
                )
            
            # Step 3: Enhance message with similar analyses for full analysis
            enhanced_message, similar_analyses = self.search_service.search_and_enhance_message(final_query)
            
            if similar_analyses:
                logger.info(f"🔍 Enhanced message with {len(similar_analyses)} similar analyses")
            
            # Use the specified model or default
            model = request.model or self.analysis_service.llm_service.default_model
            logger.info(f"🤖 Using model: {model}")
            
            # Step 4: Analyze with enhanced message
            result = await self.analysis_service.analyze_question(enhanced_message, model, request.enable_caching)
            
            if result["success"]:
                # Step 5: Save completed analysis and update conversation
                try:
                    analysis_data = result["data"]
                    response_type = analysis_data.get("response_type")
                    analysis_result = analysis_data.get("analysis_result", {})
                    
                    # Extract consistent fields from both reuse and script generation responses
                    script_name = analysis_result.get("script_name")
                    execution_info = analysis_result.get("execution", {})
                    analysis_description = analysis_result.get("analysis_description", "")
                    
                    analysis_summary = None
                    if script_name and (
                        (response_type == "reuse_decision" and analysis_result.get("should_reuse")) or
                        (response_type == "script_generation" and analysis_result.get("status") == "success")
                    ):
                        # Save the analysis with execution metadata
                        save_result = self.search_service.save_completed_analysis(
                            original_question=request.question,  # Use original question, not enhanced
                            script_path=script_name, 
                            addn_meta={"execution": execution_info, "description": analysis_description}
                        )
                        
                        if save_result.get("success"):
                            # Add save info to response data
                            analysis_data["analysis_id"] = save_result["analysis_id"]
                            
                            # Set analysis summary based on response type
                            analysis_summary = save_result.get("analysis_description", "")
                        else:
                            logger.warning(f"Failed to save analysis: {save_result.get('error')}")
                    else:
                        # Handle cases where script couldn't be saved (no script_name or failed conditions)
                        if response_type == "script_generation" and analysis_result.get("status") == "failed":
                            analysis_summary = f"Script generation failed: {analysis_result.get('final_error', 'Unknown error')}"
                    
                    # Step 6: Update conversation with analysis results
                    try:
                        session_manager = get_session_manager()
                        conversation = session_manager.get_session(session_id)
                        if conversation:
                            # Update the last turn with analysis results
                            last_turn = conversation.get_last_turn()
                            if last_turn and not last_turn.analysis_summary:
                                last_turn.analysis_summary = analysis_summary or "Financial analysis completed"
                                logger.info(f"📝 Updated conversation turn with analysis summary")
                    except Exception as conv_error:
                        logger.warning(f"Failed to update conversation: {conv_error}")
                
                except Exception as save_error:
                    logger.error(f"❌ Error saving analysis: {save_error}")
                    # Don't fail the main request, just log the error
                
                # Step 7: Build enhanced response with conversation context
                response_data = result["data"]
                
                # Add conversation context info
                response_data["conversation"] = {
                    "session_id": session_id,
                    "query_type": context_result.get("query_type"),
                    "original_query": request.question,
                    "final_query": final_query,
                    "context_used": context_result.get("context_used", False),
                    "expansion_confidence": context_result.get("expansion_confidence", 0.0)
                }
                
                # Add similar analyses info
                if similar_analyses:
                    response_data["similar_analyses_found"] = len(similar_analyses)
                    response_data["similar_analyses"] = [
                        {
                            "function_name": a["function_name"],
                            "filename": a.get("filename", f"{a['function_name']}.py"),
                            "similarity": a["similarity"],
                            "question": a["question"][:100] + "..." if len(a["question"]) > 100 else a["question"]
                        }
                        for a in similar_analyses
                    ]
                
                # Add context search results if available
                if context_result.get("search_results"):
                    response_data["context_search_results"] = len(context_result["search_results"])
                
                return AnalysisResponse(
                    success=True,
                    data=response_data,
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
        # Get analysis library stats
        library_stats = self.search_service.get_library_stats()
        
        return {
            "status": "healthy",
            "provider": self.analysis_service.llm_service.provider_type,
            "model": self.analysis_service.llm_service.default_model,
            "mcp_initialized": self.analysis_service.mcp_initialized,
            "caching_supported": self.analysis_service.llm_service.provider.supports_caching(),
            "analysis_library": library_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_analysis_library_stats(self) -> Dict[str, Any]:
        """Get analysis library statistics"""
        try:
            stats = self.search_service.get_library_stats()
            return {
                "success": True,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error getting analysis library stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def debug_mcp_tools(self) -> Dict[str, Any]:
        """Debug endpoint to check MCP tools"""
        try:
            await self.analysis_service.ensure_mcp_initialized()
            
            if not self.analysis_service.mcp_client:
                return {
                    "error": "MCP client not initialized",
                    "tools_count": 0,
                    "tools": []
                }
            
            tools = self.analysis_service.get_mcp_tools()
            
            return {
                "mcp_initialized": self.analysis_service.mcp_initialized,
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
            system_prompt = await self.analysis_service.get_system_prompt()
            
            return {
                "system_prompt_length": len(system_prompt),
                "system_prompt_preview": system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt,
                "system_prompt_path": self.analysis_service.system_prompt_path
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
            validation = self.analysis_service.mcp_integration.validate_mcp_functions(mock_tool_calls)
            
            if validation["all_valid"]:
                # Test actual tool execution
                tool_results = await self.analysis_service.mcp_integration.generate_tool_calls_only(mock_tool_calls)
                
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
            if self.analysis_service.llm_service.provider_type == "anthropic":
                models = [
                    "claude-3-5-haiku-20241022",
                    "claude-3-5-sonnet-20241022", 
                    "claude-sonnet-4-5-20250929"
                ]
                return {
                    "provider": "anthropic",
                    "current_model": self.analysis_service.llm_service.default_model,
                    "available_models": models
                }
            elif self.analysis_service.llm_service.provider_type == "openai":
                models = [
                    "gpt-4-turbo-preview",
                    "gpt-4-turbo",
                    "gpt-4o",
                    "gpt-4o-mini"
                ]
                return {
                    "provider": "openai",
                    "current_model": self.analysis_service.llm_service.default_model,
                    "available_models": models
                }
            else:
                # For other providers like Ollama
                return {
                    "provider": self.analysis_service.llm_service.provider_type,
                    "current_model": self.analysis_service.llm_service.default_model,
                    "available_models": [self.analysis_service.llm_service.default_model],
                    "note": f"Model list not implemented for {self.analysis_service.llm_service.provider_type}"
                }
        except Exception as e:
            return {"error": str(e)}
    
    async def confirm_expansion(self, session_id: str, confirmed: bool) -> Dict[str, Any]:
        """Handle user confirmation for query expansion"""
        try:
            from dialogue import get_dialogue_factory
            
            factory = get_dialogue_factory()
            result = factory.get_context_aware_search().confirm_expansion(session_id, confirmed)
            
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Confirmation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context for debugging"""
        try:
            from dialogue import get_dialogue_factory
            
            factory = get_dialogue_factory()
            context = factory.get_context_aware_search().get_session_context(session_id)
            
            return {
                "success": True,
                "session_id": session_id,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Session context error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def list_sessions(self) -> Dict[str, Any]:
        """List active conversation sessions"""
        try:
            session_manager = get_session_manager()
            stats = session_manager.get_stats()
            
            return {
                "success": True,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Session listing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }