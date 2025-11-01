#!/usr/bin/env python3
"""
Execution Queue Worker

Polls the queue for pending executions and processes them using the shared execution logic.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from .base_queue import ExecutionQueueInterface
from .base_worker import BaseQueueWorker
from ..execution import execute_script
from ..storage import get_storage
from ..services.result_formatter import create_shared_result_formatter
from shared.services.progress_service import send_progress_event

# Import AuditService for updating execution documents
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scriptEdition', 'apiServer'))
from services.audit_service import AuditService
from db import RepositoryManager, MongoDBClient

# Note: Progress communication now uses queue-based messaging via send_progress_event

logger = logging.getLogger(__name__)

class ExecutionQueueWorker(BaseQueueWorker):
    """Worker that polls execution queue and processes scripts"""
    
    def __init__(
        self, 
        queue: ExecutionQueueInterface,
        worker_id: Optional[str] = None,
        poll_interval: int = 5,
        max_concurrent_executions: int = 3
    ):
        super().__init__(
            queue=queue,
            worker_id=worker_id,
            poll_interval=poll_interval,
            max_concurrent_items=max_concurrent_executions,
            worker_type="execution_worker"
        )
        self.audit_service = None
        self.result_formatter = None
    
    async def _initialize_services(self):
        """Initialize execution worker services"""
        # Initialize AuditService for updating execution documents
        try:
            db_client = MongoDBClient()
            repo_manager = RepositoryManager(db_client)
            await repo_manager.initialize()
            self.audit_service = AuditService(repo_manager)
            logger.info("✅ AuditService initialized for execution updates")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize AuditService: {e}")
            self.audit_service = None
        
        # Initialize result formatter
        try:
            self.result_formatter = create_shared_result_formatter()
            logger.info("✅ ResultFormatter initialized for markdown generation")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize ResultFormatter: {e}")
            self.result_formatter = None
        
        # Progress communication now uses queue-based messaging via send_progress_event
        logger.info("✅ Progress communication will use queue-based messaging")
    
    async def _dequeue_item(self):
        """Dequeue an execution from the queue"""
        return await self.queue.dequeue(self.worker_id)
    
    async def _process_item(self, item: Dict[str, Any]):
        """Process a single execution (renamed from _process_execution)"""
        return await self._process_execution(item)
    
    
    async def _process_execution(self, execution: Dict[str, Any]):
        """Process a single execution"""
        execution_id = execution.get("execution_id")
        session_id = execution.get("session_id")
        analysis_id = execution.get("analysis_id")
        
        try:
            logger.info(f"🔨 Processing execution: {execution_id}")
            
            # CRITICAL: Send SSE update when execution starts running via queue
            if session_id:
                try:
                    await send_progress_event(session_id, {
                        "type": "execution_status",
                        "execution_id": execution_id,
                        "analysis_id": analysis_id,
                        "status": "running",
                        "message": "Analysis execution in progress",
                        "level": "info"
                    })
                    logger.info(f"📡 Sent SSE running status via queue for sessionL {session_id} and execution: {execution_id}")
                except Exception as sse_error:
                    logger.warning(f"⚠️ Failed to send SSE running status via queue: {sse_error}")
            
            # Log start
            await self.queue.update_logs(execution_id, {
                "level": "INFO",
                "message": f"Execution started by worker {self.worker_id}"
            })
            
            # Execute the script using shared execution logic
            result = await self._execute_script_with_logging(execution)
            
            # Update both queue and audit service
            success = result.get("success", False)
            execution_time_ms = int((result.get("execution_time", 0)) * 1000)  # Convert to milliseconds
            
            if success:
                # Step 1: Generate markdown from results if possible
                result_output = result.get("output", {})
                
                # Try to generate markdown if formatter is available
                if self.result_formatter and result_output.get("results"):
                    try:
                        logger.info(f"🤖 Generating markdown for execution: {execution_id}")
                        
                        # Try to get original question from execution context
                        user_question = execution.get("user_question")  # May not be available
                        
                        markdown = await self.result_formatter.format_execution_result(
                            result_output, 
                            user_question
                        )
                        
                        if markdown:
                            # Add markdown to result output
                            result_output["markdown"] = markdown
                            logger.info(f"✅ Generated markdown for execution: {execution_id}")
                        else:
                            logger.info(f"⚠️ No markdown generated for execution: {execution_id}")
                            
                    except Exception as markdown_error:
                        logger.warning(f"⚠️ Failed to generate markdown for {execution_id}: {markdown_error}")
                        # Continue without markdown - don't fail the execution
                
                # Step 2: CRITICAL: Update audit service execution document FIRST
                audit_success = False
                if self.audit_service:
                    try:
                        await self.audit_service.log_execution_complete(
                            execution_id=execution_id,
                            result=result_output,  # Now includes markdown if generated
                            execution_time_ms=execution_time_ms,
                            success=True
                        )
                        audit_success = True
                        logger.info(f"✅ Updated audit execution document: {execution_id}")
                    except Exception as audit_error:
                        logger.error(f"❌ CRITICAL: Failed to update audit execution: {audit_error}")
                        # Don't ack the queue - let it retry
                        await self.queue.nack(execution_id, f"Audit save failed: {audit_error}", retry=True)
                        return
                else:
                    logger.warning(f"⚠️ No audit service available - proceeding with queue ack")
                    audit_success = True  # Proceed if no audit service configured
                
                # Only ack the queue AFTER successful audit save
                if audit_success:
                    await self.queue.ack(execution_id, result)
                    logger.info(f"✅ Acknowledged queue after successful audit save: {execution_id}")
                
                # CRITICAL: Send SSE completion update with results via queue
                if session_id:
                    try:
                        await send_progress_event(session_id, {
                            "type": "execution_status",
                            "execution_id": execution_id,
                            "analysis_id": analysis_id,
                            "status": "completed",
                            "message": "Analysis execution completed",
                            "level": "success",
                            "results": result_output,
                            "markdown": result_output.get("markdown"),
                            "execution_time": result.get('execution_time', 0)
                        })
                        logger.info(f"📡 Sent SSE completed status via queue for session: {session_id} and execution: {execution_id}")
                    except Exception as sse_error:
                        logger.warning(f"⚠️ Failed to send SSE completed status via queue: {sse_error}")
                
                await self.queue.update_logs(execution_id, {
                    "level": "INFO", 
                    "message": f"Execution completed successfully in {result.get('execution_time', 0):.2f}s"
                })
                
                logger.info(f"✅ Completed execution: {execution_id}")
            else:
                # Failure case: Update audit service first, then nack queue
                error_msg = result.get("error", "Unknown error")
                
                # Try to save failure to audit service first
                if self.audit_service:
                    try:
                        await self.audit_service.log_execution_complete(
                            execution_id=execution_id,
                            result={"error": error_msg},
                            execution_time_ms=execution_time_ms,
                            success=False
                        )
                        logger.info(f"❌ Updated audit execution document with failure: {execution_id}")
                    except Exception as audit_error:
                        logger.error(f"❌ CRITICAL: Failed to update audit execution with failure: {audit_error}")
                        # Even if audit fails, still nack the queue so it can retry everything
                
                # Nack the execution in queue (after audit attempt)
                await self.queue.nack(execution_id, error_msg, retry=True)
                
                # CRITICAL: Send SSE failure update via queue
                if session_id:
                    try:
                        await send_progress_event(session_id, {
                            "type": "execution_status",
                            "execution_id": execution_id,
                            "analysis_id": analysis_id,
                            "status": "failed",
                            "message": f"Analysis execution failed: {error_msg}",
                            "level": "error",
                            "error": error_msg
                        })
                        logger.info(f"📡 Sent SSE failed status via queue for execution: {execution_id}")
                    except Exception as sse_error:
                        logger.warning(f"⚠️ Failed to send SSE failed status via queue: {sse_error}")
                
                await self.queue.update_logs(execution_id, {
                    "level": "ERROR",
                    "message": f"Execution failed: {error_msg}"
                })
                
                logger.warning(f"❌ Failed execution: {execution_id} - {error_msg}")
        
        except Exception as e:
            logger.error(f"❌ Error processing execution {execution_id}: {e}")
            
            # CRITICAL: Send SSE failure update for unexpected errors via queue
            if session_id:
                try:
                    await send_progress_event(session_id, {
                        "type": "execution_status",
                        "execution_id": execution_id,
                        "analysis_id": analysis_id,
                        "status": "failed",
                        "message": f"Worker error: {str(e)}",
                        "level": "error",
                        "error": str(e)
                    })
                    logger.info(f"📡 Sent SSE failed status via queue for worker error: {execution_id}")
                except Exception as sse_error:
                    logger.warning(f"⚠️ Failed to send SSE failed status via queue for worker error: {sse_error}")
            
            try:
                await self.queue.nack(execution_id, str(e), retry=True)
                await self.queue.update_logs(execution_id, {
                    "level": "ERROR",
                    "message": f"Worker error: {str(e)}"
                })
            except Exception as log_error:
                logger.error(f"❌ Failed to log error for {execution_id}: {log_error}")
    
    async def _execute_script_with_logging(self, execution: Dict[str, Any]) -> Dict[str, Any]:
        """Execute script and capture logs"""
        execution_id = execution.get("execution_id")
        execution_params = execution.get("execution_params", {})
        
        # Convert null values to None for Python compatibility
        def convert_nulls(obj):
            if obj is None or obj == "null":
                return None
            elif isinstance(obj, dict):
                return {k: convert_nulls(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_nulls(item) for item in obj]
            return obj
        
        
        # Extract script info from execution_params
        script_name = execution_params.get("script_name")
        parameters = execution_params.get("parameters", {})
        timeout_seconds = execution.get("timeout_seconds", 300)
        
        parameters = convert_nulls(parameters)

        if not script_name:
            return {
                "success": False,
                "error": "No script name provided",
                "execution_time": 0
            }
        
        try:
            # Log script details
            await self.queue.update_logs(execution_id, {
                "level": "INFO",
                "message": f"Executing script: {script_name}"
            })
            
            if parameters:
                await self.queue.update_logs(execution_id, {
                    "level": "INFO",
                    "message": f"Parameters: {parameters}"
                })
            
            # Execute script in production mode (mock_mode=False)
            start_time = datetime.now()
            
            # Load script content from storage
            storage = get_storage()
            
            try:
                script_content = await storage.read_script(script_name)
            except FileNotFoundError:
                return {
                    "success": False,
                    "error": f"Script file not found: {script_name}",
                    "execution_time": 0
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to read script from storage: {str(e)}",
                    "execution_time": 0
                }
            # TODO: Change it to False when ready
            result = execute_script(
                script_content=script_content,
                mock_mode=True,  #a Production mode for queue executions
                timeout=timeout_seconds,
                parameters=parameters
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log execution details
            if result.get("success"):
                await self.queue.update_logs(execution_id, {
                    "level": "INFO",
                    "message": f"Script execution successful"
                })
                
                # Log output summary if available
                output = result.get("output", {})
                if isinstance(output, dict) and "description" in output:
                    await self.queue.update_logs(execution_id, {
                        "level": "INFO",
                        "message": f"Analysis: {output['description'][:200]}..."
                    })
            else:
                await self.queue.update_logs(execution_id, {
                    "level": "ERROR",
                    "message": f"Script execution failed: {result.get('error', 'Unknown error')}"
                })
            
            # Add execution time to result
            result["execution_time"] = execution_time
            
            return result
        
        except Exception as e:
            await self.queue.update_logs(execution_id, {
                "level": "ERROR",
                "message": f"Execution exception: {str(e)}"
            })
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }