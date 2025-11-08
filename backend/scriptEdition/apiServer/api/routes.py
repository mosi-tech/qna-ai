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
from typing import Dict, Any, Optional, List

from api.models import QuestionRequest, AnalysisResponse
from shared.services.chat_service import ChatHistoryService
from shared.services.cache_service import CacheService
from shared.services.execution_queue_service import execution_queue_service
from shared.analyze.services.analysis_persistence_service import AnalysisPersistenceService
from shared.services.audit_service import AuditService
from shared.constants import MessageStatus
from services.execution_service import ExecutionService
from shared.services.progress_service import (
    send_progress_info,
    send_execution_queued,
    send_execution_failed,
)


logger = logging.getLogger("api-routes")


class APIRoutes:
    """Handles all API route logic"""
    
    def __init__(
        self,
        chat_history_service: ChatHistoryService = None,
        cache_service: CacheService = None,
        analysis_persistence_service: AnalysisPersistenceService = None,
        audit_service: AuditService = None,
        execution_service: ExecutionService = None,
        session_manager = None,
        analysis_pipeline_service = None
    ):
        self.chat_history_service = chat_history_service
        self.cache_service = cache_service
        self.analysis_persistence_service = analysis_persistence_service
        self.audit_service = audit_service
        self.execution_service = execution_service
        self.session_manager = session_manager
        self.analysis_pipeline_service = analysis_pipeline_service
        
        # Initialize hybrid message handler for chat + analysis (GitHub Issue #122)
        self.hybrid_handler = None
        if chat_history_service:
            from shared.analyze.services.hybrid_message_handler import HybridMessageHandler
            self.hybrid_handler = HybridMessageHandler(
                chat_history_service=chat_history_service,
                analyze_question_callable=self.analyze_question  # Pass existing analyze_question method
            )
        
        # Initialize data transformer for clean transformation operations
        if chat_history_service and hasattr(chat_history_service, 'data_transformer'):
            self.data_transformer = chat_history_service.data_transformer
        else:
            self.data_transformer = None
        
    
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
        
        # Return clean UI message data instead of raw metadata
        # This ensures UI never sees internal database fields
        mock_msg = {
            "messageId": msg_id,
            "role": "assistant",
            "timestamp": None,
            "analysisId": analysis_id,
            "executionId": execution_id,
            "content": message_content,
            "metadata": msg_metadata
        }
        ui_data = await self.data_transformer.transform_message_to_ui_data(mock_msg)
        
        # Normalize response types for UI - analysis results should all be "analysis"
        ui_response_type = response_type
        if response_type in ["reuse_decision", "cache_hit", "analysis"]:
            ui_response_type = "analysis"
        
        response_data = {
            "message_id": msg_id,
            "session_id": session_id,
            "content": message_content,
            "analysisId": analysis_id,
            "executionId": execution_id,
            "uiData": ui_data,
            "response_type": ui_response_type,
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
    
    async def _submit_execution(self, user_id: str, session_id: str, analysis_id: str, question: str, execution_params: Dict[str, Any], message_id: Optional[str] = None) -> Optional[str]:
        """
        Submit execution for analysis and log it.
        
        Args:
            user_id: User ID
            session_id: Session ID
            analysis_id: Analysis ID
            question: User's original question
            execution_params: Execution metadata
            message_id: Optional message ID for SSE context
            
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
                    timeout_seconds=300,
                    message_id=message_id
                )
                
                if queue_success:
                    logger.info(f"✓ Enqueued execution for processing: {execution_id}")
                    # Send execution queued status update via SSE
                    await send_execution_queued()
                else:
                    logger.warning(f"⚠️ Failed to enqueue execution: {execution_id}")
                    # Send execution failed status update via SSE
                    await send_execution_failed("Failed to enqueue execution")
                    
            except Exception as queue_error:
                # Don't fail the whole process if queue enqueue fails
                logger.warning(f"⚠️ Failed to enqueue execution {execution_id}: {queue_error}")
                # Send execution failed status update via SSE
                await send_execution_failed(f"Queue error: {queue_error}")
            
            return execution_id
            
        except Exception as e:
            logger.error(f"❌ Failed to log execution: {e}")
            return None
    
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

    async def analyze_question_simple(self, request: QuestionRequest) -> AnalysisResponse:
        """
        SIMPLE VERSION - Minimal analysis endpoint without session locking for debugging
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        user_question = request.question

        try:
            logger.info(f"📝 SIMPLE analyze request: {user_question[:100]}...")
            
            # Step 1: Validate session exists
            if not session_id:
                logger.error(f"❌ No session_id provided in request")
                raise HTTPException(400, "Session ID is required. Please start a new conversation.")
            
            # Step 2: Create user message (ONLY if not triggered by hybrid handler)
            # Check if this is a background analysis from hybrid chat confirmation
            is_background_analysis = hasattr(request, '_from_hybrid_background') and request._from_hybrid_background
            
            if not self.chat_history_service:
                raise HTTPException(500, "Chat history service not available")
            
            if not is_background_analysis:
                user_message_id = await self.chat_history_service.add_user_message(
                    session_id=session_id,
                    user_id=user_id,
                    question=user_question
                )
                logger.info(f"✓ Created user message: {user_message_id}")
            else:
                # For background analysis, we don't create a new user message
                # The original "Yes" message already exists
                user_message_id = None
                logger.info(f"🔄 Background analysis - skipping user message creation")
            
            # Step 3: Create analysis message with basic metadata
            analysis_message_id = await self.chat_history_service.add_assistant_message(
                session_id=session_id,
                user_id=user_id,
                content="Analysis in progress...",
                metadata={
                    "status": MessageStatus.PENDING,
                    "user_message_id": user_message_id,
                    "queued_at": datetime.now().isoformat(),
                    "response_type": "script_generation"
                }
            )
            logger.info(f"✓ Created analysis message: {analysis_message_id}")
            
            # Step 4: Queue analysis (without session locking)
            from shared.queue.analysis_queue import get_analysis_queue
            analysis_queue = get_analysis_queue()
            
            job_id = await analysis_queue.enqueue_analysis({
                "session_id": session_id,
                "message_id": analysis_message_id,
                "user_question": user_question,
                "user_message_id": user_message_id,
                "user_id": user_id
            })
            
            logger.info(f"📥 Queued analysis job: {job_id} for message {analysis_message_id}")
            
            # Step 5: Create minimal message structure and transform to UI format
            # Since get_message doesn't exist, we'll create the minimal structure needed for transformation
            message_for_transform = {
                "messageId": analysis_message_id,
                "role": "assistant",
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "status": MessageStatus.PENDING,
                    "user_message_id": user_message_id,
                    "job_id": job_id,
                    "queued_at": datetime.now().isoformat(),
                    "response_type": "script_generation"
                }
            }
            
            if self.data_transformer:
                clean_msg = await self.data_transformer.transform_message_to_ui_data(message_for_transform)
            else:
                # Fallback for cases where transformer is unavailable
                clean_msg = {
                    "message_id": analysis_message_id,
                    "user_message_id": user_message_id,
                    "job_id": job_id,
                    "status": MessageStatus.PENDING,
                    "queued_at": datetime.now().isoformat()
                }
            
            # Step 6: Return immediately with pending status and consistent UI format
            return AnalysisResponse(
                success=True,
                data={
                    **clean_msg,  # Use transformer-generated UI data for consistency
                    "session_id": session_id,
                    "user_id": user_id
                },
                timestamp=datetime.now().isoformat()
            )
                
        except HTTPException:
            # Re-raise HTTPExceptions as-is
            raise
        except Exception as e:
            logger.error(f"❌ SIMPLE analyze endpoint error: {e}", exc_info=True)
            
            return await self._error_response(
                user_message="We ran into an issue and couldn't queue your analysis. Please try again.",
                internal_error=str(e),
                session_id=session_id,
                user_id=user_id
            )

    async def analyze_question(self, request: QuestionRequest) -> AnalysisResponse:
        """
        Async analysis endpoint - queues analysis and returns immediately with pending status
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        user_question = request.question

        try:
            logger.info(f"📝 Async analysis request: {user_question[:100]}...")
            
            # Import required services for async processing
            from shared.locking import get_session_lock
            from shared.queue.analysis_queue import get_analysis_queue
            
            session_lock = get_session_lock()
            analysis_queue = get_analysis_queue()
            
            # Step 1: Validate session exists
            if not session_id:
                logger.error(f"❌ No session_id provided in request")
                raise HTTPException(400, "Session ID is required. Please start a new conversation.")
            
            # Optional: Check if session exists in database (if you have session persistence)
            # This could validate against a sessions table/collection
            # if not await self.chat_history_service.session_exists(session_id):
            #     raise HTTPException(404, "Session not found. Please start a new conversation.")
            
            # Step 2: TEMPORARILY BYPASS LOCK LOGIC FOR DEBUGGING
            # TODO: Re-enable after fixing database hanging issue
            logger.info(f"⚠️ BYPASSING session lock for debugging: {session_id}")
            # lock_acquired = await session_lock.acquire_lock_or_takeover(
            #     session_id, 
            #     "temp_analysis_lock",  # Temporary placeholder - will update after message creation
            #     ttl_seconds=1800, 
            #     max_wait_seconds=5  # Reduced from 30 to 5 seconds for better UX
            # )
            # 
            # if not lock_acquired:
            #     logger.warning(f"⚠️ Cannot acquire session lock - analysis still active: {session_id}")
            #     raise HTTPException(409, "Session is currently processing another analysis. Please wait and try again.")
            # 
            # logger.info(f"🔒 Session lock acquired for new analysis: {session_id}")
            
            # Step 3: Create user message (now protected by lock)
            # Skip user message creation if this is a background analysis from hybrid handler
            if not self.chat_history_service:
                raise HTTPException(500, "Chat history service not available")
            
            user_message_id = None
            if hasattr(request, '_from_hybrid_background') and request._from_hybrid_background:
                logger.info(f"⏩ Skipping user message creation for background analysis")
                # Use placeholder for message ID tracking
                user_message_id = "hybrid_background_analysis"
            else:
                user_message_id = await self.chat_history_service.add_user_message(
                    session_id=session_id,
                    user_id=user_id,
                    question=user_question
                )
                logger.info(f"✓ Created user message: {user_message_id}")
            
            # Step 4: Create analysis message with basic metadata including job placeholder
            # Skip analysis message creation if this is a background analysis from hybrid handler
            analysis_message_id = None
            if hasattr(request, '_from_hybrid_background') and request._from_hybrid_background:
                logger.info(f"⏩ Skipping analysis message creation for background analysis")
                # Use the existing assistant message ID from hybrid handler
                analysis_message_id = getattr(request, '_hybrid_assistant_message_id', 'hybrid_background_analysis_msg')
                logger.info(f"✓ Using existing assistant message: {analysis_message_id}")
            else:
                analysis_message_id = await self.chat_history_service.add_assistant_message(
                    session_id=session_id,
                    user_id=user_id,
                    content="Analysis in progress...",
                    metadata={
                        "status": MessageStatus.PENDING,
                        "user_message_id": user_message_id,
                        "queued_at": datetime.now().isoformat(),
                        "response_type": "script_generation"
                    }
                )
                logger.info(f"✓ Created analysis message: {analysis_message_id}")
            
            # Step 5: TEMPORARILY BYPASS LOCK UPDATE FOR DEBUGGING
            # TODO: Re-enable after fixing database hanging issue
            logger.info(f"⚠️ BYPASSING lock update for debugging: {session_id} → {analysis_message_id}")
            # await session_lock.release_lock(session_id)
            # final_lock_acquired = await session_lock.acquire_lock(session_id, analysis_message_id, ttl_seconds=1800)
            # 
            # if not final_lock_acquired:
            #     logger.error(f"❌ Failed to re-acquire session lock with message ID: {analysis_message_id}")
            #     raise HTTPException(500, "Failed to finalize session lock for analysis")
            # 
            # logger.info(f"🔒 Session lock updated with message ID: {session_id} → {analysis_message_id}")
            
            # Step 6: Log initial progress to message
            # TODO: We have confusing progress_info (one is memory SSE and other is queue based SSE)
            # We need to either rename or do sthg
            
            # Step 7: Queue analysis for worker processing
            job_id = await analysis_queue.enqueue_analysis({
                "session_id": session_id,
                "message_id": analysis_message_id,
                "user_question": user_question,
                "user_message_id": user_message_id,
                "user_id": user_id
            })
            await send_progress_info(session_id, "Analysis queued for processing")
            logger.info(f"📥 Queued analysis job: {job_id} for message {analysis_message_id}")
            
            # Step 8: Create minimal message structure and transform to UI format
            # Since get_message doesn't exist, we'll create the minimal structure needed for transformation
            message_for_transform = {
                "messageId": analysis_message_id,
                "role": "assistant",
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "status": MessageStatus.PENDING,
                    "user_message_id": user_message_id,
                    "job_id": job_id,
                    "queued_at": datetime.now().isoformat(),
                    "response_type": "script_generation"
                }
            }
            
            if self.data_transformer:
                clean_msg = await self.data_transformer.transform_message_to_ui_data(message_for_transform)
            else:
                # Fallback for cases where transformer is unavailable
                clean_msg = {
                    "message_id": analysis_message_id,
                    "user_message_id": user_message_id,
                    "job_id": job_id,
                    "status": MessageStatus.PENDING,
                    "queued_at": datetime.now().isoformat()
                }
            
            # Step 9: Return immediately with pending status and consistent UI format
            return AnalysisResponse(
                success=True,
                data={
                    **clean_msg,  # Use transformer-generated UI data for consistency
                    "session_id": session_id,
                    "user_id": user_id
                },
                timestamp=datetime.now().isoformat()
            )
                
        except HTTPException:
            # Re-raise HTTPExceptions as-is
            raise
        except Exception as e:
            logger.error(f"❌ Async analysis endpoint error: {e}", exc_info=True)
            
            # Release lock if we acquired it
            try:
                from shared.locking import get_session_lock
                session_lock = get_session_lock()
                await session_lock.release_lock(session_id)
                logger.info(f"🔓 Released session lock on error: {session_id}")
            except Exception as lock_error:
                logger.warning(f"⚠️ Failed to release lock on error: {lock_error}")
            
            return await self._error_response(
                user_message="We ran into an issue and couldn't queue your analysis. Please try again.",
                internal_error=str(e),
                session_id=session_id,
                user_id=user_id
            )
    
    async def chat_with_analysis(self, request: QuestionRequest) -> AnalysisResponse:
        """
        Hybrid chat + analysis endpoint (GitHub Issue #122) - FIXED VERSION
        
        Uses the corrected V2 hybrid handler that:
        1. Returns chat response immediately
        2. Flags when analysis should be triggered
        3. Uses existing analyze_question() flow instead of manual queueing
        4. Follows proper BaseService patterns
        """
        user_id = request.user_id if hasattr(request, 'user_id') and request.user_id else "anonymous"
        session_id = request.session_id
        user_message = request.question
        
        try:
            logger.info(f"💬📊 Hybrid chat V2 request: {user_message[:100]}...")
            
            # Validate session
            if not session_id:
                logger.error(f"❌ No session_id provided in hybrid request")
                raise HTTPException(400, "Session ID is required. Please start a new conversation.")
            
            # Check if hybrid handler is available
            if not self.hybrid_handler:
                logger.error("❌ Hybrid message handler not initialized")
                raise HTTPException(500, "Chat functionality is currently unavailable")
            
            # Process message through hybrid handler V2
            start_time = time.time()
            hybrid_response = await self.hybrid_handler.handle_message(
                user_message=user_message,
                session_id=session_id,
                user_id=user_id
            )
            processing_time = time.time() - start_time
            
            logger.info(f"⏱️ Hybrid V2 processing: {processing_time:.3f}s, Type: {hybrid_response.response_type}")
            
            # Create base response data from hybrid response
            response_data = {
                "message_id": hybrid_response.message_id,
                "session_id": session_id,
                "content": hybrid_response.content,
                "response_type": hybrid_response.response_type,
                "metadata": hybrid_response.metadata or {}
            }
            
            # Check if analysis should be triggered (FIXED APPROACH)
            if hybrid_response.should_trigger_analysis and hybrid_response.analysis_question:
                logger.info(f"🔄 Triggering analysis internally: {hybrid_response.analysis_question[:50]}...")
                
                # Create analysis request for internal call to existing analyze_question()
                analysis_request = QuestionRequest(
                    question=hybrid_response.analysis_question,
                    session_id=session_id,
                    user_id=user_id
                )
                # Mark as background analysis to avoid creating duplicate messages
                analysis_request._from_hybrid_background = True
                analysis_request._hybrid_assistant_message_id = hybrid_response.message_id
                
                # Trigger analysis using existing flow (background - no await)
                # This ensures chat response returns immediately while analysis runs
                try:
                    asyncio.create_task(
                        self._trigger_background_analysis(analysis_request, hybrid_response.message_id)
                    )
                    logger.info(f"✅ Background analysis triggered for question: {hybrid_response.analysis_question[:50]}...")
                    
                    # Update metadata to indicate analysis was triggered
                    response_data["metadata"]["analysis_triggered"] = True
                    response_data["metadata"]["analysis_question"] = hybrid_response.analysis_question
                    
                except Exception as background_error:
                    logger.error(f"❌ Failed to trigger background analysis: {background_error}")
                    response_data["metadata"]["analysis_trigger_failed"] = True
                    response_data["metadata"]["analysis_error"] = str(background_error)
            
            # Always return chat response immediately (KEY CHANGE)
            return AnalysisResponse(
                success=True,
                data=response_data,
                timestamp=datetime.now().isoformat()
            )
        
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"❌ Hybrid chat V2 error: {e}")
            # Ensure error is saved to chat history
            await self._ensure_error_saved(user_message, session_id, user_id)
            
            return await self._error_response(
                user_message="I apologize, but I encountered an error. Please try again.",
                internal_error=str(e),
                session_id=session_id,
                user_id=user_id
            )
    
    async def _trigger_background_analysis(self, analysis_request: QuestionRequest, chat_message_id: str):
        """
        Background task to trigger analysis using existing analyze_question() flow
        
        This allows chat response to return immediately while analysis runs in background
        """
        try:
            logger.info(f"🔄 Starting background analysis for: {analysis_request.question[:50]}...")
            
            # Call existing analyze_question method internally
            analysis_response = await self.analyze_question(analysis_request)
            
            if analysis_response.success:
                logger.info(f"✅ Background analysis completed successfully")
                # Analysis progress and results will be sent via existing SSE system
                
            else:
                logger.error(f"❌ Background analysis failed: {analysis_response.error}")
                # Send error via SSE
                await send_execution_failed(f"Analysis failed: {analysis_response.error}")
                
        except Exception as e:
            logger.error(f"❌ Background analysis exception: {e}")
            # Send error via SSE
            await send_execution_failed(f"Analysis error: {e}")
    
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
            from shared.analyze.dialogue import get_dialogue_factory
            
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
            from shared.analyze.dialogue import get_dialogue_factory
            
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
    
