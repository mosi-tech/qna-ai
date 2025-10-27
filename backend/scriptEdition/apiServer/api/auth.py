"""
Authentication and Authorization for API endpoints
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger("auth")

# Initialize security scheme
security = HTTPBearer(auto_error=False)

class UserContext:
    """User context extracted from authentication"""
    
    def __init__(self, user_id: str, session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.session_id = session_id
        self.metadata = metadata or {}
    
    def __str__(self):
        return f"UserContext(user_id={self.user_id}, session_id={self.session_id})"

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_user_id: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
) -> UserContext:
    """
    Extract user context from request headers or authentication token
    
    For now, this uses headers as a temporary solution until proper JWT auth is implemented.
    In production, this should validate JWT tokens and extract user_id from there.
    """
    
    # TODO: Replace with proper JWT token validation
    # if credentials:
    #     token = credentials.credentials
    #     user_data = validate_jwt_token(token)
    #     return UserContext(user_id=user_data['user_id'], session_id=user_data.get('session_id'))
    
    # Temporary: Use headers (for development/testing only)
    if x_user_id:
        logger.warning(f"⚠️ Using X-User-ID header for authentication (development mode): {x_user_id}")
        return UserContext(
            user_id=x_user_id,
            session_id=x_session_id,
            metadata={"auth_method": "header", "dev_mode": True}
        )
    
    # Fallback: Anonymous user (for endpoints that don't require auth)
    logger.info("🔓 No authentication provided, using anonymous user")
    return UserContext(
        user_id="anonymous",
        session_id=None,
        metadata={"auth_method": "anonymous"}
    )

async def require_authenticated_user(
    user_context: UserContext = Depends(get_current_user)
) -> UserContext:
    """
    Require authenticated user (non-anonymous)
    """
    if user_context.user_id == "anonymous":
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide X-User-ID header or valid Bearer token."
        )
    
    return user_context

async def get_optional_user(
    user_context: UserContext = Depends(get_current_user)
) -> UserContext:
    """
    Get user context but allow anonymous access
    """
    return user_context

# Utility function to extract user_id from execution data for validation
def validate_user_access_to_execution(execution_data: Dict[str, Any], user_context: UserContext) -> bool:
    """
    Validate that the user has access to the execution
    """
    if user_context.user_id == "anonymous":
        return False
    
    execution_user_id = execution_data.get("user_id")
    execution_session_id = execution_data.get("session_id")
    
    # User must match
    if execution_user_id != user_context.user_id:
        return False
    
    # If session_id is provided in context, it must match
    if user_context.session_id and execution_session_id != user_context.session_id:
        return False
    
    return True