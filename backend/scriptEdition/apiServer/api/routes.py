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
from services.chat_service import ChatHistoryService
from services.cache_service import CacheService
from services.analysis_persistence_service import AnalysisPersistenceService
from services.audit_service import AuditService
from services.execution_service import ExecutionService
from services.progress_service import (
    progress_manager,
    progress_info,
    progress_success,
    progress_warning,
    progress_error,
)
from db.schemas import AnalysisModel
from dialogue import search_with_context, initialize_dialogue_factory, get_session_manager

logger = logging.getLogger("api-routes")


class APIRoutes:
    """Handles all API route logic"""
    
    def __init__(
        self,
        analysis_service: AnalysisService,
        search_service: SearchService,
        chat_history_service: ChatHistoryService = None,
        cache_service: CacheService = None,
        analysis_persistence_service: AnalysisPersistenceService = None,
        audit_service: AuditService = None,
        execution_service: ExecutionService = None,
        code_prompt_builder: CodePromptBuilderService = None,
        reuse_evaluator: ReuseEvaluatorService = None,
        repo_manager = None
    ):
        self.analysis_service = analysis_service
        self.search_service = search_service
        self.chat_history_service = chat_history_service
        self.cache_service = cache_service
        self.analysis_persistence_service = analysis_persistence_service
        self.audit_service = audit_service
        self.execution_service = execution_service
        self.code_prompt_builder = code_prompt_builder or CodePromptBuilderService()
        self.reuse_evaluator = reuse_evaluator or ReuseEvaluatorService()
        self.repo_manager = repo_manager
        
        # Load message template
        self.message_template = self._load_message_template()
        
        # Log workflow mode
        skip_code_prompt_builder = os.getenv("SKIP_CODE_PROMPT_BUILDER", "false").lower() == "true"
        if skip_code_prompt_builder:
            logger.info("🚀 ANALYSIS MODE: Direct analysis (skipping code prompt builder)")
        else:
            code_prompt_mode = os.getenv("CODE_PROMPT_MODE", "tool_simulation").lower()
            logger.info(f"🔧 ANALYSIS MODE: Full workflow (with code prompt builder)")
            logger.info(f"📝 CODE PROMPT MODE: {code_prompt_mode}")
        
        # Initialize dialogue factory (don't try to get library at startup - it's lazy loaded)
        # The search service will lazily initialize ChromaDB when first needed
        initialize_dialogue_factory(analysis_library=None, repo_manager=repo_manager)
    
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
    
    def _error_response(self, user_message: str, internal_error: str = None) -> AnalysisResponse:
        """Create user-friendly error response (hide technical details)"""
        if internal_error:
            logger.error(f"Internal error: {internal_error}")
        return AnalysisResponse(
            success=False,
            error=user_message,
            timestamp=datetime.now().isoformat()
        )
    
    async def analyze_question(self, request: QuestionRequest) -> AnalysisResponse:
        """
        Analyze a financial question with conversation context support
        """
        start_time = time.time()
        execution_id = None
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id or "unknown"
        
        try:
            logger.info(f"📝 Received question: {request.question[:100]}...")
            logger.info(f"🔴 DEBUG: About to emit progress for session {session_id}")
            event = await progress_info(session_id, f"Processing question: {request.question[:80]}")
            logger.info(f"🟢 DEBUG: Progress event created: {event.to_dict()}")
            
            # Step 0: Initialize or retrieve session
            session_id = request.session_id
            if self.chat_history_service and not session_id:
                try:
                    session_id = await self.chat_history_service.start_session(user_id)
                    logger.info(f"✓ Started new session: {session_id}")
                    await progress_success(session_id, "Session created")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to start session: {e}")
                    await progress_warning(session_id, f"Session creation failed: {str(e)}")
            
            # Step 0.5: Add user message to chat history
            if self.chat_history_service and session_id:
                try:
                    await progress_info(session_id, "Adding message to chat history")
                    message_id = await self.chat_history_service.add_user_message(
                        session_id=session_id,
                        user_id=user_id,
                        question=request.question
                    )
                    logger.info(f"✓ Added user message to chat history: {message_id}")
                    await progress_success(session_id, "Message logged")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to add user message: {e}")
                    await progress_warning(session_id, f"Failed to log message: {str(e)}")
            
            # Step 1: Check cache before processing
            if self.cache_service:
                try:
                    await progress_info(session_id, "Checking cache for similar analyses", step=1, total_steps=5)
                    cached_result = await self.cache_service.get_cached_result(
                        question=request.question,
                        parameters={"session_id": session_id} if session_id else {}
                    )
                    if cached_result:
                        logger.info("✓ Returning cached analysis result")
                        await progress_success(session_id, "Found cached result - returning immediately")
                        return AnalysisResponse(
                            success=True,
                            data={
                                "response_type": "cache_hit",
                                "cached_result": cached_result,
                                "message": "Result retrieved from cache"
                            },
                            timestamp=datetime.now().isoformat()
                        )
                    await progress_info(session_id, "Cache miss - proceeding with analysis")
                except Exception as e:
                    logger.warning(f"⚠️ Cache check failed: {e}")
                    await progress_warning(session_id, f"Cache check failed: {str(e)}")
            
            # Step 2: Use conversation-aware search to handle contextual queries
            await progress_info(session_id, "Searching for contextual information", step=2, total_steps=5)
            step_start = time.time()
            context_result = await search_with_context(
                query=request.question,
                session_id=session_id,
                auto_expand=request.auto_expand
            )
            step_duration = time.time() - step_start
            logger.info(f"⏱️ TIMING - Step 2 (Context Search): {step_duration:.3f}s")
            await progress_info(session_id, f"Context search completed in {step_duration:.2f}s")
            
            if not context_result["success"]:
                error_msg = context_result.get('error', 'Unknown error')
                await progress_error(session_id, f"Context search failed: {error_msg}")
                return self._error_response(
                    user_message="I couldn't understand your question. Please try rephrasing it.",
                    internal_error=error_msg
                )
            
            # Check if query is meaningless
            if context_result.get("is_meaningless"):
                await progress_warning(session_id, "Query not specific enough - requesting clarification")
                return AnalysisResponse(
                    success=True,
                    data={
                        "is_meaningless": True,
                        "session_id": context_result.get("session_id"),
                        "message": context_result.get("message"),
                    },
                    timestamp=datetime.now().isoformat()
                )
            
            # Get the final query to analyze (expanded if contextual)
            final_query = context_result.get("expanded_query", request.question)
            session_id = context_result["session_id"]
            
            logger.info(f"🔍 Query type: {context_result.get('query_type', 'unknown')}")
            if final_query != request.question:
                logger.info(f"🔄 Expanded to: {final_query[:100]}...")
                await progress_info(session_id, f"Query expanded: {final_query[:80]}...", details={"expansion_confidence": context_result.get("expansion_confidence")})
            
            # Step 2: Check if we need confirmation for low-confidence expansions
            if context_result.get("needs_confirmation") or context_result.get("needs_clarification"):
                await progress_info(session_id, "Waiting for user confirmation")
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
            skip_code_prompt_builder = False

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
                    } if request.session_id else {"existing_analyses": similar_analyses},
                    provider_type=self.analysis_service.llm_service.provider_type
                )
                step_duration = time.time() - step_start
                logger.info(f"⏱️ TIMING - Step 3 (Create Code Prompt Messages): {step_duration:.3f}s")
                
                if code_prompt_result["status"] != "success":
                    return self._error_response(
                        user_message="Unable to process your question at this time. Please try again.",
                        internal_error=f"Code prompt creation failed: {code_prompt_result.get('error')}"
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
                analysis_summary = None
                analysis_id = None
                
                try:
                    analysis_data = result["data"]
                    response_type = analysis_data.get("response_type")
                    analysis_result = analysis_data.get("analysis_result", {})
                    
                    # Extract consistent fields from both reuse and script generation responses
                    script_name = analysis_result.get("script_name")
                    execution_info = analysis_result.get("execution", {})
                    analysis_description = analysis_result.get("analysis_description", "")
                    mcp_calls = analysis_result.get("mcp_calls", [])
                    
                    # Save to search service (existing behavior)
                    if script_name and (
                        (response_type == "reuse_decision" and analysis_result.get("should_reuse")) or
                        (response_type == "script_generation" and analysis_result.get("status") == "success")
                    ):
                        save_result = self.search_service.save_completed_analysis(
                            original_question=request.question,
                            script_path=script_name,
                            addn_meta={"execution": execution_info, "description": analysis_description}
                        )
                        
                        if save_result.get("success"):
                            analysis_data["analysis_id"] = save_result["analysis_id"]
                            analysis_summary = save_result.get("analysis_description", "")
                            analysis_id = save_result["analysis_id"]
                        else:
                            logger.warning(f"Failed to save analysis: {save_result.get('error')}")
                    else:
                        if response_type == "script_generation" and analysis_result.get("status") == "failed":
                            analysis_summary = f"Script generation failed: {analysis_result.get('final_error', 'Unknown error')}"
                    
                    # Step 6b: Save to MongoDB persistence layer if available
                    if self.analysis_persistence_service and analysis_id:
                        try:
                            persistence_id = await self.analysis_persistence_service.create_analysis(
                                user_id=user_id,
                                title=request.question[:100],
                                description=analysis_description or "Financial analysis",
                                result=analysis_result,
                                parameters={"session_id": session_id} if session_id else {},
                                mcp_calls=mcp_calls,
                                category="financial_analysis",
                                script=script_name,
                                data_sources=["alpaca", "eodhd"]
                            )
                            logger.info(f"✓ Persisted analysis to MongoDB: {persistence_id}")
                        except Exception as persist_error:
                            logger.warning(f"⚠️ Failed to persist to MongoDB: {persist_error}")
                    
                except Exception as save_error:
                    logger.error(f"❌ Error saving analysis: {save_error}")
                
                step_duration = time.time() - step_start
                logger.info(f"⏱️ TIMING - Step 6 (Save Analysis Results): {step_duration:.3f}s")
                
                # Step 7: Add assistant message with analysis to chat history
                step_start = time.time()
                try:
                    # Log execution start if audit service available
                    if self.audit_service and session_id:
                        try:
                            execution_id = await self.audit_service.log_execution_start(
                                user_id=user_id,
                                session_id=session_id,
                                message_id="pending",
                                question=request.question,
                                script=script_name or "",
                                parameters={"session_id": session_id},
                                mcp_calls=mcp_calls or []
                            )
                            logger.info(f"✓ Logged execution start: {execution_id}")
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to log execution: {e}")
                    
                    # Add assistant message with analysis to chat history
                    if self.chat_history_service and session_id:
                        try:
                            # Create AnalysisModel from result
                            analysis_model = AnalysisModel(
                                title=request.question[:100],
                                description=analysis_description or "Financial analysis",
                                result=analysis_result,
                                parameters={"session_id": session_id},
                                mcp_calls=mcp_calls or [],
                                generated_script=script_name,
                                is_template=True,
                                tags=["auto_generated", "financial"]
                            )
                            
                            msg_id = await self.chat_history_service.add_assistant_message_with_analysis(
                                session_id=session_id,
                                user_id=user_id,
                                script=script_name or "",
                                explanation=analysis_summary or "Analysis completed",
                                analysis=analysis_model,
                                mcp_calls=mcp_calls or [],
                                execution_id=execution_id
                            )
                            logger.info(f"✓ Added assistant message with analysis to chat: {msg_id}")
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to add assistant message: {e}")
                    
                
                except Exception as chat_error:
                    logger.error(f"❌ Error updating chat history: {chat_error}")
                
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
                
                # Step 9: Cache the analysis result
                step_start = time.time()
                if self.cache_service and analysis_id:
                    try:
                        cache_id = await self.cache_service.cache_analysis_result(
                            question=request.question,
                            parameters={"session_id": session_id} if session_id else {},
                            result=response_data,
                            analysis_id=analysis_id,
                            ttl_hours=24
                        )
                        logger.info(f"✓ Cached analysis result: {cache_id}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to cache result: {e}")
                
                step_duration = time.time() - step_start
                logger.info(f"⏱️ TIMING - Step 9 (Cache Result): {step_duration:.3f}s")
                
                # Log total analysis time
                total_duration = time.time() - start_time
                logger.info(f"⏱️ TIMING - TOTAL ANALYSIS TIME: {total_duration:.3f}s")
                
                return AnalysisResponse(
                    success=True,
                    data=response_data,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return self._error_response(
                    user_message="I couldn't analyze your question. Please try rephrasing it.",
                    internal_error=result.get("error", "Unknown analysis error")
                )
                
        except Exception as e:
            logger.error(f"❌ Analysis endpoint error: {e}", exc_info=True)
            return self._error_response(
                user_message="Something went wrong while processing your question. Please try again later.",
                internal_error=str(e)
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
    
    async def handle_clarification_response(self, 
                                          session_id: str,
                                          user_response: str,
                                          original_query: str,
                                          expanded_query: str) -> Dict[str, Any]:
        """Handle user response to clarification prompt
        
        User can respond with:
        1. Confirmation (yes/ok) → proceed to search and return results
        2. Rejection (no/wrong) → ask for rephrase
        3. Additional clarification → treat as new contextual query
        """
        try:
            from dialogue import get_dialogue_factory
            
            factory = get_dialogue_factory()
            result = await factory.get_context_aware_search().handle_clarification_response(
                session_id=session_id,
                user_response=user_response,
                original_query=original_query,
                expanded_query=expanded_query
            )
            
            return {
                "success": result.get("success", True),
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Clarification handling error: {e}")
            return self._error_response(
                user_message="I couldn't process your response. Please try again.",
                internal_error=str(e)
            )
    
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
            result = await self.code_prompt_builder.create_code_prompt_messages(
                user_query=formatted_question,
                context={"session_id": request.session_id} if request.session_id else None,
                provider_type=self.analysis_service.llm_service.provider_type
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
    
    async def get_chat_history(self, session_id: str) -> Dict[str, Any]:
        """Get chat history for a session"""
        try:
            if not self.chat_history_service:
                return {
                    "success": False,
                    "error": "Chat history service not available",
                    "timestamp": datetime.now().isoformat()
                }
            
            history = await self.chat_history_service.get_conversation_history(session_id)
            
            return {
                "success": True,
                "session_id": session_id,
                "messages": history,
                "message_count": len(history),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting chat history: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_user_sessions(self, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get all sessions for a user"""
        try:
            if not self.chat_history_service:
                return {
                    "success": False,
                    "error": "Chat history service not available",
                    "timestamp": datetime.now().isoformat()
                }
            
            sessions = await self.chat_history_service.list_sessions(user_id, limit=limit)
            
            return {
                "success": True,
                "user_id": user_id,
                "sessions": [
                    {
                        "session_id": str(s.id) if hasattr(s, 'id') else s.get('_id'),
                        "title": s.title if hasattr(s, 'title') else s.get('title'),
                        "created_at": s.created_at.isoformat() if hasattr(s, 'created_at') else s.get('created_at'),
                        "message_count": s.message_count if hasattr(s, 'message_count') else s.get('message_count', 0)
                    }
                    for s in sessions
                ],
                "session_count": len(sessions),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user sessions: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_reusable_analyses(self, user_id: str) -> Dict[str, Any]:
        """Get all reusable analyses for a user"""
        try:
            if not self.analysis_persistence_service:
                return {
                    "success": False,
                    "error": "Analysis persistence service not available",
                    "timestamp": datetime.now().isoformat()
                }
            
            analyses = await self.analysis_persistence_service.get_reusable_analyses(user_id)
            
            return {
                "success": True,
                "user_id": user_id,
                "analyses": [
                    {
                        "analysis_id": str(a.id) if hasattr(a, 'id') else a.get('_id'),
                        "title": a.title if hasattr(a, 'title') else a.get('title'),
                        "description": a.description if hasattr(a, 'description') else a.get('description'),
                        "category": a.category if hasattr(a, 'category') else a.get('category'),
                        "similar_queries_count": len(a.similar_queries) if hasattr(a, 'similar_queries') else len(a.get('similar_queries', [])),
                        "tags": a.tags if hasattr(a, 'tags') else a.get('tags', [])
                    }
                    for a in analyses
                ],
                "analyses_count": len(analyses),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting reusable analyses: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def search_analyses(self, user_id: str, search_text: str, limit: int = 50) -> Dict[str, Any]:
        """Search analyses by title/description"""
        try:
            if not self.analysis_persistence_service:
                return {
                    "success": False,
                    "error": "Analysis persistence service not available",
                    "timestamp": datetime.now().isoformat()
                }
            
            analyses = await self.analysis_persistence_service.search_analyses(
                user_id=user_id,
                search_text=search_text,
                limit=limit
            )
            
            return {
                "success": True,
                "user_id": user_id,
                "search_text": search_text,
                "results": [
                    {
                        "analysis_id": str(a.id) if hasattr(a, 'id') else a.get('_id'),
                        "title": a.title if hasattr(a, 'title') else a.get('title'),
                        "description": a.description if hasattr(a, 'description') else a.get('description'),
                        "category": a.category if hasattr(a, 'category') else a.get('category')
                    }
                    for a in analyses
                ],
                "result_count": len(analyses),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error searching analyses: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_execution_history(self, session_id: str, limit: int = 100) -> Dict[str, Any]:
        """Get execution history for a session"""
        try:
            if not self.audit_service:
                return {
                    "success": False,
                    "error": "Audit service not available",
                    "timestamp": datetime.now().isoformat()
                }
            
            executions = await self.audit_service.get_execution_history(session_id, limit=limit)
            
            return {
                "success": True,
                "session_id": session_id,
                "executions": [
                    {
                        "execution_id": str(e.id) if hasattr(e, 'id') else e.get('_id'),
                        "question": e.question if hasattr(e, 'question') else e.get('question'),
                        "status": e.status if hasattr(e, 'status') else e.get('status'),
                        "started_at": e.started_at.isoformat() if hasattr(e, 'started_at') else e.get('started_at'),
                        "execution_time_ms": e.execution_time_ms if hasattr(e, 'execution_time_ms') else e.get('execution_time_ms')
                    }
                    for e in executions
                ],
                "execution_count": len(executions),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting execution history: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_analysis(self, analysis_id: str, user_id: str, session_id: str = None) -> Dict[str, Any]:
        """Execute a pending analysis script"""
        try:
            if not self.execution_service:
                return {
                    "success": False,
                    "error": "Execution service not available",
                    "timestamp": datetime.now().isoformat()
                }
            
            logger.info(f"🚀 Starting execution of analysis: {analysis_id}")
            
            # Execute the analysis
            exec_result = await self.execution_service.execute_analysis(
                analysis_id=analysis_id,
                user_id=user_id,
                session_id=session_id
            )
            
            if exec_result.get("success"):
                logger.info(f"✅ Analysis executed successfully in {exec_result.get('execution_time_ms')}ms")
                return {
                    "success": True,
                    "data": exec_result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ Execution failed: {exec_result.get('error')}")
                return {
                    "success": False,
                    "error": exec_result.get("error"),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }