#!/usr/bin/env python3
"""
Integration helpers for verification service with analysis service
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

from .verification_service import VerificationServiceResult

logger = logging.getLogger(__name__)

class VerificationIntegrationHelper:
    """
    Helper class for integrating verification service with analysis service
    """
    
    @staticmethod
    def extract_script_content_from_tool_result(tool_result: Dict[str, Any]) -> str:
        """
        Extract script content from write_and_validate tool result
        
        Handles various tool result formats:
        1. Tool call format: {'function': '...', 'arguments': {'content': '...', 'filename': '...'}}
        2. Direct content: {'content': '...'}
        3. Nested result: {'result': {'content': '...'}}
        4. Nested with arguments: {'result': {'arguments': {'content': '...'}}}
        
        Args:
            tool_result: Tool result dictionary from write_and_validate
            
        Returns:
            str: Extracted script content or empty string if not found
        """
        try:
            if not isinstance(tool_result, dict):
                logger.error(f"❌ Tool result is not a dictionary: {type(tool_result)}")
                return ""
            
            # Case 1: Tool call format with arguments
            # {'function': 'validation-server__write_and_validate', 'arguments': {'content': '...', 'filename': '...'}}
            if 'arguments' in tool_result and isinstance(tool_result['arguments'], dict):
                arguments = tool_result['arguments']
                if 'content' in arguments and arguments['content']:
                    logger.debug("✅ Extracted script content from tool call arguments")
                    return arguments['content']
            
            # Case 2: Direct content keys in tool result
            content_keys = ['content', 'script_content', 'script', 'code']
            for key in content_keys:
                if key in tool_result and tool_result[key]:
                    logger.debug(f"✅ Extracted script content from tool result key: {key}")
                    return tool_result[key]
            
            # Case 3: Nested in 'result' field
            if 'result' in tool_result and isinstance(tool_result['result'], dict):
                result_data = tool_result['result']
                
                # Check if result has arguments
                if 'arguments' in result_data and isinstance(result_data['arguments'], dict):
                    arguments = result_data['arguments']
                    if 'content' in arguments and arguments['content']:
                        logger.debug("✅ Extracted script content from nested result arguments")
                        return arguments['content']
                
                # Check direct keys in result
                for key in content_keys:
                    if key in result_data and result_data[key]:
                        logger.debug(f"✅ Extracted script content from nested result key: {key}")
                        return result_data[key]
            
            # Case 4: Tool result is the content itself (string)
            if isinstance(tool_result.get('content'), str) and tool_result['content'].strip():
                logger.debug("✅ Tool result content is direct string")
                return tool_result['content']
            
            logger.error(f"❌ Could not extract script content from tool result. Available keys: {list(tool_result.keys())}")
            logger.debug(f"Tool result structure: {tool_result}")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Error extracting script content: {e}")
            return ""
    
    @staticmethod
    def create_verification_handoff_message(verification_result: VerificationServiceResult, original_question: str) -> Dict[str, str]:
        """
        Create formatted message to handoff verification results to conversation
        """
        
        if verification_result.verified:
            # Success case - require specific output format
            handoff_content = f"""Multi-model verification PASSED unanimously. All models approved the script.

VERIFICATION SUMMARY:
- Models: {', '.join([r.model for r in verification_result.model_results if r.success and r.verdict == "APPROVE"])}
- Consensus: Unanimous Approval
- Verification Time: {verification_result.verification_time_ms}ms
- Script Status: Ready for execution

The script has been verified by multiple independent models and is ready for execution.

REQUIRED OUTPUT FORMAT:
You must respond with EXACTLY this JSON structure:

```json
{{
  "script_generation": {{
    "status": "success",
    "script_name": "actual_filename_from_server.py",
    "validation_attempts": 1,
    "analysis_description": "Brief description of the analysis performed",
    "verification": {{
      "multi_model_consensus": true,
      "approving_models": {json.dumps([r.model for r in verification_result.model_results if r.success and r.verdict == "APPROVE"])},
      "verification_timestamp": "{datetime.now().isoformat()}",
      "verification_time_ms": {verification_result.verification_time_ms}
    }},
    "execution": {{
      "script_name": "actual_filename_from_server.py",
      "parameters": {{
        "param1": "default_value1",
        "param2": "default_value2"
      }}
    }}
  }}
}}
```

Provide this exact JSON format as your response."""
        
        else:
            # Failure case - require correction
            rejecting_models = [r.model for r in verification_result.model_results if r.success and r.verdict == "REJECT"]
            failed_models = [r.model for r in verification_result.model_results if not r.success]
            
            handoff_content = f"""Multi-model verification FAILED. Critical issues found that need to be fixed.

VERIFICATION RESULTS:
"""
            
            # Add details for each model
            for result in verification_result.model_results:
                if result.success:
                    status = "✅ APPROVED" if result.verdict == "APPROVE" else "❌ REJECTED"
                    handoff_content += f"- **{result.model}**: {status} (confidence: {result.confidence:.2f})\n"
                    if result.critical_issues:
                        handoff_content += f"  Issues: {', '.join(result.critical_issues)}\n"
                else:
                    handoff_content += f"- **{result.model}**: ❌ VERIFICATION FAILED ({result.error})\n"
            
            handoff_content += f"""
CRITICAL ISSUES TO FIX:
{chr(10).join(f"- {issue}" for issue in verification_result.consensus_details.all_issues)}

REQUIRED ACTION:
The script has critical issues that must be fixed. Please:
1. Address each of the issues listed above
2. Regenerate the script using the write_and_validate tool
3. Focus specifically on the problems identified by the verification models

The verification requires unanimous approval from all models before the script can be approved for execution."""
        
        return {
            "role": "user",
            "content": handoff_content
        }
    
    @staticmethod
    def format_model_results_summary(verification_result: VerificationServiceResult) -> str:
        """
        Format a summary of model verification results for logging
        """
        summary_lines = []
        
        for result in verification_result.model_results:
            if result.success:
                status = "APPROVED" if result.verdict == "APPROVE" else "REJECTED"
                summary_lines.append(f"{result.model}: {status} (confidence: {result.confidence:.2f})")
            else:
                summary_lines.append(f"{result.model}: FAILED ({result.error})")
        
        return "\n".join(summary_lines)