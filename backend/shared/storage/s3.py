#!/usr/bin/env python3
"""
AWS S3 storage provider
"""

import json
import tempfile
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from .interface import StorageInterface

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class S3StorageProvider(StorageInterface):
    """AWS S3 storage provider"""
    
    def __init__(self, bucket_name: str, prefix: str = "scripts/", region: str = "us-east-1"):
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for S3 storage. Install with: pip install boto3")
        
        self.bucket_name = bucket_name
        self.prefix = prefix.rstrip('/') + '/' if prefix else ''
        self.temp_prefix = f"{self.prefix}temp/"
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client('s3', region_name=region)
            # Test credentials
            self.s3_client.head_bucket(Bucket=bucket_name)
        except (ClientError, NoCredentialsError) as e:
            raise ConnectionError(f"Failed to connect to S3: {e}")
    
    def _get_script_key(self, script_name: str) -> str:
        """Get S3 key for script"""
        return f"{self.prefix}{script_name}"
    
    def _get_metadata_key(self, script_name: str) -> str:
        """Get S3 key for script metadata"""
        return f"{self.prefix}{script_name}.meta"
    
    async def read_script(self, script_name: str) -> str:
        """Read script content by name"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=self._get_script_key(script_name)
            )
            return response['Body'].read().decode('utf-8')
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"Script not found: {script_name}")
            raise
    
    async def write_script(self, script_name: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Write script content with optional metadata"""
        try:
            # Upload script content
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=self._get_script_key(script_name),
                Body=content.encode('utf-8'),
                ContentType='text/x-python'
            )
            
            # Upload metadata if provided
            if metadata:
                metadata_with_timestamp = {
                    **metadata,
                    "created_at": datetime.now().isoformat(),
                    "size": len(content)
                }
                
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=self._get_metadata_key(script_name),
                    Body=json.dumps(metadata_with_timestamp, indent=2).encode('utf-8'),
                    ContentType='application/json'
                )
            
            return True
            
        except Exception:
            return False
    
    async def delete_script(self, script_name: str) -> bool:
        """Delete script by name"""
        try:
            # Delete script and metadata
            objects_to_delete = [
                {'Key': self._get_script_key(script_name)},
                {'Key': self._get_metadata_key(script_name)}
            ]
            
            self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete={'Objects': objects_to_delete, 'Quiet': True}
            )
            
            return True
            
        except Exception:
            return False
    
    async def list_scripts(self, prefix: Optional[str] = None) -> List[str]:
        """List all script names, optionally filtered by prefix"""
        scripts = []
        search_prefix = self.prefix
        
        if prefix:
            search_prefix += prefix
        
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=search_prefix)
            
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        key = obj['Key']
                        if not key.endswith('.meta'):  # Skip metadata files
                            script_name = key[len(self.prefix):]  # Remove prefix
                            scripts.append(script_name)
            
            return sorted(scripts)
            
        except Exception:
            return []
    
    async def script_exists(self, script_name: str) -> bool:
        """Check if script exists"""
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=self._get_script_key(script_name)
            )
            return True
        except ClientError:
            return False
    
    async def get_script_metadata(self, script_name: str) -> Optional[Dict[str, Any]]:
        """Get script metadata (size, modified time, etc.)"""
        try:
            # Get object metadata
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=self._get_script_key(script_name)
            )
            
            metadata = {
                "name": script_name,
                "size": response['ContentLength'],
                "modified": response['LastModified'].isoformat(),
                "etag": response['ETag'].strip('"')
            }
            
            # Try to get custom metadata
            try:
                meta_response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=self._get_metadata_key(script_name)
                )
                custom_metadata = json.loads(meta_response['Body'].read().decode('utf-8'))
                metadata.update(custom_metadata)
            except ClientError:
                pass  # No custom metadata
            
            return metadata
            
        except ClientError:
            return None
    
    async def write_temp_script(self, content: str, prefix: str = "temp_") -> str:
        """Write temporary script and return its S3 key"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = uuid.uuid4().hex[:4]
        script_name = f"{prefix}script_{timestamp}_{random_suffix}.py"
        
        key = f"{self.temp_prefix}{script_name}"
        
        # Upload with expiration metadata
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=content.encode('utf-8'),
            ContentType='text/x-python',
            Metadata={
                'temp-file': 'true',
                'created-at': datetime.now().isoformat()
            }
        )
        
        return key  # Return S3 key for temp scripts
    
    async def cleanup_temp_scripts(self, older_than_minutes: int = 60) -> int:
        """Clean up old temporary scripts"""
        cutoff_time = datetime.now() - timedelta(minutes=older_than_minutes)
        deleted_count = 0
        
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=self.temp_prefix)
            
            objects_to_delete = []
            
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if obj['LastModified'].replace(tzinfo=None) < cutoff_time:
                            objects_to_delete.append({'Key': obj['Key']})
            
            # Delete in batches of 1000 (S3 limit)
            for i in range(0, len(objects_to_delete), 1000):
                batch = objects_to_delete[i:i+1000]
                if batch:
                    self.s3_client.delete_objects(
                        Bucket=self.bucket_name,
                        Delete={'Objects': batch, 'Quiet': True}
                    )
                    deleted_count += len(batch)
            
            return deleted_count
            
        except Exception:
            return 0