#!/usr/bin/env python3
"""
CSRF Middleware - FastAPI middleware for CSRF token validation

Automatically validates CSRF tokens on state-changing requests (POST, PUT, DELETE, PATCH).
"""

import logging
from typing import Callable
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .csrf import CSRFProtection

logger = logging.getLogger(__name__)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection middleware for FastAPI applications using session cookies.
    
    Validates CSRF tokens on state-changing requests to prevent cross-site request forgery.
    """

    # Methods that require CSRF protection
    PROTECTED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}

    # Routes to exempt from CSRF (e.g., login, logout, token generation)
    EXEMPT_ROUTES = {
        "/api/auth/login",
        "/api/auth/logout",
        "/api/auth/signup",
        "/api/auth/verify-email",
        "/api/health",
        "/csrf-token",  # CSRF token generation endpoint
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and validate CSRF token if needed.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response (either error or from next handler)
        """
        # Skip CSRF check for exempt routes
        if request.url.path in self.EXEMPT_ROUTES:
            logger.debug(f"CSRF check skipped for exempt route: {request.url.path}")
            return await call_next(request)

        # Only validate for protected methods
        if request.method not in self.PROTECTED_METHODS:
            logger.debug(f"CSRF check skipped for {request.method} request")
            return await call_next(request)

        # Validate CSRF token
        is_valid, error = await self._validate_csrf_token(request)
        if not is_valid:
            logger.warning(f"🚨 CSRF validation failed: {error}")
            raise HTTPException(status_code=403, detail=f"CSRF validation failed: {error}")

        logger.debug("✅ CSRF token validated successfully")
        return await call_next(request)

    async def _validate_csrf_token(self, request: Request) -> tuple[bool, str]:
        """
        Validate CSRF token from request.

        Args:
            request: Incoming request

        Returns:
            (is_valid: bool, error_message: str)
        """
        try:
            # Get token from header (preferred) or form data
            provided_token = request.headers.get(
                CSRFProtection.CSRF_TOKEN_HEADER
            ) or await self._get_form_token(request)

            if not provided_token:
                return False, "CSRF token missing from request"

            # Get stored token from session
            session = request.session if hasattr(request, "session") else {}
            stored_token_data = session.get(CSRFProtection.CSRF_TOKEN_SESSION_KEY)

            if not stored_token_data:
                return False, "No CSRF token in session"

            # Validate token with expiry
            is_valid, error = CSRFProtection.verify_token_with_expiry(
                provided_token, stored_token_data
            )

            if not is_valid:
                return False, error or "CSRF token invalid"

            # Also validate origin/referer for extra safety
            origin_valid, origin_error = self._validate_origin(request)
            if not origin_valid:
                logger.warning(f"Origin validation failed: {origin_error}")
                # Note: Don't fail on origin if token is valid
                # Some legitimate requests may not have origin

            return True, ""

        except Exception as e:
            logger.error(f"CSRF validation error: {e}")
            return False, f"CSRF validation error: {str(e)}"

    async def _get_form_token(self, request: Request) -> str:
        """
        Extract CSRF token from form data (fallback if not in header).

        Args:
            request: Incoming request

        Returns:
            Token string or empty string
        """
        try:
            # Only try to parse form if content-type is form data
            content_type = request.headers.get("content-type", "")
            if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                form_data = await request.form()
                return form_data.get("csrf_token", "")
        except Exception as e:
            logger.debug(f"Could not extract CSRF token from form: {e}")

        return ""

    def _validate_origin(self, request: Request) -> tuple[bool, str]:
        """
        Validate Origin header as additional CSRF protection.

        Args:
            request: Incoming request

        Returns:
            (is_valid: bool, error_message: str)
        """
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")

        # Origin is more reliable than Referer
        if origin:
            # Extract host from request
            request_host = request.url.netloc

            # Check if origin matches request host
            from urllib.parse import urlparse

            origin_parsed = urlparse(origin)
            origin_host = origin_parsed.netloc

            if origin_host != request_host:
                return False, f"Origin mismatch: {origin_host} vs {request_host}"

            return True, ""

        # Fallback to Referer if Origin not present
        if referer:
            from urllib.parse import urlparse

            referer_parsed = urlparse(referer)
            referer_host = referer_parsed.netloc
            request_host = request.url.netloc

            if referer_host != request_host:
                return False, f"Referer mismatch: {referer_host} vs {request_host}"

            return True, ""

        # Some legitimate requests may not have origin/referer
        logger.debug("No Origin or Referer header found")
        return True, ""


# Convenience function to add middleware to FastAPI app
def add_csrf_middleware(app):
    """
    Add CSRF middleware to FastAPI application.

    Args:
        app: FastAPI application instance

    Example:
        from fastapi import FastAPI
        from shared.security.csrf_middleware import add_csrf_middleware

        app = FastAPI()
        add_csrf_middleware(app)
    """
    app.add_middleware(CSRFMiddleware)
    logger.info("✅ CSRF middleware added to FastAPI application")
