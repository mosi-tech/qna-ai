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