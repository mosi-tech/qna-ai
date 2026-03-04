#!/usr/bin/env python3
"""
Hybrid Message Handler V2

FIXED VERSION - Routes user messages between chat and analysis using:
1. Intent Classification Service (proper BaseService)
2. Financial Analyst Chat Service (proper BaseService)  
3. Existing analyze_question flow (no manual queueing)

Implements GitHub Issue #122 - Mix of LLM chat + analysis
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from shared.services.progress_service import send_progress_event

# Set PRE_QUEUE_PROGRESS_LOGS=true in the environment to stream pre-queue step
# events to the SSE progress panel (useful in dev; off by default in prod).
_PRE_QUEUE_LOGS = os.getenv("PRE_QUEUE_PROGRESS_LOGS", "false").lower() == "true"


async def _dev_log(session_id: str, message: str, level: str = "info") -> None:
    """Emit a progress event only when PRE_QUEUE_PROGRESS_LOGS is enabled."""
    if not (_PRE_QUEUE_LOGS and session_id):
        return
    try:
        await send_progress_event(session_id, {
            "type": "progress",
            "level": level,
            "message": message,
        })
    except Exception:
        pass  # never block the main flow

from .intent_classifier import IntentClassifierService, IntentResult
from .financial_analyst_chat_service import FinancialAnalystChatService, AnalystResponse, AnalysisSuggestion
from shared.services.chat_service import ChatHistoryService
from shared.services.session_manager import SessionManager
from shared.constants import MetadataConstants, MessageIntent
from shared.security.input_validator import InputValidator

logger = logging.getLogger(__name__)

@dataclass 
class HybridResponse:
    """Response from hybrid message handler"""
    response_type: str  # "chat", "educational_chat", "analysis_confirmation", "analysis_trigger"
    content: str
    message_id: str
    session_id: str
    user_message_id: Optional[str] = None  # None for early-exit error responses (before user msg is saved)
    metadata: Optional[Dict[str, Any]] = None
    
    # Analysis triggering (NEW approach - calls existing analyze_question)
    should_trigger_analysis: bool = False
    analysis_question: Optional[str] = None

class HybridMessageHandler:
    """
    FIXED: Intelligent message router with proper services and existing analysis flow
    """
    
    def __init__(self, 
                 chat_history_service: ChatHistoryService,
                 analyze_question_callable=None,
                 redis_client=None):
        self.chat_history_service = chat_history_service
        self.analyze_question_callable = analyze_question_callable
        
        # Create SessionManager for ConversationStore integration (consistent with existing approach)
        self.session_manager = SessionManager(
            chat_history_service=chat_history_service,
            redis_client=redis_client
        )
        
        # Initialize proper services with session manager dependency
        self.intent_classifier = IntentClassifierService(session_manager=self.session_manager)
        self.financial_analyst = FinancialAnalystChatService()
        
        # Track session state for pending analysis suggestions
        self.session_states = {}  # session_id -> state info
        
        logger.info("✅ Hybrid message handler V2 initialized with proper services and session manager")
        
    async def handle_message(self, 
                           user_message: str,
                           session_id: str,
                           user_id: str = "anonymous") -> HybridResponse:
        """
        Main entry point - FIXED APPROACH:
        1. Classify intent with proper service
        2. Generate analyst response with proper service  
        3. Add chat message to history
        4. If analysis needed: trigger existing analyze_question + return chat message
        5. Otherwise: return chat response only
        """
        start_time = time.time()
        placeholder_id = None
        try:
            logger.info(f"🔀 Hybrid handler V2 processing: {user_message[:100]}...")
            
            # Step 0: Input validation - reject malformed/dangerous input early
            await _dev_log(session_id, "Validating input...")
            is_safe, validation_error = InputValidator.is_safe(user_message)
            if not is_safe:
                logger.error(f"🛡️ Input validation failed: {validation_error}")
                return await self._create_error_response(
                    error_message="Invalid input. Please check your message and try again.",
                    session_id=session_id,
                    user_id=user_id,
                    internal_error=validation_error,
                    start_time=start_time
                )
            
            # Validate session ID and user ID format
            if not InputValidator.validate_session_id(session_id):
                logger.error(f"🛡️ Invalid session ID format")
                return await self._create_error_response(
                    error_message="Invalid session ID. Please try again.",
                    session_id=session_id,
                    user_id=user_id,
                    internal_error="Invalid session ID format",
                    start_time=start_time
                )
            
            # Step 0.5: Save user message immediately (independent of assistant response)
            await _dev_log(session_id, "Saving message to history...")
            conversation = await self.session_manager.get_session(session_id)
            user_message_obj = await conversation.add_user_message(
                content=user_message,
                user_id=user_id
            )
            logger.debug(f"✅ User message saved immediately: {user_message_obj.id}")

            # Step 0.75: Write an AI placeholder BEFORE any LLM calls so that a page
            # refresh during classification/generation still finds a pending message.
            placeholder_obj = await conversation.add_assistant_message(
                content="",
                user_id=user_id,
                status=MetadataConstants.STATUS_PENDING,
                response_type=MetadataConstants.RESPONSE_TYPE_ANALYSIS,
            )
            placeholder_id = placeholder_obj.id
            logger.debug(f"✅ AI placeholder saved immediately: {placeholder_id}")

            # Step 1: Classify intent
            await _dev_log(session_id, "Classifying intent...")
            intent_start_time = time.time()
            intent_result = await self.intent_classifier.classify_intent(
                user_message=user_message,
                session_id=session_id
            )
            intent_duration = time.time() - intent_start_time
            await _dev_log(session_id, f"Intent: {intent_result.intent.value} ({intent_duration:.1f}s)")
            logger.info(f"⏱️ Intent classification: {intent_duration:.3f}s, Intent: {intent_result.intent.value}")
            
            # Step 1.5: Safety check - reject dangerous queries early
            if not intent_result.is_safe:
                logger.error(f"🚨 SECURITY: Blocking unsafe query - {intent_result.safety_reason}")
                return await self._create_safety_error_response(
                    safety_reason=intent_result.safety_reason,
                    detected_risks=intent_result.detected_risks,
                    session_id=session_id,
                    user_id=user_id,
                    user_message_obj=user_message_obj,
                    start_time=intent_start_time
                )
            
            # Step 2: Generate analyst response
            await _dev_log(session_id, "Generating analyst response...")
            start_time = time.time()
            analyst_response = await self.financial_analyst.generate_response(
                user_message=user_message,
                intent_result=intent_result,
                session_id=session_id,
                session_manager=self.session_manager
            )
            analyst_duration = time.time() - start_time
            await _dev_log(session_id, f"Response ready ({analyst_duration:.1f}s) — queuing analysis...")
            logger.info(f"⏱️ Analyst response: {analyst_duration:.3f}s")
            
            # Step 3: Route based on intent and update the placeholder with real content
            return await self._route_and_persist(
                intent_result=intent_result,
                analyst_response=analyst_response,
                user_message=user_message,
                session_id=session_id,
                user_id=user_id,
                user_message_obj=user_message_obj,
                placeholder_id=placeholder_id,
            )
            
        except Exception as e:
            logger.error(f"❌ Hybrid handler V2 error: {e}")
            # If a placeholder was already written to DB, update it to failed
            # instead of orphaning it as perpetually-pending.
            if placeholder_id:
                try:
                    conv = await self.session_manager.get_session(session_id)
                    await conv.update_assistant_message(
                        message_id=placeholder_id,
                        content="I encountered an error processing your message. Please try again.",
                        status=MetadataConstants.STATUS_FAILED,
                    )
                    return HybridResponse(
                        response_type=MetadataConstants.RESPONSE_TYPE_CHAT,
                        content="I encountered an error processing your message. Please try again.",
                        message_id=placeholder_id,
                        user_message_id=None,
                        session_id=session_id,
                        metadata={MetadataConstants.RESPONSE_STATUS: MetadataConstants.STATUS_FAILED},
                        should_trigger_analysis=False,
                        analysis_question=None,
                    )
                except Exception as inner_e:
                    logger.error(f"❌ Failed to update placeholder to failed: {inner_e}")
            return await self._create_error_response(
                error_message=f"I apologize, but I encountered an error processing your message. Please try again.",
                session_id=session_id,
                user_id=user_id,
                internal_error=str(e),
                start_time=start_time
            )
    
    async def _route_and_persist(self,
                               intent_result: IntentResult,
                               analyst_response: AnalystResponse,
                               user_message: str,
                               session_id: str,
                               user_id: str,
                               user_message_obj,
                               placeholder_id: str = None) -> HybridResponse:
        """Route based on intent and persist ONLY via ConversationStore (no dual calls)"""
        
        # Use the intent directly from IntentResult (already a MessageIntent enum)
        message_intent = intent_result.intent
        
        # Determine response type and analysis trigger
        if intent_result.intent.value == MetadataConstants.INTENT_ANALYSIS_CONFIRMATION:
            response_type = MetadataConstants.RESPONSE_TYPE_ANALYSIS
            triggered_analysis = True
        elif intent_result.intent.value == MetadataConstants.INTENT_ANALYSIS_REQUEST:
            response_type = MetadataConstants.RESPONSE_TYPE_ANALYSIS
            triggered_analysis = True
        elif intent_result.intent.value == MetadataConstants.INTENT_FOLLOW_UP_ANALYSIS:
            response_type = MetadataConstants.RESPONSE_TYPE_ANALYSIS
            triggered_analysis = True
        elif intent_result.intent.value == MetadataConstants.INTENT_FOLLOW_UP_CHAT:
            response_type = MetadataConstants.RESPONSE_TYPE_CHAT
            triggered_analysis = False
        else:
            response_type = intent_result.intent.value.replace('_', '_').lower()
            triggered_analysis = False
        
        # Build complete metadata first
        metadata = {
            MetadataConstants.INTENT: intent_result.intent.value,
            MetadataConstants.RESPONSE_TYPE: response_type,
            MetadataConstants.MESSAGE_TYPE: response_type,
            MetadataConstants.ANALYSIS_TRIGGERED: triggered_analysis,
        }
        
        
        if analyst_response.analysis_suggestion:
            metadata[MetadataConstants.HAS_ANALYSIS_SUGGESTION] = True
            metadata[MetadataConstants.SUGGESTED_ANALYSIS] = {
                MetadataConstants.SUGGESTION_TOPIC: analyst_response.analysis_suggestion.topic,
                MetadataConstants.SUGGESTION_DESCRIPTION: analyst_response.analysis_suggestion.description
            }
            metadata[MetadataConstants.ANALYSIS_SUGGESTION] = analyst_response.analysis_suggestion.__dict__
        
        # Determine analysis triggering details
        should_trigger_analysis = triggered_analysis
        analysis_question = None
        
        if triggered_analysis:
            metadata[MetadataConstants.RESPONSE_STATUS] = MetadataConstants.STATUS_PENDING
            # For analysis_request and follow_up_analysis: use original user message as analysis question
            # For analysis_confirmation: get pending analysis suggestion
            if intent_result.intent.value in [
                MetadataConstants.INTENT_ANALYSIS_REQUEST, 
                MetadataConstants.INTENT_FOLLOW_UP_ANALYSIS
            ]:
                analysis_question = user_message
                metadata[MetadataConstants.ANALYSIS_QUESTION] = user_message
            else:
                # For analysis_confirmation: use pending suggestion
                conversation = await self.session_manager.get_session(session_id)
                if conversation:
                    pending = await conversation.get_pending_analysis_suggestion()
                    if pending:
                        analysis_question = pending.get(MetadataConstants.SUGGESTED_QUESTION, "Analysis in progress...")
                        metadata[MetadataConstants.ANALYSIS_QUESTION] = analysis_question

                # Fallback: no stored suggestion (e.g. prior turn errored, page
                # reload, or suggestion expired in Redis).  Try to recover the
                # original question from recent message history so the user's
                # confirmation still fires the analysis instead of being silently dropped.
                if not analysis_question:
                    analysis_question = await self._recover_analysis_question(session_id, user_message)
                    if analysis_question:
                        metadata[MetadataConstants.ANALYSIS_QUESTION] = analysis_question
                        logger.warning(
                            "⚠️ No pending suggestion found for session %s — "
                            "recovered analysis question from history: %s",
                            session_id, analysis_question[:80]
                        )
                    else:
                        logger.error(
                            "❌ analysis_confirmation but could not determine analysis question "
                            "(no pending suggestion, no substantive prior message). "
                            "Dropping analysis trigger for session %s.", session_id
                        )
        else:
            # For non-analysis responses, mark as completed
            metadata[MetadataConstants.RESPONSE_STATUS] = MetadataConstants.STATUS_COMPLETED
        
        # Update the pre-written placeholder with real content + metadata.
        # If no placeholder (e.g. called from error recovery path), create fresh.
        conversation = await self.session_manager.get_session(session_id)
        if placeholder_id:
            await conversation.update_assistant_message(
                message_id=placeholder_id,
                content=analyst_response.content,
                **metadata
            )
            final_message_id = placeholder_id
        else:
            assistant_message_obj = await conversation.add_assistant_message(
                content=analyst_response.content,
                user_id=user_id,
                **metadata
            )
            final_message_id = assistant_message_obj.id

        return HybridResponse(
            response_type=response_type,
            content=analyst_response.content,
            message_id=final_message_id,
            user_message_id=user_message_obj.id,
            session_id=session_id,
            metadata=metadata,
            should_trigger_analysis=should_trigger_analysis,
            analysis_question=analysis_question
        )

    
    async def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get session context including recent analysis results"""
        context = {}
        
        try:
            # Get recent messages to understand context
            if self.chat_history_service:
                recent_messages = await self.chat_history_service.get_messages(
                    session_id=session_id,
                    limit=10
                )
                
                # Look for recent analysis in messages
                for message in recent_messages:
                    if (message.get("metadata", {}).get("response_type") in ["script_generation", "reuse_decision"] and 
                        message.get("analysisId")):
                        context["last_analysis"] = {
                            "id": message.get("analysisId"),
                            "description": message.get("content", ""),
                            "timestamp": message.get("createdAt")
                        }
                        break
            
            # Add session state if exists
            if session_id in self.session_states:
                context["session_state"] = self.session_states[session_id]
            
        except Exception as e:
            logger.warning(f"Could not get session context: {e}")
        
        return context
    

    async def _get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get recent conversation history for context"""
        try:
            if not self.chat_history_service:
                return []
            
            recent_messages = await self.chat_history_service.get_messages(
                session_id=session_id,
                limit=12
            )
            
            # Format for LLM context
            history = []
            for msg in recent_messages:
                role = "user" if msg.get("role") == "user" else "assistant"
                content = msg.get("content", "")
                if content:
                    history.append({"role": role, "content": content})
            
            return history
            
        except Exception as e:
            logger.warning(f"Could not get conversation history: {e}")
            return []
    
    async def _create_error_response(self, 
                                   error_message: str, 
                                   session_id: str,
                                   user_id: str,
                                   internal_error: str = None,
                                   start_time: float = None) -> HybridResponse:
        """Create error response"""
        error_metadata = {
            MetadataConstants.RESPONSE_STATUS: MetadataConstants.STATUS_FAILED,
            MetadataConstants.RESPONSE_ERROR: error_message,
            MetadataConstants.INTERNAL_ERROR: internal_error or "Unknown error",
            MetadataConstants.PROCESSING_TIME: (time.time() - start_time) if start_time else None,
            MetadataConstants.FAILED_AT: datetime.now().isoformat()
        }
        try:
            # Insert a fresh error message.
            error_message_id = await self.chat_history_service.add_hybrid_message(
                session_id=session_id,
                user_id=user_id,
                content=error_message,
                message_type=MetadataConstants.MESSAGE_TYPE_ERROR,
                intent=MetadataConstants.INTENT_ERROR
            )
            return HybridResponse(
                response_type=MetadataConstants.RESPONSE_TYPE_ERROR,
                content=error_message,
                message_id=error_message_id,
                session_id=session_id,
                metadata=error_metadata
            )
        except Exception as e:
            logger.error(f"Failed to create error response: {e}")
            return HybridResponse(
                response_type=MetadataConstants.RESPONSE_TYPE_ERROR,
                content=error_message,
                message_id="error",
                session_id=session_id,
                metadata={
                    MetadataConstants.RESPONSE_STATUS: MetadataConstants.STATUS_FAILED,
                    MetadataConstants.RESPONSE_ERROR: f"Failed to save chat message: {error_message}",
                    MetadataConstants.INTERNAL_ERROR: internal_error or "Unknown error",
                    MetadataConstants.PROCESSING_TIME: (time.time() - start_time) if start_time else None,
                    MetadataConstants.FAILED_AT: datetime.now().isoformat()
                }
            )
    
    async def _create_safety_error_response(self,
                                          safety_reason: str,
                                          detected_risks: List[str],
                                          session_id: str,
                                          user_id: str,
                                          user_message_obj,
                                          start_time: float = None) -> HybridResponse:
        """Create security error response for blocked queries."""
        error_message = "Sorry, I can't help you with that. Please ask a legitimate financial analysis question."
        blocked_metadata = {
            MetadataConstants.RESPONSE_STATUS: MetadataConstants.STATUS_BLOCKED,
            MetadataConstants.RESPONSE_ERROR: error_message,
            MetadataConstants.SECURITY_REASON: safety_reason,
            MetadataConstants.DETECTED_RISKS: detected_risks,
            MetadataConstants.PROCESSING_TIME: (time.time() - start_time) if start_time else None,
            MetadataConstants.BLOCKED_AT: datetime.now().isoformat()
        }
        try:
            error_message_id = await self.chat_history_service.add_hybrid_message(
                session_id=session_id,
                user_id=user_id,
                content=error_message,
                message_type=MetadataConstants.MESSAGE_TYPE_ERROR,
                intent=MetadataConstants.INTENT_ERROR
            )
            return HybridResponse(
                response_type=MetadataConstants.RESPONSE_TYPE_ERROR,
                content=error_message,
                message_id=error_message_id,
                user_message_id=user_message_obj.id,
                session_id=session_id,
                metadata=blocked_metadata
            )
        except Exception as e:
            logger.error(f"Failed to create safety error response: {e}")
            return HybridResponse(
                response_type=MetadataConstants.RESPONSE_TYPE_ERROR,
                content=error_message,
                message_id="blocked",
                user_message_id=user_message_obj.id if user_message_obj else "unknown",
                session_id=session_id,
                metadata={
                    MetadataConstants.RESPONSE_STATUS: MetadataConstants.STATUS_BLOCKED,
                    MetadataConstants.SECURITY_REASON: safety_reason,
                    MetadataConstants.DETECTED_RISKS: detected_risks,
                    MetadataConstants.PROCESSING_TIME: (time.time() - start_time) if start_time else None,
                    MetadataConstants.BLOCKED_AT: datetime.now().isoformat()
                }
            )
    
    # Short affirmation words that are NOT standalone analysis questions.
    # When the user says "Yes" / "OK" / "sure", we look *past* that message.
    _AFFIRMATION_WORDS = frozenset([
        "yes", "yeah", "yep", "yup", "sure", "ok", "okay", "go", "go ahead",
        "run", "run it", "do it", "proceed", "start", "please", "now",
        "great", "sounds good", "let's do it", "lets do it",
    ])

    async def _recover_analysis_question(self, session_id: str, current_message: str) -> Optional[str]:
        """
        Scan the last N MongoDB messages to find the most recent user message
        that looks like a genuine analysis question (not a one-word confirmation).

        Used as a fallback when `analysis_confirmation` fires but there is no
        pending suggestion stored in the ConversationStore.
        """
        try:
            if not self.chat_history_service:
                return None

            recent = await self.chat_history_service.get_messages(
                session_id=session_id, limit=15
            )

            for msg in reversed(recent):
                role = msg.get("role", "")
                content = (msg.get("content") or "").strip()
                if role != "user" or not content:
                    continue
                # Skip the current confirmation turn itself and pure affirmations
                if content.lower().rstrip("!.") in self._AFFIRMATION_WORDS:
                    continue
                if content == current_message.strip():
                    continue
                # Minimum plausible question length
                if len(content) >= 10:
                    return content
        except Exception as e:
            logger.warning("Could not recover analysis question from history: %s", e)
        return None

    async def _get_pending_analysis_from_conversation_store(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get pending analysis suggestion from ConversationStore (persistent across restarts)
        
        Uses ConversationStore's centralized method for consistency.
        """
        try:
            logger.info(f"🔍 Looking for pending analysis in ConversationStore for session {session_id}")
            
            # Get conversation from session manager
            conversation = await self.session_manager.get_session(session_id)
            if not conversation:
                logger.info(f"⚠️ No conversation found for session {session_id}")
                return None
            
            # Use ConversationStore's centralized method
            pending_analysis = conversation.get_pending_analysis_suggestion()
            
            if pending_analysis:
                logger.info(f"✅ Found pending analysis suggestion: {pending_analysis.get('topic', 'unknown')}")
            else:
                logger.info(f"⚠️ No pending analysis found in ConversationStore for session {session_id}")
            
            return pending_analysis
                
        except Exception as e:
            logger.error(f"❌ Error getting pending analysis from ConversationStore: {e}")
            return None

    def cleanup_session_state(self, session_id: str):
        """Clean up session state when session ends"""
        if session_id in self.session_states:
            del self.session_states[session_id]
            logger.debug(f"Cleaned up session state for {session_id}")
    
    async def _save_conversation_messages(self,
                                        session_id: str,
                                        user_message: str,
                                        user_id: str,
                                        assistant_response: str,
                                        message_intent,
                                        response_type: str,
                                        triggered_analysis: bool = False,
                                        analysis_suggestion: Optional[Dict[str, Any]] = None):
        """Save conversation messages independently using new message-based API"""
        try:
            # Get conversation store (load_or_create ensures we always get a store)
            conversation = await self.session_manager.get_session(session_id)
            
            # Add user and assistant messages independently (new message-based API)
            await conversation.add_conversation_exchange(
                user_content=user_message,
                assistant_content=assistant_response,
                user_id=user_id,
                # Assistant metadata
                message_type=response_type,
                intent=message_intent.value if message_intent else None,
                analysis_triggered=triggered_analysis,
                analysis_suggestion=analysis_suggestion,
                has_analysis_suggestion=bool(analysis_suggestion)
            )
            
            logger.debug(f"💾 Saved independent messages for session {session_id}: {message_intent.value if message_intent else 'unknown'}")
        except Exception as e:
            logger.error(f"❌ Failed to save conversation messages for session {session_id}: {e}")