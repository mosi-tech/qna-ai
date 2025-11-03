#!/usr/bin/env python3
"""
Analysis Pipeline Service

This is the complete analysis pipeline extracted from APIRoutes.analyze_question().
It includes all the steps from session validation to final response creation.

This service can be used by:
- APIRoutes for synchronous analysis (HTTP endpoint)
- AnalysisWorker for asynchronous analysis (queue processing)
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from ...services.base_service import BaseService
from ..dialogue.factory import initialize_dialogue_factory
from shared.services.progress_service import send_progress_info, send_analysis_progress, send_analysis_error, send_analysis_success
from shared.services.execution_queue_service import execution_queue_service
from shared.queue.worker_context import set_context, get_message_id, get_session_id, get_user_id
from ..dialogue import search_with_context
from shared.constants import MessageStatus

logger = logging.getLogger(__name__)


class QuestionRequest:
    """Simple request object to match APIRoutes interface"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class AnalysisResponse:
    """Simple response object to match APIRoutes interface"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class AnalysisPipelineService:
    """Complete analysis pipeline that handles the full analysis workflow"""
    
    def __init__(
        self,
        analysis_service=None,
        search_service=None,
        chat_history_service=None,
        cache_service=None,
        analysis_persistence_service=None,
        reuse_evaluator=None,
        code_prompt_builder=None,
        session_manager=None,
        audit_service=None
    ):
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Core services (these would be injected)
        self.analysis_service = analysis_service
        self.search_service = search_service
        self.chat_history_service = chat_history_service
        self.cache_service = cache_service
        self.analysis_persistence_service = analysis_persistence_service
        self.reuse_evaluator = reuse_evaluator
        self.code_prompt_builder = code_prompt_builder
        self.session_manager = session_manager
        self.audit_service = audit_service
        
        # Validate critical dependencies - fail fast if missing
        if not self.analysis_service:
            raise ValueError("AnalysisService is required for pipeline operation")
        if not self.search_service:
            raise ValueError("SearchService is required for pipeline operation") 
        if not self.chat_history_service:
            raise ValueError("ChatHistoryService is required for pipeline operation")
        
        # Initialize dialogue factory with server's session manager
        # The search service will lazily initialize ChromaDB when first needed
        initialize_dialogue_factory(
            analysis_library=None, 
            chat_history_service=chat_history_service,
            session_manager=session_manager
        )
    
    
    async def analyze_question(self, request_data: Dict[str, Any]) -> AnalysisResponse:
        """
        Complete analysis pipeline that mirrors APIRoutes.analyze_question()
        
        Args:
            request_data: Dictionary containing:
                - question: The user's question
                - session_id: Chat session ID
                - user_id: User ID (optional)
                - message_id: Message ID for logging (async context)
                - enable_caching: Whether to enable caching
                - other request parameters
        
        Returns:
            AnalysisResponse object containing:
                - success: Boolean indicating if analysis succeeded
                - data: Analysis data (for success cases)
                - error: Error message (for failure cases)  
                - internal_error: Internal error details (for failure cases)
                - session_id: Session ID
                - user_id: User ID
                - timestamp: Response timestamp
        """
        start_time = time.time()
        
        # Convert dict to request object for compatibility with copied methods
        request = QuestionRequest(**request_data)
        if not hasattr(request, 'user_id'):
            request.user_id = "anonymous"
        if not hasattr(request, 'enable_caching'):
            request.enable_caching = True
        if not hasattr(request, 'auto_expand'):
            request.auto_expand = True
        if not hasattr(request, 'model'):
            request.model = None
        if not hasattr(request, 'message_id'):
            request.message_id = None
        
        user_id = request.user_id
        session_id = request.session_id
        message_id = request.message_id
        
        # Initialize pipeline state
        final_response = None
        warnings = []
        context_result = {}
        
        try:
            # Set context for this analysis pipeline run
            set_context(
                session_id=session_id,
                message_id=message_id,
                user_id=user_id
            )
            
            self.logger.info(f"📝 Received question: {request.question[:100]}...")
            
            # Update message status to indicate analysis has started
            if message_id:
                try:
                    await self.chat_history_service.update_assistant_message(
                        message_id=message_id,
                        content="Analysis in progress...",
                        metadata={"status": MessageStatus.ANALYSIS_STARTED}
                    )
                except Exception as update_error:
                    self.logger.warning(f"⚠️ Failed to update message status to analysis_started: {update_error}")
            
            await send_analysis_progress("Starting analysis pipeline", step="pipeline_start", status="started")
            
            # Define pipeline steps - each returns (response, should_continue)
            pipeline_steps = [
                ("cache_check", "Checking analysis library", self._step_check_cache),
                ("context_search", "Building context and searching for similar analyses", self._step_context_search),
                ("confirmation", "Handling confirmation requests", self._step_handle_confirmation),
                ("reuse_evaluation", "Evaluating reuse potential", self._step_evaluate_reuse),
                ("analysis_generation", "Building new analysis", self._step_build_analysis),
            ]
            
            # Execute pipeline steps until one returns a response
            for step_name, step_description, step_function in pipeline_steps:
                await send_analysis_progress(step_description, step=step_name)
                
                if step_name == "context_search":
                    response, context_result = await step_function(request)
                elif step_name == "confirmation":
                    response = await step_function(request, context_result)
                elif step_name == "reuse_evaluation":
                    expanded_query = context_result.get("expanded_query", request.question)
                    response, step_warnings = await step_function(request, context_result, expanded_query)
                    warnings.extend(step_warnings)
                elif step_name == "analysis_generation":
                    expanded_query = context_result.get("expanded_query", request.question)
                    response = await step_function(request, expanded_query, context_result, warnings, start_time)
                else:
                    response, step_warnings = await step_function(request)
                    warnings.extend(step_warnings)
                
                if response:
                    final_response = response
                    break
            
            # If no response was generated, something went wrong
            if not final_response:
                raise RuntimeError("Pipeline completed without generating a response")
            
            # Save the message to database now that we have the final response
            if final_response and final_response.success and final_response.data:
                response_data = final_response.data
                
                # Update message status based on analysis completion and execution submission
                status = MessageStatus.ANALYSIS_COMPLETED
                if response_data.get("executionId"):
                    status = MessageStatus.EXECUTION_QUEUED
                
                # Add status to metadata
                metadata = response_data.get("metadata", {})
                metadata["status"] = status
                
                await self._update_message_only(
                    analysis_type=response_data.get("analysis_type", "script_generation"),
                    message_content=response_data.get("content", ""),
                    analysis_id=response_data.get("analysisId"),
                    execution_id=response_data.get("executionId"),
                    metadata=metadata,
                    cache_output=True
                )
            
            return final_response
        except Exception as e:
            self.logger.error(f"❌ Analysis endpoint error: {e}", exc_info=True)
            
            # Send pipeline failure event
            await send_analysis_error(f"Analysis pipeline failed: {str(e)}", 
                                     step="pipeline_error", 
                                     error=str(e), 
                                     processing_time=time.time() - start_time)
            
            # Update the message with error information
            error_message = "We ran into an issue and couldn't answer your question. Please try again."
            try:
                await self._update_message_only(
                    analysis_type=None,  # No analysis was completed
                    message_content=error_message,
                    metadata={
                        "status": MessageStatus.ANALYSIS_FAILED,
                        "error": error_message,
                        "internal_error": str(e),
                        "processing_time": time.time() - start_time,
                        "failed_at": datetime.now().isoformat()
                    }
                )
            except Exception as update_error:
                self.logger.error(f"❌ Failed to update message with error: {update_error}")
            
            return await self._error_response(
                user_message=error_message,
                internal_error=str(e)
            )
    
    # === PIPELINE STEP WRAPPERS ===
    
    async def _step_check_cache(self, request: QuestionRequest):
        """Step wrapper for cache checking"""
        return await self._check_message_cache(request)
    
    async def _step_context_search(self, request: QuestionRequest):
        """Step wrapper for context search"""
        return await self._perform_context_search(request)
    
    async def _step_handle_confirmation(self, request: QuestionRequest, context_result: Dict):
        """Step wrapper for confirmation handling"""
        response = await self._handle_confirmation_requests(request, context_result)
        return response  # This returns response or None
    
    async def _step_evaluate_reuse(self, request: QuestionRequest, context_result: Dict, expanded_query: str):
        """Step wrapper for reuse evaluation"""
        return await self._evaluate_reuse_potential(request, context_result, expanded_query)
    
    async def _step_build_analysis(self, request: QuestionRequest, expanded_query: str, context_result: Dict, warnings: list, start_time: float):
        """Step wrapper for building new analysis - this is the final step that always returns a response"""
        analysis_response = await self._build_analysis(request, expanded_query, context_result)
        if not analysis_response:
            raise RuntimeError("Analysis builder failed")
        
        if analysis_response["success"]:
            await send_analysis_progress("Processing and saving analysis results", step="analysis_processing")
            analysis_id, processing_warnings = await self._process_and_save_analysis(request, analysis_response["data"])
            warnings.extend(processing_warnings)
            if not analysis_id:
                raise RuntimeError("Failed to process and save analysis")
            
            await send_analysis_progress("Creating execution and finalizing response", step="execution_creation")
            final_response = await self._create_final_response(request, analysis_response["data"], analysis_id, warnings, start_time)
            
            await send_analysis_success("Analysis pipeline completed successfully", 
                                      step="pipeline_complete", 
                                      processing_time=time.time() - start_time)
            
            return final_response
        else:
            raise RuntimeError(analysis_response.get("error", "Unknown analysis error"))
    
    # === PIPELINE STEPS ===

    async def _check_message_cache(self, request: QuestionRequest) -> Tuple[Optional[AnalysisResponse], List]:
        """
        Step 1: Check message-level cache for early return
        Returns (response if cache hit, warnings list)
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        warnings = []
        
        if not self.cache_service:
            warning_msg = "Cache service not available - skipping cache check"
            self.logger.warning(f"⚠️ {warning_msg}")
            warnings.append({"step": "cache_check", "message": warning_msg})
            return None, warnings
        
        try:
            cached_message_data = await self.cache_service.get_cached_message(
                question=request.question,
                user_id=user_id
            )
            if cached_message_data:
                self.logger.info("⚡ Cache hit! Returning cached message immediately (skipping search)")
                
                # Add professional indicator that this is a cached response
                original_content = cached_message_data.get("content", "Analysis completed")
                cached_content = f"[Previously analyzed] This question has been analyzed before. Here are the insights:\\n\\n{original_content}"
                
                response = await self._create_analysis_response(
                    analysis_type="cache_hit",
                    message_content=cached_content,
                    analysis_id=cached_message_data.get("analysis_id"),
                    execution_id=cached_message_data.get("execution_id"),
                    metadata={
                        "cache_hit": True,
                    }
                )
                return response, warnings
        except Exception as e:
            warning_msg = f"Cache check failed: {e}"
            self.logger.warning(f"⚠️ {warning_msg}")
            warnings.append({"step": "cache_check", "message": warning_msg})
        
        return None, warnings

    async def _perform_context_search(self, request: QuestionRequest) -> Tuple[Optional[AnalysisResponse], Dict]:
        """
        Step 2: Context-aware search and meaningless query detection
        Returns (error response if failed/meaningless, context_result dict)
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        
        try:
            
            step_start = time.time()
            context_result = await search_with_context(
                query=request.question,
                session_id=session_id,
                auto_expand=request.auto_expand
            )
            step_duration = time.time() - step_start
            self.logger.info(f"⏱️ TIMING - Step 2 (Context Search): {step_duration:.3f}s")
        except Exception as e:
            self.logger.error(f"Context search failed: {e}")
            context_result = {
                "success": False,
                "error": str(e),
                "expanded_query": request.question,
                "search_results": []
            }
        
        if not context_result["success"]:
            error_msg = context_result.get('error', 'Unknown error')
            raise RuntimeError(f"Context search failed: {error_msg}")
        
        # Check if query is meaningless
        if context_result.get("is_meaningless"):
            error_message = context_result.get("message") or "I need more details to help you. Please tell me what you'd like to analyze."
            
            response = await self._create_analysis_response(
                analysis_type="meaningless",
                message_content=error_message,
                metadata={"is_meaningless": True}
            )
            return response, context_result
        
        return None, context_result  # Success - continue

    async def _handle_confirmation_requests(self, request: QuestionRequest, context_result: Dict) -> Optional[AnalysisResponse]:
        """
        Step 3: Handle confirmation requests for low-confidence expansions
        Returns response if confirmation needed, None if can proceed
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        
        if context_result.get("needs_confirmation") or context_result.get("needs_clarification"):
            analysis_type = "needs_clarification" if context_result.get("needs_clarification") else "needs_confirmation"
            return await self._create_analysis_response(
                analysis_type=analysis_type,
                message_content=context_result.get("message", "Please confirm if this interpretation is correct."),
                metadata={
                    "original_query": request.question,
                    "expanded_query": context_result.get("expanded_query"),
                    "confidence": context_result.get("expansion_confidence", 0.0),
                    "needs_confirmation": context_result.get("needs_confirmation", False),
                    "needs_clarification": context_result.get("needs_clarification", False),
                }
            )
        
        return None  # No confirmation needed - continue

    async def _evaluate_reuse_potential(self, request: QuestionRequest, context_result: Dict, expanded_query: str) -> Tuple[Optional[AnalysisResponse], List]:
        """
        Step 4: Evaluate similar analyses for reuse potential
        Returns (response if reuse successful, warnings list)
        """
        
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        warnings = []
        
        # Get similar analyses from context search
        similar_analyses = context_result.get("search_results", [])
        self.logger.info(f"🔍 Found {len(similar_analyses)} similar analyses from context search")
        
        if not similar_analyses or not self.reuse_evaluator:
            self.logger.warn(f"No similar analyses found or reuse evalautor service set")
            return None, warnings  # No similar analyses or evaluator - proceed with new analysis
        
        # Evaluate reuse potential
        step_start = time.time()
        self.logger.info(f"🔄 Evaluating reuse potential for {len(similar_analyses)} similar analyses...")
        
        try:
            reuse_result = await self.reuse_evaluator.evaluate_reuse(
                user_query=expanded_query,
                existing_analyses=similar_analyses,
                context={"session_id": request.session_id} if request.session_id else None
            )
            step_duration = time.time() - step_start
            self.logger.info(f"⏱️ TIMING - Step 4 (Reuse Evaluation): {step_duration:.3f}s")
            
            # Check if reuse is recommended
            if reuse_result["status"] == "success" and reuse_result["reuse_decision"]["should_reuse"]:
                self.logger.info(f"✅ Reuse decision: {reuse_result['reuse_decision']['reason']}")
                
                reuse_decision = reuse_result["reuse_decision"]
                analysis_id = reuse_decision.get("analysis_id")
                
                # Submit execution for reused analysis
                execution_id = await self._submit_execution(
                    analysis_id=analysis_id,
                    question=request.question,
                    execution_params=reuse_decision.get("execution", {})
                )
                
                if execution_id:
                    # Build metadata with essential data for UI reconstruction
                    msg_metadata = {
                        "should_reuse": reuse_decision.get("should_reuse"),
                        "reason": reuse_decision.get("reason", ""),
                        "similarity": reuse_decision.get("similariy", 0),
                        "original_execution": reuse_decision.get("original_execution", {}),
                        "original_query": request.question,
                    }
                    if warnings:
                        msg_metadata["warnings"] = warnings
                    
                    response = await self._create_analysis_response(
                        analysis_type="reuse_decision",
                        message_content=reuse_decision.get('analysis_description', ''),
                        analysis_id=analysis_id,
                        execution_id=execution_id,
                        metadata=msg_metadata
                    )
                    return response, warnings
                else:
                    warning_msg = f"Failed to run execution on reuse"
                    self.logger.warning(f"⚠️ {warning_msg}")
                    warnings.append({"step": "reuse_execution", "message": warning_msg})
            else:
                self.logger.info("➡️ No suitable analysis for reuse, proceeding with new analysis generation")
        except Exception as e:
            warning_msg = f"Reuse evaluation failed: {e}"
            self.logger.warning(f"⚠️ {warning_msg}")
            warnings.append({"step": "reuse_evaluation", "message": warning_msg})
        
        return None, warnings  # No reuse - continue with new analysis

    async def _build_analysis(self, request: QuestionRequest, expanded_query: str, context_result: Dict) -> Optional[Dict]:
        """
        Step 5: Execute analysis using either direct mode or code prompt builder
        Returns result dict or None if failed
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        similar_analyses = context_result.get("search_results", [])
        enhanced_message = expanded_query  # Use expanded_query as enhanced message
        
        # Check if we should skip code prompt builder (direct analysis mode)
        skip_code_prompt_builder = os.getenv("SKIP_CODE_PROMPT_BUILDER", "false").lower() == "true"
        skip_code_prompt_builder = False

        if skip_code_prompt_builder or not self.code_prompt_builder:
            self.logger.info("🚀 Using direct analysis mode")
            # Use the specified model or default
            model = request.model or (self.analysis_service.llm_service.default_model if self.analysis_service else None)
            self.logger.info(f"🤖 Using model: {model}")
            
            # Format the query with message template
            formatted_query = self._format_message_with_template(expanded_query)
            
            # Direct analysis with formatted message (system prompt auto-loaded)
            step_start = time.time()
            result = await self.analysis_service.analyze_question(formatted_query, None, model, request.enable_caching)
            step_duration = time.time() - step_start
            self.logger.info(f"⏱️ TIMING - Step 5 (Direct Analysis): {step_duration:.3f}s")
            
            if not result or not result.get("success"):
                error_msg = result.get('error') if result else 'Analysis service returned no result'
                raise RuntimeError(f"Critical analysis generation failed: {error_msg}")
        else:
            # Format the query with message template
            formatted_query = self._format_message_with_template(expanded_query)
            
            # Create code prompt messages with function schemas
            step_start = time.time()
            self.logger.info("🔧 Creating code prompt messages...")
            code_prompt_result = await self.code_prompt_builder.create_code_prompt_messages(
                user_query=formatted_query,
                context={
                    "session_id": request.session_id,
                    "existing_analyses": similar_analyses
                } if request.session_id else {"existing_analyses": similar_analyses},
                provider_type=self.analysis_service.llm_service.provider_type,
                enable_caching=True
            )
            step_duration = time.time() - step_start
            self.logger.info(f"⏱️ TIMING - Step 5 (Create Code Prompt Messages): {step_duration:.3f}s")
            
            if code_prompt_result["status"] != "success":
                self.logger.error(f"❌ Code prompt creation failed: {code_prompt_result.get('error')}")
                return None
            
            # Use the specified model or default
            model = request.model or self.analysis_service.llm_service.default_model
            self.logger.info(f"🤖 Using model: {model}")
            
            # Analyze with structured messages (system prompt auto-loaded)
            step_start = time.time()
            simulated_convo = code_prompt_result.get("user_messages", [])
            formatted_enhanced_message = self._format_message_with_template(enhanced_message)

            # Prepend the enhanced question 
            messages = [{"role": "user", "content": formatted_enhanced_message}]
            messages = messages + simulated_convo
            
            result = await self.analysis_service.analyze_question(formatted_enhanced_message, messages, model, True)
            step_duration = time.time() - step_start
            self.logger.info(f"⏱️ TIMING - Step 5 (Main Analysis): {step_duration:.3f}s")
            
            if not result or not result.get("success"):
                error_msg = result.get('error') if result else 'Analysis service returned no result'
                raise RuntimeError(f"Critical analysis generation failed: {error_msg}")
        
        if result and result.get("success"):
            return result
        else:
            self.logger.error(f"❌ Analysis failed: {result.get('error') if result else 'No result'}")
            return None

    async def _process_and_save_analysis(self, request: QuestionRequest, analysis_data: dict) -> tuple[Optional[str], list]:
        """
        Step 6: Process and save analysis results to MongoDB and ChromaDB
        Returns (analysis_id, warnings) or (None, []) if failed
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        warnings = []
        
        try:
            
            analysis_type = analysis_data.get("analysis_type", "script_generation")
            analysis_result = analysis_data.get("analysis_result", {})
            
            # Extract consistent fields from both reuse and script generation responses
            script_name = analysis_result.get("script_name")
            execution_params = analysis_result.get("execution", {})
            analysis_description = analysis_result.get("analysis_description", "")
            
            # Initialize analysis_summary for use in chat message
            analysis_summary = analysis_description
            
            # Check if analysis persistence service is available
            if not self.analysis_persistence_service:
                raise RuntimeError("Analysis persistence service not available - cannot save analysis")
            
            if not script_name:
                logger.error("❌ No script generated")
                return None, warnings
            
            # Validate if we should save this analysis
            should_save = (
                (analysis_type == "reuse_decision" and analysis_result.get("should_reuse")) or
                (analysis_type == "script_generation" and analysis_result.get("status") == "success")
            )
            
            if not should_save:
                error_detail = ""
                if analysis_type == "script_generation" and analysis_result.get("status") == "failed":
                    error_detail = analysis_result.get('final_error', 'Unknown error')
                else:
                    error_detail = f"Unexpected response: type={analysis_type}, should_reuse={analysis_result.get('should_reuse')}, status={analysis_result.get('status')}"
                logger.error(f"❌ Analysis not suitable for saving: {error_detail}")
                return None, warnings
            
            # Save to MongoDB first to get database-generated analysis_id
            analysis_id = await self.analysis_persistence_service.create_analysis(
                user_id=user_id,
                question=request.question,
                llm_response=analysis_result,
                script=script_name
            )
            analysis_data["analysis_id"] = analysis_id
            logger.info(f"✓ Saved analysis to MongoDB (analysis_id: {analysis_id})")
            
            # Save to ChromaDB using the MongoDB analysisId (NON-CRITICAL)
            if analysis_id and script_name and should_save:
                try:
                    save_result = self.search_service.save_completed_analysis(
                        analysis_id=analysis_id,
                        original_question=request.question,
                        addn_meta={
                            "execution": execution_params,
                            "description": analysis_description
                        }
                    )

                    if save_result.get("success"):
                        logger.info(f"✓ Saved analysis to ChromaDB (analysisId: {analysis_id})")
                    else:
                        warning_msg = f"Failed to save to ChromaDB: {save_result.get('error')}"
                        logger.warning(f"⚠️ {warning_msg}")
                        warnings.append({"step": "chromadb_save", "message": warning_msg})
                except Exception as chroma_error:
                    warning_msg = f"Failed to save to ChromaDB: {chroma_error}"
                    logger.warning(f"⚠️ {warning_msg}")
                    warnings.append({"step": "chromadb_save", "message": warning_msg})
            
            return analysis_id, warnings
            
        except Exception as save_error:
            logger.error(f"❌ Error processing analysis results: {save_error}")
            return None, warnings

    async def _create_final_response(self, request: QuestionRequest, analysis_data: Dict, analysis_id: str, warnings: List, start_time: float) -> AnalysisResponse:
        """
        Step 7: Create execution and final response
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        
        analysis_type = analysis_data.get("analysis_type", "script_generation")
        analysis_result = analysis_data.get("analysis_result", {})
        
        # Extract consistent fields from both reuse and script generation responses
        script_name = analysis_result.get("script_name")
        execution_params = analysis_result.get("execution", {})
        analysis_description = analysis_result.get("analysis_description", "")
        
        # Submit execution (CRITICAL - must succeed)
        execution_id = await self._submit_execution(
            analysis_id=analysis_id,
            question=request.question,
            execution_params=execution_params
        )
        
        if not execution_id:
            raise RuntimeError("Failed to submit execution - this is a critical error")
        
        # Build metadata with essential data for UI reconstruction
        msg_metadata = {
            "analysis_type": analysis_type,
            "script_name": script_name,
            "execution": execution_params,
            "processing_time": time.time() - start_time,
            "provider": analysis_data.get("provider", "unknown"),
            "model": analysis_data.get("model", "unknown"),
        }
        if warnings:
            msg_metadata["warnings"] = warnings
        
        # Create the response object (message will be saved later in main pipeline)
        response = await self._create_analysis_response(
            analysis_type=analysis_type,
            message_content=analysis_description,
            analysis_id=analysis_id,
            execution_id=execution_id,
            metadata=msg_metadata
        )
        
        return response

    # === HELPER METHODS ===
    
    def _format_message_with_template(self, message: str) -> str:
        """Format message with template"""
        # Simple template formatting - could be enhanced
        return f"Please analyze the following financial question: {message}"
    
    async def _submit_execution(self, analysis_id: str, question: str, execution_params: Dict[str, Any]) -> Optional[str]:
        """
        Submit execution for analysis and log it.
        
        Args:
            analysis_id: Analysis ID
            question: User's original question
            execution_params: Execution metadata
            
        Returns:
            execution_id if successful, None if failed
        """
        try:
            if self.audit_service is None:
                logger.warning("⚠️ Audit service not available for execution logging - skipping execution logging")
                return None
            
            user_id = get_user_id()
            session_id = get_session_id()

            # Log execution start in audit service
            execution_id = await self.audit_service.log_execution_start(
                user_id=user_id,
                analysis_id=analysis_id,
                session_id=session_id,
                question=question,
                generated_script=execution_params.get("script_name", ""),
                execution_params=execution_params
            )
            logger.info(f"✓ Logged execution start: {execution_id}")
            
            # Also enqueue execution in queue system for processing
            try:
                queue_success = await execution_queue_service.enqueue_execution(
                    execution_id=execution_id,
                    analysis_id=analysis_id,
                    session_id=session_id,
                    user_id=user_id,
                    execution_params=execution_params,
                    priority=1,  # High priority for user-initiated executions
                    timeout_seconds=300
                )
                
                if queue_success:
                    logger.info(f"✓ Enqueued execution for processing: {execution_id}")
                else:
                    logger.error(f"⚠️ Failed to enqueue execution: {execution_id}")
                    
            except Exception as queue_error:
                # Don't fail the whole process if queue enqueue fails
                logger.warning(f"⚠️ Failed to enqueue execution {execution_id}: {queue_error}")
            
            return execution_id
            
        except Exception as e:
            logger.error(f"❌ Failed to log execution: {e}")
            return None
    
    
    async def _update_message_with_response(self, analysis_type: str, 
                                          message_content: str, analysis_id: Optional[str] = None, 
                                          execution_id: Optional[str] = None, metadata: Optional[Dict] = None,
                                          cache_output: bool = False) -> AnalysisResponse:
        """Update message and return AnalysisResponse - for cases where both are needed"""
        await self._update_message_only(analysis_type, message_content, analysis_id, execution_id, metadata, cache_output)
        return await self._create_analysis_response(analysis_type, message_content, analysis_id, execution_id, metadata)
    
    async def _update_message_only(self, analysis_type: str, 
                                 message_content: str, analysis_id: Optional[str] = None, 
                                 execution_id: Optional[str] = None, metadata: Optional[Dict] = None,
                                 cache_output: bool = False) -> None:
        """
        Update the existing message with the analysis response.
        Since we create an empty message at the beginning, this updates it with the final content.
        Ensures all interaction types (reuse, clarification, analysis, etc.) are persisted.
        """
        # Get context values
        session_id = get_session_id()
        user_id = get_user_id()
        message_id = get_message_id()
        
        # Create message with analysis_type and essential metadata only
        msg_metadata = {"analysis_type": analysis_type}
        if metadata:
            msg_metadata.update(metadata)
        
        # Update the existing message created at the beginning of analysis
        if message_id:
            success = await self.chat_history_service.update_assistant_message(
                message_id=message_id,
                content=message_content,
                analysis_id=analysis_id,
                execution_id=execution_id,
                metadata=msg_metadata,
            )
            if success:
                self.logger.info(f"✓ Updated {analysis_type} message in chat history: {message_id}")
            else:
                raise RuntimeError(f"Failed to update message {message_id} - core persistence failed")
        else:
            raise RuntimeError("No message_id in context - cannot persist conversation")
        
        # Cache the assistant message for future reuse (NON-CRITICAL)
        if self.cache_service and analysis_id and execution_id and cache_output:
            try:
                message_cache_data = {
                    "content": message_content,
                    "analysis_id": analysis_id,
                    "execution_id": execution_id,
                    "response_data": metadata.get("response_data", {}) if metadata else {},
                }
                await self.cache_service.cache_assistant_message(
                    question=metadata.get("original_query", "") if metadata else "",
                    user_id=user_id,
                    message_data=message_cache_data,
                    ttl_hours=24
                )
                self.logger.info(f"✓ Cached {analysis_type} message")
            except Exception as cache_error:
                self.logger.warning(f"⚠️ Failed to cache {analysis_type} message: {cache_error}")
        
        # Link execution to the message it created (NON-CRITICAL - bidirectional link for convenience)
        if execution_id and self.audit_service and message_id:
            try:
                await self.audit_service.link_execution_to_message(execution_id, message_id)
                self.logger.info(f"✓ Linked execution {execution_id} to message {message_id}")
            except Exception as link_error:
                self.logger.warning(f"⚠️ Failed to link execution to message: {link_error}")

    async def _create_analysis_response(self, analysis_type: str, 
                                      message_content: str, analysis_id: Optional[str] = None, 
                                      execution_id: Optional[str] = None, metadata: Optional[Dict] = None) -> AnalysisResponse:
        """Create AnalysisResponse object for returning to caller"""
        # Get context values
        session_id = get_session_id()
        message_id = get_message_id()
        
        # Add status and error fields for better error handling
        status = "completed"  # Default for successful responses
        error_message = None
        
        # Normalize analysis types for UI - analysis results should all be "script_generation"
        ui_analysis_type = analysis_type
        if analysis_type == "analysis":
            ui_analysis_type = "script_generation"
        
        response_data = {
            "message_id": message_id,  # Use message_id from context (original empty message)
            "session_id": session_id,
            "content": message_content,
            "analysisId": analysis_id,
            "executionId": execution_id,
            "analysis_type": ui_analysis_type,
            "status": status,
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        return AnalysisResponse(
            success=True,
            data=response_data,
            timestamp=datetime.now().isoformat()
        )
    
    async def _error_response(self, user_message: str, internal_error: str) -> AnalysisResponse:
        """Create standardized error response using context values"""
        return AnalysisResponse(
            success=False,
            error=user_message,
            internal_error=internal_error,
            session_id=get_session_id(),
            user_id=get_user_id(),
            message_id=get_message_id(),
            timestamp=datetime.now().isoformat()
        )


# Factory function
def create_analysis_pipeline(**services) -> AnalysisPipelineService:
    """Create analysis pipeline with injected services"""
    return AnalysisPipelineService(**services)