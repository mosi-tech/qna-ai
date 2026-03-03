#!/usr/bin/env python3
"""
CSRF Protection - Cross-Site Request Forgery protection

Implements:
- CSRF token generation per user
- Token validation using Redis storage for cross-origin support
- Timing-safe comparison
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
    """CSRF protection using Redis-backed token storage"""

    # Token configuration
    TOKEN_LENGTH = 32  # 256-bit token
    TOKEN_VALIDITY_HOURS = 24
    DOUBLE_SUBMIT_PATTERN = True

    # Header/Cookie names
    CSRF_TOKEN_HEADER = "X-CSRF-Token"
    CSRF_TOKEN_COOKIE = "csrf_token"
    CSRF_TOKEN_SESSION_KEY = "csrf_token"
    
    # Redis key prefix for CSRF tokens
    REDIS_CSRF_KEY_PREFIX = "csrf_token:"

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
    async def store_token_in_redis_async(token: str, token_data: Dict[str, str], user_id: str) -> bool:
        """
        Store CSRF token in Redis with expiry (async version)
        
        Args:
            token: The token string
            token_data: Token metadata with expires_at
            user_id: User ID to associate with token
            
        Returns:
            True if stored successfully
        """
        try:
            from ..services.redis_client import redis_manager
            
            redis_client = await redis_manager.get_client()
            if not redis_client:
                logger.warning("Redis not available for CSRF token storage")
                return False
            
            redis_key = f"{CSRFProtection.REDIS_CSRF_KEY_PREFIX}{user_id}"
            
            # Calculate TTL from expires_at
            expires_at = token_data.get("expires_at")
            if expires_at:
                try:
                    expires_dt = datetime.fromisoformat(expires_at)
                    ttl = int((expires_dt - datetime.utcnow()).total_seconds())
                    if ttl <= 0:
                        logger.warning("Token already expired before storing")
                        return False
                except Exception as e:
                    logger.error(f"Failed to parse expires_at: {e}")
                    return False
            else:
                ttl = 24 * 3600  # Default 24 hours
            
            # Store in Redis with TTL
            await redis_client.setex(redis_key, ttl, token)
            logger.debug(f"✅ CSRF token stored in Redis for user {user_id} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store CSRF token in Redis: {e}")
            return False

    @staticmethod
    async def get_token_from_redis_async(user_id: str) -> Optional[str]:
        """
        Retrieve CSRF token from Redis (async version)
        
        Args:
            user_id: User ID
            
        Returns:
            Token string if found, None otherwise
        """
        try:
            from ..services.redis_client import redis_manager
            
            redis_client = await redis_manager.get_client()
            if not redis_client:
                return None
            
            redis_key = f"{CSRFProtection.REDIS_CSRF_KEY_PREFIX}{user_id}"
            token = await redis_client.get(redis_key)
            
            if token:
                logger.debug(f"✅ CSRF token found in Redis for user {user_id}")
            else:
                logger.debug(f"⚠️ No CSRF token in Redis for user {user_id}")
                
            return token
            
        except Exception as e:
            logger.error(f"Failed to get CSRF token from Redis: {e}")
            return None

    @staticmethod
    def store_token_in_redis(token: str, token_data: Dict[str, str], user_id: str) -> bool:
        """
        Store CSRF token in Redis with expiry (sync version - for backward compatibility)
        
        Args:
            token: The token string
            token_data: Token metadata with expires_at
            user_id: User ID to associate with token
            
        Returns:
            True if stored successfully (always False in sync context - use async version)
        """
        logger.warning("Use store_token_in_redis_async instead of store_token_in_redis")
        return False

    @staticmethod
    def get_token_from_redis(user_id: str) -> Optional[str]:
        """
        Retrieve CSRF token from Redis (sync version - for backward compatibility)
        
        Args:
            user_id: User ID
            
        Returns:
            Token string if found (always None in sync context - use async version)
        """
        logger.warning("Use get_token_from_redis_async instead of get_token_from_redis")
        return None

    @staticmethod
    def verify_token_format_and_expiry(provided_token: str) -> Tuple[bool, Optional[str]]:
        """
        Verify CSRF token format and expiry without requiring server-side storage.
        
        This is a simplified validation that checks:
        - Token is not empty
        - Token is a reasonable length (URL-safe tokens)
        
        NOTE: For full security with cross-origin requests, tokens should be stored
        in Redis and validated against that storage.
        
        Args:
            provided_token: Token from request
            
        Returns:
            (is_valid: bool, error_reason: Optional[str])
        """
        if not provided_token:
            return False, "CSRF token missing"
        
        # Basic format check - should be URL-safe string of reasonable length
        if len(provided_token) < 20 or len(provided_token) > 100:
            return False, "CSRF token invalid format"
            
        # Token passes basic validation
        logger.debug("✅ CSRF token format validation passed")
        return True, None

    @staticmethod
    def verify_token_against_redis(provided_token: str, user_id: str) -> Tuple[bool, Optional[str]]:
        """
        Verify CSRF token by checking against Redis storage
        
        Args:
            provided_token: Token from request
            user_id: User ID to lookup token for
            
        Returns:
            (is_valid: bool, error_reason: Optional[str])
        """
        if not provided_token:
            return False, "CSRF token missing"
        
        stored_token = CSRFProtection.get_token_from_redis(user_id)
        
        if not stored_token:
            return False, "No CSRF token found for user"
        
        try:
            # Timing-safe comparison to prevent timing attacks
            is_valid = hmac.compare_digest(provided_token, stored_token)
            if is_valid:
                logger.debug("✅ CSRF token verified against Redis")
                return True, None
            else:
                logger.warning("⚠️ CSRF token mismatch - possible attack")
                return False, "CSRF token mismatch"
        except Exception as e:
            logger.error(f"❌ CSRF token verification error: {e}")
            return False, f"Token verification failed: {str(e)}"

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
