"""
FastAPI Routes for Financial Analysis Server
"""

import json
import logging
import os
import time
from datetime import datetime
from fastapi import HTTPException
from typing import Dict, Any

from api.models import QuestionRequest, AnalysisResponse
from services.analysis import AnalysisService
from services.search import SearchService
from services.code_prompt_builder import CodePromptBuilderService
from services.reuse_evaluator import ReuseEvaluatorService
from dialogue import search_with_context, initialize_dialogue_factory, get_session_manager

logger = logging.getLogger("api-routes")


class APIRoutes:
    """Handles all API route logic"""
    
    def __init__(self, analysis_service: AnalysisService, search_service: SearchService, code_prompt_builder: CodePromptBuilderService = None, reuse_evaluator: ReuseEvaluatorService = None):
        self.analysis_service = analysis_service
        self.search_service = search_service
        self.code_prompt_builder = code_prompt_builder or CodePromptBuilderService()
        self.reuse_evaluator = reuse_evaluator or ReuseEvaluatorService()
        
        # Load message template
        self.message_template = self._load_message_template()
        
        # Log workflow mode
        skip_code_prompt_builder = os.getenv("SKIP_CODE_PROMPT_BUILDER", "false").lower() == "true"
        if skip_code_prompt_builder:
            logger.info("🚀 ANALYSIS MODE: Direct analysis (skipping code prompt builder)")
        else:
            logger.info("🔧 ANALYSIS MODE: Full workflow (with code prompt builder)")
        
        # Initialize dialogue factory using search service's library
        try:
            analysis_library = search_service._get_library_client()
        except Exception:
            analysis_library = None
        
        initialize_dialogue_factory(analysis_library=analysis_library)
    
    def _load_message_template(self) -> str:
        """Load the message template from config file"""
        try:
            template_path = os.path.join(os.path.dirname(__file__), "..", "config", "message-template-analysis.txt")
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            logger.info("✅ Loaded message template successfully")
            return template
        except Exception as e:
            logger.warning(f"⚠️ Could not load message template: {e}")
            return "**QUESTION:** {user_question}\n\n**REQUIREMENTS:**\n1. Be completely parameterized - no hardcoded values\n2. Accept all inputs as parameters\n3. Use tool references instead of mock data\n4. Create comprehensive JSON output\n5. Be easily reproducible for different inputs"
    
    def _format_message_with_template(self, user_question: str) -> str:
        """Format the user question with the loaded template"""
        try:
            return self.message_template.format(user_question=user_question)
        except Exception as e:
            logger.warning(f"⚠️ Error formatting message template: {e}")
            return user_question
    
    async def analyze_question(self, request: QuestionRequest) -> AnalysisResponse:
        """
        Analyze a financial question with conversation context support
        """
        start_time = time.time()
        try:
            logger.info(f"📝 Received question: {request.question[:100]}...")
            
            # Step 1: Use conversation-aware search to handle contextual queries
            step_start = time.time()
            context_result = await search_with_context(
                query=request.question,
                session_id=request.session_id,
                auto_expand=request.auto_expand
            )
            step_duration = time.time() - step_start
            logger.info(f"⏱️ TIMING - Step 1 (Context Search): {step_duration:.3f}s")
            
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
            
            # Step 2: Get similar analyses for reuse evaluation
            step_start = time.time()
            logger.info("🔍 Searching for similar analyses...")
            enhanced_message, similar_analyses = self.search_service.search_and_enhance_message(final_query)
            step_duration = time.time() - step_start
            logger.info(f"⏱️ TIMING - Step 2 (Similar Analysis Search): {step_duration:.3f}s")
            
            # Step 2.5: Evaluate if existing analyses can be reused
            reuse_result = None
            if similar_analyses:
                step_start = time.time()
                logger.info(f"🔄 Evaluating reuse potential for {len(similar_analyses)} similar analyses...")
                reuse_result = await self.reuse_evaluator.evaluate_reuse(
                    user_query=final_query,
                    existing_analyses=similar_analyses,
                    context={"session_id": request.session_id} if request.session_id else None
                )
                step_duration = time.time() - step_start
                logger.info(f"⏱️ TIMING - Step 2.5 (Reuse Evaluation): {step_duration:.3f}s")
                
                if reuse_result["status"] == "success" and reuse_result["reuse_decision"]["should_reuse"]:
                    logger.info(f"✅ Reuse decision: {reuse_result['reuse_decision']['reason']}")
                    # Return reuse result immediately - skip code generation
                    return AnalysisResponse(
                        success=True,
                        data={
                            "response_type": "reuse_decision",
                            "analysis_result": reuse_result["reuse_decision"],
                            "message": f"Reusing existing analysis: {reuse_result['reuse_decision']['script_name']}"
                        },
                        timestamp=datetime.now().isoformat()
                    )
                else:
                    logger.info("➡️ No suitable analysis for reuse, proceeding with new analysis generation")
            
            # Check if we should skip code prompt builder (direct analysis mode)
            skip_code_prompt_builder = os.getenv("SKIP_CODE_PROMPT_BUILDER", "false").lower() == "true"
            # skip_code_prompt_builder = False

            if skip_code_prompt_builder:
                logger.info("🚀 Skipping code prompt builder - using direct analysis mode")
                # Use the specified model or default
                model = request.model or self.analysis_service.llm_service.default_model
                logger.info(f"🤖 Using model: {model}")
                
                # Format the query with message template
                formatted_query = self._format_message_with_template(final_query)
                
                # Step 3: Direct analysis with formatted message (system prompt auto-loaded)
                step_start = time.time()
                result = await self.analysis_service.analyze_question(formatted_query, None, model, request.enable_caching)
                step_duration = time.time() - step_start
                logger.info(f"⏱️ TIMING - Step 3 (Direct Analysis): {step_duration:.3f}s")
            else:
                # Format the query with message template
                formatted_query = self._format_message_with_template(final_query)
                
                # Step 3: Create code prompt messages with function schemas
                step_start = time.time()
                logger.info("🔧 Creating code prompt messages...")
                code_prompt_result = await self.code_prompt_builder.create_code_prompt_messages(
                    user_query=formatted_query,
                    context={
                        "session_id": request.session_id,
                        "existing_analyses": similar_analyses
                    } if request.session_id else {"existing_analyses": similar_analyses}
                )
                step_duration = time.time() - step_start
                logger.info(f"⏱️ TIMING - Step 3 (Create Code Prompt Messages): {step_duration:.3f}s")
                
                if code_prompt_result["status"] != "success":
                    logger.error(f"❌ Code prompt message creation failed: {code_prompt_result.get('error')}")
                    return AnalysisResponse(
                        success=False,
                        error=f"Code prompt message creation failed: {code_prompt_result.get('error')}",
                        timestamp=datetime.now().isoformat()
                    )
                
                # Use the specified model or default
                model = request.model or self.analysis_service.llm_service.default_model
                logger.info(f"🤖 Using model: {model}")
                
                # Step 4: Analyze with structured messages (system prompt auto-loaded)
                step_start = time.time()
                messages = code_prompt_result.get("user_messages", [])
                formatted_enhanced_message = self._format_message_with_template(enhanced_message)
                
                # APpend question
                messages.append({"role": "user", "content": formatted_enhanced_message})
                
                result = await self.analysis_service.analyze_question(formatted_enhanced_message, messages, model, request.enable_caching)
                step_duration = time.time() - step_start
                logger.info(f"⏱️ TIMING - Step 4 (Main Analysis): {step_duration:.3f}s")
            
            if result["success"]:
                # Step 6: Save completed analysis and update conversation
                step_start = time.time()
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
                    
                except Exception as save_error:
                    logger.error(f"❌ Error saving analysis: {save_error}")
                    # Don't fail the main request, just log the error
                
                step_duration = time.time() - step_start
                logger.info(f"⏱️ TIMING - Step 6 (Save Analysis Results): {step_duration:.3f}s")
                
                # Step 7: Update conversation with analysis results
                step_start = time.time()
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
                
                step_duration = time.time() - step_start
                logger.info(f"⏱️ TIMING - Step 7 (Update Conversation): {step_duration:.3f}s")
                
                # Step 8: Build enhanced response with conversation context
                step_start = time.time()
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
                
                step_duration = time.time() - step_start
                logger.info(f"⏱️ TIMING - Step 8 (Build Enhanced Response): {step_duration:.3f}s")
                
                # Log total analysis time
                total_duration = time.time() - start_time
                logger.info(f"⏱️ TIMING - TOTAL ANALYSIS TIME: {total_duration:.3f}s")
                
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
    
    async def build_code_prompt(self, request: QuestionRequest) -> Dict[str, Any]:
        """
        Build enriched prompt for code generation by selecting MCP functions and fetching schemas
        """
        try:
            logger.info(f"🔧 Building code prompt for: {request.question[:100]}...")
            
            # Format the question with message template
            formatted_question = self._format_message_with_template(request.question)
            
            # Build enriched prompt using the code prompt builder service
            result = await self.code_prompt_builder.build_enriched_prompt(
                user_query=formatted_question,
                context={"session_id": request.session_id} if request.session_id else None
            )
            
            return {
                "success": result["status"] == "success",
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Code prompt building error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }