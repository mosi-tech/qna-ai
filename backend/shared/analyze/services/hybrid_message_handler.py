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
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .intent_classifier import IntentClassifierService, MessageIntent, IntentResult
from .financial_analyst_chat_service import FinancialAnalystChatService, AnalystResponse, AnalysisSuggestion
from shared.services.chat_service import ChatHistoryService

logger = logging.getLogger(__name__)

@dataclass 
class HybridResponse:
    """Response from hybrid message handler"""
    response_type: str  # "chat", "educational_chat", "analysis_confirmation", "analysis_trigger"
    content: str
    message_id: str
    session_id: str
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
                 analyze_question_callable=None):
        self.chat_history_service = chat_history_service
        self.analyze_question_callable = analyze_question_callable
        
        # Create SessionManager for ConversationStore integration (consistent with existing approach)
        from shared.analyze.dialogue.conversation.session_manager import SessionManager
        self.session_manager = SessionManager(chat_history_service=chat_history_service)
        
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
        try:
            logger.info(f"🔀 Hybrid handler V2 processing: {user_message[:100]}...")
            
            # Step 0: Save user message immediately (independent of assistant response)
            conversation = await self.session_manager.get_session(session_id)
            user_message_obj = await conversation.add_user_message(
                content=user_message,
                user_id=user_id
            )
            logger.debug(f"✅ User message saved immediately: {user_message_obj.id}")
            
            # Step 1: Classify intent
            start_time = time.time()
            intent_result = await self.intent_classifier.classify_intent(
                user_message=user_message,
                session_id=session_id
            )
            intent_duration = time.time() - start_time
            
            logger.info(f"⏱️ Intent classification: {intent_duration:.3f}s, Intent: {intent_result.intent.value}")
            
            # Step 2: Generate analyst response
            start_time = time.time()
            analyst_response = await self.financial_analyst.generate_response(
                user_message=user_message,
                intent_result=intent_result,
                session_id=session_id,
                session_manager=self.session_manager
            )
            analyst_duration = time.time() - start_time
            
            logger.info(f"⏱️ Analyst response: {analyst_duration:.3f}s")
            
            # Step 3: Route based on intent and persist ONLY via ConversationStore
            return await self._route_and_persist(
                intent_result=intent_result,
                analyst_response=analyst_response,
                user_message=user_message,
                session_id=session_id,
                user_id=user_id,
                user_message_obj=user_message_obj
            )
            
        except Exception as e:
            logger.error(f"❌ Hybrid handler V2 error: {e}")
            return await self._create_error_response(
                error_message=f"I apologize, but I encountered an error processing your message. Please try again.",
                session_id=session_id,
                user_id=user_id
            )
    
    async def _route_and_persist(self,
                               intent_result: IntentResult,
                               analyst_response: AnalystResponse,
                               user_message: str,
                               session_id: str,
                               user_id: str,
                               user_message_obj) -> HybridResponse:
        """Route based on intent and persist ONLY via ConversationStore (no dual calls)"""
        from shared.analyze.dialogue.conversation.store import MessageIntent
        
        # Map IntentResult.intent to MessageIntent
        message_intent_map = {
            'pure_chat': MessageIntent.PURE_CHAT,
            'educational': MessageIntent.EDUCATIONAL,
            'analysis_request': MessageIntent.ANALYSIS_REQUEST,
            'analysis_confirmation': MessageIntent.ANALYSIS_CONFIRMATION,
            'follow_up': MessageIntent.FOLLOW_UP
        }
        message_intent = message_intent_map.get(intent_result.intent.value, MessageIntent.PURE_CHAT)
        
        # Determine response type and analysis trigger
        if intent_result.intent.value == "analysis_confirmation":
            response_type = "analysis_trigger"
            triggered_analysis = True
        else:
            response_type = intent_result.intent.value.replace('_', '_').lower()
            triggered_analysis = False
        
        # Save assistant message independently (user message already saved immediately)
        conversation = await self.session_manager.get_session(session_id)
        assistant_message_obj = await conversation.add_assistant_message(
            content=analyst_response.content,
            user_id=user_id,
            message_type=response_type,
            intent=message_intent.value if message_intent else None,
            analysis_triggered=triggered_analysis,
            analysis_suggestion=analyst_response.analysis_suggestion.__dict__ if analyst_response.analysis_suggestion else None
        )
        
        # Build metadata for response
        metadata = {
            "intent": intent_result.intent.value,
            "message_type": response_type,
        }
        
        if analyst_response.analysis_suggestion:
            metadata["has_analysis_suggestion"] = True
            metadata["suggested_analysis"] = {
                "topic": analyst_response.analysis_suggestion.topic,
                "description": analyst_response.analysis_suggestion.description
            }
        
        if triggered_analysis:
            metadata["analysis_triggered"] = True
            # Get pending analysis for the expanded question
            conversation = await self.session_manager.get_session(session_id)
            if conversation:
                pending = await conversation.get_pending_analysis_suggestion()
                if pending:
                    metadata["analysis_question"] = pending.get("suggested_question", "Analysis in progress...")
        
        return HybridResponse(
            response_type=response_type,
            content=analyst_response.content,
            message_id=assistant_message_obj.id,
            session_id=session_id,
            metadata=metadata
        )

    async def _route_based_on_intent(self,
                                   intent_result: IntentResult,
                                   analyst_response: AnalystResponse,
                                   user_message: str,
                                   session_id: str,
                                   user_id: str) -> HybridResponse:
        """
        FIXED: Route based on intent using existing analyze_question flow
        """
        
        # Route to appropriate handler based on intent
        if intent_result.intent == MessageIntent.PURE_CHAT:
            return await self._handle_pure_chat(
                analyst_response, session_id, user_id, user_message_obj.id
            )
                
        elif intent_result.intent == MessageIntent.EDUCATIONAL:
            return await self._handle_educational_response(
                analyst_response, intent_result, user_message, session_id, user_id, user_message_obj.id
            )
                
        elif intent_result.intent == MessageIntent.ANALYSIS_REQUEST:
            return await self._handle_analysis_request(
                analyst_response, user_message, session_id, user_id, user_message_obj.id
            )
                
        elif intent_result.intent == MessageIntent.ANALYSIS_CONFIRMATION:
            return await self._handle_analysis_confirmation(
                analyst_response, session_id, user_id, user_message_obj.id
            )
                
        elif intent_result.intent == MessageIntent.FOLLOW_UP:
            return await self._handle_follow_up_response(
                analyst_response, session_id, user_id, user_message_obj.id
            )
        
        else:
            # Default to educational chat
            return await self._handle_educational_response(
                analyst_response, intent_result, user_message, session_id, user_id, user_message_obj.id
            )
    
    async def _handle_pure_chat(self, 
                              analyst_response: AnalystResponse,
                              session_id: str,
                              user_id: str,
                              user_message_id: str) -> HybridResponse:
        """Handle pure chat interactions (greetings, thanks, etc.)"""
        
        # Add chat response to history using hybrid method
        assistant_message_id = await self.chat_history_service.add_hybrid_message(
            session_id=session_id,
            user_id=user_id,
            content=analyst_response.content,
            message_type="chat",
            intent="pure_chat",
            in_reply_to=user_message_id
        )
        
        return HybridResponse(
            response_type="chat",
            content=analyst_response.content,
            message_id=assistant_message_id,
            session_id=session_id,
            metadata={"intent": "pure_chat"}
        )
    
    async def _handle_educational_response(self,
                                         analyst_response: AnalystResponse,
                                         intent_result: IntentResult,
                                         user_message: str,
                                         session_id: str,
                                         user_id: str,
                                         user_message_id: str) -> HybridResponse:
        """Handle educational responses with potential analysis suggestions"""
        
        # Analysis suggestion is automatically persisted in message metadata (line 231)
        # No need for volatile session state - we can reconstruct from conversation history
        if analyst_response.analysis_suggestion:
            logger.info(f"✅ Analysis suggestion will be persisted in message metadata for session {session_id}: {analyst_response.analysis_suggestion.topic}")
        else:
            logger.warning(f"⚠️ No analysis suggestion provided by financial analyst for session {session_id}")
        
        # Prepare analysis suggestion data for metadata
        suggestion_data = None
        if analyst_response.analysis_suggestion:
            suggestion_data = {
                "topic": analyst_response.analysis_suggestion.topic,
                "description": analyst_response.analysis_suggestion.description,
                "suggested_question": analyst_response.analysis_suggestion.suggested_question,
                "analysis_type": analyst_response.analysis_suggestion.analysis_type
            }
        
        # Add educational response to history
        assistant_message_id = await self.chat_history_service.add_hybrid_message(
            session_id=session_id,
            user_id=user_id,
            content=analyst_response.content,
            message_type="educational_chat",
            intent="educational",
            analysis_suggestion=suggestion_data,
            in_reply_to=user_message_id
        )
        
        # Update ConversationStore with hybrid turn
        await self._save_hybrid_turn(
            session_id=session_id,
            user_query=user_message,
            message_intent=intent_result.intent,
            response_type="educational_chat", 
            assistant_response=analyst_response.content,
            triggered_analysis=False,
            analysis_suggestion=suggestion_data
        )
        
        metadata = {
            "intent": "educational",
            "has_analysis_suggestion": bool(analyst_response.analysis_suggestion)
        }
        
        if suggestion_data:
            metadata["suggested_analysis"] = {
                "topic": suggestion_data["topic"],
                "description": suggestion_data["description"]
            }
        
        return HybridResponse(
            response_type="educational_chat",
            content=analyst_response.content,
            message_id=assistant_message_id,
            session_id=session_id,
            metadata=metadata
        )
    
    async def _handle_analysis_request(self,
                                     analyst_response: AnalystResponse,
                                     user_message: str,
                                     session_id: str,
                                     user_id: str,
                                     user_message_id: str) -> HybridResponse:
        """Handle direct analysis requests - FIXED: uses existing flow"""
        
        # Add confirmation message to chat
        assistant_message_id = await self.chat_history_service.add_hybrid_message(
            session_id=session_id,
            user_id=user_id,
            content=analyst_response.content,
            message_type="analysis_confirmation",
            intent="analysis_request",
            in_reply_to=user_message_id
        )
        
        # FIXED: Return chat response + flag to trigger analysis
        return HybridResponse(
            response_type="analysis_trigger",
            content=analyst_response.content,
            message_id=assistant_message_id,
            session_id=session_id,
            should_trigger_analysis=True,  # KEY: Flag for API to call analyze_question
            analysis_question=user_message,  # Original user question
            metadata={"intent": "direct_analysis"}
        )
    
    async def _handle_analysis_confirmation(self,
                                          analyst_response: AnalystResponse,
                                          session_id: str,
                                          user_id: str,
                                          user_message_id: str) -> HybridResponse:
        """Handle user confirmation of suggested analysis - FIXED: uses existing flow"""
        
        # Get pending analysis from ConversationStore (persistent across restarts)
        pending_analysis = await self._get_pending_analysis_from_conversation_store(session_id)
        
        if not pending_analysis:
            # No pending analysis - treat as general chat
            assistant_message_id = await self.chat_history_service.add_hybrid_message(
                session_id=session_id,
                user_id=user_id,
                content="I'd be happy to help with analysis! Could you please specify what you'd like me to analyze?",
                message_type="chat",
                intent="confirmation_without_pending",
                in_reply_to=user_message_id
            )
            
            return HybridResponse(
                response_type="chat",
                content="I'd be happy to help with analysis! Could you please specify what you'd like me to analyze?",
                message_id=assistant_message_id,
                session_id=session_id,
                metadata={"intent": "confirmation_without_pending"}
            )
        
        # Add confirmation response to chat
        assistant_message_id = await self.chat_history_service.add_hybrid_message(
            session_id=session_id,
            user_id=user_id,
            content=analyst_response.content,
            message_type="analysis_confirmation",
            intent="analysis_confirmation",
            in_reply_to=user_message_id
        )
        
        # Get analysis question from pending suggestion
        analysis_question = pending_analysis.get("suggested_question")
        
        # FIXED: Return chat response + flag to trigger analysis
        return HybridResponse(
            response_type="analysis_trigger",
            content=analyst_response.content,
            message_id=assistant_message_id,
            session_id=session_id,
            should_trigger_analysis=True,  # KEY: Flag for API to call analyze_question
            analysis_question=analysis_question,  # Suggested analysis question
            metadata={
                "intent": "confirmed_analysis",
                "original_suggestion": pending_analysis.get("topic", "unknown")
            }
        )
    
    async def _handle_follow_up_response(self,
                                       analyst_response: AnalystResponse,
                                       session_id: str,
                                       user_id: str,
                                       user_message_id: str) -> HybridResponse:
        """Handle follow-up questions about previous analysis"""
        
        # Add follow-up response to chat
        assistant_message_id = await self.chat_history_service.add_hybrid_message(
            session_id=session_id,
            user_id=user_id,
            content=analyst_response.content,
            message_type="follow_up_chat",
            intent="follow_up",
            in_reply_to=user_message_id
        )
        
        return HybridResponse(
            response_type="follow_up_chat",
            content=analyst_response.content,
            message_id=assistant_message_id,
            session_id=session_id,
            metadata={"intent": "follow_up"}
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
                                   user_id: str) -> HybridResponse:
        """Create error response"""
        try:
            # Add error message to chat history
            error_message_id = await self.chat_history_service.add_hybrid_message(
                session_id=session_id,
                user_id=user_id,
                content=error_message,
                message_type="error",
                intent="error"
            )
            
            return HybridResponse(
                response_type="error",
                content=error_message,
                message_id=error_message_id,
                session_id=session_id,
                metadata={"error": True}
            )
        except Exception as e:
            logger.error(f"Failed to create error response: {e}")
            # Fallback response without chat history
            return HybridResponse(
                response_type="error",
                content=error_message,
                message_id="error",
                session_id=session_id,
                metadata={"error": True, "chat_save_failed": True}
            )
    
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