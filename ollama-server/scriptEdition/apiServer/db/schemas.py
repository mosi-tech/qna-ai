"""
MongoDB Schema Definitions using Pydantic
All collections support both immediate storage and reuse of analyses
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class QueryType(str, Enum):
    """Query classification"""
    COMPLETE = "complete"
    CONTEXTUAL = "contextual"
    COMPARATIVE = "comparative"
    PARAMETER = "parameter"


class ExecutionStatus(str, Enum):
    """Execution status tracking"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class RoleType(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ============================================================================
# USER COLLECTION
# ============================================================================

class UserModel(BaseModel):
    """User account and profile"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # User preferences
    preferences: Dict[str, Any] = Field(default_factory=dict)
    # e.g., {"timezone": "UTC", "theme": "dark", "default_lookback_days": 30}
    
    # Metadata for flexibility
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # e.g., {"subscription_tier": "free", "api_quota": 1000}
    
    class Config:
        collection = "users"
        indexes = [
            {"fields": [("email", 1)], "unique": True},
            {"fields": [("created_at", -1)]},
        ]


# ============================================================================
# ANALYSIS COLLECTION
# ============================================================================

class AnalysisResultBody(BaseModel):
    """Individual data point in analysis result"""
    key: str  # unique identifier within analysis
    value: Any  # actual value (string, number, object, array)
    description: str  # explanation for retail investors


class AnalysisModel(BaseModel):
    """
    Standalone analysis that can be saved and reused.
    When user runs a query and gets analysis output, it's stored here
    and can be directly executed without LLM interaction.
    """
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # reference to user
    
    # Analysis identification
    title: str  # e.g., "AAPL Volatility Analysis"
    description: str  # what this analysis represents
    category: str  # e.g., "technical_analysis", "portfolio_optimization"
    
    # Core output (what gets displayed to user)
    result: Dict[str, Any] = Field(default_factory=dict)
    # {
    #   "description": "Overall explanation",
    #   "body": [
    #     {"key": "rank_1", "value": "NVDA", "description": "..."},
    #     ...
    #   ]
    # }
    
    # Metadata for reusability
    parameters: Dict[str, Any] = Field(default_factory=dict)
    # Original parameters used to generate this analysis
    # e.g., {"lookback_days": 30, "limit": 5, "min_volume": 1000000}
    
    # Execution details
    mcp_calls: List[str] = Field(default_factory=list)
    # ["alpaca_market_screener_most_actives", "calculate_volatility"]
    
    generated_script: Optional[str] = None
    # Full Python script that was executed (optional, for reference)
    
    execution_time_ms: int = 0
    data_sources: List[str] = Field(default_factory=list)
    # ["Alpaca Market Data", "Technical Analysis Engine"]
    
    # Versioning and reusability
    version: int = 1
    is_template: bool = False  # If true, can be used as template for similar queries
    similar_queries: List[str] = Field(default_factory=list)
    # List of questions that can use this analysis
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None
    
    # Tags for organization
    tags: List[str] = Field(default_factory=list)
    # ["volatility", "stock-screening", "top-5"]
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        collection = "analyses"
        indexes = [
            {"fields": [("user_id", 1), ("created_at", -1)]},
            {"fields": [("category", 1)]},
            {"fields": [("is_template", 1)]},
            {"fields": [("tags", 1)]},
            {"fields": [("title", "text"), ("description", "text")]},
        ]


# ============================================================================
# CHAT SESSION COLLECTION
# ============================================================================

class ChatSessionModel(BaseModel):
    """Conversation session grouping multiple messages"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Session metadata
    title: str = "Untitled Conversation"
    description: Optional[str] = None
    
    # Message tracking
    message_count: int = 0
    
    # Analysis references (quick access to analyses in this session)
    analysis_ids: List[str] = Field(default_factory=list)
    # References to analyses created in this session
    
    # Context tracking
    context_summary: Dict[str, Any] = Field(default_factory=dict)
    # {
    #   "last_query": "What is AAPL current price?",
    #   "last_query_type": "complete",
    #   "last_analysis": "Price snapshot",
    #   "turn_count": 5
    # }
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None
    
    # Status
    is_archived: bool = False
    is_favorited: bool = False
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        collection = "chat_sessions"
        indexes = [
            {"fields": [("user_id", 1), ("created_at", -1)]},
            {"fields": [("user_id", 1), ("is_archived", 1)]},
            {"fields": [("last_message_at", -1)]},
            {"fields": [("title", "text")]},
        ]


# ============================================================================
# CHAT MESSAGE COLLECTION
# ============================================================================

class ChatMessageModel(BaseModel):
    """Individual message in conversation with full analysis storage"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    
    # Message content
    role: RoleType  # user, assistant, system
    content: str  # Original text of the message
    
    # Analysis Storage (KEY FEATURE)
    # When LLM generates analysis, store complete output here
    analysis: Optional[AnalysisModel] = None
    # If this is an assistant message with generated analysis, store full object
    # Allows direct replay/reuse without LLM
    
    analysis_id: Optional[str] = None
    # Reference to AnalysisModel if analysis is saved separately
    
    # Query metadata (for user messages)
    query_type: Optional[QueryType] = None
    original_question: Optional[str] = None  # Before expansion
    expanded_question: Optional[str] = None  # After LLM expansion
    expansion_confidence: float = 0.0
    
    # Script metadata (for assistant messages with code)
    generated_script: Optional[str] = None
    script_explanation: Optional[str] = None
    mcp_calls: List[str] = Field(default_factory=list)
    
    # Execution metadata (for assistant messages)
    execution_id: Optional[str] = None
    execution_status: Optional[ExecutionStatus] = None
    execution_time_ms: Optional[int] = None
    execution_error: Optional[str] = None
    
    # Message metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # e.g., {"client_version": "1.0", "user_agent": "..."}
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Context from session
    message_index: int = 0  # Position in conversation
    
    class Config:
        collection = "chat_messages"
        indexes = [
            {"fields": [("session_id", 1), ("created_at", 1)]},
            {"fields": [("user_id", 1), ("created_at", -1)]},
            {"fields": [("role", 1)]},
            {"fields": [("analysis_id", 1)]},
        ]


# ============================================================================
# EXECUTION COLLECTION (Audit Trail)
# ============================================================================

class ExecutionModel(BaseModel):
    """Script execution record for audit and analysis"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    message_id: str
    
    # Input
    question: str
    generated_script: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution details
    status: ExecutionStatus
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    execution_time_ms: int = 0
    
    # Output
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    
    # MCP tracking
    mcp_calls: List[str] = Field(default_factory=list)
    mcp_errors: Dict[str, str] = Field(default_factory=dict)  # {call_name: error}
    
    # Resource usage
    memory_used_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    
    # Caching
    cache_hit: bool = False
    cache_key: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        collection = "executions"
        indexes = [
            {"fields": [("user_id", 1), ("created_at", -1)]},
            {"fields": [("session_id", 1)]},
            {"fields": [("status", 1)]},
            {"fields": [("started_at", -1)]},
        ]


# ============================================================================
# SAVED ANALYSIS COLLECTION (Reusable Templates)
# ============================================================================

class SavedAnalysisModel(BaseModel):
    """
    Saved analysis available for direct execution.
    Users can save analyses and run them again with different parameters
    without LLM regeneration, improving performance.
    """
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    analysis_id: str  # Reference to original AnalysisModel
    
    # Save metadata
    saved_name: str  # User-friendly name
    description: Optional[str] = None
    
    # Reusability tracking
    usage_count: int = 0
    last_used_at: Optional[datetime] = None
    
    # Template settings
    is_template: bool = True
    template_variables: Dict[str, Any] = Field(default_factory=dict)
    # Which parameters can be changed for reruns
    # e.g., {"lookback_days": "30", "limit": "5"}
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Organization
    tags: List[str] = Field(default_factory=list)
    category: str = ""
    
    class Config:
        collection = "saved_analyses"
        indexes = [
            {"fields": [("user_id", 1), ("created_at", -1)]},
            {"fields": [("user_id", 1), ("is_template", 1)]},
            {"fields": [("tags", 1)]},
        ]


# ============================================================================
# AUDIT LOG COLLECTION
# ============================================================================

class AuditLogModel(BaseModel):
    """System audit trail for compliance and debugging"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Action tracking
    action: str
    # e.g., "question_submitted", "script_generated", "execution_started",
    #       "analysis_saved", "session_created", "execution_failed"
    
    resource_type: str
    # "message", "execution", "analysis", "session"
    
    resource_id: str
    # ID of affected resource
    
    # Changes
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    # What changed
    
    # Request context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Status
    success: bool = True
    error_message: Optional[str] = None
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        collection = "audit_logs"
        indexes = [
            {"fields": [("user_id", 1), ("created_at", -1)]},
            {"fields": [("action", 1)]},
            {"fields": [("resource_type", 1), ("resource_id", 1)]},
            {"fields": [("created_at", -1)]},
        ]


# ============================================================================
# CACHE COLLECTION
# ============================================================================

class CacheModel(BaseModel):
    """
    Query result caching for performance optimization.
    Avoid re-running expensive analyses.
    """
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cache_key: str  # Hash of question + parameters
    
    # Cached data
    result: Dict[str, Any]
    analysis_id: Optional[str] = None
    
    # Metadata
    hit_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime  # TTL for cache (24 hours default)
    last_used_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        collection = "cache"
        indexes = [
            {"fields": [("cache_key", 1)]},
            {"fields": [("expires_at", 1)], "expireAfterSeconds": 0},
            # MongoDB TTL index - auto-delete expired docs
        ]
