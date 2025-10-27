"""
Shared utilities and services for QnA AI Admin backend
"""

from .storage import get_storage
from .execution import execute_script
from .queue import ExecutionQueueInterface

__version__ = "1.0.0"

__all__ = [
    'get_storage',
    'execute_script', 
    'ExecutionQueueInterface',
]