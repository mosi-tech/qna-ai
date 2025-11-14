#!/usr/bin/env python3
"""
Appwrite Authentication Integration for Backend
Handles session validation and user authorization
"""

import os
import logging
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Request
from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.users import Users
from appwrite.exception import AppwriteException

logger = logging.getLogger(__name__)

# Configuration
APPWRITE_ENDPOINT = os.getenv('APPWRITE_ENDPOINT', 'https://your-dev-domain.com/v1')
APPWRITE_PROJECT_ID = os.getenv('APPWRITE_PROJECT_ID', 'your-project-id')
APPWRITE_API_KEY = os.getenv('APPWRITE_API_KEY')  # Server-side API key for admin operations

# User roles for the financial platform
USER_ROLES = {
    'ANALYST': 'analyst',      # Read-only access
    'PREMIUM': 'premium',      # Full analysis access  
    'ADMIN': 'admin'          # System management
}

class AppwriteAuth:
    """Handles Appwrite authentication for the backend"""
    
    def __init__(self):
        if not APPWRITE_ENDPOINT or not APPWRITE_PROJECT_ID:
            raise ValueError("APPWRITE_ENDPOINT and APPWRITE_PROJECT_ID must be set")
        
        # Admin client for user management operations
        self.admin_client = None
        if APPWRITE_API_KEY:
            self.admin_client = Client()
            self.admin_client.set_endpoint(APPWRITE_ENDPOINT)
            self.admin_client.set_project(APPWRITE_PROJECT_ID)
            self.admin_client.set_key(APPWRITE_API_KEY)
            logger.info("✅ Appwrite admin client initialized")
        else:
            logger.warning("⚠️ APPWRITE_API_KEY not set - admin operations disabled")
    
    def _get_auth_info(self, request: Request) -> tuple[Optional[str], str]:
        """Extract auth token and determine type (session or jwt)"""
        
        # Check cookies first (session tokens)
        if request.cookies:
            session_token = request.cookies.get('a_session') or request.cookies.get('a_session_console')
            if session_token:
                logger.debug("Found session token from cookies")
                return session_token.strip(), 'session'

        # Check Authorization header (JWT tokens)
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            jwt_token = auth_header.replace('Bearer ', '').strip()
            logger.debug("Found JWT token from Authorization header")
            return jwt_token, 'jwt'

        logger.debug("No valid auth token found")
        return None, 'none'
    
    async def validate_session(self, request: Request) -> Dict[str, Any]:
        """
        Validate Appwrite session or JWT and return user info
        
        Returns:
            Dict containing user information if valid
            
        Raises:
            HTTPException: If session is invalid or missing
        """
        auth_token, auth_type = self._get_auth_info(request)
        
        if not auth_token:
            logger.warning("❌ No auth token found in request")
            raise HTTPException(
                status_code=401,
                detail="Authentication required. Please log in."
            )
        
        try:
            # Create client with appropriate auth method
            client = Client()
            client.set_endpoint(APPWRITE_ENDPOINT)
            client.set_project(APPWRITE_PROJECT_ID)
            
            if auth_type == 'session':
                # Cookie-based session authentication
                client.set_session(auth_token)
                logger.debug("Using session-based authentication")
            elif auth_type == 'jwt':
                # JWT-based authentication  
                client.set_jwt(auth_token)
                logger.debug("Using JWT-based authentication")
            else:
                raise ValueError(f"Unknown auth type: {auth_type}")
            
            # Validate by getting user account
            account = Account(client)
            user = account.get()
            
            logger.info(f"✅ Valid {auth_type} authentication for user: {user['email']}")
            
            return {
                'user_id': user['$id'],
                'email': user['email'],
                'name': user['name'],
                'email_verified': user['emailVerification'],
                'roles': user.get('prefs', {}).get('roles', []),
                'preferences': user.get('prefs', {}),
                'auth_token': auth_token,
                'auth_type': auth_type
            }
            
        except AppwriteException as e:
            logger.warning(f"❌ Invalid session: {e}")
            
            if e.code == 401:
                raise HTTPException(
                    status_code=401,
                    detail="Session expired. Please log in again."
                )
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid session. Please log in again."
                )
        except Exception as e:
            logger.error(f"❌ Session validation error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Authentication service error"
            )
    
    async def require_role(self, user_info: Dict[str, Any], required_role: str) -> None:
        """
        Check if user has required role
        
        Args:
            user_info: User info from validate_session()
            required_role: Role required (USER_ROLES.ANALYST, etc.)
            
        Raises:
            HTTPException: If user doesn't have required role
        """
        user_roles = user_info.get('roles', [])
        
        if required_role not in user_roles:
            logger.warning(f"❌ Access denied for user {user_info['email']}: required role {required_role}, has {user_roles}")
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {required_role}"
            )
        
        logger.info(f"✅ Role check passed for user {user_info['email']}: {required_role}")
    
    async def add_user_role(self, user_id: str, role: str) -> bool:
        """
        Add role to user (admin operation)
        
        Args:
            user_id: Appwrite user ID
            role: Role to add
            
        Returns:
            True if successful
        """
        if not self.admin_client:
            logger.error("❌ Admin client not available - cannot add role")
            return False
        
        try:
            users_service = Users(self.admin_client)
            
            # Get current user data
            user = users_service.get(user_id)
            current_roles = user.get('prefs', {}).get('roles', [])
            
            if role not in current_roles:
                current_roles.append(role)
                
                # Update user preferences
                users_service.update_prefs(user_id, {'roles': current_roles})
                logger.info(f"✅ Added role {role} to user {user_id}")
                return True
            else:
                logger.info(f"ℹ️ User {user_id} already has role {role}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to add role {role} to user {user_id}: {e}")
            return False
    
    async def remove_user_role(self, user_id: str, role: str) -> bool:
        """Remove role from user (admin operation)"""
        if not self.admin_client:
            logger.error("❌ Admin client not available - cannot remove role")
            return False
        
        try:
            users_service = Users(self.admin_client)
            
            # Get current user data
            user = users_service.get(user_id)
            current_roles = user.get('prefs', {}).get('roles', [])
            
            if role in current_roles:
                current_roles.remove(role)
                
                # Update user preferences
                users_service.update_prefs(user_id, {'roles': current_roles})
                logger.info(f"✅ Removed role {role} from user {user_id}")
                return True
            else:
                logger.info(f"ℹ️ User {user_id} doesn't have role {role}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to remove role {role} from user {user_id}: {e}")
            return False

# Singleton instance
appwrite_auth = AppwriteAuth()

# Middleware function for FastAPI
async def auth_middleware(request: Request, call_next):
    """
    FastAPI middleware to validate authentication on protected routes
    """
    # Skip authentication for public routes
    public_paths = [
        '/health',
        '/docs',
        '/openapi.json',
        '/auth/',  # Auth-related endpoints
        '/public/'  # Public API endpoints
    ]
    
    # Check if this is a public path
    path = request.url.path
    if any(path.startswith(public_path) for public_path in public_paths):
        return await call_next(request)
    
    try:
        # Validate session and add user info to request state
        user_info = await appwrite_auth.validate_session(request)
        request.state.user = user_info
        
        # Continue with request
        response = await call_next(request)
        return response
        
    except HTTPException:
        # Re-raise authentication errors
        raise
    except Exception as e:
        logger.error(f"❌ Auth middleware error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Authentication service error"
        )

# Dependency functions for FastAPI route protection
def require_auth(request: Request) -> Dict[str, Any]:
    """FastAPI dependency to require authentication"""
    if not hasattr(request.state, 'user') or not request.state.user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    return request.state.user

def require_role(role: str):
    """FastAPI dependency factory to require specific role"""
    async def role_dependency(request: Request) -> Dict[str, Any]:
        user_info = require_auth(request)
        await appwrite_auth.require_role(user_info, role)
        return user_info
    return role_dependency

# Convenience functions
require_analyst = require_role(USER_ROLES['ANALYST'])
require_premium = require_role(USER_ROLES['PREMIUM'])
require_admin = require_role(USER_ROLES['ADMIN'])