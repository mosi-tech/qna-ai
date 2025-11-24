#!/usr/bin/env python3
"""
Input Validator - Centralized input validation and sanitization

Prevents:
- Injection attacks (SQL, NoSQL, Command)
- XSS attacks
- Path traversal
- Buffer overflow
- Malformed input
"""

import re
import logging
from typing import Optional, List, Any
from pydantic import BaseModel, validator, constr, field_validator

logger = logging.getLogger(__name__)


class InputValidator:
    """Centralized input validation utility"""

    # Dangerous patterns that indicate injection attempts
    DANGEROUS_PATTERNS = [
        # SQL injection patterns
        (r"('|\")\s*(OR|AND)\s*('|\")", "SQL injection pattern"),
        (r"(UNION|SELECT|INSERT|DELETE|UPDATE|DROP)\s", "SQL keywords"),
        (r";\s*(DROP|DELETE|INSERT|UPDATE)", "SQL statement chaining"),
        # NoSQL injection patterns
        (r"\{\s*\$", "NoSQL operator"),
        (r"\)\s*\{", "NoSQL injection pattern"),
        # Command injection
        (r"[;&|`$(){}[\]<>]", "Shell metacharacters"),
        # XSS patterns
        (r"<script", "Script tag"),
        (r"javascript:", "JavaScript protocol"),
        (r"onerror\s*=", "Event handler"),
        (r"onclick\s*=", "Event handler"),
        # Path traversal
        (r"\.\./", "Path traversal"),
        (r"\.\\\.", "Windows path traversal"),
        # Prototype pollution
        (r"__proto__", "Prototype pollution"),
        (r"constructor\s*\[", "Constructor access"),
        (r"prototype\s*\[", "Prototype access"),
    ]

    # Whitelist characters for various input types
    SESSION_ID_PATTERN = r"^[a-zA-Z0-9_-]{20,100}$"
    USER_ID_PATTERN = r"^[a-zA-Z0-9_-]{5,50}$"
    OBJECT_ID_PATTERN = r"^[a-f0-9]{24}$"

    @staticmethod
    def is_safe(text: str, strict: bool = False) -> tuple[bool, Optional[str]]:
        """
        Check if text contains dangerous patterns

        Args:
            text: Text to validate
            strict: If True, reject more patterns

        Returns:
            (is_safe: bool, reason: Optional[str])
        """
        if not isinstance(text, str):
            return False, "Input must be string"

        if len(text) > 100000:
            return False, "Input exceeds maximum length"

        if not text.strip():
            return False, "Input cannot be empty"

        # Check for dangerous patterns
        text_lower = text.lower()
        for pattern, reason in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"⚠️ Dangerous pattern detected: {reason} in input")
                return False, f"Input contains {reason}"

        # Additional strict checks
        if strict:
            if any(ord(c) < 32 and c not in "\n\r\t" for c in text):
                return False, "Input contains control characters"

        return True, None

    @staticmethod
    def sanitize(text: str) -> str:
        """
        Sanitize text by removing/escaping dangerous content

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        if not isinstance(text, str):
            return ""

        # Remove null bytes
        text = text.replace("\x00", "")

        # Remove control characters (except newline, tab, carriage return)
        text = "".join(
            c for c in text if ord(c) >= 32 or c in "\n\r\t"
        )

        # Trim whitespace
        text = text.strip()

        return text

    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """Validate session ID format"""
        if not isinstance(session_id, str):
            return False
        return bool(re.match(InputValidator.SESSION_ID_PATTERN, session_id))

    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """Validate user ID format"""
        if not isinstance(user_id, str):
            return False
        return bool(re.match(InputValidator.USER_ID_PATTERN, user_id))

    @staticmethod
    def validate_object_id(obj_id: str) -> bool:
        """Validate MongoDB ObjectId format"""
        if not isinstance(obj_id, str):
            return False
        return bool(re.match(InputValidator.OBJECT_ID_PATTERN, obj_id))


def validate_input(value: str, max_length: int = 10000, strict: bool = False) -> str:
    """
    Validate and sanitize input

    Args:
        value: Input to validate
        max_length: Maximum allowed length
        strict: Strict validation mode

    Returns:
        Sanitized input

    Raises:
        ValueError: If input is invalid
    """
    if not isinstance(value, str):
        raise ValueError("Input must be string")

    if len(value) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length}")

    is_safe, reason = InputValidator.is_safe(value, strict=strict)
    if not is_safe:
        raise ValueError(f"Input validation failed: {reason}")

    return InputValidator.sanitize(value)


# Pydantic Models for input validation

class SafeStringInput(BaseModel):
    """Base model for safe string input"""

    text: constr(
        max_length=10000,
        strip_whitespace=True,
        min_length=1,
    )

    @field_validator("text")
    @classmethod
    def validate_no_injection(cls, v: str) -> str:
        """Validate text contains no injection patterns"""
        is_safe, reason = InputValidator.is_safe(v)
        if not is_safe:
            raise ValueError(f"Input validation failed: {reason}")
        return InputValidator.sanitize(v)


class QueryInput(SafeStringInput):
    """Validated financial query input"""

    text: constr(
        max_length=5000,
        strip_whitespace=True,
        min_length=5,
    )


class SessionIdInput(BaseModel):
    """Validated session ID input"""

    session_id: str

    @field_validator("session_id")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate session ID format"""
        if not InputValidator.validate_session_id(v):
            raise ValueError("Invalid session ID format")
        return v


class UserIdInput(BaseModel):
    """Validated user ID input"""

    user_id: str

    @field_validator("user_id")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate user ID format"""
        if not InputValidator.validate_user_id(v):
            raise ValueError("Invalid user ID format")
        return v


class ObjectIdInput(BaseModel):
    """Validated MongoDB ObjectId input"""

    object_id: str

    @field_validator("object_id")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate ObjectId format"""
        if not InputValidator.validate_object_id(v):
            raise ValueError("Invalid ObjectId format")
        return v


class MessageInput(BaseModel):
    """Validated chat message input"""

    message: constr(
        max_length=5000,
        strip_whitespace=True,
        min_length=1,
    )
    session_id: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message contains no injection"""
        is_safe, reason = InputValidator.is_safe(v)
        if not is_safe:
            raise ValueError(f"Message validation failed: {reason}")
        return InputValidator.sanitize(v)

    @field_validator("session_id")
    @classmethod
    def validate_session(cls, v: str) -> str:
        """Validate session ID format"""
        if not InputValidator.validate_session_id(v):
            raise ValueError("Invalid session ID format")
        return v


class AnalysisParameterInput(BaseModel):
    """Validated analysis parameter input"""

    parameter_name: constr(
        max_length=100,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
    )
    parameter_value: str

    @field_validator("parameter_value")
    @classmethod
    def validate_value(cls, v: str) -> str:
        """Validate parameter value"""
        if len(v) > 1000:
            raise ValueError("Parameter value too long")
        return InputValidator.sanitize(v)
