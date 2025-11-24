#!/usr/bin/env python3
"""
CSRF Helper Functions - Utilities for CSRF token handling in routes

Use these helpers to generate and manage CSRF tokens in your route handlers.
"""

import logging
from typing import Dict, Any
from fastapi import Request

from .csrf import CSRFProtection

logger = logging.getLogger(__name__)


async def generate_csrf_token_for_session(request: Request) -> Dict[str, Any]:
    """
    Generate and store CSRF token in session.
    
    Call this after successful authentication to give user a CSRF token.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        {
            "csrf_token": str,
            "token_metadata": dict
        }
        
    Example:
        @app.post("/api/auth/login")
        async def login(request: Request, credentials: LoginData):
            # ... validate credentials ...
            csrf_result = await generate_csrf_token_for_session(request)
            return {
                "success": True,
                "user_id": user_id,
                "csrf_token": csrf_result["csrf_token"]
            }
    """
    try:
        # Generate token with metadata
        token_metadata = CSRFProtection.generate_token_with_metadata()
        
        # Store in session
        if not hasattr(request, "session"):
            logger.error("Request has no session - SessionMiddleware not configured")
            raise RuntimeError("Session middleware not configured")
        
        request.session[CSRFProtection.CSRF_TOKEN_SESSION_KEY] = token_metadata
        logger.debug("✅ CSRF token generated and stored in session")
        
        return {
            "csrf_token": token_metadata["token"],
            "token_metadata": token_metadata,
        }
        
    except Exception as e:
        logger.error(f"Failed to generate CSRF token: {e}")
        raise


async def get_csrf_token_from_session(request: Request) -> str:
    """
    Get CSRF token from request session.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        CSRF token string, or empty string if not found
    """
    try:
        if not hasattr(request, "session"):
            return ""
        
        token_data = request.session.get(CSRFProtection.CSRF_TOKEN_SESSION_KEY, {})
        return token_data.get("token", "")
        
    except Exception as e:
        logger.warning(f"Failed to get CSRF token from session: {e}")
        return ""


async def regenerate_csrf_token_for_session(request: Request) -> Dict[str, Any]:
    """
    Regenerate CSRF token (useful for re-authentication).
    
    Args:
        request: FastAPI Request object
        
    Returns:
        {
            "csrf_token": str,
            "token_metadata": dict
        }
    """
    logger.debug("Regenerating CSRF token...")
    return await generate_csrf_token_for_session(request)


def csrf_token_response(csrf_token: str) -> Dict[str, Any]:
    """
    Create response dict with CSRF token.
    
    Use this to include CSRF token in login/authentication responses.
    
    Args:
        csrf_token: CSRF token string
        
    Returns:
        Dict with csrf_token key
        
    Example:
        return {
            "success": True,
            "user_id": user_id,
            **csrf_token_response(token)
        }
    """
    return {
        "csrf_token": csrf_token,
    }
