#!/usr/bin/env python3
"""
Progress Message Types for Type-Safe Progress Event Communication

Provides typed classes for sending progress events instead of raw dictionaries.
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ProgressType(str, Enum):
    """Types of progress events"""
    ANALYSIS_PROGRESS = "analysis_progress"
    ANALYSIS_STATUS = "analysis_status"
    EXECUTION_STATUS = "execution_status"


class ProgressLevel(str, Enum):
    """Log levels for progress messages"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"


class ProgressStatus(str, Enum):
    """Status values for progress messages"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ProgressMessage(BaseModel):
    """
    Typed progress message for send_progress_event
    
    Replaces raw dictionaries with type-safe structure
    """
    
    # Core fields (always present)
    type: ProgressType
    message: str
    
    # Status and level
    status: Optional[ProgressStatus] = None
    level: ProgressLevel = ProgressLevel.INFO
    
    # ID references
    job_id: Optional[str] = None
    message_id: Optional[str] = None
    execution_id: Optional[str] = None
    analysis_id: Optional[str] = None
    
    # Logging control
    log_to_message: bool = False
    
    # Timestamp (auto-generated)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility with JSON serialization"""
        data = self.model_dump(exclude_none=True)
        
        # Convert datetime to ISO string for JSON serialization
        if 'timestamp' in data and isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        
        return data


# Factory functions for common message types
def analysis_progress_message(
    message: str,
    job_id: Optional[str] = None,
    message_id: Optional[str] = None,
    status: Optional[ProgressStatus] = None,
    level: ProgressLevel = ProgressLevel.INFO,
    log_to_message: bool = True
) -> ProgressMessage:
    """Create an analysis progress message"""
    return ProgressMessage(
        type=ProgressType.ANALYSIS_PROGRESS,
        message=message,
        job_id=job_id,
        message_id=message_id,
        status=status,
        level=level,
        log_to_message=log_to_message
    )


def analysis_status_message(
    message: str,
    status: ProgressStatus,
    job_id: Optional[str] = None,
    message_id: Optional[str] = None,
    level: ProgressLevel = ProgressLevel.INFO
) -> ProgressMessage:
    """Create an analysis status message"""
    return ProgressMessage(
        type=ProgressType.ANALYSIS_STATUS,
        message=message,
        status=status,
        job_id=job_id,
        message_id=message_id,
        level=level,
        log_to_message=True
    )


def execution_status_message(
    message: str,
    status: ProgressStatus,
    execution_id: Optional[str] = None,
    analysis_id: Optional[str] = None,
    level: ProgressLevel = ProgressLevel.INFO
) -> ProgressMessage:
    """Create an execution status message"""
    return ProgressMessage(
        type=ProgressType.EXECUTION_STATUS,
        message=message,
        status=status,
        execution_id=execution_id,
        analysis_id=analysis_id,
        level=level,
        log_to_message=True
    )