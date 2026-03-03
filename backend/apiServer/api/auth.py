"""
Authentication and Authorization for API endpoints
Integrated with Appwrite for production-ready auth
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Import the Appwrite auth module
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.auth.appwrite_auth import appwrite_auth, USER_ROLES

logger = logging.getLogger("auth")

# Initialize security scheme
security = HTTPBearer(auto_error=False)

class UserContext:
    """User context extracted from Appwrite authentication"""
    
    def __init__(self, user_id: str, email: str, name: str, roles: List[str], session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.roles = roles
        self.session_id = session_id
        self.metadata = metadata or {}
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role"""
        return role in self.roles
    
    def __str__(self):
        return f"UserContext(user_id={self.user_id}, email={self.email}, roles={self.roles})"

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_user_id: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
) -> UserContext:
    """
    Extract user context from Appwrite session or fallback to dev headers
    """
    
    # Production: Use Appwrite session validation
    try:
        user_info = await appwrite_auth.validate_session(request)
        
        return UserContext(
            user_id=user_info['user_id'],
            email=user_info['email'],
            name=user_info['name'],
            roles=user_info.get('roles', []),
            session_id=x_session_id,  # Use session_id from request if provided
            metadata={
                "auth_method": "appwrite",
                "email_verified": user_info.get('email_verified', False),
                "preferences": user_info.get('preferences', {})
            }
        )
    except HTTPException as e:
        # Check if we're in development mode with header-based auth
        if x_user_id and os.getenv('ENV', 'production').lower() == 'development':
            logger.warning(f"⚠️ Using X-User-ID header for authentication (development mode): {x_user_id}")
            return UserContext(
                user_id=x_user_id,
                email=f"{x_user_id}@dev.local",
                name=f"Dev User {x_user_id}",
                roles=[USER_ROLES['PREMIUM']],  # Give dev users premium access
                session_id=x_session_id,
                metadata={"auth_method": "header", "dev_mode": True}
            )
        
        # Re-raise the authentication error
        raise e

async def require_authenticated_user(
    user_context: UserContext = Depends(get_current_user)
) -> UserContext:
    """
    Require authenticated user
    """
    if not user_context.user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please log in."
        )
    
    logger.info(f"✅ Authenticated user: {user_context.email}")
    return user_context

async def require_role(required_role: str):
    """
    FastAPI dependency factory to require specific role
    """
    async def role_dependency(user_context: UserContext = Depends(require_authenticated_user)) -> UserContext:
        if not user_context.has_role(required_role):
            logger.warning(f"❌ Access denied for user {user_context.email}: required role {required_role}, has {user_context.roles}")
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {required_role}"
            )
        
        logger.info(f"✅ Role check passed for user {user_context.email}: {required_role}")
        return user_context
    
    return role_dependency

async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_user_id: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
) -> Optional[UserContext]:
    """
    Get user context but allow anonymous access
    """
    try:
        return await get_current_user(request, credentials, x_user_id, x_session_id)
    except HTTPException:
        # Return None for anonymous access
        logger.info("🔓 No authentication provided, allowing anonymous access")
        return None

# Convenience role dependencies
require_analyst = require_role(USER_ROLES['ANALYST'])
require_premium = require_role(USER_ROLES['PREMIUM'])
require_admin = require_role(USER_ROLES['ADMIN'])

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