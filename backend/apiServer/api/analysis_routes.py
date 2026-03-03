"""
Analysis Management Routes - Handle analysis details and execution history
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from pydantic import BaseModel

# Import auth components
from .auth import UserContext, require_authenticated_user

# Import shared services
from shared.services.schema_formatter import create_shared_schema_formatter

logger = logging.getLogger("analysis-routes")

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


class AnalysisDetails(BaseModel):
    """Analysis metadata and details"""
    analysisId: str
    messageId: Optional[str] = None
    sessionId: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    originalQuestion: Optional[str] = None
    createdAt: str
    updatedAt: str
    parameterSchema: List[dict] = []


class ExecutionDetails(BaseModel):
    """Execution details with results"""
    executionId: str
    analysisId: str
    parameters: Dict[str, Any]
    status: str
    results: Optional[Dict[str, Any]] = None
    createdAt: str
    duration: Optional[int] = None
    error: Optional[str] = None


class ExecuteAnalysisRequest(BaseModel):
    """Request to execute analysis with parameters"""
    parameters: Dict[str, Any] = {}
    sessionId: Optional[str] = None


@router.get("/{analysis_id}", response_model=AnalysisDetails)
async def get_analysis_details(
    request: Request,
    analysis_id: str,
    user_context: UserContext = Depends(require_authenticated_user)
):
    """
    Get analysis details and metadata
    """
    try:
        # Get analysis repository
        repo_manager = request.app.state.repo_manager
        if not repo_manager:
            raise HTTPException(status_code=500, detail="Repository service not available")
        analysis_repo = repo_manager.analysis
        
        # Get analysis from database
        analysis = await analysis_repo.get_analysis_by_id(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Enhanced ownership check - analysis can be:
        # 1. Public/shared (accessible to all users)
        # 2. User-specific (only accessible to the creator)
        # 3. Session-specific (accessible to session owner)
        
        analysis_user_id = analysis.get('userId', analysis.get('user_id'))
        is_public = analysis.get('isPublic', False)
        
        if not is_public and analysis_user_id != user_context.user_id:
            # Check if user has access through session ownership
            session_id = analysis.get('sessionId')
            if session_id:
                chat_history_service = request.app.state.chat_history_service
                if chat_history_service:
                    is_owner = await chat_history_service.validate_session_ownership(
                        session_id, 
                        user_context.user_id
                    )
                    if not is_owner:
                        raise HTTPException(status_code=403, detail="Access denied: Analysis not accessible")
                else:
                    raise HTTPException(status_code=403, detail="Access denied: Cannot verify analysis ownership")
            else:
                raise HTTPException(status_code=403, detail="Access denied: Analysis belongs to different user")
        
        # Extract parameter schema from analysis
        parameter_schema = analysis.get('parameterSchema', [])
        if not parameter_schema:
            # Try to extract from analysis metadata or create basic schema
            parameters = analysis.get('parameters', {})
            parameter_schema = []
            for key, value in parameters.items():
                param_type = "text"
                if isinstance(value, (int, float)):
                    param_type = "number"
                elif isinstance(value, bool):
                    param_type = "boolean"
                    
                parameter_schema.append({
                    "id": key,
                    "name": key.replace("_", " ").title(),
                    "type": param_type,
                    "defaultValue": value,
                    "required": True
                })
        
        # Convert datetime objects to strings for API response
        created_at = analysis.get('createdAt', analysis.get('created_at'))
        updated_at = analysis.get('updatedAt', analysis.get('updated_at'))
        
        if hasattr(created_at, 'isoformat'):
            created_at = created_at.isoformat()
        elif created_at is None:
            created_at = ''
        
        if hasattr(updated_at, 'isoformat'):
            updated_at = updated_at.isoformat()
        elif updated_at is None:
            updated_at = ''

        # Return analysis details
        result = AnalysisDetails(
            analysisId=analysis_id,
            messageId=analysis.get('messageId'),
            sessionId=analysis.get('sessionId'),
            title=analysis.get('title', f"Analysis {analysis_id[:8]}"),
            description=analysis.get('description', analysis.get('analysisDescription')),
            originalQuestion=analysis.get('originalQuestion', analysis.get('question')),
            createdAt=created_at,
            updatedAt=updated_at,
            parameterSchema=parameter_schema
        )
        
        logger.info(f"✓ Retrieved analysis details: {analysis_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Failed to get analysis details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{analysis_id}/executions", response_model=List[ExecutionDetails])
async def get_analysis_executions(
    request: Request,
    analysis_id: str,
    limit: int = Query(50, ge=1, le=100),
    execution_type: Optional[str] = Query(None, description="Filter by execution type: 'primary', 'user_rerun', 'all'"),
    user_context: UserContext = Depends(require_authenticated_user)
):
    """
    Get executions for this analysis, optionally filtered by type
    """
    try:
        # Get execution repository  
        repo_manager = request.app.state.repo_manager
        if not repo_manager:
            raise HTTPException(status_code=500, detail="Repository service not available")
        execution_repo = repo_manager.execution
        
        # Verify user owns this analysis first
        analysis_repo = repo_manager.analysis
        analysis = await analysis_repo.get_analysis_by_id(analysis_id)
        if analysis and analysis.get('sessionId'):
            chat_history_service = request.app.state.chat_history_service
            if chat_history_service:
                is_owner = await chat_history_service.validate_session_ownership(
                    analysis['sessionId'], 
                    user_context.user_id
                )
                if not is_owner:
                    raise HTTPException(status_code=403, detail="Access denied")
        
        # Get executions based on type filter
        if execution_type == "primary":
            primary_exec = await execution_repo.get_primary_execution_by_analysis_id(analysis_id)
            executions = [primary_exec] if primary_exec else []
        elif execution_type == "user_rerun":
            executions = await execution_repo.get_user_reruns_by_analysis_id(analysis_id, limit)
        else:  # execution_type == "all" or None
            executions = await execution_repo.get_executions_by_analysis_id(analysis_id, limit)
        
        # Transform to response format
        result = []
        for execution in executions:
            if execution:  # Skip None entries
                # Convert datetime to string
                created_at = execution.get('createdAt', execution.get('created_at'))
                if hasattr(created_at, 'isoformat'):
                    created_at = created_at.isoformat()
                elif created_at is None:
                    created_at = ''
                
                exec_detail = ExecutionDetails(
                    executionId=execution.get('executionId', execution.get('execution_id', '')),
                    analysisId=analysis_id,
                    parameters=execution.get('parameters', {}),
                    status=execution.get('status', 'unknown'),
                    results=execution.get('results'),
                    createdAt=created_at,
                    duration=execution.get('duration', execution.get('execution_time')),
                    error=execution.get('error')
                )
                result.append(exec_detail)
        
        logger.info(f"✓ Retrieved {len(result)} {execution_type or 'all'} executions for analysis: {analysis_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Failed to get executions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{message_id}/analysis", response_model=AnalysisDetails)
async def get_message_analysis(
    request: Request,
    message_id: str,
    user_context: UserContext = Depends(require_authenticated_user)
):
    """
    Get analysis associated with a specific message with JIT parameter schema generation
    """
    
    try:
        # Validate message ownership using centralized service
        chat_history_service = request.app.state.chat_history_service
        if not chat_history_service:
            raise HTTPException(status_code=500, detail="Chat history service not available")
        
        # Check if user owns this message
        is_owner = await chat_history_service.validate_message_ownership(message_id, user_context.user_id)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Access denied: Message not found or belongs to different user")
        
        # Get repository for analysis operations
        repo_manager = request.app.state.repo_manager
        if not repo_manager:
            raise HTTPException(status_code=500, detail="Repository service not available")
        
        # Get the message to extract analysis information
        chat_repo = repo_manager.chat
        message = await chat_repo.get_raw_message_by_id(message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Get analysis_id from message
        analysis_id = message.get('analysisId')
        if not analysis_id:
            raise HTTPException(status_code=404, detail="No analysis associated with this message")
        
        # Get analysis from database using existing repo_manager
        analysis_repo = repo_manager.analysis
        
        # Get analysis from database
        analysis = await analysis_repo.get_analysis_by_id(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Check if analysis already has parameterSchema
        parameter_schema = analysis.get('parameterSchema', [])
        
        if not parameter_schema:
            logger.info(f"No parameterSchema found for analysis {analysis_id}, generating JIT...")
            
            # Try to generate parameter schema using script name
            try:
                llm_response = analysis.get('llmResponse', {})
                script_name = llm_response.get('script_name')
                analysis_type = analysis.get('analysisType', analysis.get('analysis_type'))
                
                if script_name:
                    # Generate schema using the schema formatter service with just script name
                    schema_formatter = create_shared_schema_formatter()
                    generated_schema = await schema_formatter.generate_parameter_schema(
                        script_name=script_name,
                        analysis_type=analysis_type
                    )
                    
                    if generated_schema:
                        parameter_schema = generated_schema
                        
                        # Update analysis with generated schema for future use
                        try:
                            await analysis_repo.db.update_analysis(analysis_id, {"parameterSchema": parameter_schema})
                            logger.info(f"✅ Generated and saved parameterSchema for analysis {analysis_id}")
                        except Exception as update_error:
                            logger.warning(f"Failed to save parameterSchema to analysis {analysis_id}: {update_error}")
                    else:
                        logger.warning(f"Failed to generate parameterSchema for analysis {analysis_id}")
                else:
                    logger.warning(f"No script_name found in llmResponse for analysis {analysis_id}")
                        
            except Exception as schema_error:
                logger.error(f"Error generating parameterSchema for analysis {analysis_id}: {schema_error}")
        
        # Fallback: extract from top-level parameters field if no schema generated
        if not parameter_schema and 'parameters' in analysis:
            logger.info(f"Falling back to extracting schema from parameters field for analysis {analysis_id}")
            parameters = analysis.get('parameters', {})
            parameter_schema = []
            
            for param_key, param_info in parameters.items():
                # Handle both dict and simple value formats
                if isinstance(param_info, dict):
                    # Structured parameter definition
                    param_schema = {
                        "id": param_key,
                        "name": param_info.get('name', param_key.replace("_", " ").title()),
                        "type": param_info.get('type', 'text'),
                        "description": param_info.get('description', ''),
                        "defaultValue": param_info.get('default', param_info.get('value', '')),
                        "required": param_info.get('required', True)
                    }
                    
                    # Add validation rules if present
                    if 'validation' in param_info:
                        param_schema['validation'] = param_info['validation']
                    
                    parameter_schema.append(param_schema)
                else:
                    # Simple value - create basic schema
                    param_type = "text"
                    if isinstance(param_info, (int, float)):
                        param_type = "number"
                    elif isinstance(param_info, bool):
                        param_type = "boolean"
                        
                    parameter_schema.append({
                        "id": param_key,
                        "name": param_key.replace("_", " ").title(),
                        "type": param_type,
                        "defaultValue": param_info,
                        "required": True
                    })
            
        # Convert datetime objects to strings for API response
        created_at = analysis.get('createdAt', analysis.get('created_at'))
        updated_at = analysis.get('updatedAt', analysis.get('updated_at'))
        
        if hasattr(created_at, 'isoformat'):
            created_at = created_at.isoformat()
        elif created_at is None:
            created_at = ''
        
        if hasattr(updated_at, 'isoformat'):
            updated_at = updated_at.isoformat()
        elif updated_at is None:
            updated_at = ''

        # Return analysis details
        result = AnalysisDetails(
            analysisId=analysis_id,
            messageId=message_id,
            sessionId=message.get('sessionId'),
            title=analysis.get('title', f"Analysis {analysis_id[:8]}"),
            description=analysis.get('description', ""),
            originalQuestion=analysis.get('originalQuestion', analysis.get('question')),
            createdAt=created_at,
            updatedAt=updated_at,
            analysisType=analysis.get('analysisType', analysis.get('analysis_type')),
            parameterSchema=parameter_schema
        )
        
        logger.info(f"✓ Retrieved message analysis: {message_id} -> {analysis_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Failed to get message analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{message_id}/execution", response_model=ExecutionDetails)
async def get_message_execution(
    request: Request,
    message_id: str,
    user_context: UserContext = Depends(require_authenticated_user)
):
    """
    Get the primary execution result associated with a specific message
    This is the execution result shown in the chat message
    """
    try:
        # Validate message ownership using centralized service
        chat_history_service = request.app.state.chat_history_service
        if not chat_history_service:
            raise HTTPException(status_code=500, detail="Chat history service not available")
        
        # Check if user owns this message
        is_owner = await chat_history_service.validate_message_ownership(message_id, user_context.user_id)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Access denied: Message not found or belongs to different user")
        
        # Get repository for execution operations
        repo_manager = request.app.state.repo_manager
        if not repo_manager:
            raise HTTPException(status_code=500, detail="Repository service not available")
        
        # Get execution repository using existing repo_manager
        execution_repo = repo_manager.execution
        
        # Get execution associated with this message
        execution = await execution_repo.get_execution_by_message_id(message_id)
        if not execution:
            raise HTTPException(status_code=404, detail="No execution associated with this message")
        
        # Convert datetime to string
        created_at = execution.get('createdAt', execution.get('created_at'))
        if hasattr(created_at, 'isoformat'):
            created_at = created_at.isoformat()
        elif created_at is None:
            created_at = ''

        # Transform to response format
        result = ExecutionDetails(
            executionId=execution.get('executionId', execution.get('execution_id', '')),
            analysisId=execution.get('analysisId', execution.get('analysis_id', '')),
            parameters=execution.get('parameters', {}),
            status=execution.get('status', 'unknown'),
            results=execution.get('results'),
            createdAt=created_at,
            duration=execution.get('duration', execution.get('execution_time')),
            error=execution.get('error')
        )
        
        logger.info(f"✓ Retrieved message execution: {message_id} -> {result.executionId}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Failed to get message execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{analysis_id}/execute")
async def execute_analysis(
    request: Request,
    analysis_id: str,
    execute_req: ExecuteAnalysisRequest,
    user_context: UserContext = Depends(require_authenticated_user)
):
    """
    Execute analysis with given parameters
    """
    try:
        # Get analysis repository
        repo_manager = request.app.state.repo_manager
        if not repo_manager:
            raise HTTPException(status_code=500, detail="Repository service not available")
        analysis_repo = repo_manager.analysis
        analysis = await analysis_repo.get_analysis_by_id(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Enhanced ownership check - analysis can be:
        # 1. Public/shared (accessible to all users)
        # 2. User-specific (only accessible to the creator)
        # 3. Session-specific (accessible to session owner)
        
        analysis_user_id = analysis.get('userId', analysis.get('user_id'))
        is_public = analysis.get('isPublic', False)
        
        if not is_public and analysis_user_id != user_context.user_id:
            # Check if user has access through session ownership
            session_id = analysis.get('sessionId')
            if session_id:
                chat_history_service = request.app.state.chat_history_service
                if chat_history_service:
                    is_owner = await chat_history_service.validate_session_ownership(
                        session_id, 
                        user_context.user_id
                    )
                    if not is_owner:
                        raise HTTPException(status_code=403, detail="Access denied: Analysis not accessible")
                else:
                    raise HTTPException(status_code=403, detail="Access denied: Cannot verify analysis ownership")
            else:
                raise HTTPException(status_code=403, detail="Access denied: Analysis belongs to different user")
        
        # Execute analysis using existing execution service
        execution_routes = request.app.state.execution_routes
        if not execution_routes:
            raise HTTPException(status_code=500, detail="Execution service not available")
        
        # Create execution request with proper execution type
        execution_result = await execution_routes.execute_analysis(
            analysis_id=analysis_id,
            user_context=user_context,
            parameters=execute_req.parameters,
            session_id=execute_req.sessionId,
            execution_type="user_rerun"  # Mark as user-initiated re-run
        )
        
        logger.info(f"✓ Started execution for analysis: {analysis_id}")
        return execution_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Failed to execute analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))