"""
Session Management Routes - Handle chat history and session management
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from pydantic import BaseModel

# Import auth components
from .auth import UserContext, require_authenticated_user


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


@router.get("/list", response_model=List[SessionMetadata])
async def list_user_sessions(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    archived: Optional[bool] = Query(None),
    user_context: UserContext = Depends(require_authenticated_user)
):
    """
    List all sessions for the authenticated user with optional filtering
    """
    try:
        chat_history_service = request.app.state.chat_history_service
        if not chat_history_service:
            raise HTTPException(status_code=500, detail="Chat service not available")
        
        sessions = await chat_history_service.get_user_sessions(
            user_id=user_context.user_id,
            skip=skip,
            limit=limit,
            search_text=search,
            archived=archived,
        )
        
        logger.info(f"✓ Retrieved {len(sessions)} sessions for user {user_context.user_id}")
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
    user_context: UserContext = Depends(require_authenticated_user)
):
    """
    Get session details with paginated messages (user must own the session)
    offset: number of newest messages to skip (for loading older messages)
    limit: number of messages to return (default 5)
    """
    try:
        # First verify user owns this session using ChatHistoryService (before expensive DB call)
        chat_history_service = request.app.state.chat_history_service
        if not chat_history_service:
            raise HTTPException(status_code=500, detail="Chat service not available")
        
        is_owner = await chat_history_service.validate_session_ownership(session_id, user_context.user_id)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Access denied: Session not found or belongs to different user")
        
        # Now get the session data (we know user owns it)
        
        session = await chat_history_service.get_session_with_messages(
            session_id=session_id,
            limit=limit,
            offset=offset,
        )
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"✓ Retrieved session {session_id} with {len(session.get('messages', []))} messages for user {user_context.user_id}")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Failed to get session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{session_id}")
async def update_session(
    request: Request, 
    session_id: str, 
    update_req: UpdateSessionRequest,
    user_context: UserContext = Depends(require_authenticated_user)
):
    """
    Update session metadata (title, archive status) - user must own the session
    """
    try:
        # Verify user owns this session using ChatHistoryService
        chat_history_service = request.app.state.chat_history_service
        if not chat_history_service:
            raise HTTPException(status_code=500, detail="Chat service not available")
        
        is_owner = await chat_history_service.validate_session_ownership(session_id, user_context.user_id)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Access denied: Session not found or belongs to different user")
        
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
async def delete_session(
    request: Request, 
    session_id: str,
    user_context: UserContext = Depends(require_authenticated_user)
):
    """
    Delete a session and all its messages - user must own the session
    """
    try:
        # Verify user owns this session using ChatHistoryService
        chat_history_service = request.app.state.chat_history_service
        if not chat_history_service:
            raise HTTPException(status_code=500, detail="Chat service not available")
        
        is_owner = await chat_history_service.validate_session_ownership(session_id, user_context.user_id)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Access denied: Session not found or belongs to different user")
        
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


@router.get("/{session_id}/messages/{message_id}")
async def get_session_message(
    request: Request,
    session_id: str,
    message_id: str,
    user_context: UserContext = Depends(require_authenticated_user)
) -> Dict[str, Any]:
    """
    Get a specific message from a session with UI transformation - user must own the session
    
    Args:
        request: FastAPI request object
        session_id: Chat session identifier  
        message_id: Message identifier
        user_context: Authenticated user context
    
    Returns:
        UI-transformed message data
    """
    try:
        # First verify user owns this session using ChatHistoryService
        chat_history_service = request.app.state.chat_history_service
        if not chat_history_service:
            raise HTTPException(status_code=500, detail="Chat service not available")
        
        is_owner = await chat_history_service.validate_session_ownership(session_id, user_context.user_id)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Access denied: Session not found or belongs to different user")
        
        logger.info(f"📨 Fetching message {message_id} from session {session_id}")
        
        # Get the specific message (already UI-transformed by service)
        message = await chat_history_service.get_message_by_id(message_id)
        
        if not message:
            logger.warning(f"❌ Message {message_id} not found")
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Verify the message belongs to the requested session
        if message.get('sessionId') != session_id:
            logger.warning(f"❌ Message {message_id} does not belong to session {session_id}")
            raise HTTPException(status_code=404, detail="Message not found in specified session")
        
        logger.info(f"✅ Successfully retrieved message {message_id}")
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching message {message_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


