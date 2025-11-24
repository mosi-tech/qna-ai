#!/usr/bin/env python3
"""
CSRF Protection - Cross-Site Request Forgery protection

Implements:
- CSRF token generation per session
- Token validation (timing-safe comparison)
- Double-submit cookie pattern
- SameSite cookie support
"""

import secrets
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import hmac

logger = logging.getLogger(__name__)


class CSRFProtection:
    """CSRF protection using token validation and SameSite cookies"""

    # Token configuration
    TOKEN_LENGTH = 32  # 256-bit token
    TOKEN_VALIDITY_HOURS = 24
    DOUBLE_SUBMIT_PATTERN = True

    # Header/Cookie names
    CSRF_TOKEN_HEADER = "X-CSRF-Token"
    CSRF_TOKEN_COOKIE = "csrf_token"
    CSRF_TOKEN_SESSION_KEY = "csrf_token"

    # Methods that require CSRF protection
    PROTECTED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}

    @staticmethod
    def generate_token() -> str:
        """
        Generate a cryptographically secure CSRF token

        Returns:
            URL-safe token (base64-encoded)
        """
        token = secrets.token_urlsafe(CSRFProtection.TOKEN_LENGTH)
        logger.debug("✅ Generated new CSRF token")
        return token

    @staticmethod
    def generate_token_with_metadata() -> Dict[str, Any]:
        """
        Generate CSRF token with metadata for tracking

        Returns:
            {
                "token": str,
                "created_at": str (ISO format),
                "expires_at": str (ISO format),
                "fingerprint": str (hash)
            }
        """
        token = CSRFProtection.generate_token()
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=CSRFProtection.TOKEN_VALIDITY_HOURS)

        fingerprint = hashlib.sha256(token.encode()).hexdigest()[:16]

        return {
            "token": token,
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "fingerprint": fingerprint,
        }

    @staticmethod
    def verify_token(provided_token: str, stored_token: str) -> Tuple[bool, Optional[str]]:
        """
        Verify CSRF token using timing-safe comparison

        Args:
            provided_token: Token from request (header or form)
            stored_token: Token stored in session/cookie

        Returns:
            (is_valid: bool, error_reason: Optional[str])
        """
        if not provided_token or not stored_token:
            return False, "CSRF token missing"

        try:
            # Timing-safe comparison to prevent timing attacks
            is_valid = hmac.compare_digest(provided_token, stored_token)
            if is_valid:
                logger.debug("✅ CSRF token verified successfully")
                return True, None
            else:
                logger.warning("⚠️ CSRF token mismatch - possible attack")
                return False, "CSRF token mismatch"

        except Exception as e:
            logger.error(f"❌ CSRF token verification error: {e}")
            return False, f"Token verification failed: {str(e)}"

    @staticmethod
    def verify_token_with_expiry(
        provided_token: str, token_metadata: Dict[str, str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify CSRF token with expiry check

        Args:
            provided_token: Token from request
            token_metadata: Token metadata dict with expiry

        Returns:
            (is_valid: bool, error_reason: Optional[str])
        """
        stored_token = token_metadata.get("token")
        expires_at_str = token_metadata.get("expires_at")

        if not stored_token or not expires_at_str:
            return False, "Token metadata incomplete"

        # Check expiry
        try:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.utcnow() > expires_at:
                logger.warning("⚠️ CSRF token expired")
                return False, "CSRF token expired"
        except Exception as e:
            logger.error(f"Failed to parse token expiry: {e}")
            return False, "Invalid token metadata"

        # Verify token value
        return CSRFProtection.verify_token(provided_token, stored_token)

    @staticmethod
    def validate_request_csrf(
        request_method: str, provided_token: Optional[str], stored_token: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate CSRF for incoming request

        Args:
            request_method: HTTP method (GET, POST, etc.)
            provided_token: Token from request header or form
            stored_token: Token stored in session

        Returns:
            (is_valid: bool, error_reason: Optional[str])
        """
        # Only validate for state-changing methods
        if request_method not in CSRFProtection.PROTECTED_METHODS:
            logger.debug(f"CSRF check skipped for {request_method} request")
            return True, None

        # Require token for protected methods
        if not provided_token:
            logger.warning(f"⚠️ CSRF token missing for {request_method} request")
            return False, "CSRF token required for state-changing requests"

        # Verify token
        return CSRFProtection.verify_token(provided_token, stored_token)

    @staticmethod
    def get_double_submit_cookie_config() -> Dict[str, Any]:
        """
        Get configuration for double-submit cookie pattern

        Returns:
            {
                "name": str (cookie name),
                "samesite": str ("Strict", "Lax", or "None"),
                "secure": bool (HTTPS only),
                "httponly": bool (JS-inaccessible),
                "max_age": int (seconds)
            }
        """
        return {
            "name": CSRFProtection.CSRF_TOKEN_COOKIE,
            "samesite": "Lax",
            "secure": True,
            "httponly": False,
            "max_age": 24 * 3600,  # 24 hours
        }

    @staticmethod
    def get_samesite_cookie_header() -> str:
        """
        Get SameSite cookie attribute

        Returns:
            "Strict", "Lax", or "None"
        """
        return "Lax"

    @staticmethod
    def check_origin_header(
        origin_header: Optional[str], allowed_origins: list
    ) -> Tuple[bool, Optional[str]]:
        """
        Check Origin header for CSRF protection

        Args:
            origin_header: Origin header from request
            allowed_origins: List of allowed origins

        Returns:
            (is_valid: bool, error_reason: Optional[str])
        """
        if not origin_header:
            logger.warning("⚠️ Origin header missing")
            return False, "Origin header required"

        if origin_header not in allowed_origins:
            logger.warning(f"⚠️ Origin not allowed: {origin_header}")
            return False, f"Origin {origin_header} not allowed"

        logger.debug(f"✅ Origin validation passed: {origin_header}")
        return True, None

    @staticmethod
    def check_referer_header(
        referer_header: Optional[str], allowed_hosts: list
    ) -> Tuple[bool, Optional[str]]:
        """
        Check Referer header for CSRF protection

        Args:
            referer_header: Referer header from request
            allowed_hosts: List of allowed hosts

        Returns:
            (is_valid: bool, error_reason: Optional[str])
        """
        if not referer_header:
            logger.warning("⚠️ Referer header missing")
            return False, "Referer header missing"

        try:
            from urllib.parse import urlparse

            parsed = urlparse(referer_header)
            referer_host = parsed.netloc

            if referer_host not in allowed_hosts:
                logger.warning(f"⚠️ Referer host not allowed: {referer_host}")
                return False, f"Referer host {referer_host} not allowed"

            logger.debug(f"✅ Referer validation passed: {referer_host}")
            return True, None

        except Exception as e:
            logger.error(f"Failed to parse Referer header: {e}")
            return False, "Invalid Referer header"
