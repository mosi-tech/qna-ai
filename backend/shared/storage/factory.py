#!/usr/bin/env python3
"""
Storage provider factory
"""

import os
from typing import Optional, Dict, Any

from .interface import StorageInterface
from .local import LocalStorageProvider


def create_storage_provider(
    provider_type: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> StorageInterface:
    """
    Create storage provider based on environment or configuration
    
    Args:
        provider_type: 'local' or 's3'. If None, reads from STORAGE_PROVIDER env var
        config: Provider-specific configuration
    
    Returns:
        StorageInterface instance
    """
    
    if provider_type is None:
        provider_type = os.getenv('STORAGE_PROVIDER', 'local').lower()
    
    config = config or {}
    
    if provider_type == 'local':
        base_path = config.get('base_path') or os.getenv(
            'STORAGE_LOCAL_PATH', 
            '/Users/shivc/Documents/Workspace/JS/qna-ai-admin/backend/mcp-server/scripts'
        )
        temp_path = config.get('temp_path') or os.getenv(
            'STORAGE_LOCAL_TEMP_PATH',
            '/Users/shivc/Documents/Workspace/JS/qna-ai-admin/backend/mcp-server/temp'
        )
        
        return LocalStorageProvider(base_path=base_path, temp_path=temp_path)
    
    elif provider_type == 's3':
        try:
            from .s3 import S3StorageProvider
        except ImportError:
            raise ImportError("boto3 is required for S3 storage. Install with: pip install boto3")
        
        bucket_name = config.get('bucket_name') or os.getenv('STORAGE_S3_BUCKET')
        if not bucket_name:
            raise ValueError("S3 bucket name must be provided via config or STORAGE_S3_BUCKET env var")
        
        prefix = config.get('prefix') or os.getenv('STORAGE_S3_PREFIX', 'scripts/')
        region = config.get('region') or os.getenv('AWS_REGION', 'us-east-1')
        
        return S3StorageProvider(
            bucket_name=bucket_name,
            prefix=prefix,
            region=region
        )
    
    else:
        raise ValueError(f"Unknown storage provider: {provider_type}. Supported: 'local', 's3'")


# Global storage instance (lazy-loaded)
_storage_instance: Optional[StorageInterface] = None


def get_storage() -> StorageInterface:
    """Get global storage instance (singleton pattern)"""
    global _storage_instance
    
    if _storage_instance is None:
        _storage_instance = create_storage_provider()
    
    return _storage_instance


def set_storage(storage: StorageInterface) -> None:
    """Set global storage instance (for testing)"""
    global _storage_instance
    _storage_instance = storage