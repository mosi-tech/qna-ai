"""
FastAPI Routes for Execution Management
"""

import json
import logging
from datetime import datetime
from fastapi import HTTPException
from typing import Dict, Any, Optional, List

from shared.services.execution_queue_service import execution_queue_service
from .auth import UserContext, validate_user_access_to_execution

logger = logging.getLogger("execution-routes")


class ExecutionRoutes:
    """Handles execution-related API route logic"""
    
    def __init__(self):
        pass
    
    async def get_execution_status(self, execution_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Get the status of an execution from the queue with user authentication"""
        try:
            status_data = await execution_queue_service.get_execution_status(execution_id)
            
            # Validate user access to this execution
            if not validate_user_access_to_execution(status_data, user_context):
                raise HTTPException(
                    status_code=403, 
                    detail="Access denied: You don't have permission to view this execution"
                )
            
            return {
                "success": True,
                "data": status_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to get execution status {execution_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_execution_logs(self, execution_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Get the logs for an execution with user authentication"""
        try:
            status_data = await execution_queue_service.get_execution_status(execution_id)
            
            # Validate user access to this execution
            if not validate_user_access_to_execution(status_data, user_context):
                raise HTTPException(
                    status_code=403, 
                    detail="Access denied: You don't have permission to view this execution"
                )
            
            logs = status_data.get("execution_logs", [])
            
            return {
                "success": True,
                "data": {
                    "execution_id": execution_id,
                    "logs": logs,
                    "status": status_data.get("status"),
                    "user_id": status_data.get("user_id"),
                    "session_id": status_data.get("session_id")
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to get execution logs {execution_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    
    async def get_user_executions(self, user_context: UserContext, limit: int = 50, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """Get all executions for the authenticated user"""
        try:
            # Use the authenticated user's ID
            executions = await execution_queue_service.get_executions_by_user(
                user_id=user_context.user_id, 
                limit=limit, 
                status_filter=status_filter
            )
            
            return {
                "success": True,
                "data": {
                    "user_id": user_context.user_id,
                    "executions": executions,
                    "total_count": len(executions),
                    "status_filter": status_filter
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get user executions for {user_context.user_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_session_executions(self, session_id: str, user_context: UserContext, limit: int = 50, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """Get all executions for a specific session (with user validation)"""
        try:
            # Get executions for the session
            executions = await execution_queue_service.get_executions_by_session(
                session_id=session_id, 
                limit=limit, 
                status_filter=status_filter
            )
            
            # Filter executions to only include those belonging to the authenticated user
            user_executions = [
                execution for execution in executions 
                if execution.get("user_id") == user_context.user_id
            ]
            
            return {
                "success": True,
                "data": {
                    "session_id": session_id,
                    "user_id": user_context.user_id,
                    "executions": user_executions,
                    "total_count": len(user_executions),
                    "status_filter": status_filter
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get session executions for {session_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }