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
    
    def _initialize_service_specific(self):
        """Initialize analyst chat specific components"""
        # Load analysis suggestion templates
        self.suggestion_templates = self._load_suggestion_templates()
        logger.info("✅ Financial analyst chat service initialized")
    
    def _load_suggestion_templates(self) -> Dict[str, Dict[str, str]]:
        """Load templates for analysis suggestions by topic"""
        return {
            "diversification": {
                "description": "Compare diversified vs concentrated portfolio performance",
                "suggested_question": "How has a diversified portfolio performed vs a concentrated one over the last 10 years?",
                "analysis_type": "performance_comparison"
            },
            "risk": {
                "description": "Analyze risk metrics and volatility for different investments",
                "suggested_question": "What are the risk metrics and volatility for these investments?",
                "analysis_type": "risk_analysis"
            },
            "correlation": {
                "description": "Show correlation between different assets or sectors",
                "suggested_question": "What is the correlation between these assets over different time periods?",
                "analysis_type": "correlation_analysis"
            },
            "performance": {
                "description": "Compare investment performance over various timeframes",
                "suggested_question": "How have these investments performed over different time periods?",
                "analysis_type": "performance_analysis"
            },
            "volatility": {
                "description": "Analyze volatility patterns and trends",
                "suggested_question": "What are the volatility patterns for these investments?",
                "analysis_type": "volatility_analysis"
            }
        }
    
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
            
            # Extract conversation context using session manager (consistent approach)
            conversation_history = []
            session_context = {}
            
            if session_manager and session_id:
                try:
                    conversation = await session_manager.get_session(session_id)
                    if conversation and hasattr(conversation, 'messages'):
                        # Use new message-based architecture
                        recent_messages = conversation.get_messages(limit=10)  # Last 10 messages (5 exchanges)
                        for message in recent_messages:
                            conversation_history.append({
                                "role": message.role,
                                "content": message.content
                            })
                        
                        # Get session context from ConversationStore
                        session_context = conversation.get_context_summary()
                except Exception as e:
                    logger.warning(f"⚠️ Could not get conversation context: {e}")
            
            # Route to appropriate response generator based on intent
            if intent_result.intent == MessageIntent.PURE_CHAT:
                return await self._generate_chat_response(user_message, conversation_history)
                
            elif intent_result.intent == MessageIntent.EDUCATIONAL:
                return await self._generate_educational_response(
                    user_message, intent_result, conversation_history, session_context
                )
                
            elif intent_result.intent == MessageIntent.ANALYSIS_REQUEST:
                return await self._generate_analysis_request_response(user_message, session_context)
                
            elif intent_result.intent == MessageIntent.ANALYSIS_CONFIRMATION:
                return await self._generate_confirmation_response(user_message, session_context)
                
            elif intent_result.intent == MessageIntent.FOLLOW_UP:
                return await self._generate_follow_up_response(
                    user_message, conversation_history, session_context
                )
            
            else:
                # Fallback to educational response
                return await self._generate_educational_response(
                    user_message, intent_result, conversation_history, session_context
                )
                
        except Exception as e:
            logger.error(f"❌ Analyst response generation error: {e}")
            raise
    
    async def _generate_chat_response(self, 
                                    user_message: str, 
                                    conversation_history: List[Dict[str, str]]) -> AnalystResponse:
        """Generate response for pure chat interactions"""
        
        # Simple response templates for common chat patterns
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["hello", "hi", "good morning", "good afternoon"]):
            content = "Hello! I'm your financial analysis assistant. I'm here to help you understand financial concepts and run analysis when needed. What would you like to explore today?"
            
        elif any(word in message_lower for word in ["thank", "thanks"]):
            content = "You're very welcome! I'm always here to help you with financial questions and analysis. Is there anything else you'd like to explore?"
            
        elif any(word in message_lower for word in ["bye", "goodbye", "see you"]):
            content = "Goodbye! Feel free to return anytime you have financial questions or need analysis. Have a great day!"
            
        else:
            # Use LLM for more complex chat responses
            content = await self._generate_llm_chat_response(user_message, conversation_history)
        
        return AnalystResponse(content=content)
    
    async def _generate_educational_response(self, 
                                           user_message: str,
                                           intent_result: IntentResult,
                                           conversation_history: List[Dict[str, str]],
                                           session_context: Dict[str, Any]) -> AnalystResponse:
        """Generate educational response with analysis suggestion"""
        
        # Prepare context for educational response
        context_info = self._prepare_educational_context(conversation_history, session_context)
        
        # Create educational prompt
        educational_prompt = self._create_educational_prompt(user_message, context_info, intent_result)
        
        # Get LLM response
        start_time = time.time()
        messages = [{"role": "user", "content": educational_prompt}]
        
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
                                                session_context: Dict[str, Any]) -> AnalystResponse:
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
                                            session_context: Dict[str, Any]) -> AnalystResponse:
        """Generate response for analysis confirmations"""
        
        # Check if there's a pending analysis suggestion
        if session_context and session_context.get("pending_analysis"):
            pending = session_context["pending_analysis"]
            if isinstance(pending, dict):
                suggested_topic = pending.get("suggestion", {}).get("topic", "analysis")
                content = f"Perfect! Let me run that {suggested_topic} analysis for you. This will provide valuable insights into your question."
            else:
                content = "Perfect! Let me run that analysis for you. This will provide valuable insights into your question."
        else:
            content = "Great! Let me run that analysis for you right away."
        
        return AnalystResponse(content=content)
    
    async def _generate_follow_up_response(self, 
                                         user_message: str,
                                         conversation_history: List[Dict[str, str]],
                                         session_context: Dict[str, Any]) -> AnalystResponse:
        """Generate response for follow-up questions"""
        
        # Use LLM to generate contextual follow-up response
        context_info = self._prepare_follow_up_context(conversation_history, session_context)
        follow_up_prompt = self._create_follow_up_prompt(user_message, context_info)
        
        start_time = time.time()
        messages = [{"role": "user", "content": follow_up_prompt}]
        
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
    
    def _prepare_educational_context(self, 
                                   conversation_history: List[Dict[str, str]], 
                                   session_context: Dict[str, Any]) -> str:
        """Prepare context for educational responses"""
        context_parts = []
        
        if conversation_history:
            recent_messages = conversation_history[-4:]
            history_text = "\\n".join([f"{msg['role']}: {msg['content'][:150]}" for msg in recent_messages])
            context_parts.append(f"CONVERSATION HISTORY:\\n{history_text}")
        
        if session_context and session_context.get("last_analysis"):
            analysis = session_context["last_analysis"]
            if isinstance(analysis, dict):
                context_parts.append(f"PREVIOUS ANALYSIS: {analysis.get('description', '')[:200]}")
            elif isinstance(analysis, str):
                context_parts.append(f"PREVIOUS ANALYSIS: {analysis[:200]}")
            else:
                logger.debug(f"Unexpected analysis type: {type(analysis)}")
        
        return "\\n\\n".join(context_parts) if context_parts else "No previous context"
    
    def _create_educational_prompt(self, 
                                 user_message: str, 
                                 context_info: str, 
                                 intent_result: IntentResult) -> str:
        """Create prompt for educational response generation"""
        
        educational_topic = intent_result.educational_topic or "financial topic"
        
        return f"""CONTEXT:
{context_info}

USER QUESTION: {user_message}
EDUCATIONAL TOPIC: {educational_topic}

Please provide an educational response as a professional financial analyst. Follow the established response format from your system prompt."""
    
    def _parse_educational_response(self, 
                                  content: str, 
                                  intent_result: IntentResult) -> AnalystResponse:
        """Parse educational response and extract analysis suggestions"""
        
        # Try to parse JSON response first
        try:
            cleaned_content = content.strip()
            if cleaned_content.startswith("```json"):
                start_index = cleaned_content.find("{")
                end_index = cleaned_content.rfind("}") + 1
                if start_index != -1 and end_index != -1:
                    json_part = cleaned_content[start_index:end_index]
                    parsed = safe_json_loads(json_part, default={})
                    
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
        
        # Fallback to using content as-is
        # Try to generate analysis suggestion based on educational topic
        analysis_suggestion = None
        if intent_result.educational_topic:
            topic_key = intent_result.educational_topic.lower()
            for key, template in self.suggestion_templates.items():
                if key in topic_key:
                    analysis_suggestion = AnalysisSuggestion(
                        topic=key,
                        description=template["description"],
                        suggested_question=template["suggested_question"],
                        analysis_type=template["analysis_type"]
                    )
                    break
        
        return AnalystResponse(
            content=content,
            analysis_suggestion=analysis_suggestion,
            educational_topic=intent_result.educational_topic
        )
    
    async def _generate_llm_chat_response(self, 
                                        user_message: str,
                                        conversation_history: List[Dict[str, str]]) -> str:
        """Generate LLM-based chat response for complex interactions"""
        
        context_info = ""
        if conversation_history:
            recent_messages = conversation_history[-4:]
            context_info = "\\n".join([f"{msg['role']}: {msg['content'][:100]}" for msg in recent_messages])
        
        chat_prompt = f"""CONTEXT:
{context_info}

USER MESSAGE: {user_message}

Please provide a friendly, professional response as a financial analyst assistant. Keep it conversational and helpful."""
        
        messages = [{"role": "user", "content": chat_prompt}]
        
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
    
    def _prepare_follow_up_context(self, 
                                 conversation_history: List[Dict[str, str]], 
                                 session_context: Dict[str, Any]) -> str:
        """Prepare context for follow-up responses"""
        context_parts = []
        
        if conversation_history:
            recent_messages = conversation_history[-6:]
            history_text = "\\n".join([f"{msg['role']}: {msg['content'][:200]}" for msg in recent_messages])
            context_parts.append(f"RECENT CONVERSATION:\\n{history_text}")
        
        if session_context and session_context.get("last_analysis"):
            analysis = session_context["last_analysis"]
            if isinstance(analysis, dict):
                context_parts.append(f"LAST ANALYSIS RESULTS: {analysis.get('description', '')[:300]}")
            elif isinstance(analysis, str):
                context_parts.append(f"LAST ANALYSIS RESULTS: {analysis[:300]}")
            else:
                logger.debug(f"Unexpected analysis type in follow-up context: {type(analysis)}")
        
        return "\\n\\n".join(context_parts) if context_parts else "No previous context"
    
    def _create_follow_up_prompt(self, user_message: str, context_info: str) -> str:
        """Create prompt for follow-up response generation"""
        return f"""CONTEXT:
{context_info}

FOLLOW-UP QUESTION: {user_message}

Please provide a helpful response that addresses the user's follow-up question based on the previous conversation and analysis. Be specific and educational.

If appropriate, suggest a related analysis that would provide deeper insights. Use the following JSON format:

```json
{{
    "content": "Your detailed educational response here...",
    "analysis_suggestion": {{
        "topic": "Short descriptive name for the analysis",
        "description": "What this analysis would reveal",
        "suggested_question": "Specific analysis question to run",
        "analysis_type": "correlation|volatility|returns|comparison|general"
    }}
}}
```

If no analysis suggestion is appropriate, just provide the response as plain text."""
    