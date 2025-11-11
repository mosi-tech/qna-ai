#!/usr/bin/env python3
"""
Intent Classifier Service

Classifies user messages to determine appropriate routing between chat and analysis.
Follows BaseService pattern with proper LLM integration.
"""

import logging
import time
from typing import Optional
from enum import Enum
from dataclasses import dataclass

from ...llm import LLMService
from ...services.base_service import BaseService
from shared.utils.json_utils import safe_json_loads

logger = logging.getLogger(__name__)

class MessageIntent(Enum):
    """Classification of user message intent"""
    PURE_CHAT = "pure_chat"           # General conversation, greetings
    EDUCATIONAL = "educational"        # Wants to learn about financial concepts
    ANALYSIS_REQUEST = "analysis_request"  # Direct request for analysis
    ANALYSIS_CONFIRMATION = "analysis_confirmation"  # Confirming suggested analysis
    FOLLOW_UP = "follow_up"           # Follow-up on previous analysis

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
                max_tokens=300,
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
            requires_analysis = intent in [MessageIntent.ANALYSIS_REQUEST, MessageIntent.ANALYSIS_CONFIRMATION]
            
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
    
