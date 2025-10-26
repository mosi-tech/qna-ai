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
from ..execution import execute_script

logger = logging.getLogger(__name__)

class ExecutionQueueWorker:
    """Worker that polls execution queue and processes scripts"""
    
    def __init__(
        self, 
        queue: ExecutionQueueInterface,
        worker_id: Optional[str] = None,
        poll_interval: int = 5,
        max_concurrent_executions: int = 3
    ):
        self.queue = queue
        self.worker_id = worker_id or f"worker_{uuid.uuid4().hex[:8]}"
        self.poll_interval = poll_interval
        self.max_concurrent_executions = max_concurrent_executions
        self.running = False
        self.active_executions = set()
        
        logger.info(f"🔧 Created worker: {self.worker_id}")
    
    async def start(self):
        """Start the worker polling loop"""
        logger.info(f"🚀 Starting worker {self.worker_id}")
        self.running = True
        
        try:
            while self.running:
                try:
                    # Check if we can handle more executions
                    if len(self.active_executions) < self.max_concurrent_executions:
                        # Try to claim an execution
                        execution = await self.queue.dequeue(self.worker_id)
                        
                        if execution:
                            # Process execution in background
                            task = asyncio.create_task(self._process_execution(execution))
                            self.active_executions.add(task)
                            
                            # Clean up completed tasks
                            self.active_executions = {
                                task for task in self.active_executions 
                                if not task.done()
                            }
                        else:
                            # No executions available, wait before next poll
                            await asyncio.sleep(self.poll_interval)
                    else:
                        # At capacity, wait for some executions to complete
                        await asyncio.sleep(1)
                        
                        # Clean up completed tasks
                        self.active_executions = {
                            task for task in self.active_executions 
                            if not task.done()
                        }
                
                except Exception as e:
                    logger.error(f"❌ Error in worker polling loop: {e}")
                    await asyncio.sleep(5)  # Wait longer on error
        
        except asyncio.CancelledError:
            logger.info(f"🛑 Worker {self.worker_id} cancelled")
        finally:
            await self._shutdown()
    
    async def stop(self):
        """Stop the worker gracefully"""
        logger.info(f"🛑 Stopping worker {self.worker_id}")
        self.running = False
        
        # Wait for active executions to complete (with timeout)
        if self.active_executions:
            logger.info(f"⏳ Waiting for {len(self.active_executions)} active executions to complete")
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.active_executions, return_exceptions=True),
                    timeout=30
                )
            except asyncio.TimeoutError:
                logger.warning("⚠️ Timeout waiting for executions to complete")
    
    async def _shutdown(self):
        """Clean up worker resources"""
        # Cancel any remaining tasks
        for task in self.active_executions:
            if not task.done():
                task.cancel()
        
        logger.info(f"✅ Worker {self.worker_id} shutdown complete")
    
    async def _process_execution(self, execution: Dict[str, Any]):
        """Process a single execution"""
        execution_id = execution.get("execution_id")
        
        try:
            logger.info(f"🔨 Processing execution: {execution_id}")
            
            # Log start
            await self.queue.update_logs(execution_id, {
                "level": "INFO",
                "message": f"Execution started by worker {self.worker_id}"
            })
            
            # Execute the script using shared execution logic
            result = await self._execute_script_with_logging(execution)
            
            if result.get("success"):
                # Success - ack the execution
                await self.queue.ack(execution_id, result)
                
                await self.queue.update_logs(execution_id, {
                    "level": "INFO", 
                    "message": f"Execution completed successfully in {result.get('execution_time', 0):.2f}s"
                })
                
                logger.info(f"✅ Completed execution: {execution_id}")
            else:
                # Failure - nack the execution
                error_msg = result.get("error", "Unknown error")
                await self.queue.nack(execution_id, error_msg, retry=True)
                
                await self.queue.update_logs(execution_id, {
                    "level": "ERROR",
                    "message": f"Execution failed: {error_msg}"
                })
                
                logger.warning(f"❌ Failed execution: {execution_id} - {error_msg}")
        
        except Exception as e:
            logger.error(f"❌ Error processing execution {execution_id}: {e}")
            
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
        script_content = execution.get("script_content")
        parameters = execution.get("parameters", {})
        timeout_seconds = execution.get("timeout_seconds", 300)
        
        if not script_content:
            return {
                "success": False,
                "error": "No script content provided",
                "execution_time": 0
            }
        
        try:
            # Log script details
            await self.queue.update_logs(execution_id, {
                "level": "INFO",
                "message": f"Executing script: {execution.get('script_name', 'Unknown')}"
            })
            
            if parameters:
                await self.queue.update_logs(execution_id, {
                    "level": "INFO",
                    "message": f"Parameters: {parameters}"
                })
            
            # Execute script in production mode (mock_mode=False)
            start_time = datetime.now()
            
            result = execute_script(
                script_content=script_content,
                mock_mode=False,  # Production mode for queue executions
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