#!/usr/bin/env python3
"""
Storage interface for scripts and assets
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pathlib import Path


class StorageInterface(ABC):
    """Abstract interface for storage providers (S3, local filesystem, etc.)"""
    
    @abstractmethod
    async def read_script(self, script_name: str) -> str:
        """Read script content by name"""
        pass
    
    @abstractmethod
    async def write_script(self, script_name: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Write script content with optional metadata"""
        pass
    
    @abstractmethod
    async def delete_script(self, script_name: str) -> bool:
        """Delete script by name"""
        pass
    
    @abstractmethod
    async def list_scripts(self, prefix: Optional[str] = None) -> List[str]:
        """List all script names, optionally filtered by prefix"""
        pass
    
    @abstractmethod
    async def script_exists(self, script_name: str) -> bool:
        """Check if script exists"""
        pass
    
    @abstractmethod
    async def get_script_metadata(self, script_name: str) -> Optional[Dict[str, Any]]:
        """Get script metadata (size, modified time, etc.)"""
        pass
    
    @abstractmethod
    async def write_temp_script(self, content: str, prefix: str = "temp_") -> str:
        """Write temporary script and return its name/path"""
        pass
    
    @abstractmethod
    async def cleanup_temp_scripts(self, older_than_minutes: int = 60) -> int:
        """Clean up old temporary scripts"""
        pass