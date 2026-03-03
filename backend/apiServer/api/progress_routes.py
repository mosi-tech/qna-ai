"""
Progress streaming routes for real-time execution updates
"""

import asyncio
import json
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from services.sse import progress_sse_manager, ProgressEvent
from shared.queue.progress_event_queue import get_progress_event_queue

logger = logging.getLogger("progress-routes")

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/{session_id}")
async def stream_progress(session_id: str, request: Request):
    """
    Stream progress events for a session via SSE
    Client connects here to receive real-time progress updates
    Sends heartbeat every 5 seconds to detect connection drops
    
    Validates that session exists before opening connection.
    """
    # Validate session exists before opening SSE connection
    try:
        chat_history_service = request.app.state.chat_history_service
        if not chat_history_service:
            raise HTTPException(status_code=500, detail="Chat service not available")
        
        session = await chat_history_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Failed to validate session: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate session")
    
    async def event_generator():
        """Generate SSE events for client"""
        # Send initial connection message (no id: — not a replayable event)
        yield "data: {\"type\": \"connected\", \"sessionId\": \"" + session_id + "\"}\n\n"

        # --- Missed-event replay (Fix #1 / Phase 3) ---
        # The browser sends Last-Event-ID (lower-cased by HTTP) on reconnect.
        # It contains the ISO timestamp of the last SSE frame it received.
        # We replay every event newer than that timestamp before going live.
        last_event_id = request.headers.get("last-event-id")
        if last_event_id:
            try:
                since_dt = datetime.fromisoformat(last_event_id)
                event_queue = get_progress_event_queue()
                if event_queue:
                    missed = await event_queue.get_progress_events(session_id, since=since_dt)
                    for m_event in missed:
                        sse_id = m_event.get("timestamp", "")
                        replay_data = {k: v for k, v in m_event.items() if k != "event_id"}
                        yield f"id: {sse_id}\ndata: {json.dumps(replay_data)}\n\n"
                    if missed:
                        logger.info(f"🔄 Replayed {len(missed)} missed event(s) for session {session_id} since {since_dt.isoformat()}")
            except (ValueError, TypeError) as e:
                logger.warning(f"⚠️ Cannot parse Last-Event-ID '{last_event_id}': {e}")
            except Exception as e:
                logger.error(f"❌ Error replaying missed events for session {session_id}: {e}")

        # Subscribe to new events
        queue: asyncio.Queue = asyncio.Queue()

        async def on_progress(event: ProgressEvent):
            await queue.put(event)

        unsubscribe = progress_sse_manager.subscribe(session_id, on_progress)

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
    events = progress_sse_manager.get_events(session_id)
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
    progress_sse_manager.clear(session_id)
    return {"success": True, "session_id": session_id, "message": "Progress cleared"}


@router.get("/{session_id}/lock-status")
async def get_session_lock_status(session_id: str, request: Request):
    """
    Return whether this session currently holds an active processing lock.
    Used by the frontend on refresh to detect an in-flight job whose AI
    placeholder message may not yet exist in the DB (race condition).
    """
    try:
        from shared.locking import get_session_lock
        session_lock = get_session_lock()
        locked = await session_lock.is_session_locked(session_id)
        return {"session_id": session_id, "locked": locked}
    except Exception as e:
        logger.error(f"❌ Failed to check lock status for {session_id}: {e}")
        return {"session_id": session_id, "locked": False}


@router.get("/{session_id}/messages/{message_id}/status")
async def get_message_status(
    session_id: str,
    message_id: str,
    request: Request,
):
    """
    Get the current processing status of a specific message.

    Used by the frontend as a polling fallback when the SSE connection is
    unavailable (Fix #6 / Phase 3).  Returns the `metadata.status` field from
    the chat history document so the UI can detect completion without SSE.
    """
    try:
        chat_history_service = request.app.state.chat_history_service
        if not chat_history_service:
            raise HTTPException(status_code=500, detail="Chat service not available")

        message = await chat_history_service.get_message_by_id(message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        if isinstance(message, dict):
            metadata = message.get("metadata", {})
        else:
            metadata = getattr(message, "metadata", {}) or {}

        status = (
            metadata.get("status") if isinstance(metadata, dict)
            else getattr(metadata, "status", None)
        ) or "unknown"

        response_type = (
            metadata.get("response_type") if isinstance(metadata, dict)
            else getattr(metadata, "response_type", None)
        )

        return {
            "message_id": message_id,
            "session_id": session_id,
            "status": status,
            "response_type": response_type,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get message status for {message_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
