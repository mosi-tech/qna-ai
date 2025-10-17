"""
Execution Service - Orchestrates script execution via execution server
"""

import logging
import os
import json
import httpx
from typing import Optional, Dict, Any
from datetime import datetime

from db.repositories import RepositoryManager
from db.schemas import AnalysisModel, ExecutionStatus

logger = logging.getLogger("execution-service")


class ExecutionService:
    """Service for executing analysis scripts and managing results"""
    
    def __init__(self, repo_manager: RepositoryManager):
        self.repo = repo_manager
        self.analysis_repo = repo_manager.analysis
        self.audit_repo = repo_manager.execution
        self.logger = logger
    
    async def execute_analysis(
        self,
        analysis_id: str,
        user_id: str,
        session_id: Optional[str] = None,
        timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Execute an analysis script and populate results
        
        Flow:
        1. Fetch AnalysisModel by ID
        2. Download script from script_url
        3. Execute with parameters
        4. Collect execution results
        5. Update AnalysisModel with results
        6. Log execution in audit trail
        """
        start_time = datetime.utcnow()
        execution_start_ms = int(start_time.timestamp() * 1000)
        
        try:
            # Step 1: Fetch analysis
            self.logger.info(f"📦 Fetching analysis: {analysis_id}")
            analysis = await self.repo.db.get_analysis(analysis_id)
            
            if not analysis:
                return {
                    "success": False,
                    "error": f"Analysis not found: {analysis_id}"
                }
            
            if analysis.status != ExecutionStatus.PENDING:
                self.logger.warning(f"⚠️ Analysis already executed: {analysis_id}")
                return {
                    "success": False,
                    "error": f"Analysis already executed (status: {analysis.status})"
                }
            
            # Step 2: Get execution parameters
            self.logger.info("📋 Extracting execution parameters")
            llm_response = analysis.llm_response
            
            if llm_response.get("status") != "success":
                return {
                    "success": False,
                    "error": f"Cannot execute failed analysis: {llm_response.get('error')}"
                }
            
            execution_config = llm_response.get("execution", {})
            script_name = execution_config.get("script_name", "analysis.py")
            parameters = execution_config.get("parameters", {})
            
            self.logger.info(f"📝 Script: {script_name}, Parameters: {parameters}")
            
            # Step 3: Get script content
            self.logger.info(f"📥 Loading script from: {analysis.script_url}")
            script_content = await self._load_script(analysis.script_url)
            
            if not script_content:
                return {
                    "success": False,
                    "error": f"Failed to load script from {analysis.script_url}"
                }
            
            # Step 4: Execute script
            self.logger.info("⚙️ Executing script...")
            execution_result = await self._execute_script(
                script_content=script_content,
                parameters=parameters,
                timeout_seconds=timeout_seconds
            )
            
            execution_time_ms = int((datetime.utcnow().timestamp() * 1000) - execution_start_ms)
            
            if not execution_result["success"]:
                # Execution failed
                self.logger.error(f"❌ Execution failed: {execution_result.get('error')}")
                
                # Update analysis with failure
                await self.repo.db.update_analysis(
                    analysis_id,
                    {
                        "status": ExecutionStatus.FAILED,
                        "error": execution_result.get("error"),
                        "execution_time_ms": execution_time_ms,
                        "executed_at": datetime.utcnow()
                    }
                )
                
                return {
                    "success": False,
                    "error": execution_result.get("error"),
                    "execution_time_ms": execution_time_ms
                }
            
            # Step 5: Update analysis with results
            self.logger.info("💾 Updating analysis with execution results")
            result_data = execution_result.get("result", {})
            
            await self.repo.db.update_analysis(
                analysis_id,
                {
                    "status": ExecutionStatus.SUCCESS,
                    "result": result_data,
                    "execution_time_ms": execution_time_ms,
                    "executed_at": datetime.utcnow()
                }
            )
            
            self.logger.info(f"✅ Execution completed successfully in {execution_time_ms}ms")
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "result": result_data,
                "execution_time_ms": execution_time_ms,
                "executed_at": start_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Execution service error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }
    
    async def _load_script(self, script_url: str) -> Optional[str]:
        """Load script content from URL or file path"""
        try:
            if script_url.startswith("s3://"):
                # TODO: Implement S3 loading
                self.logger.warning("S3 loading not yet implemented")
                return None
            else:
                # Load from local file
                with open(script_url, 'r') as f:
                    content = f.read()
                    self.logger.info(f"✅ Loaded script: {len(content)} bytes")
                    return content
        except Exception as e:
            self.logger.error(f"❌ Failed to load script: {e}")
            return None
    
    async def _execute_script(
        self,
        script_content: str,
        parameters: Dict[str, Any],
        timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Call execution server to execute script with parameters
        """
        try:
            self.logger.info(f"🚀 Calling execution server (timeout: {timeout_seconds}s)")
            
            # Get execution server URL from environment
            exec_server_url = os.getenv("EXECUTION_SERVER_URL", "http://localhost:8011")
            
            # Prepare request payload
            payload = {
                "script": script_content,
                "parameters": parameters,
                "timeout_seconds": timeout_seconds
            }
            
            # Call execution server
            async with httpx.AsyncClient(timeout=timeout_seconds + 10) as client:
                response = await client.post(
                    f"{exec_server_url}/execute",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("success"):
                        self.logger.info("✅ Execution server returned success")
                        return {
                            "success": True,
                            "result": result.get("data", {})
                        }
                    else:
                        self.logger.error(f"❌ Execution server error: {result.get('error')}")
                        return {
                            "success": False,
                            "error": result.get("error", "Execution server returned error")
                        }
                else:
                    self.logger.error(f"❌ Execution server HTTP {response.status_code}")
                    return {
                        "success": False,
                        "error": f"Execution server error: HTTP {response.status_code}"
                    }
            
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": f"Script execution timeout after {timeout_seconds}s"
            }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": f"Failed to connect to execution server at {os.getenv('EXECUTION_SERVER_URL', 'http://localhost:8011')}"
            }
        except Exception as e:
            self.logger.error(f"❌ Execution service error: {e}")
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }
