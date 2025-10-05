"""
API Models and Schemas
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str
    model: Optional[str] = None  # Will use provider default if not specified
    enable_caching: Optional[bool] = True  # Controls whether to use caching


class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str