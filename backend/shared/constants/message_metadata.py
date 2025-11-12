"""
Metadata constants for the hybrid message handler and related services
"""
from enum import Enum

class QueryType(Enum):
    """Legacy analysis types for backward compatibility"""
    COMPLETE = "complete"           # Full standalone question
    CONTEXTUAL = "contextual"       # "what about QQQ to SPY"
    COMPARATIVE = "comparative"     # "how does that compare"
    PARAMETER = "parameter"         # "what if 3% instead"

class MetadataConstants:
    """Constants for metadata keys to improve maintainability"""
    # Intent keys
    INTENT = "intent"
    MESSAGE_TYPE = "message_type"
    RESPONSE_TYPE = "response_type"
    RESPONSE_STATUS = "status"
    RESPONSE_ERROR = "error"
    
    # Analysis-related keys
    ANALYSIS_TRIGGERED = "analysis_triggered"
    ANALYSIS_QUESTION = "analysis_question"
    HAS_ANALYSIS_SUGGESTION = "has_analysis_suggestion"
    SUGGESTED_ANALYSIS = "suggested_analysis"
    ANALYSIS_SUGGESTION = "analysis_suggestion"
    ORIGINAL_SUGGESTION = "original_suggestion"
    
    # Response types
    RESPONSE_TYPE_CHAT = "chat"
    RESPONSE_TYPE_EDUCATIONAL_CHAT = "educational_chat"
    RESPONSE_TYPE_ANALYSIS = "analysis"
    RESPONSE_TYPE_FOLLOW_UP_CHAT = "follow_up_chat"
    RESPONSE_TYPE_ERROR = "error"
    
    # Message types
    MESSAGE_TYPE_ANALYSIS_CONFIRMATION = "analysis_confirmation"
    MESSAGE_TYPE_EDUCATIONAL_CHAT = "educational_chat"
    MESSAGE_TYPE_FOLLOW_UP_CHAT = "follow_up_chat"
    MESSAGE_TYPE_CHAT = "chat"
    MESSAGE_TYPE_ERROR = "error"
    
    # Intent values
    INTENT_PURE_CHAT = "pure_chat"
    INTENT_EDUCATIONAL = "educational"
    INTENT_ANALYSIS_REQUEST = "analysis_request"
    INTENT_ANALYSIS_CONFIRMATION = "analysis_confirmation"
    INTENT_FOLLOW_UP = "follow_up"
    INTENT_DIRECT_ANALYSIS = "direct_analysis"
    INTENT_CONFIRMED_ANALYSIS = "confirmed_analysis"
    INTENT_CONFIRMATION_WITHOUT_PENDING = "confirmation_without_pending"
    INTENT_ERROR = "error"
    
    # Suggestion keys
    SUGGESTION_TOPIC = "topic"
    SUGGESTION_DESCRIPTION = "description"
    SUGGESTED_QUESTION = "suggested_question"
    ANALYSIS_TYPE = "analysis_type"
    
    # Status values
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    
    # Error and timing keys
    INTERNAL_ERROR = "internal_error"
    PROCESSING_TIME = "processing_time"
    FAILED_AT = "failed_at"
    
    # Other keys
    ERROR = "error"

class MessageIntent(Enum):
    """Message intents for hybrid chat pattern"""
    PURE_CHAT = MetadataConstants.INTENT_PURE_CHAT                    # General conversation
    EDUCATIONAL = MetadataConstants.INTENT_EDUCATIONAL                # Educational about finance
    ANALYSIS_REQUEST = MetadataConstants.INTENT_ANALYSIS_REQUEST      # Direct analysis request
    ANALYSIS_CONFIRMATION = MetadataConstants.INTENT_ANALYSIS_CONFIRMATION  # Confirming analysis suggestion
    FOLLOW_UP = MetadataConstants.INTENT_FOLLOW_UP                   # Follow-up to previous analysis