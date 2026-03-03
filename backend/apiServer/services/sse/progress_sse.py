"""
SSE Progress Service - Direct SSE emissions only

IMPORTANT: These functions emit directly to SSE and bypass the queue system.
They should ONLY be used by:
- Progress Monitor (reading from queue and broadcasting to SSE)
- SSE infrastructure components

DO NOT use these in API routes or business logic - use shared.services.progress_service instead.
"""

import logging
from typing import Dict, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger("sse-progress")


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
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "level": self.level.value,
            "message": self.message,
            "details": self.details,
        }

    def to_sse(self) -> str:
        """Convert to Server-Sent Event format"""
        try:
            import orjson
            data_dict = self.to_dict()
            json_bytes = orjson.dumps(data_dict, option=orjson.OPT_SERIALIZE_DATACLASS)
            return f"data: {json_bytes.decode()}\n\n"
        except Exception as e:
            logger.error(f"❌ SSE serialization error: {e}")
            return f'data: {{"error": "Serialization failed", "message": "{str(e)}"}}\n\n'


class ProgressStreamManager:
    """Manages progress streams for different sessions"""

    def __init__(self):
        import asyncio
        from typing import List, Callable
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
        import asyncio
        
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

            logger.info(f"📊 SSE event emitted: {message} ({session_id}) to {len(self.subscribers.get(session_id, []))} subscribers")
            return event

    def subscribe(
        self, session_id: str, callback
    ):
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

    def get_events(self, session_id: str):
        """Get all events for a session (returns empty - no history stored)"""
        return []

    def clear(self, session_id: str):
        """Clear subscribers and locks for a session"""
        self.subscribers.pop(session_id, None)
        self.locks.pop(session_id, None)


# Global SSE manager instance
progress_sse_manager = ProgressStreamManager()


# =============================================================================
# INTERNAL SSE FUNCTIONS - DO NOT USE IN API ROUTES
# Use shared.services.progress_service functions instead
# =============================================================================

async def _sse_emit_progress(
    session_id: str,
    level: ProgressLevel,
    message: str,
    details: Optional[Dict] = None,
) -> ProgressEvent:
    """INTERNAL: Direct emit to SSE (Progress Monitor use only)"""
    return await progress_sse_manager.emit(
        session_id=session_id,
        level=level,
        message=message,
        details=details,
    )


# Removed _sse_execution_* functions - they were unnecessary complexity
# Now using _sse_progress_info for all execution status updates


async def _sse_progress_info(session_id: str, message: str, **kwargs):
    """INTERNAL: Direct SSE emit for info-level progress"""
    return await _sse_emit_progress(session_id, ProgressLevel.INFO, message, kwargs)


async def _sse_progress_success(session_id: str, message: str, **kwargs):
    """INTERNAL: Direct SSE emit for success-level progress"""
    return await _sse_emit_progress(session_id, ProgressLevel.SUCCESS, message, kwargs)


async def _sse_progress_error(session_id: str, message: str, **kwargs):
    """INTERNAL: Direct SSE emit for error-level progress"""
    return await _sse_emit_progress(session_id, ProgressLevel.ERROR, message, kwargs)