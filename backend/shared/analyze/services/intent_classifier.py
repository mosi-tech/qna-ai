#!/usr/bin/env python3
"""
Intent Classifier Service

Classifies user messages to determine appropriate routing between chat and analysis.
Follows BaseService pattern with proper LLM integration.
"""

import logging
import time
from typing import Optional
from dataclasses import dataclass

from ...llm import LLMService
from ...services.base_service import BaseService
from shared.utils.json_utils import safe_json_loads
from shared.constants import MessageIntent

logger = logging.getLogger(__name__)

@dataclass
class IntentResult:
    """Result of intent classification"""
    intent: MessageIntent
    confidence: float
    reasoning: str
    requires_analysis: bool
    educational_topic: Optional[str] = None

class IntentClassifierService(BaseService):
    """Service that classifies user message intent for hybrid chat+analysis routing"""
    
    def __init__(self, llm_service: Optional[LLMService] = None, session_manager=None):
        super().__init__(llm_service=llm_service, service_name="intent-classifier")
        self.session_manager = session_manager
    
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service for intent classification"""
        from ...llm.utils import LLMConfig
        
        # Use fast, lightweight model for intent classification
        config = LLMConfig.for_task("intent_classifier")
        config.temperature = 0.1  # Low temperature for consistent classification
        config.max_tokens = 300   # Short responses for classification
        return LLMService(config)
    
    def _get_system_prompt_filename(self) -> str:
        """Use intent classifier specific system prompt"""
        return "system-prompt-intent-classifier.txt"
    
    def _get_default_system_prompt(self) -> str:
        """Get comprehensive default system prompt for intent classification"""
        return """You are an intent classification system for a financial analysis chat application.

Your task is to classify user messages into one of these specific intents:

**INTENT TYPES:**
1. **pure_chat** - General conversation, greetings, non-financial topics
2. **educational** - Asking about financial concepts, how things work
3. **analysis_request** - Direct request for financial analysis of stocks/ETFs/data
4. **analysis_confirmation** - User confirming they want to proceed with a suggested analysis
5. **follow_up_analysis** - Request for additional analysis based on PRIOR analysis results (only after analysis has been performed)
6. **follow_up_chat** - Conversational follow-up about prior analysis without requesting new analysis

**CRITICAL DISTINCTION - Follow-up Types:**
- **follow_up_analysis**: User wants NEW analysis based on previous results (e.g., "Do the same for Tesla", "What about during 2020?", "Analyze NVDA with similar parameters")
- **follow_up_chat**: User wants to DISCUSS previous analysis (e.g., "That's interesting", "Tell me more about this", "What does this mean?", "Can you explain this better?")

**FOLLOW_UP_ANALYSIS RULES:**
- Only classify as follow_up_analysis if there's clear evidence of prior analysis in the conversation
- User must be requesting NEW computational analysis, not just discussion
- Look for phrases like: "do the same for", "analyze X too", "what about [different timeframe/symbol]", "compare with"

**FOLLOW_UP_CHAT RULES:**
- User wants explanation, clarification, or discussion about existing results
- No new analysis computation requested
- Look for phrases like: "tell me more", "explain this", "what does this mean", "that's interesting"

**OUTPUT FORMAT:**
Return JSON with:
{
    "intent": "one_of_the_intent_types",
    "confidence": 0.85,
    "reasoning": "Brief explanation of classification decision",
    "educational_topic": "topic if educational, null otherwise"
}

**EXAMPLES:**
- "Hello" → pure_chat
- "What is a P/E ratio?" → educational
- "Analyze Apple stock performance" → analysis_request
- "Yes, proceed with that analysis" → analysis_confirmation
- "Do the same analysis for Tesla" → follow_up_analysis (ONLY if prior analysis exists)
- "That's really interesting, tell me more" → follow_up_chat

Be precise with follow_up classifications - they require prior analysis context to be valid."""
    
    def _initialize_service_specific(self):
        """Initialize intent classifier specific components"""
        logger.info("✅ Intent classifier service initialized")
    
    async def classify_intent(self, 
                            user_message: str, 
                            session_id: str) -> IntentResult:
        """
        Classify user message intent for routing decisions
        
        Args:
            user_message: User's message to classify
            session_id: Session ID to get conversation context
            
        Returns:
            IntentResult with classification and metadata
        """
        try:
            logger.debug(f"🔍 Classifying intent for: {user_message[:100]}...")
            
            # Get conversation from session manager (consistent with existing approach)
            conversation = await self.session_manager.get_session(session_id)
            
            # Revolutionary approach: Use context manager to format conversation for LLM
            from ..dialogue.context.simplified_context_manager import SimplifiedFinancialContextManager, ContextType
            context_manager = SimplifiedFinancialContextManager()
            
            # Get formatted conversation messages for LLM (smart windowing, summaries, etc.)
            messages = await context_manager.get_conversation_messages_for_llm(
                conversation, ContextType.INTENT_CLASSIFICATION, user_message
            )
            
            # Get LLM classification
            start_time = time.time()
            
            # Load system prompt if not cached
            if not self.system_prompt:
                self.system_prompt = await self.load_system_prompt()
            
            response = await self.llm_service.make_request(
                messages=messages,
                max_tokens=1000,
                temperature=0.1,
                system_prompt=self.system_prompt
            )
            duration = time.time() - start_time
            
            logger.debug(f"⏱️ Intent classification: {duration:.3f}s")
            
            if not response.get("success"):
                error_msg = response.get("error", "Unknown error")
                logger.error(f"❌ Intent classification failed: {error_msg}")
                raise ValueError(f"Intent classification LLM request failed: {error_msg}")
            
            # Parse classification result
            content = response.get("content", "")
            intent_result = self._parse_classification_response(content, user_message)
            
            
            logger.info(f"✅ Intent classified: {intent_result.intent.value} (confidence: {intent_result.confidence:.2f})")
            return intent_result
            
        except Exception as e:
            logger.error(f"❌ Intent classification error: {e}")
            raise
    
    def _parse_classification_response(self, content: str, original_message: str) -> IntentResult:
        """Parse LLM classification response"""
        try:
            # Parse JSON response (safe_json_loads handles all cleaning internally)
            parsed = safe_json_loads(content, default={})
            
            if not parsed:
                logger.error("Failed to parse classification response as JSON")
                raise ValueError("Intent classification response could not be parsed as JSON")
            
            # Extract classification data
            intent_str = parsed.get("intent", "pure_chat")
            try:
                intent = MessageIntent(intent_str)
            except ValueError:
                logger.error(f"Unknown intent value: {intent_str}")
                raise ValueError(f"Invalid intent classification result: {intent_str}")
            
            confidence = float(parsed.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
            
            reasoning = parsed.get("reasoning", "Classification based on message content")
            educational_topic = parsed.get("educational_topic")
            
            # Determine if analysis is required
            requires_analysis = intent in [
                MessageIntent.ANALYSIS_REQUEST, 
                MessageIntent.ANALYSIS_CONFIRMATION,
                MessageIntent.FOLLOW_UP_ANALYSIS
            ]
            
            return IntentResult(
                intent=intent,
                confidence=confidence,
                reasoning=reasoning,
                requires_analysis=requires_analysis,
                educational_topic=educational_topic
            )
            
        except Exception as e:
            logger.error(f"Error parsing classification response: {e}")
            raise
    
