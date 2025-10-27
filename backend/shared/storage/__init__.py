"""
Storage abstraction layer for scripts and assets
"""

from .interface import StorageInterface
from .local import LocalStorageProvider
from .factory import create_storage_provider, get_storage

__all__ = [
    'StorageInterface',
    'LocalStorageProvider', 
    'create_storage_provider',
    'get_storage'
]