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
    
    userId: str = Field(default_factory=lambda: str(uuid.uuid4()))
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
    Analysis generated from LLM at /analyze time.
    Stores complete LLM response + execution details.
    Results populated AFTER execution completes.
    """
    
    analysisId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    
    # LLM Response (COMPLETE structure from script_generation or reuse_decision)
    llm_response: Dict[str, Any]
    # {
    #   "status": "success|failed",
    #   "script_name": "...",
    #   "script_content": "...",  (if markdown extraction)
    #   "analysis_description": "...",
    #   "validation_attempts": int,
    #   "execution": {
    #     "script_name": "...",
    #     "parameters": {...}
    #   },
    #   ... any other fields from LLM ...
    # }
    
    # Question that generated this analysis
    question: str
    
    # Script storage reference (after /analyze saves to S3/file)
    script_url: str  # S3 path or local file path
    script_size_bytes: int = 0
    
    # Execution status and results (populated AFTER execution)
    status: ExecutionStatus = ExecutionStatus.PENDING  # pending → running → success/failed
    result: Dict[str, Any] = Field(default_factory=dict)  # Populated after execution
    execution_id: Optional[str] = None  # Links to execution log
    execution_time_ms: Optional[int] = None
    error: Optional[str] = None  # Error message if execution failed
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
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
            {"fields": [("userId", 1), ("created_at", -1)]},
            {"fields": [("status", 1)]},
            {"fields": [("question", "text")]},
            {"fields": [("tags", 1)]},
        ]


# ============================================================================
# CHAT SESSION COLLECTION
# ============================================================================

class ChatSessionModel(BaseModel):
    """Conversation session grouping multiple messages"""
    
    sessionId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    
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
# QUESTION CONTEXT MODEL
# ============================================================================

class QuestionContext(BaseModel):
    """Context output for question processing (expansion and classification)"""
    original_question: str  # User's original question
    expanded_question: Optional[str] = None  # LLM-expanded version
    expansion_confidence: float = 0.0  # Confidence in expansion
    query_type: Optional[QueryType] = None  # Classification: complete, contextual, comparative, parameter


# ============================================================================
# CHAT MESSAGE COLLECTION
# ============================================================================

class ChatMessageModel(BaseModel):
    """Individual message in conversation"""
    
    messageId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sessionId: str
    userId: str
    
    # Message content
    role: RoleType  # user, assistant, system
    content: str  # Original text of the message
    
    # Reference to associated analysis (if any)
    # If this message has an analysis, access execution details via:
    # analysisId → Analysis.executionId → Execution collection
    analysisId: Optional[str] = None  # Links to AnalysisModel in analyses collection
    
    # Question context (for user messages) - output from context service
    questionContext: Optional[QuestionContext] = None
    
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
            {"fields": [("sessionId", 1), ("created_at", 1)]},
            {"fields": [("userId", 1), ("created_at", -1)]},
            {"fields": [("role", 1)]},
            {"fields": [("analysisId", 1)]},
        ]


# ============================================================================
# EXECUTION COLLECTION (Audit Trail)
# ============================================================================

class ExecutionModel(BaseModel):
    """Script execution record for audit and analysis"""
    
    executionId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    sessionId: str
    messageId: str
    
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
            {"fields": [("userId", 1), ("created_at", -1)]},
            {"fields": [("sessionId", 1)]},
            {"fields": [("status", 1)]},
            {"fields": [("started_at", -1)]},
        ]


# ============================================================================
# SAVED ANALYSIS COLLECTION (Reusable Templates)
# ============================================================================

class SavedAnalysisModel(BaseModel):
    """
    Reusable analysis template saved for repeated use with variable parameters.
    
    WORKFLOW:
    1. User runs an analysis (creates AnalysisModel)
    2. User likes it and saves as template (creates SavedAnalysisModel)
    3. Next time: load SavedAnalysisModel → reference AnalysisModel → reuse script
    4. Can override template_variables (e.g., lookback_days: 30 → 60) for reruns
    
    NOT a duplicate - SavedAnalysisModel is a BOOKMARK with metadata for reuse.
    """
    
    savedAnalysisId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    analysisId: str  # Reference to original AnalysisModel (the actual analysis)
    
    # Save metadata
    saved_name: str  # User-friendly name for this saved template
    description: Optional[str] = None
    
    # Reusability tracking
    usage_count: int = 0  # How many times this template has been reused
    last_used_at: Optional[datetime] = None
    
    # Template settings - which parameters can be changed for reruns
    template_variables: Dict[str, Any] = Field(default_factory=dict)
    # e.g., {"lookback_days": "30", "limit": "5", "symbols": ["AAPL", "MSFT"]}
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Organization
    tags: List[str] = Field(default_factory=list)
    category: str = ""
    
    class Config:
        collection = "saved_analyses"
        indexes = [
            {"fields": [("userId", 1), ("created_at", -1)]},
            {"fields": [("userId", 1), ("tags", 1)]},
            {"fields": [("category", 1)]},
        ]


# ============================================================================
# AUDIT LOG COLLECTION
# ============================================================================

class AuditLogModel(BaseModel):
    """System audit trail for compliance and debugging"""
    
    auditLogId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    
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
            {"fields": [("userId", 1), ("created_at", -1)]},
            {"fields": [("action", 1)]},
            {"fields": [("resource_type", 1), ("resource_id", 1)]},
        ]


# ============================================================================
# CACHE COLLECTION
# ============================================================================

class CacheModel(BaseModel):
    """
    Query result caching for performance optimization.
    Avoid re-running expensive analyses.
    """
    
    cacheId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cache_key: str  # Hash of question + parameters
    
    # Cached data
    result: Dict[str, Any]
    analysisId: Optional[str] = None
    
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
