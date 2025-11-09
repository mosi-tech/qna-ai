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
            conversation = None
            if self.session_manager and session_id:
                try:
                    conversation = await self.session_manager.get_session(session_id)
                except Exception as e:
                    logger.warning(f"⚠️ Could not get session from session manager: {e}")
            
            # Prepare context for classification
            context_info = self._prepare_classification_context(conversation)
            
            # Create classification prompt
            classification_prompt = self._create_classification_prompt(user_message, context_info)
            
            # Get LLM classification
            start_time = time.time()
            messages = [{"role": "user", "content": classification_prompt}]
            
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
    
    def _prepare_classification_context(self, conversation) -> str:
        """Prepare context information for classification using ConversationStore"""
        context_parts = []
        
        if not conversation or not hasattr(conversation, 'messages'):
            return "No previous context"
        
        # Get context summary from ConversationStore (consistent with existing approach)
        context_summary = conversation.get_context_summary()
        
        # Add conversation context
        if context_summary.get("has_history"):
            context_info = []
            if context_summary.get("last_query"):
                last_query = context_summary['last_query']
                # Allow longer queries for better context
                if len(last_query) > 300:
                    last_query = last_query[:300] + "..."
                context_info.append(f"Last query: {last_query}")
            if context_summary.get("last_analysis"):
                last_analysis = context_summary['last_analysis']
                # Keep more analysis context since it's critical for intent classification
                if len(last_analysis) > 500:
                    last_analysis = last_analysis[:500] + "..."
                context_info.append(f"Previous analysis: {last_analysis}")
            if context_summary.get("message_count"):
                context_info.append(f"Message count: {context_summary['message_count']}")
            
            if context_info:
                context_parts.append(f"CONVERSATION CONTEXT:\\n{'; '.join(context_info)}")
        
        # Add recent messages for more detailed context
        if hasattr(conversation, 'messages') and conversation.messages:
            recent_messages = conversation.get_messages(limit=6)  # Last 6 messages (3 exchanges)
            message_texts = []
            for message in recent_messages:
                if hasattr(message, 'role'):
                    role = message.role
                    content = message.content
                    
                    # Format based on message type
                    if role == "user":
                        # Keep user queries reasonably short but not too truncated
                        if len(content) > 200:
                            content = content[:200] + "..."
                        message_texts.append(f"User: {content}")
                    
                    elif role == "assistant":
                        # Include FULL assistant responses (especially important for analysis suggestions)
                        response_label = "Assistant"
                        if hasattr(message, 'message_type') and message.message_type:
                            if message.message_type == "educational_chat":
                                response_label = "Assistant (Educational)"
                            elif message.message_type in ["script_generation", "reuse_decision"]:
                                response_label = "Assistant (Analysis Result)"
                            elif message.message_type == "analysis_confirmation":
                                response_label = "Assistant (Analysis Started)"
                        
                        # Use full assistant response - critical for analysis suggestions at the end!
                        assistant_text = content
                        # Only truncate if extremely long (>2000 chars) to preserve analysis suggestions
                        if len(assistant_text) > 2000:
                            # Smart truncation: keep end of message where analysis suggestions are
                            assistant_text = "..." + assistant_text[-1800:]
                        
                        message_texts.append(f"{response_label}: {assistant_text}")
            
            if message_texts:
                context_parts.append(f"RECENT CONVERSATION:\\n{chr(10).join(message_texts)}")
        
        return "\\n\\n".join(context_parts) if context_parts else "No previous context"
    
    def _create_classification_prompt(self, user_message: str, context_info: str) -> str:
        """Create the classification prompt"""
        return f"""CONTEXT:
{context_info}

USER MESSAGE: {user_message}

Please classify this message and respond in JSON format with your analysis."""
    
    def _parse_classification_response(self, content: str, original_message: str) -> IntentResult:
        """Parse LLM classification response"""
        try:
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
    
    def _create_fallback_intent(self, user_message: str) -> IntentResult:
        """Create fallback intent classification using simple heuristics"""
        message_lower = user_message.lower()
        
        # Simple keyword-based classification
        if any(word in message_lower for word in ["hello", "hi", "thanks", "thank you", "bye"]):
            intent = MessageIntent.PURE_CHAT
            reasoning = "Greeting or social interaction detected"
        elif any(word in message_lower for word in ["yes", "sure", "ok", "please", "go ahead", "run it"]):
            intent = MessageIntent.ANALYSIS_CONFIRMATION
            reasoning = "Confirmation language detected"
        elif any(word in message_lower for word in ["analyze", "analysis", "show me", "calculate", "compare"]):
            intent = MessageIntent.ANALYSIS_REQUEST
            reasoning = "Analysis request keywords detected"
        elif any(word in message_lower for word in ["what is", "tell me about", "explain", "how does"]):
            intent = MessageIntent.EDUCATIONAL
            reasoning = "Educational question pattern detected"
        else:
            intent = MessageIntent.FOLLOW_UP
            reasoning = "Default classification - treating as follow-up"
        
        return IntentResult(
            intent=intent,
            confidence=0.7,  # Moderate confidence for heuristic classification
            reasoning=f"Fallback classification: {reasoning}",
            requires_analysis=(intent in [MessageIntent.ANALYSIS_REQUEST, MessageIntent.ANALYSIS_CONFIRMATION])
        )
    
