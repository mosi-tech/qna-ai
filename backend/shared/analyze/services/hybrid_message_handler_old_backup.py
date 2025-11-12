#!/usr/bin/env python3
"""
Hybrid Message Handler

Routes user messages between:
1. Financial Analyst Chat (educational, confirmations, follow-ups)  
2. Analysis Pipeline (when analysis is needed)

Implements GitHub Issue #122 - Mix of LLM chat + analysis
Uses proper BaseService pattern and existing analysis infrastructure
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from .intent_classifier import IntentClassifierService, MessageIntent, IntentResult
from .financial_analyst_chat_service import FinancialAnalystChatService, AnalystResponse
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
    analysis_task: Optional[asyncio.Task] = None  # Background analysis task

class HybridMessageHandler:
    """
    Intelligent message router that combines chat and analysis capabilities
    Uses proper BaseService pattern and existing analysis infrastructure
    """
    
    def __init__(self, 
                 chat_history_service: ChatHistoryService,
                 analyze_question_callable=None):  # Callable to existing analyze_question method
        self.chat_history_service = chat_history_service
        self.analyze_question_callable = analyze_question_callable
        
        # Initialize proper services
        self.intent_classifier = IntentClassifierService()
        self.financial_analyst = FinancialAnalystChatService()
        
        # Track session state for pending analysis suggestions
        self.session_states = {}  # session_id -> state info
        
        logger.info("✅ Hybrid message handler initialized with proper services")
        
    async def handle_message(self, 
                           user_message: str,
                           session_id: str,
                           user_id: str = "anonymous") -> HybridResponse:
        """
        Main entry point for handling user messages
        
        NEW APPROACH:
        1. Classify intent
        2. Generate analyst response  
        3. If analysis needed: return chat + trigger analysis in background
        4. Otherwise: return chat response
        """
        try:
            logger.info(f"🔀 Hybrid handler processing: {user_message[:100]}...")
            
            # Step 1: Add user message to chat history
            user_message_id = await self.chat_history_service.add_user_message(
                session_id=session_id,
                user_id=user_id,
                question=user_message
            )
            
            # Step 2: Get session context and conversation history
            session_context = await self._get_session_context(session_id)
            conversation_history = await self._get_conversation_history(session_id)
            
            # Step 3: Classify intent
            start_time = time.time()
            intent_result = await self.intent_classifier.classify_intent(
                user_message=user_message,
                conversation_history=conversation_history,
                session_context=session_context
            )
            intent_duration = time.time() - start_time
            
            logger.info(f"⏱️ Intent classification: {intent_duration:.3f}s, Intent: {intent_result.intent.value}")
            
            # Step 4: Generate analyst response
            start_time = time.time()
            analyst_response = await self.financial_analyst.generate_response(
                user_message=user_message,
                intent_result=intent_result,
                conversation_history=conversation_history,
                session_context=session_context
            )
            analyst_duration = time.time() - start_time
            
            logger.info(f"⏱️ Analyst response: {analyst_duration:.3f}s")
            
            # Step 5: Route based on intent - NEW APPROACH
            return await self._route_response_new(
                intent_result=intent_result,
                analyst_response=analyst_response,
                user_message=user_message,
                user_message_id=user_message_id,
                session_id=session_id,
                user_id=user_id,
                session_context=session_context
            )
            
        except Exception as e:
            logger.error(f"❌ Hybrid handler error: {e}")
            return await self._create_error_response(
                error_message=f"I apologize, but I encountered an error processing your message. Please try again.",
                session_id=session_id,
                user_id=user_id,
                internal_error=str(e)
            )
    
    async def _route_response_new(self,
                                intent_result: IntentResult,
                                analyst_response: AnalystResponse,
                                user_message: str,
                                user_message_id: str,
                                session_id: str,
                                user_id: str,
                                session_context: Dict[str, Any]) -> HybridResponse:
        """
        Route the response based on intent - NEW APPROACH
        
        Key change: Return chat immediately + trigger analysis in background if needed
        """
        
        # Handle different intent types
        if intent_result.message_type == MessageIntent.PURE_CHAT:
            return await self._handle_pure_chat(chat_response, session_id, user_message_id)
            
        elif chat_response.message_type == MessageIntent.EDUCATIONAL:
            return await self._handle_educational_chat(chat_response, session_id, user_message_id)
            
        elif chat_response.message_type == MessageIntent.ANALYSIS_REQUEST:
            return await self._handle_direct_analysis_request(chat_response, user_message, session_id, user_id, user_message_id)
            
        elif chat_response.message_type == MessageIntent.ANALYSIS_CONFIRMATION:
            return await self._handle_analysis_confirmation(chat_response, session_id, user_id, user_message_id)
            
        elif chat_response.message_type == MessageIntent.FOLLOW_UP:
            return await self._handle_follow_up(chat_response, session_id, user_message_id, session_context)
            
        else:
            # Default to educational chat
            return await self._handle_educational_chat(chat_response, session_id, user_message_id)
    
    async def _handle_pure_chat(self, chat_response: ChatResponse, session_id: str, user_message_id: str) -> HybridResponse:
        """Handle pure chat interactions (greetings, thanks, etc.)"""
        
        # Add assistant response to chat history
        assistant_message_id = await self.chat_history_service.add_assistant_message(
            session_id=session_id,
            message=chat_response.content,
            response_type="chat",
            in_reply_to=user_message_id
        )
        
        return HybridResponse(
            response_type="chat",
            content=chat_response.content,
            session_id=session_id,
            message_id=assistant_message_id,
            metadata={"intent": "pure_chat"}
        )
    
    async def _handle_educational_chat(self, chat_response: ChatResponse, session_id: str, user_message_id: str) -> HybridResponse:
        """Handle educational responses with potential analysis suggestions"""
        
        # Add assistant response to chat history
        assistant_message_id = await self.chat_history_service.add_assistant_message(
            session_id=session_id,
            message=chat_response.content,
            response_type="educational_chat",
            in_reply_to=user_message_id
        )
        
        # Store analysis suggestion in session state for potential confirmation
        if chat_response.analysis_suggestion:
            if session_id not in self.session_states:
                self.session_states[session_id] = {}
            
            self.session_states[session_id]["pending_analysis"] = {
                "suggestion": chat_response.analysis_suggestion,
                "timestamp": time.time()
            }
        
        metadata = {
            "intent": "educational",
            "has_analysis_suggestion": bool(chat_response.analysis_suggestion)
        }
        
        if chat_response.analysis_suggestion:
            metadata["suggested_analysis"] = {
                "topic": chat_response.analysis_suggestion.topic,
                "description": chat_response.analysis_suggestion.description
            }
        
        return HybridResponse(
            response_type="educational_chat",
            content=chat_response.content,
            session_id=session_id,
            message_id=assistant_message_id,
            metadata=metadata
        )
    
    async def _handle_direct_analysis_request(self, 
                                            chat_response: ChatResponse, 
                                            user_message: str,
                                            session_id: str, 
                                            user_id: str,
                                            user_message_id: str) -> HybridResponse:
        """Handle direct analysis requests"""
        
        if not self.analysis_pipeline_service:
            logger.error("Analysis pipeline service not available")
            error_response = "I apologize, but analysis functionality is currently unavailable. Please try again later."
            
            assistant_message_id = await self.chat_history_service.add_assistant_message(
                session_id=session_id,
                message=error_response,
                response_type="error",
                in_reply_to=user_message_id
            )
            
            return HybridResponse(
                response_type="error",
                content=error_response,
                session_id=session_id,
                message_id=assistant_message_id
            )
        
        # Queue the analysis
        return HybridResponse(
            response_type="analysis_queued",
            content="Let me analyze that for you. This may take a moment...",
            session_id=session_id,
            message_id=user_message_id,
            should_queue_analysis=True,
            analysis_question=user_message,  # Use original user message
            metadata={"intent": "direct_analysis"}
        )
    
    async def _handle_analysis_confirmation(self, 
                                          chat_response: ChatResponse,
                                          session_id: str, 
                                          user_id: str,
                                          user_message_id: str) -> HybridResponse:
        """Handle user confirmation of suggested analysis"""
        
        # Get pending analysis from session state
        pending_analysis = None
        if session_id in self.session_states and "pending_analysis" in self.session_states[session_id]:
            pending_analysis = self.session_states[session_id]["pending_analysis"]
            
            # Clear pending analysis
            del self.session_states[session_id]["pending_analysis"]
        
        if not pending_analysis:
            # No pending analysis found, treat as general confirmation
            response_content = "I'd be happy to help with analysis! Could you please specify what you'd like me to analyze?"
            
            assistant_message_id = await self.chat_history_service.add_assistant_message(
                session_id=session_id,
                message=response_content,
                response_type="chat",
                in_reply_to=user_message_id
            )
            
            return HybridResponse(
                response_type="chat",
                content=response_content,
                session_id=session_id,
                message_id=assistant_message_id
            )
        
        # Add confirmation response to chat
        confirmation_message = chat_response.content or "Great! Let me run that analysis for you."
        assistant_message_id = await self.chat_history_service.add_assistant_message(
            session_id=session_id,
            message=confirmation_message,
            response_type="analysis_confirmation",
            in_reply_to=user_message_id
        )
        
        # Extract analysis question from the pending suggestion
        analysis_question = pending_analysis["suggestion"].suggested_question
        
        return HybridResponse(
            response_type="analysis_queued",
            content=confirmation_message,
            session_id=session_id,
            message_id=assistant_message_id,
            should_queue_analysis=True,
            analysis_question=analysis_question,
            metadata={
                "intent": "confirmed_analysis",
                "original_suggestion": pending_analysis["suggestion"].topic
            }
        )
    
    async def _handle_follow_up(self, 
                              chat_response: ChatResponse,
                              session_id: str, 
                              user_message_id: str,
                              session_context: Dict[str, Any]) -> HybridResponse:
        """Handle follow-up questions about previous analysis"""
        
        # Add assistant response to chat history
        assistant_message_id = await self.chat_history_service.add_assistant_message(
            session_id=session_id,
            message=chat_response.content,
            response_type="follow_up_chat",
            in_reply_to=user_message_id
        )
        
        # If chat response suggests running new analysis
        if chat_response.should_run_analysis and chat_response.analysis_question:
            return HybridResponse(
                response_type="analysis_queued",
                content=chat_response.content,
                session_id=session_id,
                message_id=assistant_message_id,
                should_queue_analysis=True,
                analysis_question=chat_response.analysis_question,
                metadata={"intent": "follow_up_analysis"}
            )
        
        return HybridResponse(
            response_type="follow_up_chat",
            content=chat_response.content,
            session_id=session_id,
            message_id=assistant_message_id,
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
                    limit=10  # Last 10 messages
                )
                
                # Look for recent analysis in messages
                for message in recent_messages:
                    if (message.get("response_type") in ["script_generation", "reuse_decision"] and 
                        message.get("analysisId")):
                        context["last_analysis"] = {
                            "id": message.get("analysisId"),
                            "description": message.get("content", ""),
                            "timestamp": message.get("timestamp")
                        }
                        break  # Use most recent analysis
            
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
                limit=12  # Last 12 messages for context
            )
            
            # Format for LLM context
            history = []
            for msg in recent_messages:
                role = "user" if msg.get("role") == "user" else "assistant"
                content = msg.get("content", "")
                if content:  # Only include non-empty messages
                    history.append({"role": role, "content": content})
            
            return history
            
        except Exception as e:
            logger.warning(f"Could not get conversation history: {e}")
            return []
    
    def _create_error_response(self, error_message: str, session_id: str) -> HybridResponse:
        """Create standardized error response"""
        return HybridResponse(
            response_type="error",
            content=error_message,
            session_id=session_id,
            metadata={"error": True}
        )
    
    def cleanup_session_state(self, session_id: str):
        """Clean up session state when session ends"""
        if session_id in self.session_states:
            del self.session_states[session_id]
            logger.debug(f"Cleaned up session state for {session_id}")