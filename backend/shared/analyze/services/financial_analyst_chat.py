#!/usr/bin/env python3
"""
Financial Analyst Chat Service

Provides intelligent financial analyst persona chat that can:
1. Understand financial topics and educate users
2. Suggest relevant analysis when appropriate
3. Route to analysis pipeline when user confirms
4. Maintain context between chat and analysis
"""

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

from shared.llm.service import LLMService
from shared.llm.utils import LLMConfig

logger = logging.getLogger(__name__)

class MessageIntent(Enum):
    """Classification of user message intent"""
    PURE_CHAT = "pure_chat"           # General conversation, greetings
    EDUCATIONAL = "educational"        # Wants to learn about financial concepts
    ANALYSIS_REQUEST = "analysis_request"  # Direct request for analysis
    ANALYSIS_CONFIRMATION = "analysis_confirmation"  # Confirming suggested analysis
    FOLLOW_UP = "follow_up"           # Follow-up on previous analysis

@dataclass
class AnalysisSuggestion:
    """Suggested analysis based on user's educational inquiry"""
    topic: str
    description: str
    suggested_question: str
    analysis_type: str  # correlation, performance, risk, etc.
    
@dataclass
class ChatResponse:
    """Response from financial analyst chat"""
    message_type: MessageIntent
    content: str
    analysis_suggestion: Optional[AnalysisSuggestion] = None
    should_run_analysis: bool = False
    analysis_question: Optional[str] = None

class FinancialAnalystChat:
    """
    Financial analyst persona that provides educational chat and suggests analysis
    """
    
    def __init__(self):
        self.llm_service = self._initialize_llm_service()
        self.analyst_system_prompt = self._load_analyst_system_prompt()
        
    def _initialize_llm_service(self) -> LLMService:
        """Initialize LLM service for analyst chat"""
        try:
            # Use chat-optimized configuration 
            config = LLMConfig.for_task("analyst_chat")
            config.temperature = 0.7  # More conversational
            config.max_tokens = 1000  # Longer responses for education
            return LLMService(config)
        except Exception as e:
            logger.error(f"Failed to initialize LLM service for analyst chat: {e}")
            raise
    
    def _load_analyst_system_prompt(self) -> str:
        """Load the financial analyst persona system prompt"""
        return """You are a professional financial analyst and advisor. Your role is to:

1. **EDUCATE FIRST**: When users ask about financial concepts, provide clear, educational explanations before suggesting analysis
2. **SUGGEST ANALYSIS**: After explaining concepts, suggest specific analysis that would be valuable to demonstrate the concept
3. **BE CONVERSATIONAL**: Use a professional but friendly tone, like talking to a client
4. **PROVIDE CONTEXT**: Always explain why the suggested analysis would be valuable

**RESPONSE FORMAT**:
For educational topics, structure your response as:
1. Acknowledge their interest: "I see you want to know about [topic]"
2. Provide educational explanation (2-3 paragraphs)
3. Suggest specific analysis: "Would you like me to run an analysis to..."

**INTENT CLASSIFICATION**:
- PURE_CHAT: Greetings, general conversation, thanks
- EDUCATIONAL: Questions about financial concepts, strategies, terms
- ANALYSIS_REQUEST: Direct requests for analysis ("analyze my portfolio")
- ANALYSIS_CONFIRMATION: User saying yes/no to suggested analysis
- FOLLOW_UP: Questions about previous analysis results

**ANALYSIS SUGGESTIONS**:
Always suggest concrete, actionable analysis that demonstrates the concept:
- For diversification → "Compare diversified vs concentrated portfolio performance"
- For risk → "Analyze risk metrics for different asset allocations" 
- For correlation → "Show correlation between different asset classes"
- For performance → "Compare performance of different strategies"

Respond in JSON format:
{
    "intent": "educational|pure_chat|analysis_request|analysis_confirmation|follow_up",
    "content": "Your educational response",
    "analysis_suggestion": {
        "topic": "diversification",
        "description": "Compare diversified vs concentrated portfolio performance",
        "suggested_question": "How has a diversified portfolio performed vs a concentrated one over the last 10 years?",
        "analysis_type": "performance_comparison"
    }
}

For ANALYSIS_CONFIRMATION intent, also include:
{
    "should_run_analysis": true,
    "analysis_question": "The specific question to send to analysis pipeline"
}
"""

    async def handle_message(self, 
                           user_message: str, 
                           session_context: Dict[str, Any],
                           conversation_history: List[Dict[str, str]] = None) -> ChatResponse:
        """
        Handle user message with financial analyst persona
        
        Args:
            user_message: User's message
            session_context: Session context including previous analysis
            conversation_history: Recent conversation history
            
        Returns:
            ChatResponse with intent, content, and potential analysis suggestion
        """
        try:
            logger.info(f"🤖 Analyst chat processing: {user_message[:100]}...")
            
            # Prepare context for LLM
            context_info = self._prepare_context_info(session_context, conversation_history)
            
            # Create conversation prompt
            user_prompt = self._create_user_prompt(user_message, context_info)
            
            # Get LLM response
            messages = [{"role": "user", "content": user_prompt}]
            
            start_time = time.time()
            response = await self.llm_service.make_request(
                messages=messages,
                system_prompt=self.analyst_system_prompt,
                max_tokens=1000,
                temperature=0.7
            )
            duration = time.time() - start_time
            
            logger.info(f"⏱️ Analyst chat LLM call: {duration:.3f}s")
            
            if not response.get("success"):
                error_msg = response.get("error", "Unknown error")
                logger.error(f"❌ Analyst chat LLM call failed: {error_msg}")
                return self._create_fallback_response(user_message)
            
            # Parse structured response
            content = response.get("content", "")
            return self._parse_analyst_response(content, user_message)
            
        except Exception as e:
            logger.error(f"❌ Analyst chat error: {e}")
            return self._create_fallback_response(user_message)
    
    def _prepare_context_info(self, session_context: Dict[str, Any], conversation_history: List[Dict[str, str]]) -> str:
        """Prepare context information for the LLM"""
        context_parts = []
        
        # Add recent conversation history
        if conversation_history:
            recent_messages = conversation_history[-6:]  # Last 6 messages
            history_text = "\n".join([f"{msg['role']}: {msg['content'][:200]}" for msg in recent_messages])
            context_parts.append(f"RECENT CONVERSATION:\n{history_text}")
        
        # Add previous analysis context if available
        if session_context.get("last_analysis"):
            analysis = session_context["last_analysis"]
            context_parts.append(f"PREVIOUS ANALYSIS: {analysis.get('description', 'Recent analysis available')}")
        
        # Add user context
        if session_context.get("user_profile"):
            profile = session_context["user_profile"]
            context_parts.append(f"USER CONTEXT: {profile}")
        
        return "\n\n".join(context_parts) if context_parts else "No previous context"
    
    def _create_user_prompt(self, user_message: str, context_info: str) -> str:
        """Create the user prompt with context"""
        return f"""CONTEXT:
{context_info}

USER MESSAGE: {user_message}

Please respond as a professional financial analyst. Classify the intent and provide an appropriate response."""

    def _parse_analyst_response(self, content: str, original_message: str) -> ChatResponse:
        """Parse the analyst's structured response"""
        try:
            import json
            from shared.utils.json_utils import safe_json_loads
            
            # Clean up response - remove markdown if present
            cleaned_content = content.strip()
            if cleaned_content.startswith("```json"):
                start_index = cleaned_content.find("{")
                end_index = cleaned_content.rfind("}") + 1
                if start_index != -1 and end_index != -1:
                    cleaned_content = cleaned_content[start_index:end_index]
            
            # Parse JSON response
            parsed = safe_json_loads(cleaned_content, default={})
            
            if not parsed:
                logger.warning("Failed to parse analyst response as JSON, using fallback")
                return self._create_fallback_response(original_message)
            
            # Extract intent
            intent_str = parsed.get("intent", "pure_chat")
            try:
                intent = MessageIntent(intent_str)
            except ValueError:
                intent = MessageIntent.PURE_CHAT
            
            # Extract analysis suggestion if present
            analysis_suggestion = None
            if parsed.get("analysis_suggestion"):
                suggestion_data = parsed["analysis_suggestion"]
                analysis_suggestion = AnalysisSuggestion(
                    topic=suggestion_data.get("topic", ""),
                    description=suggestion_data.get("description", ""),
                    suggested_question=suggestion_data.get("suggested_question", ""),
                    analysis_type=suggestion_data.get("analysis_type", "general")
                )
            
            return ChatResponse(
                message_type=intent,
                content=parsed.get("content", "I understand your question. How can I help you further?"),
                analysis_suggestion=analysis_suggestion,
                should_run_analysis=parsed.get("should_run_analysis", False),
                analysis_question=parsed.get("analysis_question")
            )
            
        except Exception as e:
            logger.error(f"Error parsing analyst response: {e}")
            return self._create_fallback_response(original_message)
    
    def _create_fallback_response(self, user_message: str) -> ChatResponse:
        """Create a fallback response when parsing fails"""
        # Simple heuristic-based classification
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["hello", "hi", "thanks", "thank you"]):
            intent = MessageIntent.PURE_CHAT
            content = "Hello! I'm here to help you with financial analysis and education. What would you like to explore today?"
        elif any(word in message_lower for word in ["yes", "sure", "ok", "please", "go ahead"]):
            intent = MessageIntent.ANALYSIS_CONFIRMATION
            content = "Great! Let me run that analysis for you."
        elif any(word in message_lower for word in ["analyze", "analysis", "show me", "calculate"]):
            intent = MessageIntent.ANALYSIS_REQUEST
            content = "I'll help you with that analysis. Could you be more specific about what you'd like to analyze?"
        else:
            intent = MessageIntent.EDUCATIONAL
            content = "That's an interesting financial topic. Let me help you understand it better and suggest some analysis that might be valuable."
        
        return ChatResponse(
            message_type=intent,
            content=content
        )

    async def suggest_follow_up_analysis(self, previous_analysis: Dict[str, Any]) -> Optional[AnalysisSuggestion]:
        """Suggest follow-up analysis based on previous results"""
        try:
            analysis_type = previous_analysis.get("type", "")
            topic = previous_analysis.get("topic", "")
            
            # Smart follow-up suggestions based on analysis type
            suggestions_map = {
                "correlation": AnalysisSuggestion(
                    topic="risk_analysis",
                    description="Analyze risk metrics for the correlated assets",
                    suggested_question=f"What are the risk metrics for these correlated assets?",
                    analysis_type="risk"
                ),
                "performance": AnalysisSuggestion(
                    topic="risk_adjusted_returns",
                    description="Look at risk-adjusted returns (Sharpe ratio) for better comparison",
                    suggested_question=f"What are the risk-adjusted returns for these investments?",
                    analysis_type="risk_adjusted"
                ),
                "diversification": AnalysisSuggestion(
                    topic="sector_analysis",
                    description="Analyze sector allocation for better diversification insights",
                    suggested_question=f"How is this portfolio diversified across sectors?",
                    analysis_type="sector_analysis"
                )
            }
            
            return suggestions_map.get(analysis_type.lower())
            
        except Exception as e:
            logger.error(f"Error suggesting follow-up analysis: {e}")
            return None