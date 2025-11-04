"""
SSE Services Package

Contains internal SSE emission functions that bypass the queue system.
These should ONLY be used by Progress Monitor and SSE infrastructure.

For API routes and business logic, use shared.services.progress_service instead.
"""

from .progress_sse import (
    progress_sse_manager,
    ProgressEvent,
    ProgressLevel,
    ExecutionStatus,
    # Internal SSE functions (prefixed with _sse_)
    _sse_emit_progress,
    _sse_progress_info,
    _sse_progress_success,
    _sse_progress_error,
)

__all__ = [
    'progress_sse_manager',
    'ProgressEvent',
    'ProgressLevel', 
    'ExecutionStatus',
    '_sse_emit_progress',
    '_sse_progress_info',
    '_sse_progress_success',
    '_sse_progress_error',
]