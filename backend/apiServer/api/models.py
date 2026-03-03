"""
API Models and Schemas
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str
    user_id: Optional[str] = None  # User identifier for chat history and analysis tracking
    model: Optional[str] = None  # Will use provider default if not specified
    enable_caching: Optional[bool] = True  # Controls whether to use caching
    session_id: Optional[str] = None  # Set from URL path in /sessions/{session_id}/chat
    auto_expand: Optional[bool] = True  # Auto-expand contextual queries
    auto_execute: Optional[bool] = True  # Auto-execute script immediately after analysis


class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str