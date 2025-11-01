#!/usr/bin/env python3
"""
Abstract queue interface for execution queue implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, AsyncGenerator, Optional

class ExecutionQueueInterface(ABC):
    """Abstract interface for execution queue implementations"""
    
    @abstractmethod
    async def enqueue(self, execution_data: Dict[str, Any]) -> str:
        """
        Add execution to queue
        
        Args:
            execution_data: Dict containing execution details
            
        Returns:
            execution_id: Unique identifier for the queued execution
        """
        pass
    
    @abstractmethod 
    async def dequeue(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Get next execution for worker (atomic claim operation)
        
        Args:
            worker_id: Unique identifier for the worker
            
        Returns:
            Execution data dict or None if queue empty
        """
        pass
    
    @abstractmethod
    async def ack(self, execution_id: str, result: Dict[str, Any]) -> bool:
        """
        Mark execution as completed successfully
        
        Args:
            execution_id: Execution identifier
            result: Execution result data
            
        Returns:
            True if successfully acknowledged
        """
        pass
    
    @abstractmethod
    async def nack(self, execution_id: str, error: str, retry: bool = True) -> bool:
        """
        Mark execution as failed
        
        Args:
            execution_id: Execution identifier
            error: Error description
            retry: Whether execution should be retried
            
        Returns:
            True if successfully marked as failed
        """
        pass
    
    @abstractmethod
    async def get_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get execution status and logs
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Dict with status, logs, and other metadata
        """
        pass
    
    @abstractmethod
    async def stream_logs(self, execution_id: str) -> AsyncGenerator[Dict, None]:
        """
        Stream real-time execution logs
        
        Args:
            execution_id: Execution identifier
            
        Yields:
            Log entry dictionaries
        """
        pass
    
    @abstractmethod
    async def update_logs(self, execution_id: str, log_entry: Dict[str, Any]) -> bool:
        """
        Add a log entry to execution
        
        Args:
            execution_id: Execution identifier
            log_entry: Log entry with timestamp, level, message
            
        Returns:
            True if log was added successfully
        """
        pass
    