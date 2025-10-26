"""
FastAPI Routes for Financial Analysis Server
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from fastapi import HTTPException
from typing import Dict, Any, Optional

from api.models import QuestionRequest, AnalysisResponse
from services.analysis import AnalysisService
from services.search import SearchService
from services.code_prompt_builder import CodePromptBuilderService
from services.reuse_evaluator import ReuseEvaluatorService
from services.chat_service import ChatHistoryService
from services.cache_service import CacheService
from services.execution_queue_service import execution_queue_service
from services.analysis_persistence_service import AnalysisPersistenceService
from services.audit_service import AuditService
from services.execution_service import ExecutionService
from db.schemas import AnalysisModel
from dialogue import search_with_context, initialize_dialogue_factory
from services.progress_service import (
    progress_manager,
    progress_info,
    progress_success,
    progress_warning,
)

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
        session_manager = None
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
        self.session_manager = session_manager
        
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
        
        # Initialize dialogue factory with server's session manager
        # The search service will lazily initialize ChromaDB when first needed
        initialize_dialogue_factory(
            analysis_library=None, 
            chat_history_service=chat_history_service,
            session_manager=session_manager
        )
    
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
    
    async def _ensure_error_saved(self, user_message: str, session_id: str = None, user_id: str = None) -> bool:
        """ALWAYS try to save error message to chat history - critical for debugging"""
        if not self.chat_history_service or not session_id or not user_id:
            logger.warning("⚠️ Cannot save error: missing chat_history_service, session_id, or user_id")
            return False

        max_retries = 3
        for attempt in range(max_retries):
            try:
                await self.chat_history_service.add_assistant_message(
                    session_id=session_id,
                    user_id=user_id,
                    content=user_message,
                )
                logger.info(f"✅ Saved error message to session: {session_id}")
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ Failed to save error (attempt {attempt + 1}/{max_retries}): {e}")
                    await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"❌ CRITICAL: Failed to save error message after {max_retries} attempts: {e}")
                    return False
        return False

    async def _create_response_with_message(
        self,
        session_id: str,
        user_id: str,
        response_type: str,
        message_content: str,
        analysis_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        cache_output: bool = False,
    ) -> AnalysisResponse:
        """
        Create a chat message record AND return it as the response.
        Message IS the response - single source of truth.
        Ensures all interaction types (reuse, clarification, analysis, etc.) are persisted.
        
        Args:
            session_id: Chat session ID
            user_id: User ID
            response_type: Type of response (reuse_decision, clarification, analysis, meaningless, etc.)
            message_content: Content for the chat message
            analysis_id: Optional reference to analysis
            execution_id: Optional reference to execution
            metadata: Essential metadata for rendering (response_type will be added automatically)
                     Should contain minimal data needed to reconstruct UI state
            cache_output: Whether to cache this message for future reuse
        
        Returns:
            AnalysisResponse where data contains the message itself
        """
        msg_id = None
        try:
            # Create message with response_type and essential metadata only
            msg_metadata = {"response_type": response_type}
            if metadata:
                msg_metadata.update(metadata)
            
            msg_id = await self.chat_history_service.add_assistant_message(
                session_id=session_id,
                user_id=user_id,
                content=message_content,
                analysis_id=analysis_id,
                execution_id=execution_id,
                metadata=msg_metadata,
            )
            logger.info(f"✓ Created {response_type} message in chat history: {msg_id}")
            
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
                    logger.info(f"✓ Cached {response_type} message")
                except Exception as cache_error:
                    logger.warning(f"⚠️ Failed to cache {response_type} message: {cache_error}")
            
            # Link execution to the message it created (NON-CRITICAL - bidirectional link for convenience)
            # The critical link is message→execution (embedded in message), this is just execution→message
            if execution_id and self.audit_service and msg_id:
                try:
                    await self.audit_service.link_execution_to_message(execution_id, msg_id)
                    logger.info(f"✓ Linked execution {execution_id} to message {msg_id}")
                except Exception as link_error:
                    logger.warning(f"⚠️ Failed to link execution to message: {link_error}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to create {response_type} message: {e}")
            # Continue anyway - don't fail response if message creation fails
        
        # Return message as the response data
        # This ensures consistency: fresh load and refresh both use same data structure
        response_data = {
            "message_id": msg_id,
            "session_id": session_id,
            "content": message_content,
            "analysis_id": analysis_id,
            "execution_id": execution_id,
            "metadata": msg_metadata,
        }
        
        return AnalysisResponse(
            success=True,
            data=response_data,
            timestamp=datetime.now().isoformat()
        )
    
    async def _error_response(self, user_message: str, internal_error: str = None, session_id: str = None, user_id: str = None) -> AnalysisResponse:
        """Create user-friendly error response (hide technical details)"""
        if internal_error:
            logger.error(f"Internal error: {internal_error}")

        # ALWAYS try to save error message - this is critical for debugging
        saved = await self._ensure_error_saved(user_message, session_id, user_id)

        return AnalysisResponse(
            success=False,
            error=user_message,
            metadata={"error_saved_to_db": saved} if not saved else None,
            timestamp=datetime.now().isoformat()
        )
    
    async def _submit_execution(self, user_id: str, session_id: str, analysis_id: str, question: str, execution_params: Dict[str, Any]) -> Optional[str]:
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
                script_name = execution_params.get("script_name", "")
                script_content = execution_params.get("script_content", "")
                parameters = execution_params.get("parameters", {})
                
                if script_content and script_name:
                    queue_success = await execution_queue_service.enqueue_execution(
                        execution_id=execution_id,
                        analysis_id=analysis_id,
                        session_id=session_id,
                        user_id=user_id,
                        script_content=script_content,
                        script_name=script_name,
                        parameters=parameters,
                        priority=1,  # High priority for user-initiated executions
                        timeout_seconds=300
                    )
                    
                    if queue_success:
                        logger.info(f"✓ Enqueued execution for processing: {execution_id}")
                    else:
                        logger.warning(f"⚠️ Failed to enqueue execution: {execution_id}")
                else:
                    logger.warning(f"⚠️ No script content available for execution: {execution_id}")
                    
            except Exception as queue_error:
                # Don't fail the whole process if queue enqueue fails
                logger.warning(f"⚠️ Failed to enqueue execution {execution_id}: {queue_error}")
            
            return execution_id
            
        except Exception as e:
            logger.error(f"❌ Failed to log execution: {e}")
            return None
    
    async def _validate_session_and_log_user_message(self, request: QuestionRequest) -> Optional[AnalysisResponse]:
        """
        Step 0: Validate session and log user message
        Returns error response if validation fails, None if successful
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        
        # Verify session exists (CRITICAL - fail if missing)
        if not session_id:
            logger.error(f"❌ CRITICAL: No session_id provided in request")
            return AnalysisResponse(
                success=False,
                error="Session ID is required. Please start a new conversation.",
                timestamp=datetime.now().isoformat()
            )

        await progress_info(session_id, "Evaluating your question...")

        # Add user message to chat history (CRITICAL - fail if this doesn't work)
        if not self.chat_history_service:
            logger.error(f"❌ CRITICAL: Chat history service not available")
            return await self._error_response(
                user_message="System error: Chat service unavailable. Please try again.",
                internal_error="Chat history service not initialized",
                session_id=session_id,
                user_id=user_id
            )
            
        try:
            message_id = await self.chat_history_service.add_user_message(
                session_id=session_id,
                user_id=user_id,
                question=request.question
            )
            logger.info(f"✓ Added user message to chat history: {message_id}")
        except Exception as e:
            logger.error(f"❌ CRITICAL: Failed to add user message: {e}")
            # This is critical - the user's question must be recorded
            return await self._error_response(
                user_message="We ran into an issue and couldn't answer your question. Please try again.",
                internal_error=f"Failed to save user message: {e}",
                session_id=session_id,
                user_id=user_id
            )
        
        return None  # Success - continue with analysis

    async def _check_message_cache(self, request: QuestionRequest) -> tuple[Optional[AnalysisResponse], list]:
        """
        Step 1: Check message-level cache for early return
        Returns (response if cache hit, warnings list)
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        warnings = []
        
        if not self.cache_service:
            warning_msg = "Cache service not available - skipping cache check"
            logger.warning(f"⚠️ {warning_msg}")
            warnings.append({"step": "cache_check", "message": warning_msg})
            return None, warnings
        
        try:
            cached_message_data = await self.cache_service.get_cached_message(
                question=request.question,
                user_id=user_id
            )
            if cached_message_data:
                logger.info("⚡ Cache hit! Returning cached message immediately (skipping search)")
                await progress_info(session_id, "Found cached analysis!")
                
                # Add professional indicator that this is a cached response
                original_content = cached_message_data.get("content", "Analysis completed")
                cached_content = f"[Previously analyzed] This question has been analyzed before. Here are the insights:\n\n{original_content}"
                
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
            warning_msg = f"Message cache check failed: {e}"
            logger.warning(f"⚠️ {warning_msg}")
            warnings.append({"step": "cache_check", "message": warning_msg})
        
        return None, warnings  # No cache hit - continue

    async def _perform_context_search(self, request: QuestionRequest) -> tuple[Optional[AnalysisResponse], dict]:
        """
        Step 2: Context-aware search and meaningless query detection
        Returns (error response if failed/meaningless, context_result dict)
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        
        step_start = time.time()
        context_result = await search_with_context(
            query=request.question,
            session_id=session_id,
            auto_expand=request.auto_expand
        )
        step_duration = time.time() - step_start
        logger.info(f"⏱️ TIMING - Step 2 (Context Search): {step_duration:.3f}s")
        
        if not context_result["success"]:
            error_msg = context_result.get('error', 'Unknown error')
            error_response = await self._error_response(
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

    async def _handle_confirmation_requests(self, request: QuestionRequest, context_result: dict) -> Optional[AnalysisResponse]:
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

    async def _evaluate_reuse_potential(self, request: QuestionRequest, context_result: dict, expanded_query: str) -> tuple[Optional[AnalysisResponse], list]:
        """
        Step 4: Evaluate similar analyses for reuse potential
        Returns (response if reuse successful, warnings list)
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        warnings = []
        
        # Get similar analyses from context search
        similar_analyses = context_result.get("search_results", [])
        logger.info(f"🔍 Found {len(similar_analyses)} similar analyses from context search")
        
        if not similar_analyses:
            return None, warnings  # No similar analyses - proceed with new analysis
        
        # Evaluate reuse potential
        step_start = time.time()
        logger.info(f"🔄 Evaluating reuse potential for {len(similar_analyses)} similar analyses...")
        await progress_info(session_id, "Evaluating similar analyses....")
        
        reuse_result = await self.reuse_evaluator.evaluate_reuse(
            user_query=expanded_query,
            existing_analyses=similar_analyses,
            context={"session_id": request.session_id} if request.session_id else None
        )
        step_duration = time.time() - step_start
        logger.info(f"⏱️ TIMING - Step 4 (Reuse Evaluation): {step_duration:.3f}s")
        
        # Check if reuse is recommended
        if reuse_result["status"] == "success" and reuse_result["reuse_decision"]["should_reuse"]:
            logger.info(f"✅ Reuse decision: {reuse_result['reuse_decision']['reason']}")
            
            reuse_decision = reuse_result["reuse_decision"]
            analysis_id = reuse_decision.get("analysis_id")
            
            # Submit execution for reused analysis
            execution_id = await self._submit_execution(
                user_id=user_id,
                session_id=session_id,
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
                
                response = await self._create_response_with_message(
                    session_id=session_id,
                    user_id=user_id,
                    response_type="reuse_decision",
                    message_content=f"Reused existing analysis: {reuse_decision.get('reason')}",
                    analysis_id=analysis_id,
                    execution_id=execution_id,
                    metadata=msg_metadata,
                    cache_output=True,
                )
                return response, warnings
            else:
                warning_msg = f"Failed to run execution on reuse"
                logger.warning(f"⚠️ {warning_msg}")
                warnings.append({"step": "reuse_execution", "message": warning_msg})
        else:
            logger.info("➡️ No suitable analysis for reuse, proceeding with new analysis generation")
        
        return None, warnings  # No reuse - continue with new analysis

    async def _build_analysis(self, request: QuestionRequest, expanded_query: str, context_result: dict) -> Optional[dict]:
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

        await progress_info(session_id, "Building new analyses....")
        
        if skip_code_prompt_builder:
            logger.info("🚀 Skipping code prompt builder - using direct analysis mode")
            # Use the specified model or default
            model = request.model or self.analysis_service.llm_service.default_model
            logger.info(f"🤖 Using model: {model}")
            
            # Format the query with message template
            formatted_query = self._format_message_with_template(expanded_query)
            
            # Direct analysis with formatted message (system prompt auto-loaded)
            step_start = time.time()
            result = await self.analysis_service.analyze_question(formatted_query, None, model, request.enable_caching)
            step_duration = time.time() - step_start
            logger.info(f"⏱️ TIMING - Step 5 (Direct Analysis): {step_duration:.3f}s")
        else:
            # Format the query with message template
            formatted_query = self._format_message_with_template(expanded_query)
            
            # Create code prompt messages with function schemas
            step_start = time.time()
            logger.info("🔧 Creating code prompt messages...")
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
            logger.info(f"⏱️ TIMING - Step 5 (Create Code Prompt Messages): {step_duration:.3f}s")
            
            if code_prompt_result["status"] != "success":
                logger.error(f"❌ Code prompt creation failed: {code_prompt_result.get('error')}")
                return None, None
            
            # Use the specified model or default
            model = request.model or self.analysis_service.llm_service.default_model
            logger.info(f"🤖 Using model: {model}")
            
            # Analyze with structured messages (system prompt auto-loaded)
            step_start = time.time()
            simulated_convo = code_prompt_result.get("user_messages", [])
            formatted_enhanced_message = self._format_message_with_template(enhanced_message)

            # Prepend the enhanced question 
            messages = [{"role": "user", "content": formatted_enhanced_message}]
            messages = messages + simulated_convo
            
            result = await self.analysis_service.analyze_question(formatted_enhanced_message, messages, model, True)
            step_duration = time.time() - step_start
            logger.info(f"⏱️ TIMING - Step 5 (Main Analysis): {step_duration:.3f}s")
        
        if result["success"]:
            return result
        else:
            logger.error(f"❌ Analysis failed: {result.get('error')}")
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
            await progress_info(session_id, "Running analyses....")
            
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
                logger.error("❌ Analysis persistence service not available")
                return None, warnings
            
            if not script_name:
                logger.error("❌ No script generated")
                return None, warnings
            
            # Validate if we should save this analysis
            should_save = (
                (response_type == "reuse_decision" and analysis_result.get("should_reuse")) or
                (response_type == "script_generation" and analysis_result.get("status") == "success")
            )
            
            if not should_save:
                error_detail = ""
                if response_type == "script_generation" and analysis_result.get("status") == "failed":
                    error_detail = analysis_result.get('final_error', 'Unknown error')
                else:
                    error_detail = f"Unexpected response: type={response_type}, should_reuse={analysis_result.get('should_reuse')}, status={analysis_result.get('status')}"
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

    async def _create_final_response(self, request: QuestionRequest, analysis_data: dict, analysis_id: str, warnings: list, start_time: float) -> AnalysisResponse:
        """
        Step 7: Create execution and final response
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        
        # Extract data from result
        analysis_result = analysis_data.get("analysis_result", {})
        execution_params = analysis_result.get("execution", {})
        analysis_summary = analysis_result.get("analysis_description", "")
        
        # Log execution start (CRITICAL - needed to track execution and link results to messages)
        execution_id = await self._submit_execution(
            user_id=user_id,
            session_id=session_id,
            analysis_id=analysis_id,
            question=request.question,
            execution_params=execution_params
        )
        
        if not execution_id:
            return await self._error_response(
                user_message="Failed to initialize execution. Please try again.",
                internal_error="Failed to log execution",
                session_id=session_id,
                user_id=user_id
            )
        
        # Prepare response metadata
        response_metadata = {
            "response_data": analysis_data,
            "warnings": warnings,
            "original_query": request.question
        }
        
        # Log total analysis time
        total_duration = time.time() - start_time
        logger.info(f"⏱️ TIMING - TOTAL ANALYSIS TIME: {total_duration:.3f}s")

        return await self._create_response_with_message(
            session_id=session_id,
            user_id=user_id,
            response_type="analysis",
            message_content=analysis_summary or "Analysis completed",
            analysis_id=analysis_id,
            execution_id=execution_id,
            metadata=response_metadata,
            cache_output=True,
        )

    async def analyze_question(self, request: QuestionRequest) -> AnalysisResponse:
        """
        Analyze a financial question with conversation context support
        """
        start_time = time.time()
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id

        try:
            logger.info(f"📝 Received question: {request.question[:100]}...")
            
            # Step 0: Validate session and log user message
            validation_error = await self._validate_session_and_log_user_message(request)
            if validation_error:
                return validation_error
            
            # Step 1: Check message-level cache for early return
            cache_response, warnings = await self._check_message_cache(request)
            if cache_response:
                return cache_response
            
            # Step 2: Context-aware search and meaningless query detection  
            search_response, context_result = await self._perform_context_search(request)
            if search_response:
                return search_response
            
            # Step 3: Handle confirmation requests for low-confidence expansions
            confirmation_response = await self._handle_confirmation_requests(request, context_result)
            if confirmation_response:
                return confirmation_response
            
            # Get the final query to analyze (expanded if contextual)
            expanded_query = context_result.get("expanded_query", request.question)
            
            # Step 4: Evaluate reuse potential with similar analyses
            reuse_response, reuse_warnings = await self._evaluate_reuse_potential(request, context_result, expanded_query)
            warnings.extend(reuse_warnings)
            if reuse_response:
                return reuse_response
            
            # Step 5: Execute analysis using either direct mode or code prompt builder
            analysis_response = await self._build_analysis(request, expanded_query, context_result)
            if not analysis_response:
                return await self._error_response(
                    user_message="We ran into an issue and couldn't answer your question. Please try again.",
                    internal_error="Analysis builder failed",
                    session_id=session_id,
                    user_id=user_id
                )
            
            # Step 6: Process and save analysis results
            if analysis_response["success"]:
                analysis_id, processing_warnings = await self._process_and_save_analysis(request, analysis_response["data"])
                warnings.extend(processing_warnings)
                if not analysis_id:
                    return await self._error_response(
                        user_message="We ran into an issue processing your analysis. Please try again.",
                        internal_error="Failed to process and save analysis",
                        session_id=session_id,
                        user_id=user_id
                    )
                
                # Step 7: Create execution and final response
                return await self._create_final_response(request, analysis_response["data"], analysis_id, warnings, start_time)
            else:
                return await self._error_response(
                    user_message="We ran into an issue and couldn't answer your question. Please try again.",
                    internal_error=analysis_response.get("error", "Unknown analysis error"),
                    session_id=session_id,
                    user_id=user_id
                )
                
        except Exception as e:
            logger.error(f"❌ Analysis endpoint error: {e}", exc_info=True)
            return await self._error_response(
                user_message="We ran into an issue and couldn't answer your question. Please try again.",
                internal_error=str(e),
                session_id=session_id,
                user_id=user_id
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
            return await self._error_response(
                user_message="I couldn't process your response. Please try again.",
                internal_error=str(e),
                session_id=session_id,
                user_id="anonymous"
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
            if not self.session_manager:
                return {
                    "success": False,
                    "error": "Session manager not available",
                    "timestamp": datetime.now().isoformat()
                }
            
            stats = self.session_manager.get_cache_stats()
            
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
                        "execution_id": e.execution_id if hasattr(e, 'execution_id') else e.get('executionId'),
                        "question": e.question if hasattr(e, 'question') else e.get('question'),
                        "status": e.status if hasattr(e, 'status') else e.get('status'),
                        "started_at": e.started_at.isoformat() if hasattr(e, 'started_at') and hasattr(e.started_at, 'isoformat') else str(e.get('startedAt')),
                        "execution_time_ms": e.execution_time_ms if hasattr(e, 'execution_time_ms') else e.get('executionTimeMs')
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
    
