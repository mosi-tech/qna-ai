"""
Progress streaming service for real-time execution updates
"""

import asyncio
import json
import orjson
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
        details: Optional[Dict] = None,
    ):
        self.id = f"{datetime.now().isoformat()}-{id(self)}"
        self.timestamp = datetime.now().isoformat()
        self.level = level
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict:
        # Debug: Log details content (orjson will handle datetime objects automatically)
        logger.debug(f"🔍 ProgressEvent.to_dict details: {self.details}")
        
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "level": self.level.value,
            "message": self.message,
            "details": self.details,  # orjson will handle datetime objects automatically
        }

    def to_sse(self) -> str:
        """Convert to Server-Sent Event format"""
        try:
            data_dict = self.to_dict()
            logger.debug(f"🔍 Serializing SSE data: {data_dict}")
            
            # Use orjson which automatically handles datetime objects
            json_bytes = orjson.dumps(data_dict, option=orjson.OPT_SERIALIZE_DATACLASS)
            return f"data: {json_bytes.decode()}\n\n"
        except Exception as e:
            logger.error(f"❌ orjson serialization error in SSE: {e}")
            logger.error(f"❌ Data causing error: {self.to_dict()}")
            # Return a safe fallback using orjson
            try:
                fallback_bytes = orjson.dumps({'error': 'Serialization failed', 'message': str(e)})
                return f"data: {fallback_bytes.decode()}\n\n"
            except Exception as fallback_error:
                logger.error(f"❌ Even fallback serialization failed: {fallback_error}")
                return f"data: {{\"error\": \"Critical serialization failure\"}}\n\n"


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
        details: Optional[Dict] = None,
    ) -> ProgressEvent:
        """Emit a progress event to active subscribers only (fire and forget)"""
        if session_id not in self.locks:
            self.locks[session_id] = asyncio.Lock()

        async with self.locks[session_id]:
            event = ProgressEvent(
                level=level,
                message=message,
                details=details,
            )

            # Notify only active subscribers (no history storage)
            if session_id in self.subscribers:
                for callback in self.subscribers[session_id]:
                    try:
                        await callback(event)
                    except Exception as e:
                        logger.error(f"Error calling progress subscriber: {e}")

            logger.info(f"📊 Progress event emitted: {message} ({session_id}) to {len(self.subscribers.get(session_id, []))} subscribers")
            return event

    def subscribe(
        self, session_id: str, callback: Callable
    ) -> Callable:
        """Subscribe to progress events for a session"""
        if session_id not in self.subscribers:
            self.subscribers[session_id] = []

        self.subscribers[session_id].append(callback)
        logger.info(f"📡 New SSE subscriber for session {session_id}. Total: {len(self.subscribers[session_id])}")

        def unsubscribe():
            if session_id in self.subscribers:
                try:
                    self.subscribers[session_id].remove(callback)
                    logger.info(f"📡 SSE subscriber removed for session {session_id}. Remaining: {len(self.subscribers[session_id])}")
                except ValueError:
                    logger.warning(f"📡 Attempted to remove non-existent subscriber for session {session_id}")

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
    details: Optional[Dict] = None,
) -> ProgressEvent:
    """Convenience function to emit progress"""
    return await progress_manager.emit(
        session_id=session_id,
        level=level,
        message=message,
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


# Message-based progress logging functions
async def log_progress_to_message(
    message_id: str,
    level: str,
    message: str,
    details: Optional[Dict] = None
):
    """
    Log progress directly to a message's logs array in MongoDB.
    
    Args:
        message_id: ID of the message to append log to
        level: Log level ("info", "success", "warning", "error")
        message: Progress message
        details: Optional additional details
    """
    try:
        from db.mongodb_client import MongoDBClient
        from datetime import datetime
        
        # Get MongoDB client
        # Note: This is a simple implementation. In production, we'd inject the DB connection
        db_client = MongoDBClient()
        await db_client.connect()
        
        # Create log entry
        log_entry = {
            "message": message,
            "timestamp": datetime.utcnow(),
            "level": level,
            "details": details or {}
        }
        
        # Append to message logs array
        result = await db_client.db.chat_messages.update_one(
            {"messageId": message_id},
            {"$push": {"logs": log_entry}}
        )
        
        if result.modified_count > 0:
            logger.info(f"📝 Log added to message {message_id}: {message}")
        else:
            logger.warning(f"⚠️ Failed to add log to message {message_id}")
            
    except Exception as e:
        logger.error(f"❌ Failed to log to message: {e}")


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
    
    # Debug: Log kwargs content (orjson will handle datetime objects automatically)
    logger.debug(f"🔍 execution_status_update kwargs: {kwargs}")
    
    details = {
        "execution_id": execution_id,
        "execution_status": status.value,
        **({"analysis_id": analysis_id} if analysis_id else {}),
        **({"execution_logs": execution_logs} if execution_logs else {}),
        **kwargs  # orjson will handle datetime objects automatically
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
