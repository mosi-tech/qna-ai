"""
MongoDB Schema Definitions using Pydantic
All collections support both immediate storage and reuse of analyses
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import uuid


class BaseMongoModel(BaseModel):
    """Base model with automatic snake_case ↔ camelCase conversion for MongoDB"""
    model_config = ConfigDict(
        populate_by_name=True  # Accept both snake_case and camelCase in deserialization
    )


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


class ExecutionType(str, Enum):
    """Execution type classification"""
    PRIMARY = "primary"       # Original execution from chat message
    USER_RERUN = "user_rerun" # User-initiated re-run with different parameters
    SCHEDULED = "scheduled"   # System-scheduled execution
    API = "api"              # Direct API execution


class RoleType(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ProgressLogEntry(BaseMongoModel):
    """Individual progress log entry within a message"""
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str  # "info", "success", "warning", "error"
    details: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# USER COLLECTION
# ============================================================================

class UserModel(BaseMongoModel):
    """User account and profile"""
    
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='userId')
    email: str
    username: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, alias='createdAt')
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias='updatedAt')
    last_login: Optional[datetime] = Field(None, alias='lastLogin')
    
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
            {"fields": [("createdAt", -1)]},
        ]


# ============================================================================
# ANALYSIS COLLECTION
# ============================================================================

class AnalysisResultBody(BaseMongoModel):
    """Individual data point in analysis result"""
    key: str  # unique identifier within analysis
    value: Any  # actual value (string, number, object, array)
    description: str  # explanation for retail investors


class AnalysisModel(BaseMongoModel):
    """
    Analysis generated from LLM at /analyze time.
    Stores complete LLM response template (not execution results).
    Can be executed multiple times with different parameters.
    """

    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='analysisId')
    user_id: str = Field(..., alias='userId')
    
    # LLM Response (COMPLETE structure from script_generation or reuse_decision)
    llm_response: Dict[str, Any] = Field(..., alias='llmResponse')
    
    # Question that generated this analysis
    question: str
    
    # Top-level extracted fields for easier access (promoted from llmResponse)
    description: Optional[str] = Field(None)  # Extracted from llmResponse.analysis_description
    parameters: Optional[Dict[str, Any]] = Field(None)  # Extracted from llmResponse.execution.parameters
    parameter_schema: Optional[List[Dict[str, Any]]] = Field(None, alias='parameterSchema')  # Generated parameter form schema
    
    # Script storage reference (after /analyze saves to S3/file)
    script_url: str = Field(..., alias='scriptUrl')  # S3 path or local file path
    
    # Link back to the chat message that created this analysis
    created_message_id: Optional[str] = Field(None, alias='createdMessageId')
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, alias='createdAt')
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias='updatedAt')
    last_used_at: Optional[datetime] = Field(None, alias='lastUsedAt')
    
    # Tags for organization
    tags: List[str] = Field(default_factory=list)
    
    # Sharing and reusability
    is_public: bool = Field(False, alias='isPublic')  # Can other users access this analysis?
    usage_count: int = Field(0, alias='usageCount')   # How many times this analysis has been reused
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        collection = "analyses"
        indexes = [
            {"fields": [("userId", 1), ("createdAt", -1)]},
            {"fields": [("question", "text")]},
            {"fields": [("tags", 1)]},
            {"fields": [("createdMessageId", 1)]},
            {"fields": [("isPublic", 1)]},
            {"fields": [("isPublic", 1), ("usageCount", -1)]},  # Find popular public analyses
        ]


# ============================================================================
# CHAT SESSION COLLECTION
# ============================================================================

class ChatSessionModel(BaseMongoModel):
    """Conversation session grouping multiple messages"""
    
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='sessionId')
    user_id: str = Field(..., alias='userId')
    
    # Session metadata
    title: str = "Untitled Conversation"
    description: Optional[str] = None
    
    # Message tracking
    message_count: int = Field(0, alias='messageCount')
    
    # Analysis references (quick access to analyses in this session)
    analysis_ids: List[str] = Field(default_factory=list, alias='analysisIds')
    # References to analyses created in this session
    
    # Context tracking
    context_summary: Dict[str, Any] = Field(default_factory=dict, alias='contextSummary')
    # {
    #   "last_query": "What is AAPL current price?",
    #   "last_query_type": "complete",
    #   "last_analysis": "Price snapshot",
    #   "turn_count": 5
    # }
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, alias='createdAt')
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias='updatedAt')
    last_message_at: Optional[datetime] = Field(None, alias='lastMessageAt')
    
    # Status
    is_archived: bool = Field(False, alias='isArchived')
    is_favorited: bool = Field(False, alias='isFavorited')
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        collection = "chat_sessions"
        indexes = [
            {"fields": [("userId", 1), ("createdAt", -1)]},
            {"fields": [("userId", 1), ("isArchived", 1)]},
            {"fields": [("lastMessageAt", -1)]},
            {"fields": [("title", "text")]},
        ]


# ============================================================================
# CHAT MESSAGE COLLECTION
# ============================================================================

class ChatMessageModel(BaseMongoModel):
    """Individual message in conversation"""
    
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='messageId')
    session_id: str = Field(..., alias='sessionId')
    user_id: str = Field(..., alias='userId')
    
    # Message content
    role: RoleType  # user, assistant, system
    content: str  # Original text of the message
    
    # Reference to associated analysis and execution (if any)
    # - analysis_id: which analysis/script was used
    # - execution_id: which specific execution produced this message
    analysis_id: Optional[str] = Field(None, alias='analysisId')
    execution_id: Optional[str] = Field(None, alias='executionId')
    
    # Progress logs for real-time tracking (NEW for async analysis)
    logs: List[ProgressLogEntry] = Field(default_factory=list)
    
    # Message metadata
    # Contains response-type specific data:
    # - For user messages: response_type, original_question, query_type
    # - For assistant messages: response_type and response-specific fields
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, alias='createdAt')
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias='updatedAt')
    
    # Context from session
    message_index: int = Field(0, alias='messageIndex')  # Position in conversation
    
    class Config:
        collection = "chat_messages"
        indexes = [
            {"fields": [("sessionId", 1), ("createdAt", 1)]},
            {"fields": [("userId", 1), ("createdAt", -1)]},
            {"fields": [("role", 1)]},
            {"fields": [("analysisId", 1)]},
            {"fields": [("executionId", 1)]},
        ]


# ============================================================================
# EXECUTION COLLECTION (Audit Trail)
# ============================================================================

class ExecutionModel(BaseMongoModel):
    """Script execution record for audit and analysis"""
    
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='executionId')
    user_id: str = Field(..., alias='userId')
    
    # Session and message context (optional - null if executed from UI, not from chat)
    session_id: Optional[str] = Field(None, alias='sessionId')
    created_message_id: Optional[str] = Field(None, alias='createdMessageId')
    
    # Analysis being executed
    analysis_id: str = Field(..., alias='analysisId')
    
    # Input
    question: str
    generated_script: str = Field(..., alias='generatedScript')
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution details
    execution_type: ExecutionType = Field(ExecutionType.PRIMARY, alias='executionType')
    status: ExecutionStatus
    started_at: datetime = Field(default_factory=datetime.utcnow, alias='startedAt')
    completed_at: Optional[datetime] = Field(None, alias='completedAt')
    execution_time_ms: int = Field(0, alias='executionTimeMs')
    
    # Parent execution reference (for re-runs)
    parent_execution_id: Optional[str] = Field(None, alias='parentExecutionId')
    
    # Output
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    
    # MCP tracking
    mcp_calls: List[str] = Field(default_factory=list, alias='mcpCalls')
    mcp_errors: Dict[str, str] = Field(default_factory=dict, alias='mcpErrors')
    
    # Resource usage
    memory_used_mb: Optional[float] = Field(None, alias='memoryUsedMb')
    cpu_percent: Optional[float] = Field(None, alias='cpuPercent')
    
    # Caching
    cache_hit: bool = Field(False, alias='cacheHit')
    cache_key: Optional[str] = Field(None, alias='cacheKey')
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        collection = "executions"
        indexes = [
            {"fields": [("userId", 1), ("startedAt", -1)]},
            {"fields": [("analysisId", 1)]},
            {"fields": [("sessionId", 1)]},
            {"fields": [("createdMessageId", 1)]},
            {"fields": [("status", 1)]},
            {"fields": [("executionType", 1)]},
            {"fields": [("parentExecutionId", 1)]},
            {"fields": [("analysisId", 1), ("executionType", 1)]},
            {"fields": [("startedAt", -1)]},
        ]


# ============================================================================
# SAVED ANALYSIS COLLECTION (Reusable Templates)
# ============================================================================

class SavedAnalysisModel(BaseMongoModel):
    """
    Reusable analysis template saved for repeated use with variable parameters.
    
    WORKFLOW:
    1. User runs an analysis (creates AnalysisModel)
    2. User likes it and saves as template (creates SavedAnalysisModel)
    3. Next time: load SavedAnalysisModel → reference AnalysisModel → reuse script
    4. Can override template_variables (e.g., lookback_days: 30 → 60) for reruns
    
    NOT a duplicate - SavedAnalysisModel is a BOOKMARK with metadata for reuse.
    """
    
    saved_analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='savedAnalysisId')
    user_id: str = Field(..., alias='userId')
    analysis_id: str = Field(..., alias='analysisId')  # Reference to original AnalysisModel (the actual analysis)
    
    # Save metadata
    saved_name: str  # User-friendly name for this saved template
    description: Optional[str] = None
    
    # Reusability tracking
    usage_count: int = Field(0, alias='usageCount')  # How many times this template has been reused
    last_used_at: Optional[datetime] = Field(None, alias='lastUsedAt')
    
    # Template settings - which parameters can be changed for reruns
    template_variables: Dict[str, Any] = Field(default_factory=dict, alias='templateVariables')
    # e.g., {"lookback_days": "30", "limit": "5", "symbols": ["AAPL", "MSFT"]}
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, alias='createdAt')
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias='updatedAt')
    
    # Organization
    tags: List[str] = Field(default_factory=list)
    category: str = ""
    
    class Config:
        collection = "saved_analyses"
        indexes = [
            {"fields": [("userId", 1), ("createdAt", -1)]},
            {"fields": [("userId", 1), ("tags", 1)]},
            {"fields": [("category", 1)]},
        ]


# ============================================================================
# AUDIT LOG COLLECTION
# ============================================================================

class AuditLogModel(BaseMongoModel):
    """System audit trail for compliance and debugging"""
    
    audit_log_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='auditLogId')
    user_id: str = Field(..., alias='userId')
    
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
    ip_address: Optional[str] = Field(None, alias='ipAddress')
    user_agent: Optional[str] = Field(None, alias='userAgent')
    
    # Status
    success: bool = True
    error_message: Optional[str] = Field(None, alias='errorMessage')
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, alias='createdAt')
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        collection = "audit_logs"
        indexes = [
            {"fields": [("userId", 1), ("createdAt", -1)]},
            {"fields": [("action", 1)]},
            {"fields": [("resourceType", 1), ("resourceId", 1)]},
        ]


# ============================================================================
# CACHE COLLECTION
# ============================================================================

class CacheModel(BaseMongoModel):
    """
    Query result caching for performance optimization.
    Avoid re-running expensive analyses.
    """
    
    cache_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='cacheId')
    cache_key: str = Field(..., alias='cacheKey')  # Hash of question + parameters
    
    # Cached data
    result: Dict[str, Any]
    analysis_id: Optional[str] = Field(None, alias='analysisId')
    
    # Metadata
    hit_count: int = Field(0, alias='hitCount')
    created_at: datetime = Field(default_factory=datetime.utcnow, alias='createdAt')
    expires_at: datetime = Field(..., alias='expiresAt')  # TTL for cache (24 hours default)
    last_used_at: datetime = Field(default_factory=datetime.utcnow, alias='lastUsedAt')
    
    class Config:
        collection = "cache"
        indexes = [
            {"fields": [("cacheKey", 1)]},
            {"fields": [("expiresAt", 1)], "expireAfterSeconds": 0},
            # MongoDB TTL index - auto-delete expired docs
        ]
