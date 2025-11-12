"""
Shared Progress Service

Simple interface for sending progress events from anywhere in the application.
"""

import logging
from typing import Dict, Any, Union
from shared.queue.progress_event_queue import get_progress_event_queue
from shared.queue.progress_message import ProgressMessage

logger = logging.getLogger(__name__)

async def send_progress_event(session_id: str, event_data: Union[ProgressMessage, Dict[str, Any]]):
    """
    Send progress event using the queue system.
    
    Args:
        session_id: Session ID for routing
        event_data: ProgressMessage object or dict with event data
    """
    try:
        queue = get_progress_event_queue()
        await queue.send_progress_event(session_id, event_data)
        logger.debug(f"📤 Progress event sent: {session_id}")
    except Exception as e:
        logger.error(f"❌ Failed to send progress event: {e}")


async def send_progress_info(session_id: str, message: str, **kwargs):
    """Send info-level progress message"""
    await send_progress_event(session_id, {
        "type": "progress",
        "level": "info",
        "message": message,
        **kwargs
    })


async def send_progress_error(session_id: str, message: str, **kwargs):
    """Send error-level progress message"""
    await send_progress_event(session_id, {
        "type": "progress", 
        "level": "error",
        "message": message,
        **kwargs
    })


# Context-aware progress functions (no parameters needed!)
async def send_analysis_progress(message: str, **kwargs):
    """Send analysis progress using execution context"""
    try:
        from shared.queue.worker_context import get_session_id, get_message_id
        
        session_id = get_session_id()
        message_id = get_message_id()
        
        if session_id:  # Only send if context available
            event_data = {
                "type": "analysis_progress",
                "message": message,
                "status": "running",
                "level": "info",
                "message_id": message_id,
                "log_to_message": True if message_id else False,
                **kwargs
            }
            
            # Debug: Log SSE event with message_id
            logger.info(f"📡 Sending SSE event: {event_data['type']} for session={session_id}, message={message_id}, status={event_data.get('status', 'running')}")
            
            await send_progress_event(session_id, event_data)
    except Exception as e:
        # Graceful fallback - don't break pipeline if progress fails
        logger.warning(f"Failed to send analysis progress: {e}")


async def send_analysis_error(message: str, error: str = None, **kwargs):
    """Send analysis error using execution context"""
    await send_analysis_progress(
        message=message,
        status="failed",
        level="error",
        error=error,
        **kwargs
    )


async def send_analysis_success(message: str, **kwargs):
    """Send analysis success using execution context"""
    await send_analysis_progress(
        message=message,
        status="completed", 
        level="success",
        **kwargs
    )


# Context-aware execution progress functions
async def send_execution_progress(message: str, status: str = "running", level: str = "info", **kwargs):
    """Send execution progress using execution context"""
    try:
        from shared.queue.worker_context import get_session_id, get_message_id, get_context_value
        
        session_id = get_session_id()
        message_id = get_message_id()
        execution_id = get_context_value('execution_id')
        analysis_id = get_context_value('analysis_id')
        
        if session_id:  # Only send if context available
            event_data = {
                "type": "execution_status",
                "execution_id": execution_id,
                "analysis_id": analysis_id,
                "message_id": message_id,
                "status": status,
                "message": message,
                "level": level,
                "log_to_message": True if message_id else False,
                **kwargs
            }
            
            # Debug: Log SSE event with message_id
            logger.info(f"📡 Sending SSE event: {event_data['type']} for session={session_id}, message={message_id}, status={status}")
            
            await send_progress_event(session_id, event_data)
    except Exception as e:
        # Graceful fallback - don't break execution if progress fails
        logger.warning(f"Failed to send execution progress: {e}")


async def send_execution_running(message: str = "Analysis execution in progress", **kwargs):
    """Send execution running status using execution context"""
    await send_execution_progress(
        message=message,
        status="running",
        level="info",
        **kwargs
    )


async def send_execution_completed(message: str = "Analysis execution completed", results: dict = None, **kwargs):
    """Send execution completed status using execution context"""
    extra_data = {}
    
    # Removing results from execution completed message as results can be verbose
    # Will require a change on UI
    # if results:
    #     extra_data["results"] = results
        
    await send_execution_progress(
        message=message,
        status="completed",
        level="success",
        **extra_data,
        **kwargs
    )


async def send_execution_failed(message: str = "Analysis execution failed", error: str = None, **kwargs):
    """Send execution failed status using execution context"""
    await send_execution_progress(
        message=message,
        status="failed",
        level="error",
        error=error,
        **kwargs
    )


async def send_execution_queued(message: str = "Analysis queued for execution", **kwargs):
    """Send execution queued status using execution context"""
    await send_execution_progress(
        message=message,
        status="queued",
        level="info",
        **kwargs
    )