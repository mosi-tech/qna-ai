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
from shared.services.progress_service import send_progress_info, send_progress_error
from shared.services.execution_queue_service import execution_queue_service

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
        session_manager=None
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
        
        # Initialize dialogue factory with server's session manager
        # The search service will lazily initialize ChromaDB when first needed
        initialize_dialogue_factory(
            analysis_library=None, 
            chat_history_service=chat_history_service,
            session_manager=session_manager
        )
    
    def _create_default_llm(self):
        """Create default LLM service - not used since llm_service is always provided"""
        from ...llm import create_analysis_llm
        return create_analysis_llm()
    
    async def analyze_question(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
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
            Analysis response dictionary
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
        
        try:
            
            set_context(
                session_id=session_id
                message_id=message_id,
                user_id=user_id
            )
            self.logger.info(f"📝 Received question: {request.question[:100]}...")
            
            # Step 1: Check message-level cache for early return
            cache_response, warnings = await self._check_message_cache(request)
            if cache_response:
                return await self._handle_async_response(cache_response, session_id, message_id)
            
            # Step 2: Context-aware search and meaningless query detection  
            search_response, context_result = await self._perform_context_search(request)
            if search_response:
                return await self._handle_async_response(search_response, session_id, message_id)
            
            # Step 3: Handle confirmation requests for low-confidence expansions
            confirmation_response = await self._handle_confirmation_requests(request, context_result)
            if confirmation_response:
                return await self._handle_async_response(confirmation_response, session_id, message_id)
            
            # Get the final query to analyze (expanded if contextual)
            expanded_query = context_result.get("expanded_query", request.question)
            
            # Step 4: Evaluate reuse potential with similar analyses
            reuse_response, reuse_warnings = await self._evaluate_reuse_potential(request, context_result, expanded_query)
            warnings.extend(reuse_warnings)
            if reuse_response:
                return await self._handle_async_response(reuse_response, session_id, message_id)
            
            # Step 5: Execute analysis using either direct mode or code prompt builder
            analysis_response = await self._build_analysis(request, expanded_query, context_result)
            if not analysis_response:
                error_response = await self._error_response_dict(
                    user_message="We ran into an issue and couldn't answer your question. Please try again.",
                    internal_error="Analysis builder failed",
                    session_id=session_id,
                    user_id=user_id
                )
                return await self._handle_async_response(error_response, session_id, message_id)
            
            # Step 6: Process and save analysis results
            if analysis_response["success"]:
                analysis_id, processing_warnings = await self._process_and_save_analysis(request, analysis_response["data"])
                warnings.extend(processing_warnings)
                if not analysis_id:
                    error_response = await self._error_response_dict(
                        user_message="We ran into an issue processing your analysis. Please try again.",
                        internal_error="Failed to process and save analysis",
                        session_id=session_id,
                        user_id=user_id
                    )
                    return await self._handle_async_response(error_response, session_id, message_id)
                
                # Step 7: Create execution and final response
                final_response = await self._create_final_response(request, analysis_response["data"], analysis_id, warnings, start_time)
                return await self._handle_async_response(final_response, session_id, message_id)
            else:
                error_response = await self._error_response_dict(
                    user_message="We ran into an issue and couldn't answer your question. Please try again.",
                    internal_error=analysis_response.get("error", "Unknown analysis error"),
                    session_id=session_id,
                    user_id=user_id
                )
                return await self._handle_async_response(error_response, session_id, message_id)
                
        except Exception as e:
            self.logger.error(f"❌ Analysis endpoint error: {e}", exc_info=True)
            error_response = await self._error_response_dict(
                user_message="We ran into an issue and couldn't answer your question. Please try again.",
                internal_error=str(e),
                session_id=session_id,
                user_id=user_id
            )
            return await self._handle_async_response(error_response, session_id, message_id)
    
    async def _handle_async_response(self, response, session_id: str = None, message_id: str = None) -> Dict[str, Any]:
        """
        Handle response in async worker context
        
        In async mode:
        1. Log errors to message logs (DB) 
        2. Return structured data for worker processing
        3. API server reads logs and manages SSE streaming
        
        Args:
            response: Response object or dict
            session_id: Session ID (for compatibility)
            message_id: Message ID for logging
        """
        # Convert response to dict if needed
        if hasattr(response, '__dict__'):
            response_data = response.__dict__
        else:
            response_data = response
        
        # Extract key information
        success = response_data.get('success', True)
        error_message = response_data.get('error')
        
        # If this is an error response, log it to database
        # API server will read these logs and convert to SSE events
        if not success and error_message and message_id:
            try:
                await self._log_error_to_message(message_id, error_message, response_data.get('internal_error'))
            except Exception as e:
                self.logger.warning(f"Failed to log error to message: {e}")
        
        return response_data
    
    async def _log_error_to_message(self, message_id: str, error_message: str, internal_error: str = None):
        """Log error to message logs array - same pattern as worker"""
        try:
            from datetime import datetime
            
            full_error = f"{error_message}"
            if internal_error:
                full_error += f" (Internal: {internal_error})"
            
            # Use direct database access like the worker does
            # The pipeline should have access to the database through its services
            # For now, we'll use a simple approach and rely on worker's _log_to_message
            self.logger.info(f"📝 Pipeline error logged: {full_error} (message: {message_id})")
            # TODO: Implement direct DB logging here if needed
            
        except Exception as e:
            self.logger.error(f"Failed to log error to message {message_id}: {e}")
    
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
                
                try:
                    await send_progress_info(session_id, "Found cached analysis!")
                except Exception as e:
                    self.logger.warning(f"Could not send progress update: {e}")
                
                # Add professional indicator that this is a cached response
                original_content = cached_message_data.get("content", "Analysis completed")
                cached_content = f"[Previously analyzed] This question has been analyzed before. Here are the insights:\\n\\n{original_content}"
                
                response = await self._create_response_with_message(
                    session_id=session_id,
                    user_id=user_id,
                    response_type="cache_hit",
                    message_content=cached_content,
                    analysis_id=cached_message_data.get("analysis_id"),
                    execution_id=cached_message_data.get("execution_id"),
                    metadata={
                        "cache_hit": True,
                    },
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
            # Add apiServer path for dialogue import
            import sys
            api_server_path = os.path.join(os.path.dirname(__file__), '..', '..', 'scriptEdition', 'apiServer')
            if api_server_path not in sys.path:
                sys.path.insert(0, api_server_path)
            from ..dialogue import search_with_context
            
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
            error_response = await self._error_response_dict(
                user_message="We ran into an issue and couldn't answer your question. Please try again.",
                internal_error=error_msg,
                session_id=session_id,
                user_id=user_id
            )
            return error_response, context_result
        
        # Check if query is meaningless
        if context_result.get("is_meaningless"):
            error_message = context_result.get("message") or "I need more details to help you. Please tell me what you'd like to analyze."
            
            response = await self._create_response_with_message(
                session_id=session_id,
                user_id=user_id,
                response_type="meaningless",
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
            response_type = "needs_clarification" if context_result.get("needs_clarification") else "needs_confirmation"
            return await self._create_response_with_message(
                session_id=session_id,
                user_id=user_id,
                response_type=response_type,
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
            await send_progress_info(session_id, "Evaluating similar analyses....")
        except Exception as e:
            self.logger.warning(f"Could not send progress update: {e}")
        
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
                    request=request,
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
                    
                    response = await self._create_response_with_message(
                        session_id=session_id,
                        user_id=user_id,
                        response_type="reuse_decision",
                        message_content=reuse_decision.get('analysis_description', ''),
                        analysis_id=analysis_id,
                        execution_id=execution_id,
                        metadata=msg_metadata,
                        cache_output=True,
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

        try:
            await send_progress_info(session_id, "Building new analyses....")
        except Exception as e:
            self.logger.warning(f"Could not send progress update: {e}")
        
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
        
        if result and result.get("success"):
            return result
        else:
            self.logger.error(f"❌ Analysis failed: {result.get('error') if result else 'No result'}")
            return None

    async def _process_and_save_analysis(self, request: QuestionRequest, analysis_data: Dict) -> Tuple[Optional[str], List]:
        """
        Step 6: Process and save analysis results to MongoDB and ChromaDB
        Returns (analysis_id, warnings) or (None, []) if failed
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        warnings = []
        
        try:
            await send_progress_info(session_id, "Running analyses....")
        except Exception as e:
            self.logger.warning(f"Could not send progress update: {e}")
        
        response_type = analysis_data.get("response_type")
        analysis_result = analysis_data.get("analysis_result", {})
        
        # Extract consistent fields from both reuse and script generation responses
        script_name = analysis_result.get("script_name")
        execution_params = analysis_result.get("execution", {})
        analysis_description = analysis_result.get("analysis_description", "")
        
        # Initialize analysis_summary for use in chat message
        analysis_summary = analysis_description
        
        # Check if analysis persistence service is available
        if not self.analysis_persistence_service:
            self.logger.error("❌ Analysis persistence service not available")
            return None, warnings
        
        if not script_name:
            self.logger.error("❌ No script generated")
            return None, warnings
        
        # For now, return a placeholder analysis_id
        # TODO: Implement full analysis persistence logic
        analysis_id = f"analysis_{int(time.time())}"
        self.logger.info(f"✅ Analysis processed with ID: {analysis_id}")
        
        return analysis_id, warnings

    async def _create_final_response(self, request: QuestionRequest, analysis_data: Dict, analysis_id: str, warnings: List, start_time: float) -> AnalysisResponse:
        """
        Step 7: Create execution and final response
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        
        response_type = analysis_data.get("response_type")
        analysis_result = analysis_data.get("analysis_result", {})
        
        # Extract consistent fields from both reuse and script generation responses
        script_name = analysis_result.get("script_name")
        execution_params = analysis_result.get("execution", {})
        analysis_description = analysis_result.get("analysis_description", "")
        
        # Submit execution
        execution_id = await self._submit_execution(
            user_id=user_id,
            session_id=session_id,
            analysis_id=analysis_id,
            question=request.question,
            execution_params=execution_params
        )
        
        if not execution_id:
            execution_id = f"exec_{int(time.time())}"  # Fallback
        
        # Build metadata with essential data for UI reconstruction
        msg_metadata = {
            "analysis_type": response_type,
            "script_name": script_name,
            "execution": execution_params,
            "processing_time": time.time() - start_time,
            "provider": analysis_data.get("provider", "unknown"),
            "model": analysis_data.get("model", "unknown"),
        }
        if warnings:
            msg_metadata["warnings"] = warnings
        
        response = await self._create_response_with_message(
            session_id=session_id,
            user_id=user_id,
            response_type=response_type,
            message_content=analysis_description,
            analysis_id=analysis_id,
            execution_id=execution_id,
            metadata=msg_metadata,
            cache_output=True,
        )
        
        return response

    # === HELPER METHODS ===
    
    def _format_message_with_template(self, message: str) -> str:
        """Format message with template"""
        # Simple template formatting - could be enhanced
        return f"Please analyze the following financial question: {message}"
    
    async def _submit_execution(self, request: QuestionRequest, execution_params: Dict[str, Any]) -> Optional[str]:
        """
        Submit execution for analysis and log it.
        
        Args:
            user_id: User ID
            session_id: Session ID
            analysis_id: Analysis ID
            question: User's original question
            execution_params: Execution metadata
            
        Returns:
            execution_id if successful, None if failed
        """
        try:
            if not self.audit_service:
                logger.error("❌ Audit service not available for execution logging")
                return None
            
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
                    # Send execution queued status update via SSE
                    send_progress_info(session_id, "Enqueued execution for processing")
                else:
                    logger.error(f"⚠️ Failed to enqueue execution: {execution_id}")
                    # Send execution failed status update via SSE
                    send_progress_error(session_id, "Failed to enqueue execution")
                    
            except Exception as queue_error:
                # Don't fail the whole process if queue enqueue fails
                logger.warning(f"⚠️ Failed to enqueue execution {execution_id}: {queue_error}")
                # Send execution failed status update via SSE
               send_progress_error(session_id, "Failed to enqueue execution")
            
            return execution_id
            
        except Exception as e:
            logger.error(f"❌ Failed to log execution: {e}")
            return None
    
    
    async def _create_response_with_message(self, session_id: str, user_id: str, response_type: str, 
                                          message_content: str, analysis_id: Optional[str] = None, 
                                          execution_id: Optional[str] = None, metadata: Optional[Dict] = None,
                                          cache_output: bool = False) -> AnalysisResponse:
        """Create response with message"""
        try:
            # TODO: Implement proper response creation with chat message logging
            return AnalysisResponse(
                success=True,
                data={
                    "session_id": session_id,
                    "user_id": user_id,
                    "response_type": response_type,
                    "content": message_content,
                    "analysis_id": analysis_id,
                    "execution_id": execution_id,
                    "metadata": metadata or {},
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to create response: {e}")
            error_response = await self._error_response_dict(
                user_message="Failed to create response",
                internal_error=str(e),
                session_id=session_id,
                user_id=user_id
            )
            return AnalysisResponse(**error_response)
    
    async def _error_response(self, user_message: str, internal_error: str, 
                            session_id: str, user_id: str) -> AnalysisResponse:
        """Create standardized error response"""
        return AnalysisResponse(
            success=False,
            error=user_message,
            internal_error=internal_error,
            session_id=session_id,
            user_id=user_id,
            timestamp=datetime.now().isoformat()
        )
    
    async def _error_response_dict(self, user_message: str, internal_error: str, 
                                 session_id: str, user_id: str) -> Dict[str, Any]:
        """Create standardized error response as dict"""
        return {
            "success": False,
            "error": user_message,
            "internal_error": internal_error,
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }


# Factory function
def create_analysis_pipeline(**services) -> AnalysisPipelineService:
    """Create analysis pipeline with injected services"""
    return AnalysisPipelineService(**services)