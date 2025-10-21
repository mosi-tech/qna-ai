"""
Session Management Routes - Handle chat history and session management
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

logger = logging.getLogger("session-routes")

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class SessionMetadata(BaseModel):
    """Session metadata for list view"""
    session_id: str
    title: Optional[str] = None
    created_at: str
    updated_at: str
    message_count: int
    last_message: Optional[str] = None
    is_archived: bool = False


class SessionDetail(BaseModel):
    """Full session details with messages"""
    session_id: str
    user_id: str
    title: Optional[str] = None
    created_at: str
    updated_at: str
    is_archived: bool
    messages: List[dict]


class UpdateSessionRequest(BaseModel):
    """Request to update session metadata"""
    title: Optional[str] = None
    is_archived: Optional[bool] = None


@router.get("/user/{user_id}", response_model=List[SessionMetadata])
async def list_user_sessions(
    request: Request,
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    archived: Optional[bool] = Query(None),
):
    """
    List all sessions for a user with optional filtering
    """
    try:
        chat_history_service = request.app.state.chat_history_service
        if not chat_history_service:
            raise HTTPException(status_code=500, detail="Chat service not available")
        
        sessions = await chat_history_service.get_user_sessions(
            user_id=user_id,
            skip=skip,
            limit=limit,
            search_text=search,
            archived=archived,
        )
        
        logger.info(f"✓ Retrieved {len(sessions)} sessions for user {user_id}")
        return sessions
    except Exception as e:
        logger.error(f"✗ Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
async def get_session_detail(
    request: Request,
    session_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(5, ge=1, le=50),
):
    """
    Get session details with paginated messages
    offset: number of newest messages to skip (for loading older messages)
    limit: number of messages to return (default 5)
    """
    try:
        chat_history_service = request.app.state.chat_history_service
        if not chat_history_service:
            raise HTTPException(status_code=500, detail="Chat service not available")
        
        session = await chat_history_service.get_session_with_messages(
            session_id=session_id,
            limit=limit,
            offset=offset,
        )
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"✓ Retrieved session {session_id} with {len(session.get('messages', []))} messages")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Failed to get session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{session_id}")
async def update_session(request: Request, session_id: str, update_req: UpdateSessionRequest):
    """
    Update session metadata (title, archive status)
    """
    try:
        chat_history_service = request.app.state.chat_history_service
        if not chat_history_service:
            raise HTTPException(status_code=500, detail="Chat service not available")
        
        updated = await chat_history_service.update_session(
            session_id=session_id,
            title=update_req.title,
            is_archived=update_req.is_archived,
        )
        
        if not updated:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"✓ Updated session {session_id}")
        return {"success": True, "message": "Session updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Failed to update session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def delete_session(request: Request, session_id: str):
    """
    Delete a session and all its messages
    """
    try:
        chat_history_service = request.app.state.chat_history_service
        if not chat_history_service:
            raise HTTPException(status_code=500, detail="Chat service not available")
        
        deleted = await chat_history_service.delete_session(
            session_id=session_id
        )
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"✓ Deleted session {session_id}")
        return {"success": True, "message": "Session deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


