#!/usr/bin/env python3
"""
Local filesystem storage provider
"""

import os
import json
import aiofiles
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import tempfile
import uuid

from .interface import StorageInterface


class LocalStorageProvider(StorageInterface):
    """Local filesystem storage provider"""
    
    def __init__(self, base_path: str, temp_path: Optional[str] = None):
        self.base_path = Path(base_path)
        self.temp_path = Path(temp_path) if temp_path else self.base_path / "temp"
        
        # Ensure directories exist
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
    
    def _get_script_path(self, script_name: str) -> Path:
        """Get full path for script file"""
        return self.base_path / script_name
    
    def _get_metadata_path(self, script_name: str) -> Path:
        """Get path for script metadata file"""
        return self.base_path / f"{script_name}.meta"
    
    async def read_script(self, script_name: str) -> str:
        """Read script content by name"""
        script_path = self._get_script_path(script_name)
        
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_name}")
        
        async with aiofiles.open(script_path, 'r') as f:
            return await f.read()
    
    async def write_script(self, script_name: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Write script content with optional metadata"""
        try:
            script_path = self._get_script_path(script_name)
            
            # Write script content
            async with aiofiles.open(script_path, 'w') as f:
                await f.write(content)
            
            # Make executable if it's a Python script
            if script_name.endswith('.py'):
                os.chmod(script_path, 0o755)
            
            # Write metadata if provided
            if metadata:
                metadata_path = self._get_metadata_path(script_name)
                metadata_with_timestamp = {
                    **metadata,
                    "created_at": datetime.now().isoformat(),
                    "size": len(content)
                }
                
                async with aiofiles.open(metadata_path, 'w') as f:
                    await f.write(json.dumps(metadata_with_timestamp, indent=2))
            
            return True
            
        except Exception:
            return False
    
    async def delete_script(self, script_name: str) -> bool:
        """Delete script by name"""
        try:
            script_path = self._get_script_path(script_name)
            metadata_path = self._get_metadata_path(script_name)
            
            if script_path.exists():
                script_path.unlink()
            
            if metadata_path.exists():
                metadata_path.unlink()
            
            return True
            
        except Exception:
            return False
    
    async def list_scripts(self, prefix: Optional[str] = None) -> List[str]:
        """List all script names, optionally filtered by prefix"""
        scripts = []
        
        for file_path in self.base_path.iterdir():
            if file_path.is_file() and not file_path.name.endswith('.meta'):
                if prefix is None or file_path.name.startswith(prefix):
                    scripts.append(file_path.name)
        
        return sorted(scripts)
    
    async def script_exists(self, script_name: str) -> bool:
        """Check if script exists"""
        return self._get_script_path(script_name).exists()
    
    async def get_script_metadata(self, script_name: str) -> Optional[Dict[str, Any]]:
        """Get script metadata (size, modified time, etc.)"""
        script_path = self._get_script_path(script_name)
        metadata_path = self._get_metadata_path(script_name)
        
        if not script_path.exists():
            return None
        
        # Get file stats
        stat = script_path.stat()
        metadata = {
            "name": script_name,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
        }
        
        # Add custom metadata if exists
        if metadata_path.exists():
            try:
                async with aiofiles.open(metadata_path, 'r') as f:
                    custom_metadata = json.loads(await f.read())
                    metadata.update(custom_metadata)
            except Exception:
                pass  # Ignore metadata read errors
        
        return metadata
    
    async def write_temp_script(self, content: str, prefix: str = "temp_") -> str:
        """Write temporary script and return its name/path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = uuid.uuid4().hex[:4]
        script_name = f"{prefix}script_{timestamp}_{random_suffix}.py"
        
        script_path = self.temp_path / script_name
        
        async with aiofiles.open(script_path, 'w') as f:
            await f.write(content)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        return str(script_path)  # Return full path for temp scripts
    
    async def cleanup_temp_scripts(self, older_than_minutes: int = 60) -> int:
        """Clean up old temporary scripts"""
        cutoff_time = datetime.now() - timedelta(minutes=older_than_minutes)
        deleted_count = 0
        
        for file_path in self.temp_path.iterdir():
            if file_path.is_file():
                file_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_modified < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception:
                        pass  # Ignore deletion errors
        
        return deleted_count