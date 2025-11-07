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
            
            # Step 1: Add user message to chat history
            user_message_id = await self.chat_history_service.add_user_message(
                session_id=session_id,
                user_id=user_id,
                question=user_message
            )
            
            # Step 2: Classify intent with proper service using session manager (consistent approach)
            start_time = time.time()
            intent_result = await self.intent_classifier.classify_intent(
                user_message=user_message,
                session_id=session_id
            )
            intent_duration = time.time() - start_time
            
            logger.info(f"⏱️ Intent classification: {intent_duration:.3f}s, Intent: {intent_result.intent.value}")
            
            # Step 3: Generate analyst response with proper service
            start_time = time.time()
            analyst_response = await self.financial_analyst.generate_response(
                user_message=user_message,
                intent_result=intent_result,
                session_id=session_id,
                session_manager=self.session_manager
            )
            analyst_duration = time.time() - start_time
            
            logger.info(f"⏱️ Analyst response: {analyst_duration:.3f}s")
            
            # Step 5: Route based on intent - FIXED APPROACH
            return await self._route_based_on_intent(
                intent_result=intent_result,
                analyst_response=analyst_response,
                user_message=user_message,
                user_message_id=user_message_id,
                session_id=session_id,
                user_id=user_id
            )
            
        except Exception as e:
            logger.error(f"❌ Hybrid handler V2 error: {e}")
            return await self._create_error_response(
                error_message=f"I apologize, but I encountered an error processing your message. Please try again.",
                session_id=session_id,
                user_id=user_id
            )
    
    async def _route_based_on_intent(self,
                                   intent_result: IntentResult,
                                   analyst_response: AnalystResponse,
                                   user_message: str,
                                   user_message_id: str,
                                   session_id: str,
                                   user_id: str) -> HybridResponse:
        """
        FIXED: Route based on intent using existing analyze_question flow
        """
        
        # Route to appropriate handler based on intent
        if intent_result.intent == MessageIntent.PURE_CHAT:
            return await self._handle_pure_chat(
                analyst_response, session_id, user_id, user_message_id
            )
                
        elif intent_result.intent == MessageIntent.EDUCATIONAL:
            return await self._handle_educational_response(
                analyst_response, intent_result, user_message, session_id, user_id, user_message_id
            )
                
        elif intent_result.intent == MessageIntent.ANALYSIS_REQUEST:
            return await self._handle_analysis_request(
                analyst_response, user_message, session_id, user_id, user_message_id
            )
                
        elif intent_result.intent == MessageIntent.ANALYSIS_CONFIRMATION:
            return await self._handle_analysis_confirmation(
                analyst_response, session_id, user_id, user_message_id
            )
                
        elif intent_result.intent == MessageIntent.FOLLOW_UP:
            return await self._handle_follow_up_response(
                analyst_response, session_id, user_id, user_message_id
            )
        
        else:
            # Default to educational chat
            return await self._handle_educational_response(
                analyst_response, intent_result, user_message, session_id, user_id, user_message_id
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
        
        # Store analysis suggestion in session state if provided
        if analyst_response.analysis_suggestion:
            if session_id not in self.session_states:
                self.session_states[session_id] = {}
            
            self.session_states[session_id]["pending_analysis"] = {
                "suggestion": analyst_response.analysis_suggestion,
                "timestamp": time.time()
            }
        
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
            triggered_analysis=False
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
        
        # Get pending analysis from session state
        pending_analysis = None
        if session_id in self.session_states and "pending_analysis" in self.session_states[session_id]:
            pending_analysis = self.session_states[session_id]["pending_analysis"]
            # Clear pending analysis
            del self.session_states[session_id]["pending_analysis"]
        
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
        analysis_question = pending_analysis["suggestion"].suggested_question
        
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
                "original_suggestion": pending_analysis["suggestion"].topic
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
    
    def cleanup_session_state(self, session_id: str):
        """Clean up session state when session ends"""
        if session_id in self.session_states:
            del self.session_states[session_id]
            logger.debug(f"Cleaned up session state for {session_id}")
    
    async def _save_hybrid_turn(self,
                              session_id: str,
                              user_query: str,
                              message_intent,  # MessageIntent enum
                              response_type: str,
                              assistant_response: str,
                              triggered_analysis: bool = False):
        """Save conversation turn to ConversationStore using session manager"""
        try:
            # Import MessageIntent from ConversationStore
            from shared.analyze.dialogue.conversation.store import MessageIntent
            
            # Get conversation store via session manager
            conversation = await self.session_manager.get_session(session_id)
            if conversation:
                conversation.add_hybrid_turn(
                    user_query=user_query,
                    message_intent=message_intent,
                    response_type=response_type,
                    assistant_response=assistant_response,
                    triggered_analysis=triggered_analysis
                )
                # Save the updated conversation
                await self.session_manager.save_session(conversation)
                logger.debug(f"💾 Saved hybrid turn for session {session_id}: {message_intent.value if message_intent else 'unknown'}")
            else:
                logger.warning(f"⚠️ No conversation found for session {session_id}")
        except Exception as e:
            logger.error(f"❌ Failed to save hybrid turn for session {session_id}: {e}")