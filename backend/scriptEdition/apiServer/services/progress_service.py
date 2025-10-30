"""
Progress streaming service for real-time execution updates
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger("progress-service")


class ProgressLevel(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class ExecutionStatus(str, Enum):
    """Execution status values for SSE updates"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ProgressEvent:
    """Represents a single progress event"""

    def __init__(
        self,
        level: ProgressLevel,
        message: str,
        step: Optional[int] = None,
        total_steps: Optional[int] = None,
        details: Optional[Dict] = None,
    ):
        self.id = f"{datetime.now().isoformat()}-{id(self)}"
        self.timestamp = datetime.now().isoformat()
        self.level = level
        self.message = message
        self.step = step
        self.total_steps = total_steps
        self.details = details or {}

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "level": self.level.value,
            "message": self.message,
            "step": self.step,
            "totalSteps": self.total_steps,
            "details": self.details,
        }

    def to_sse(self) -> str:
        """Convert to Server-Sent Event format"""
        return f"data: {json.dumps(self.to_dict())}\n\n"


class ProgressStreamManager:
    """Manages progress streams for different sessions"""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.locks: Dict[str, asyncio.Lock] = {}

    async def emit(
        self,
        session_id: str,
        level: ProgressLevel,
        message: str,
        step: Optional[int] = None,
        total_steps: Optional[int] = None,
        details: Optional[Dict] = None,
    ) -> ProgressEvent:
        """Emit a progress event to active subscribers only (fire and forget)"""
        if session_id not in self.locks:
            self.locks[session_id] = asyncio.Lock()

        async with self.locks[session_id]:
            event = ProgressEvent(
                level=level,
                message=message,
                step=step,
                total_steps=total_steps,
                details=details,
            )

            # Notify only active subscribers (no history storage)
            if session_id in self.subscribers:
                for callback in self.subscribers[session_id]:
                    try:
                        await callback(event)
                    except Exception as e:
                        logger.error(f"Error calling progress subscriber: {e}")

            logger.debug(f"📊 Progress event: {message} ({session_id})")
            return event

    def subscribe(
        self, session_id: str, callback: Callable
    ) -> Callable:
        """Subscribe to progress events for a session"""
        if session_id not in self.subscribers:
            self.subscribers[session_id] = []

        self.subscribers[session_id].append(callback)

        def unsubscribe():
            if session_id in self.subscribers:
                self.subscribers[session_id].remove(callback)

        return unsubscribe

    def get_events(self, session_id: str) -> List[ProgressEvent]:
        """Get all events for a session (returns empty - no history stored)"""
        return []

    def clear(self, session_id: str):
        """Clear subscribers and locks for a session"""
        self.subscribers.pop(session_id, None)
        self.locks.pop(session_id, None)


# Global instance
progress_manager = ProgressStreamManager()


async def emit_progress(
    session_id: str,
    level: ProgressLevel,
    message: str,
    step: Optional[int] = None,
    total_steps: Optional[int] = None,
    details: Optional[Dict] = None,
) -> ProgressEvent:
    """Convenience function to emit progress"""
    return await progress_manager.emit(
        session_id=session_id,
        level=level,
        message=message,
        step=step,
        total_steps=total_steps,
        details=details,
    )


# Create convenience functions for each level
async def progress_info(session_id: str, message: str, **kwargs):
    return await emit_progress(session_id, ProgressLevel.INFO, message, **kwargs)


async def progress_success(session_id: str, message: str, **kwargs):
    return await emit_progress(session_id, ProgressLevel.SUCCESS, message, **kwargs)


async def progress_warning(session_id: str, message: str, **kwargs):
    return await emit_progress(session_id, ProgressLevel.WARNING, message, **kwargs)


async def progress_error(session_id: str, message: str, **kwargs):
    return await emit_progress(session_id, ProgressLevel.ERROR, message, **kwargs)


# Execution status update functions
async def execution_status_update(
    session_id: str,
    execution_id: str,
    status: ExecutionStatus,
    message: str = None,
    analysis_id: str = None,
    execution_logs: str = None,
    **kwargs
) -> ProgressEvent:
    """
    Send execution status update via SSE
    
    Args:
        session_id: Session ID for SSE routing
        execution_id: Execution ID
        status: New execution status
        message: Optional status message
        analysis_id: Optional analysis ID
        execution_logs: Optional execution logs
    """
    default_messages = {
        ExecutionStatus.QUEUED: "Analysis queued for execution",
        ExecutionStatus.RUNNING: "Analysis execution in progress",
        ExecutionStatus.COMPLETED: "Analysis execution completed",
        ExecutionStatus.FAILED: "Analysis execution failed"
    }
    
    final_message = message or default_messages.get(status, f"Execution status: {status}")
    
    details = {
        "execution_id": execution_id,
        "execution_status": status.value,
        **({"analysis_id": analysis_id} if analysis_id else {}),
        **({"execution_logs": execution_logs} if execution_logs else {}),
        **kwargs
    }
    
    # Use appropriate progress level based on status
    level = ProgressLevel.ERROR if status == ExecutionStatus.FAILED else ProgressLevel.INFO
    if status == ExecutionStatus.COMPLETED:
        level = ProgressLevel.SUCCESS
    
    return await emit_progress(
        session_id=session_id,
        level=level,
        message=final_message,
        details=details
    )


# Convenience functions for execution status updates
async def execution_queued(session_id: str, execution_id: str, analysis_id: str = None, **kwargs):
    """Send execution queued status update"""
    return await execution_status_update(
        session_id, execution_id, ExecutionStatus.QUEUED,
        analysis_id=analysis_id, **kwargs
    )


async def execution_running(session_id: str, execution_id: str, analysis_id: str = None, **kwargs):
    """Send execution running status update"""
    return await execution_status_update(
        session_id, execution_id, ExecutionStatus.RUNNING,
        analysis_id=analysis_id, **kwargs
    )


async def execution_completed(session_id: str, execution_id: str, analysis_id: str = None, **kwargs):
    """Send execution completed status update"""
    return await execution_status_update(
        session_id, execution_id, ExecutionStatus.COMPLETED,
        analysis_id=analysis_id, **kwargs
    )


async def execution_failed(session_id: str, execution_id: str, error_message: str = None, analysis_id: str = None, **kwargs):
    """Send execution failed status update"""
    message = f"Analysis execution failed: {error_message}" if error_message else None
    return await execution_status_update(
        session_id, execution_id, ExecutionStatus.FAILED,
        message=message, analysis_id=analysis_id, **kwargs
    )
