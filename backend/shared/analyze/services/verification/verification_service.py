#!/usr/bin/env python3
"""
Standalone Multi-Model Script Verification Service
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

import sys

# Import shared services
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
sys.path.insert(0, shared_path)
from shared.llm.service import LLMService
from shared.llm.utils import LLMConfig
from shared.execution.script_executor import create_enhanced_script
from shared.utils.json_utils import safe_json_loads

logger = logging.getLogger(__name__)

@dataclass
class ModelVerificationResult:
    """Result from a single model verification"""
    model: str
    verdict: str  # "APPROVE" or "REJECT"
    confidence: float
    critical_issues: List[str]
    reasoning: str
    success: bool = True
    error: Optional[str] = None

@dataclass
class ConsensusResult:
    """Result of consensus calculation"""
    unanimous_approval: bool
    approving_models: List[str]
    rejecting_models: List[str]
    all_issues: List[str]
    consensus_details: Dict[str, Any]

@dataclass
class VerificationServiceResult:
    """Final result from verification service"""
    verified: bool
    model_results: List[ModelVerificationResult]
    consensus_details: ConsensusResult
    verification_time_ms: int

class StandaloneVerificationService:
    """
    Independent verification service that operates outside conversation context
    """
    
    def __init__(self, existing_verification_prompt: str):
        self.verification_configs = self._load_verification_configs_from_env()
        self.existing_verification_prompt = existing_verification_prompt
        self.llm_services = self._initialize_llm_services()
    
    def _load_verification_configs_from_env(self) -> List[Dict[str, str]]:
        """
        Load verification configurations from environment variables
        Format: 
        VERIFICATION_LLM_PROVIDER_1=anthropic, VERIFICATION_LLM_MODEL_1=claude-3-5-sonnet
        VERIFICATION_LLM_PROVIDER_2=openai, VERIFICATION_LLM_MODEL_2=gpt-4
        
        Fallbacks:
        - If VERIFICATION_LLM_PROVIDER_X not set, use VERIFICATION_LLM_PROVIDER
        - If VERIFICATION_LLM_PROVIDER not set, use LLM_PROVIDER
        - Default models based on provider if not specified
        """
        configs = []
        
        # Default fallback values
        default_provider = os.getenv("VERIFICATION_LLM_PROVIDER") or os.getenv("LLM_PROVIDER", "anthropic")
        
        # Try to load configs from environment variables
        for i in range(1, 10):  # Support up to 9 verification models
            provider_key = f"VERIFICATION_LLM_PROVIDER_{i}"
            model_key = f"VERIFICATION_LLM_MODEL_{i}"
            
            provider = os.getenv(provider_key) or default_provider
            model = os.getenv(model_key)
            
            # If we have a model specified, use it
            if model:
                configs.append({
                    "id": f"verification_{i}",
                    "provider": provider.strip(),
                    "model": model.strip()
                })
                logger.debug(f"✅ Added verification config {i}: {provider}/{model}")
            elif i <= 3:  # Only add defaults for first 3 slots if no custom configs
                # Add default configs only if no custom configs found
                if not configs:
                    continue  # Will be handled after the loop
        
        # If no configs were found, use defaults
        if not configs:
            configs = [
                {"id": "verification_1", "provider": "anthropic", "model": "claude-3-5-sonnet"},
                {"id": "verification_2", "provider": "openai", "model": "gpt-4"},
                {"id": "verification_3", "provider": "anthropic", "model": "claude-3-haiku"}
            ]
            logger.info(f"🔧 Using default verification configs: {[f'{c['provider']}/{c['model']}' for c in configs]}")
        else:
            logger.info(f"🔧 Using configured verification models: {[f'{c['provider']}/{c['model']}' for c in configs]}")
        
        return configs
    
    async def verify_script(self, question: str, script_content: str) -> VerificationServiceResult:
        """
        Standalone verification - no conversation context needed
        Returns structured result for handoff to conversation
        """
        start_time = datetime.now()
        
        # Enhance the script with MCP injection wrapper before verification
        try:
            enhanced_script = create_enhanced_script(script_content, mock_mode=True)
            logger.info(f"✅ Enhanced script for verification (original: {len(script_content)} chars, enhanced: {len(enhanced_script)} chars)")
        except Exception as e:
            logger.warning(f"⚠️ Script enhancement failed, using original script: {e}")
            enhanced_script = script_content
        
        # Filter to only available services
        available_services = [(config["id"], service) for config, service in zip(self.verification_configs, self.llm_services) if service is not None]
        
        if not available_services:
            logger.error("❌ No LLM services available for verification")
            return VerificationServiceResult(
                verified=False,
                model_results=[],
                consensus_details=ConsensusResult(
                    unanimous_approval=False,
                    approving_models=[],
                    rejecting_models=[],
                    all_issues=["No LLM services available"],
                    consensus_details={"error": "No services initialized"}
                ),
                verification_time_ms=0
            )
        
        available_ids = [service_id for service_id, _ in available_services]
        logger.info(f"🔍 Starting multi-model verification with {len(available_services)} services: {available_ids}")
        
        # Run parallel verification across available services using enhanced script
        verification_tasks = []
        for service_id, llm_service in available_services:
            task = asyncio.create_task(self._verify_with_service(question, enhanced_script, service_id, llm_service))
            verification_tasks.append(task)
        
        # Wait for all results
        model_results = await asyncio.gather(*verification_tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(model_results):
            if isinstance(result, Exception):
                logger.error(f"❌ Service {available_ids[i]} verification failed: {result}")
                processed_results.append(ModelVerificationResult(
                    model=available_ids[i],
                    verdict="REJECT",
                    confidence=0.0,
                    critical_issues=[f"Verification failed: {str(result)}"],
                    reasoning="Service verification error",
                    success=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        # Calculate consensus using available services
        consensus_result = self._calculate_unanimous_consensus(processed_results, available_ids)
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        logger.info(f"✅ Multi-model verification completed in {execution_time}ms - Result: {'APPROVED' if consensus_result.unanimous_approval else 'REJECTED'}")
        
        return VerificationServiceResult(
            verified=consensus_result.unanimous_approval,
            model_results=processed_results,
            consensus_details=consensus_result,
            verification_time_ms=execution_time
        )
    
    def _extract_core_question(self, question: str) -> str:
        """
        Extract the core question before REQUIREMENTS or other expanded sections
        """
        # Split on common section markers and take the first part
        section_markers = ["**REQUIREMENTS", "REQUIREMENTS:", "**ADDITIONAL", "**CONTEXT", "**NOTE"]
        
        for marker in section_markers:
            if marker in question:
                question = question.split(marker)[0].strip()
                break
        
        # Clean up any trailing formatting
        question = question.rstrip("*").rstrip(":").strip()
        
        return question
    
    def _create_verification_content(self, question: str, script_content: str) -> tuple[str, str]:
        """
        Create system prompt and user message content for provider-agnostic verification
        Returns (system_prompt, user_message)
        """
        # Extract core question without expanded requirements
        core_question = self._extract_core_question(question)
        
        # System prompt with verification instructions
        system_prompt = """You are a financial script verification expert. Your task is to verify that Python scripts correctly answer specific financial questions.

The script has been enhanced with MCP function injection wrapper to provide access to financial data and analytics functions. Focus on verifying the core script logic (after the MCP wrapper code at the beginning).

RESPONSE FORMAT:
You must respond in EXACTLY this JSON format (no other text):
{
    "verdict": "APPROVE" or "REJECT",
    "confidence": 0.0-1.0,
    "critical_issues": ["list of critical problems found"],
    "reasoning": "brief explanation of decision"
}"""

        # Use existing verification prompt as base with core question
        base_verification = self.existing_verification_prompt.format(question=core_question)
        
        # User message with verification task and script
        user_message = f"""{base_verification}

ENHANCED SCRIPT TO VERIFY:
```python
{script_content}
```

Based on the verification criteria above, please evaluate this script and respond in the required JSON format."""

        return system_prompt, user_message
    
    async def _verify_with_service(self, question: str, script_content: str, service_id: str, llm_service: LLMService) -> ModelVerificationResult:
        """
        Single service verification - completely independent
        """
        try:
            logger.debug(f"🔍 Verifying with {service_id}")
            
            # Create system prompt and user message content
            system_prompt, user_message = self._create_verification_content(question, script_content)
            
            # Create user message only - let provider handle system prompt formatting
            messages = [{"role": "user", "content": user_message}]
            
            # Call LLM service with verification-specific settings
            response = await llm_service.make_request(
                messages=messages,
                max_tokens=2000,  # Sufficient for structured verification response
                enable_caching=False,  # Disable caching for verification
                system_prompt=system_prompt  # Let provider handle system prompt formatting
            )
            
            if not response.get("success"):
                error_msg = response.get("error", "Unknown API error")
                logger.error(f"❌ API call failed for {service_id}: {error_msg}")
                raise Exception(f"API call failed: {error_msg}")
            
            # Extract content from LLMService response
            content = response.get("content", "")
            
            logger.debug(f"✅ Received response from {service_id}: {len(content)} chars")
            return self._parse_verification_response(content, service_id)
            
        except Exception as e:
            logger.error(f"❌ Verification failed for {service_id}: {e}")
            return ModelVerificationResult(
                model=service_id,
                verdict="REJECT",
                confidence=0.0,
                critical_issues=[f"Verification error: {str(e)}"],
                reasoning="Service API error",
                success=False,
                error=str(e)
            )
    
    def _initialize_llm_services(self) -> List[Optional[LLMService]]:
        """Initialize LLM services for each verification configuration"""
        services = []
        
        for i, config in enumerate(self.verification_configs):
            try:
                # Set environment variables temporarily for this verification service config
                # This allows LLMConfig.for_task() to pick up the right provider and model
                task_name = f"verification_{i+1}"
                task_upper = task_name.upper()
                
                # LLMConfig.for_task expects TASKNAME_LLM_PROVIDER format
                temp_provider_key = f"{task_upper}_LLM_PROVIDER"
                temp_model_key = f"{task_upper}_LLM_MODEL"
                
                # Temporarily set env vars for LLMConfig.for_task() to use
                original_temp_provider = os.environ.get(temp_provider_key)
                original_temp_model = os.environ.get(temp_model_key)
                
                os.environ[temp_provider_key] = config["provider"]
                os.environ[temp_model_key] = config["model"]
                
                try:
                    # Use for_task to get proper configuration with auto API key detection
                    llm_config = LLMConfig.for_task(task_name)
                    
                    # Override settings specific to verification
                    llm_config.use_cli = False  # Always use API for verification
                    llm_config.temperature = 0.1  # Low temperature for consistent verification
                    llm_config.service_name = "verification"  # Use verification service config - no tools
                    
                    # Create LLM service
                    llm_service = LLMService(llm_config)
                    services.append(llm_service)
                    logger.debug(f"✅ LLM service initialized for {config['id']}: {config['provider']}/{config['model']}")
                    
                finally:
                    # Restore original environment variables
                    if original_temp_provider is not None:
                        os.environ[temp_provider_key] = original_temp_provider
                    else:
                        os.environ.pop(temp_provider_key, None)
                        
                    if original_temp_model is not None:
                        os.environ[temp_model_key] = original_temp_model
                    else:
                        os.environ.pop(temp_model_key, None)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize LLM service for {config['id']}: {e}")
                services.append(None)
        
        available_count = sum(1 for s in services if s is not None)
        if available_count > 0:
            logger.info(f"✅ Initialized {available_count}/{len(self.verification_configs)} verification services")
        else:
            logger.warning("⚠️ No verification services initialized - check API keys and configuration")
        
        return services
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of verification service"""
        available_services = [(config, service) for config, service in zip(self.verification_configs, self.llm_services) if service is not None]
        total_services = len(self.verification_configs)
        
        health_status = {
            "total_configured": total_services,
            "available_services": len(available_services),
            "ready": len(available_services) > 0,
            "consensus_possible": len(available_services) >= 2,  # Need at least 2 for meaningful consensus
            "services": []
        }
        
        for config, service in zip(self.verification_configs, self.llm_services):
            service_status = {
                "id": config["id"],
                "provider": config["provider"],
                "model": config["model"],
                "available": service is not None
            }
            
            if service is not None:
                service_status["provider_type"] = service.config.provider_type
                service_status["default_model"] = service.config.default_model
            
            health_status["services"].append(service_status)
        
        return health_status
    
    def _parse_verification_response(self, response: str, model_name: str) -> ModelVerificationResult:
        """
        Parse model response into structured result
        """
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned_response = response.strip()
            
            # Handle markdown JSON blocks
            if cleaned_response.startswith("```json"):
                start_index = cleaned_response.find("{")
                end_index = cleaned_response.rfind("}")
                if start_index != -1 and end_index != -1:
                    cleaned_response = cleaned_response[start_index:end_index + 1]
            elif cleaned_response.startswith("```"):
                # Remove generic code blocks
                lines = cleaned_response.split("\n")
                cleaned_response = "\n".join(lines[1:-1])
            
            # Extract JSON from text if it's embedded
            if "{" in cleaned_response and "}" in cleaned_response:
                start_index = cleaned_response.find("{")
                end_index = cleaned_response.rfind("}") + 1
                cleaned_response = cleaned_response[start_index:end_index]
            
            # Try to parse JSON response using safe parser
            parsed = safe_json_loads(cleaned_response, default={})
            
            # Check if parsing was successful
            if not parsed or not isinstance(parsed, dict):
                raise json.JSONDecodeError("Failed to parse response as valid JSON object", cleaned_response, 0)
            
            # Validate required fields and normalize values
            verdict = parsed.get("verdict", "REJECT").upper()
            if verdict not in ["APPROVE", "REJECT"]:
                verdict = "REJECT"
                
            confidence = parsed.get("confidence", 0.0)
            if isinstance(confidence, str):
                try:
                    confidence = float(confidence)
                except (ValueError, TypeError):
                    confidence = 0.0
            confidence = max(0.0, min(1.0, float(confidence)))  # Clamp to 0-1 range
            
            critical_issues = parsed.get("critical_issues", [])
            if not isinstance(critical_issues, list):
                critical_issues = [str(critical_issues)] if critical_issues else []
            
            reasoning = parsed.get("reasoning", "No reasoning provided")
            if not isinstance(reasoning, str):
                reasoning = str(reasoning)
            
            return ModelVerificationResult(
                model=model_name,
                verdict=verdict,
                confidence=confidence,
                critical_issues=critical_issues,
                reasoning=reasoning,
                success=True
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse {model_name} response as JSON: {e}")
            logger.debug(f"Raw response: {response[:500]}...")
            
            # Try to extract verdict from text using pattern matching
            fallback_verdict = "REJECT"
            fallback_reasoning = "Failed to parse structured response"
            
            response_lower = response.lower()
            if "approve" in response_lower and "reject" not in response_lower:
                fallback_verdict = "APPROVE"
                fallback_reasoning = "Inferred approval from text response"
            
            return ModelVerificationResult(
                model=model_name,
                verdict=fallback_verdict,
                confidence=0.0,
                critical_issues=[f"Invalid response format: {str(e)}"],
                reasoning=fallback_reasoning,
                success=False,
                error=f"JSON parsing error: {str(e)}"
            )
    
    def _calculate_unanimous_consensus(self, model_results: List[ModelVerificationResult], available_models: List[str]) -> ConsensusResult:
        """
        Calculate unanimous consensus - ALL available models must approve
        """
        successful_results = [r for r in model_results if r.success]
        
        if len(successful_results) == 0:
            return ConsensusResult(
                unanimous_approval=False,
                approving_models=[],
                rejecting_models=[r.model for r in model_results],
                all_issues=["All model verifications failed"],
                consensus_details={"error": "No successful verifications"}
            )
        
        approving_models = [r.model for r in successful_results if r.verdict == "APPROVE"]
        rejecting_models = [r.model for r in successful_results if r.verdict == "REJECT"]
        
        # Collect all critical issues
        all_issues = []
        for result in successful_results:
            all_issues.extend(result.critical_issues)
        
        # Unanimous approval requires ALL available models to approve successfully
        unanimous_approval = (
            len(approving_models) == len(successful_results) and 
            len(successful_results) == len(available_models)
        )
        
        return ConsensusResult(
            unanimous_approval=unanimous_approval,
            approving_models=approving_models,
            rejecting_models=rejecting_models,
            all_issues=list(set(all_issues)),  # Remove duplicates
            consensus_details={
                "total_models": len(available_models),
                "successful_verifications": len(successful_results),
                "failed_verifications": len(model_results) - len(successful_results),
                "approval_rate": len(approving_models) / len(successful_results) if successful_results else 0
            }
        )