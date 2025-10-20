"""
Progress streaming routes for real-time execution updates
"""

import asyncio
import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services.progress_service import progress_manager, ProgressEvent

logger = logging.getLogger("progress-routes")

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/{session_id}")
async def stream_progress(session_id: str):
    """
    Stream progress events for a session via SSE
    Client connects here to receive real-time progress updates
    Sends heartbeat every 5 seconds to detect connection drops
    """

    async def event_generator():
        """Generate SSE events for client"""
        # Send initial connection message
        yield "data: {\"type\": \"connected\", \"sessionId\": \"" + session_id + "\"}\n\n"

        # Subscribe to new events
        queue: asyncio.Queue = asyncio.Queue()

        async def on_progress(event: ProgressEvent):
            await queue.put(event)

        unsubscribe = progress_manager.subscribe(session_id, on_progress)

        try:
            while True:
                try:
                    # Wait for new events with 5s timeout for heartbeat
                    event = await asyncio.wait_for(queue.get(), timeout=5)
                    yield event.to_sse()
                except asyncio.TimeoutError:
                    # Send heartbeat every 5 seconds of silence
                    yield "data: {\"type\": \"heartbeat\"}\n\n"
        except GeneratorExit:
            pass
        finally:
            unsubscribe()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/{session_id}/events")
async def get_progress_events(session_id: str):
    """
    Get all progress events for a session (non-streaming)
    """
    events = progress_manager.get_events(session_id)
    return {
        "session_id": session_id,
        "events": [event.to_dict() for event in events],
        "count": len(events),
    }


@router.delete("/{session_id}")
async def clear_progress(session_id: str):
    """
    Clear all progress events for a session
    """
    progress_manager.clear(session_id)
    return {"success": True, "session_id": session_id, "message": "Progress cleared"}
