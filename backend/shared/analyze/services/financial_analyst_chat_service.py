#!/usr/bin/env python3
"""
Financial Analyst Chat Service

Provides professional financial analyst persona responses with educational content
and analysis suggestions. Follows BaseService pattern with proper LLM integration.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ...llm import LLMService
from ...services.base_service import BaseService
from .intent_classifier import MessageIntent, IntentResult
from shared.utils.json_utils import safe_json_loads
from ..dialogue.context.simplified_context_manager import SimplifiedFinancialContextManager, ContextType
logger = logging.getLogger(__name__)

@dataclass
class AnalysisSuggestion:
    """Suggested analysis based on user's educational inquiry"""
    topic: str
    description: str
    suggested_question: str
    analysis_type: str  # correlation, performance, risk, etc.

@dataclass
class AnalystResponse:
    """Response from financial analyst chat service"""
    content: str
    analysis_suggestion: Optional[AnalysisSuggestion] = None
    follow_up_questions: List[str] = None
    educational_topic: Optional[str] = None
    
class FinancialAnalystChatService(BaseService):
    """Service that generates professional financial analyst responses"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(llm_service=llm_service, service_name="financial-analyst-chat")
    
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service for analyst chat"""
        from ...llm.utils import LLMConfig
        
        # Use conversational model for analyst chat
        config = LLMConfig.for_task("analyst_chat")
        config.temperature = 0.7  # More conversational
        config.max_tokens = 1200  # Longer responses for education
        return LLMService(config)
    
    def _get_system_prompt_filename(self) -> str:
        """Use financial analyst specific system prompt"""
        return "system-prompt-financial-analyst.txt"
    
    async def generate_response(self, 
                              user_message: str,
                              intent_result: IntentResult,
                              session_id: str = None,
                              session_manager = None) -> AnalystResponse:
        """
        Generate analyst response based on classified intent
        
        Args:
            user_message: User's message
            intent_result: Classification result from IntentClassifierService
            session_id: Session ID for context
            session_manager: SessionManager for getting conversation context (consistent with intent classifier)
            
        Returns:
            AnalystResponse with content and potential analysis suggestion
        """
        try:
            logger.debug(f"🤖 Generating analyst response for intent: {intent_result.intent.value}")
            
            # Use smart conversation logic instead of manual extraction
            conversation = None
            if session_manager and session_id:
                try:
                    conversation = await session_manager.get_session(session_id)
                except Exception as e:
                    logger.warning(f"⚠️ Could not get conversation: {e}")
            
            # Route to appropriate response generator based on intent
            if intent_result.intent == MessageIntent.PURE_CHAT:
                return await self._generate_chat_response(user_message, conversation)
                
            elif intent_result.intent == MessageIntent.EDUCATIONAL:
                return await self._generate_educational_response(
                    user_message, intent_result, conversation)
                
            elif intent_result.intent == MessageIntent.ANALYSIS_REQUEST:
                return await self._generate_analysis_request_response(user_message, conversation)
                
            elif intent_result.intent == MessageIntent.ANALYSIS_CONFIRMATION:
                return await self._generate_confirmation_response(user_message, conversation)
                
            elif intent_result.intent == MessageIntent.FOLLOW_UP:
                return await self._generate_follow_up_response(user_message, conversation)
            
            else:
                # Fallback to educational response
                return await self._generate_educational_response(
                    user_message, intent_result, conversation)
                
        except Exception as e:
            logger.error(f"❌ Analyst response generation error: {e}")
            raise
    
    async def _generate_chat_response(self, 
                                    user_message: str, 
                                    conversation) -> AnalystResponse:
        """Generate response for pure chat interactions"""
        
        # Use LLM for more complex chat responses
        content = await self._generate_llm_chat_response(user_message, conversation)
        
        return AnalystResponse(content=content)
    
    async def _generate_educational_response(self, 
                                           user_message: str,
                                           intent_result: IntentResult,
                                           conversation,
                                           ) -> AnalystResponse:
        """Generate educational response with analysis suggestion"""
        context_manager = SimplifiedFinancialContextManager()
        
        # Get properly formatted messages for LLM (smart windowing, summaries, etc.)
        messages = await context_manager.get_conversation_messages_for_llm(
            conversation, ContextType.FOLLOW_UP_GENERATION, user_message
        )
        
        # Add intent-specific instruction for educational response
        educational_topic = intent_result.educational_topic or "financial topic"
        instruction = f"Please provide an educational response about {educational_topic}. If appropriate, suggest a specific analysis. Respond in JSON format: {{'content': 'your educational response', 'analysis_suggestion': {{'topic': 'analysis name', 'description': 'what it analyzes', 'suggested_question': 'specific question'}}}}"
        
        messages.append({
            "role": "user",
            "content": instruction
        })
        
        # Get LLM response with cached system prompt
        start_time = time.time()
        
        # Load system prompt if not cached
        if not self.system_prompt:
            self.system_prompt = await self.load_system_prompt()
        
        response = await self.llm_service.make_request(
            messages=messages,
            max_tokens=1200,
            temperature=0.7,
            system_prompt=self.system_prompt
        )
        duration = time.time() - start_time
        
        logger.debug(f"⏱️ Educational response generation: {duration:.3f}s")
        logger.debug(f"🔍 LLM response type: {type(response)}, content: {str(response)[:200]}...")
        
        # Check if response is a string (unexpected) vs dict (expected)
        if isinstance(response, str):
            logger.error(f"❌ Expected dict response but got string: {response[:100]}...")
            return self._create_fallback_response(user_message)
        
        if not response.get("success"):
            error_msg = response.get("error", "Unknown error")
            logger.error(f"❌ Educational response generation failed: {error_msg}")
            return self._create_fallback_response(user_message)
        
        # Parse educational response
        content = response.get("content", "")
        return self._parse_educational_response(content, intent_result)
    
    async def _generate_analysis_request_response(self, 
                                                user_message: str,
                                                conversation) -> AnalystResponse:
        """Generate response for direct analysis requests"""
        
        content = "I'll help you with that analysis. Let me process your request and run the analysis for you."
        
        # Could enhance this to be more specific based on the request
        if any(word in user_message.lower() for word in ["correlation", "correlate"]):
            content = "I'll run a correlation analysis for you. This will show how different assets move in relation to each other."
        elif any(word in user_message.lower() for word in ["performance", "return"]):
            content = "I'll analyze the performance for you. This will show returns, growth, and comparative metrics."
        elif any(word in user_message.lower() for word in ["risk", "volatility"]):
            content = "I'll run a risk analysis for you. This will examine volatility, drawdowns, and risk-adjusted returns."
        
        return AnalystResponse(content=content)
    
    async def _generate_confirmation_response(self, 
                                            user_message: str,
                                            conversation) -> AnalystResponse:
        """Generate response for analysis confirmations"""
        
        # Check if there's a pending analysis suggestion from conversation
        if conversation:
            # Use the conversation store method to check for pending analysis
            pending_analysis = await conversation.get_pending_analysis_suggestion()
            if pending_analysis:
                suggested_topic = pending_analysis.get('topic', 'analysis')
                content = f"Perfect! Let me run that {suggested_topic} analysis for you. This will provide valuable insights into your question."
            else:
                content = "I'll help you with that analysis. Let me run it for you right away."
        else:
            content = "Great! Let me run that analysis for you right away."
        
        return AnalystResponse(content=content)
    
    async def _generate_follow_up_response(self, 
                                         user_message: str,
                                         conversation) -> AnalystResponse:
        """Generate response for follow-up questions"""
        
        # Use smart conversation logic for follow-up responses
        
        context_manager = SimplifiedFinancialContextManager()
        # Get properly formatted messages for LLM
        messages = await context_manager.get_conversation_messages_for_llm(
            conversation, ContextType.FOLLOW_UP_GENERATION, user_message
        )
        
        # Add intent-specific instruction for follow-up response
        instruction = "Please provide a helpful response that addresses the user's follow-up question based on the previous conversation. Be specific and educational. If appropriate, suggest a related analysis. Respond in JSON format: {'content': 'your response', 'analysis_suggestion': {'topic': 'analysis name', 'description': 'what it analyzes', 'suggested_question': 'specific question'}}"
        
        messages.append({
            "role": "user",
            "content": instruction
        })
        
        start_time = time.time()
        
        # Load system prompt if not cached
        if not self.system_prompt:
            self.system_prompt = await self.load_system_prompt()
        
        response = await self.llm_service.make_request(
            messages=messages,
            max_tokens=800,
            temperature=0.6,
            system_prompt=self.system_prompt
        )
        duration = time.time() - start_time
        
        logger.debug(f"⏱️ Follow-up response generation: {duration:.3f}s")
        logger.debug(f"🔍 Follow-up response type: {type(response)}, content: {str(response)[:200]}...")
        
        # TODO: Fix this response
        if not response.get("success"):
            logger.error("Error generating follow-up response")
            raise

        content = response.get("content", "").strip()
        
        # Try to parse analysis suggestion from follow-up response (same logic as educational)
        return self._parse_educational_response(content, IntentResult(
            intent=MessageIntent.FOLLOW_UP,
            confidence=0.9,
            reasoning="Follow-up response generated",
            requires_analysis=False,
            educational_topic="follow_up"
        ))
    
    def _parse_educational_response(self, 
                                  content: str, 
                                  intent_result: IntentResult) -> AnalystResponse:
        """Parse educational response and extract analysis suggestions"""
        
        # Try to parse JSON response (safe_json_loads handles all cleaning internally)
        try:
            parsed = safe_json_loads(content, default={})
            if parsed:
                analysis_suggestion = None
                if parsed.get("analysis_suggestion"):
                    suggestion_data = parsed["analysis_suggestion"]
                    analysis_suggestion = AnalysisSuggestion(
                        topic=suggestion_data.get("topic", ""),
                        description=suggestion_data.get("description", ""),
                        suggested_question=suggestion_data.get("suggested_question", ""),
                        analysis_type=suggestion_data.get("analysis_type", "general")
                    )
                    logger.info(f"✅ Parsed analysis suggestion: {analysis_suggestion.topic} - {analysis_suggestion.description}")
                else:
                    logger.warning(f"⚠️ No analysis_suggestion found in parsed JSON: {parsed.keys()}")
                
                return AnalystResponse(
                    content=parsed.get("content", content),
                    analysis_suggestion=analysis_suggestion,
                    educational_topic=intent_result.educational_topic
                )
        except Exception as e:
            logger.debug(f"Could not parse structured educational response: {e}")
            raise
      
    async def _generate_llm_chat_response(self, 
                                        user_message: str,
                                        conversation) -> str:
        """Generate LLM-based chat response for complex interactions"""
        
        # Use smart conversation logic for chat responses
        context_manager = SimplifiedFinancialContextManager()
        # Get properly formatted messages for LLM  
        messages = await context_manager.get_conversation_messages_for_llm(
            conversation, ContextType.INTENT_CLASSIFICATION, user_message
        )
        
        # Add intent-specific instruction for chat response
        instruction = "Please provide a friendly, conversational response. Keep it warm and helpful."
        
        messages.append({
            "role": "user",
            "content": instruction
        })
        
        # Load system prompt if not cached
        if not self.system_prompt:
            self.system_prompt = await self.load_system_prompt()
        
        response = await self.llm_service.make_request(
            messages=messages,
            max_tokens=400,
            temperature=0.8,
            system_prompt=self.system_prompt
        )
        
        logger.debug(f"🔍 Chat response type: {type(response)}, content: {str(response)[:200]}...")
        
        # Check if response is a string (unexpected) vs dict (expected)
        if isinstance(response, str):
            logger.error(f"❌ Expected dict response but got string: {response[:100]}...")
            return "I'm here to help with your financial questions and analysis. What can I assist you with today?"
        
        if response.get("success"):
            return response.get("content", "I'm here to help with your financial questions!").strip()
        else:
            return "I'm here to help with your financial questions and analysis. What can I assist you with today?"
    