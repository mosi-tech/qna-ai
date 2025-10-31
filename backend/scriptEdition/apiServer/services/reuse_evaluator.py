#!/usr/bin/env python3
"""
Reuse Evaluator Service

Analyzes financial questions against existing analyses to determine if existing scripts
can be reused with different parameters instead of creating new ones.

WORKFLOW:
1. Classify: Is the core financial methodology the same?
2. If YES: Extract argparse section and use LLM to convert user parameters
3. Return reuse decision WITH validated/converted parameters and confidence scores
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import shared services
import sys
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, shared_path)
from shared.llm import create_reuse_evaluator_llm, LLMService
from shared.services.base_service import BaseService
from utils.json_utils import safe_json_loads

# Configure logging
logger = logging.getLogger(__name__)


class ReuseEvaluatorService(BaseService):
    """Service that evaluates whether existing analyses can be reused for new queries"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(llm_service=llm_service, service_name="reuse-evaluator")
    
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service for reuse evaluator"""
        return create_reuse_evaluator_llm()
    
    def _get_system_prompt_filename(self) -> str:
        """Use reuse evaluator specific system prompt"""
        return "system-prompt-reuse-evaluator.txt"
    
    def _get_default_system_prompt(self) -> str:
        """Default system prompt for reuse evaluator"""
        return "You are a financial analysis reuse evaluator."
    
    def _extract_three_sources(self, script_path: str, function_name: str = "analyze_question") -> Optional[Dict[str, str]]:
        """
        Extract THREE SOURCES as raw text (no parsing/AST):
        1. Function signature - raw text of function definition
        2. Function docstring - raw docstring text
        3. Argparse section - raw parser.add_argument() lines
        
        Returns dict with three raw text sources for LLM to understand.
        
        Args:
            script_path: Path to the Python script file
            function_name: Name of the main function (default: analyze_question)
            
        Returns:
            {
                "function_signature": "def analyze_question(primary_symbol: str = 'SPY', ...)",
                "docstring": "Main analysis function: backtest conditional buying strategy...",
                "argparse_section": "parser.add_argument('--primary_symbol', default='SPY', help='Primary symbol (default: SPY)')\nparser.add_argument(...)"
            }
        """
        try:
            if not os.path.exists(script_path):
                logger.warning(f"Script path does not exist: {script_path}")
                return None
            
            with open(script_path, 'r') as f:
                source_code = f.read()
            
            sources = {
                "function_signature": "",
                "docstring": "",
                "argparse_section": ""
            }
            
            # SOURCE 1: Extract function signature as raw text
            lines = source_code.split('\n')
            
            for i, line in enumerate(lines):
                if f"def {function_name}(" in line:
                    # Get function signature until closing paren
                    func_signature = line
                    j = i + 1
                    while j < len(lines) and ')' not in func_signature:
                        func_signature += '\n' + lines[j]
                        j += 1
                    
                    # Extract up to the colon
                    if ':' in func_signature:
                        func_signature = func_signature[:func_signature.index(':')+1]
                    
                    sources["function_signature"] = func_signature.strip()
                    logger.info(f"✅ SOURCE 1 (Function signature): Extracted")
                    
                    # SOURCE 2: Extract docstring right after function def
                    if j < len(lines):
                        next_line = lines[j].strip()
                        if next_line.startswith('"""') or next_line.startswith("'''"):
                            docstring = ""
                            quote_type = '"""' if next_line.startswith('"""') else "'''"
                            docstring = next_line[3:] if len(next_line) > 3 else ""
                            j += 1
                            
                            # Find closing quotes
                            while j < len(lines) and quote_type not in docstring:
                                docstring += '\n' + lines[j]
                                j += 1
                            
                            if j < len(lines) and quote_type not in docstring:
                                docstring += '\n' + lines[j]
                            
                            # Remove closing quotes
                            if quote_type in docstring:
                                docstring = docstring[:docstring.index(quote_type)]
                            
                            sources["docstring"] = docstring.strip()
                            logger.info(f"✅ SOURCE 2 (Docstring): Extracted")
                    break
            
            # SOURCE 3: Extract argparse section as raw text
            argparse_lines = [line.strip() for line in lines if 'add_argument' in line]
            
            if argparse_lines:
                sources["argparse_section"] = '\n'.join(argparse_lines)
                logger.info(f"✅ SOURCE 3 (Argparse): Extracted {len(argparse_lines)} argument definitions")
            else:
                logger.warning(f"⚠️  No argparse section found in {script_path}")
            
            logger.info(f"✅ Three sources extracted successfully")
            return sources
            
        except Exception as e:
            logger.error(f"❌ Failed to extract three sources: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    
    
    async def _convert_parameters_with_sources(self, user_query: str, execution_params: Dict[str, Any], sources: Dict[str, str]) -> Dict[str, Any]:
        """
        Use LLM with three text sources to convert parameters
        
        Sources are just raw text:
        - Function signature: "def analyze_question(primary_symbol: str = 'SPY', ...)"
        - Docstring: "Main analysis function..."
        - Argparse: "parser.add_argument('--start_date', help='Start date YYYY-MM-DD')"
        
        Handles:
        - Type conversions (string to float/int/list)
        - Format conversions (e.g., "2 years ago" → "YYYY-MM-DD")
        - Value mappings (e.g., "monthly" → "M")
        
        Args:
            user_query: Original user query
            execution_params: Parameters provided by reuse evaluator
            sources: Dict with function_signature, docstring, argparse_section (all raw text)
            
        Returns:
            {
                "converted_parameters": {...},
                "confidence": 0.95,
                "conversions_applied": [...],
                "reasoning": "..."
            }
        """
        try:
            logger.info(f"🔄 Converting parameters using LLM with three text sources")
            
            param_prompt = f"""Given three text sources from a Python script and current parameters, convert the parameters to match the function's expected format and type.

SOURCE 1 - FUNCTION SIGNATURE:
```python
{sources.get('function_signature', 'N/A')}
```

SOURCE 2 - FUNCTION DOCSTRING:
```
{sources.get('docstring', 'N/A')}
```

SOURCE 3 - ARGPARSE DEFINITIONS:
```python
{sources.get('argparse_section', 'N/A')}
```

CURRENT PARAMETERS:
```json
{json.dumps(execution_params, indent=2)}
```

USER QUERY:
{user_query}

Convert the parameters to match what the function expects based on the three sources above.

Return ONLY valid JSON:
{{
    "converted_parameters": {{"param_name": "value"}},
    "confidence": 0.95,
    "conversions_applied": [
        {{"parameter": "param_name", "from": "original", "to": "converted"}}
    ]
}}"""
            
            conversion_response = await self.llm_service.make_request(
                messages=[{
                    "role": "user",
                    "content": f"{param_prompt}\n\nUSER QUERY: {user_query}"
                }],
                system_prompt="You are a financial analysis parameter converter. Return ONLY valid JSON."
            )
            
            if not conversion_response.get("success"):
                logger.warning(f"Parameter conversion LLM call failed: {conversion_response.get('error')}")
                return {
                    "converted_parameters": execution_params,
                    "conversion_confidence": 0.5,
                    "conversions_made": [],
                    "reasoning": "LLM conversion failed, using original parameters",
                    "issues": [conversion_response.get("error")]
                }
            
            try:
                result = safe_json_loads(conversion_response["content"])
                logger.info(f"✅ Parameter conversion successful (confidence: {result.get('confidence', 0)})")
                return result
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse parameter conversion response")
                return {
                    "converted_parameters": execution_params,
                    "conversion_confidence": 0.5,
                    "conversions_made": [],
                    "reasoning": "Parameter conversion JSON parsing failed",
                    "issues": ["JSON parsing failed"]
                }
            
        except Exception as e:
            logger.error(f"❌ Parameter conversion error: {e}")
            return {
                "converted_parameters": execution_params,
                "conversion_confidence": 0.0,
                "conversions_made": [],
                "reasoning": f"Parameter conversion error: {str(e)}",
                "issues": [str(e)]
            }
    
    async def evaluate_reuse(self, user_query: str, existing_analyses: List[Dict], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Evaluate if existing analyses can be reused for the user query
        
        Args:
            user_query: User's financial question
            existing_analyses: List of existing analysis metadata
            context: Optional context information
            
        Returns:
            Dict containing reuse decision and reasoning
        """
        try:
            logger.info(f"🔍 Evaluating reuse for query: {user_query[:100]}...")
            
            # Build evaluation prompt with existing analyses
            evaluation_prompt = self._build_evaluation_prompt(user_query, existing_analyses, context)
            
            # Get reuse decision from LLM
            response = await self.llm_service.make_request(
                messages=[{
                    "role": "user", 
                    "content": evaluation_prompt
                }],
                system_prompt=self.system_prompt
            )
            
            # Check if LLM request was successful
            if not response.get("success"):
                logger.error(f"❌ LLM request failed: {response.get('error')}")
                return {
                    "status": "error",
                    "reuse_decision": {
                        "should_reuse": False,
                        "reason": f"LLM request failed: {response.get('error')}"
                    },
                    "error": response.get('error'),
                    "timestamp": datetime.now().isoformat()
                }
            
            # Parse JSON response with comment cleaning
            try:
                reuse_decision = safe_json_loads(response["content"])
                logger.info(f"📋 Reuse decision: {reuse_decision['reuse_decision']['should_reuse']}")

                decision = reuse_decision["reuse_decision"]

                # If should_reuse is True, find the analysis_id by matching script_name
                if decision.get("should_reuse") and decision.get("script_name"):
                    script_name = decision["script_name"].lower().strip()

                    logger.info(f"🔍 Searching for script_name '{script_name}' in {len(existing_analyses)} analyses")

                    # Search for matching analysis in existing_analyses
                    found = False
                    matched_analysis = None
                    for idx, analysis in enumerate(existing_analyses):
                        # Log the full structure of the first analysis for debugging
                        if idx == 0:
                            logger.info(f"📋 First analysis structure: {list(analysis.keys())}")

                        # Check in execution metadata (if it exists)
                        execution_data = analysis.get("execution", {})
                        execution_script = (execution_data.get("script_name") or "").lower().strip() if isinstance(execution_data, dict) else ""

                        # Check if script_name matches any of the fields (case-insensitive)
                        if script_name == execution_script:
                            decision["analysis_id"] = analysis.get("id")
                            decision["similarity"] = analysis.get("similarity", 0.0)
                            logger.info(f"✓ Found match! analysis_id={decision['analysis_id']}, similarity={decision['similarity']}")
                            found = True
                            matched_analysis = analysis
                            break

                    # Warn if we couldn't find the analysis_id
                    if not found:
                        logger.warning(f"⚠️ Could not find matching analysis for script_name: '{script_name}'")
                    
                    # Step 2: PARAMETER CONVERSION (same step as reuse decision)
                    # If reuse found and has execution parameters, validate and convert them
                    if found and matched_analysis:
                        logger.info(f"🔄 Step 2: Converting parameters for reused analysis")
                        
                        execution_params = matched_analysis.get("execution", {}).get("parameters", {})
                        llm_provided_params = decision.get("execution", {}).get("parameters", {})
                        
                        # Merge: use LLM-provided params, fallback to existing execution params
                        params_to_convert = {**execution_params, **llm_provided_params}
                        
                        if params_to_convert:
                            # Extract three text sources (signature + argparse + docstring)
                            script_name = matched_analysis.get("execution", {}).get("script_name", {})
                            project_root = "/Users/shivc/Documents/Workspace/JS/qna-ai-admin"
                            script_path = os.path.join(project_root, 'mcp-server/scripts', script_name)
 
                            if script_path:
                                sources = self._extract_three_sources(script_path)
                                
                                if sources:
                                    # Convert parameters using LLM with three text sources
                                    conversion_result = await self._convert_parameters_with_sources(
                                        user_query=user_query,
                                        execution_params=params_to_convert,
                                        sources=sources
                                    )
                                    
                                    # Add conversion results to decision
                                    decision["original_execution"] = decision["execution"]
                                    decision["execution"] = {"script_name": script_name, "parameters": conversion_result.get("converted_parameters", params_to_convert)}
                                    decision["conversion_confidence"] = conversion_result.get("confidence", 0.5)
                                    
                                    logger.info(f"✅ Parameters converted with confidence: {decision['conversion_confidence']}")
                                else:
                                    logger.warning(f"Could not extract three sources from {script_path}")
                                    decision["converted_parameters"] = params_to_convert
                            else:
                                logger.warning(f"No script path found for parameter conversion")
                        else:
                            logger.info(f"No parameters to convert")
                            decision["converted_parameters"] = {}

                result = {
                    "status": "success",
                    "reuse_decision": decision,
                    "timestamp": datetime.now().isoformat()
                }

                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse reuse decision JSON: {e}")
                logger.error(f"Raw response: {response['content']}")
                
                # Fallback to no reuse if parsing fails
                return {
                    "status": "success",
                    "reuse_decision": {
                        "should_reuse": False,
                        "reason": "Failed to parse reuse evaluation response"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"❌ Error evaluating reuse: {e}")
            
            # Fallback to no reuse on error
            return {
                "status": "error",
                "reuse_decision": {
                    "should_reuse": False,
                    "reason": f"Error during reuse evaluation: {str(e)}"
                },
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_evaluation_prompt(self, user_query: str, existing_analyses: List[Dict], context: Optional[Dict] = None) -> str:
        """Build evaluation prompt with user query and existing analyses"""

        # Format existing analyses section
        # Include FULL JSON for each analysis so LLM has complete information
        if existing_analyses:
            analyses_section = "📋 RELEVANT EXISTING ANALYSES:\n\n"
            for i, analysis in enumerate(existing_analyses, 1):
                # Show key information first for readability
                analysis_Id = analysis.get('id') or analysis.get('function_name', 'Unknown Analysis')
                analyses_section += f"{i}. **{analysis_Id}**\n"

                # Dump the FULL analysis JSON with all metadata fields
                analyses_section += "```json\n"
                analyses_section += json.dumps(analysis, indent=2)
                analyses_section += "\n```\n\n"
        else:
            analyses_section = "📋 RELEVANT EXISTING ANALYSES: None provided\n\n"

        # Build context section
        context_section = ""
        if context:
            context_section = f"CONTEXT: {json.dumps(context, indent=2)}\n\n"

        # Build evaluation prompt
        evaluation_prompt = f"""USER QUERY: {user_query}

{context_section}{analyses_section}TASK: Evaluate if any of the existing analyses can be reused for this user query.

Consider:
1. Is the core financial methodology the same?
2. Are only parameters different (symbols, timeframes, thresholds)?
3. Is the expected output format similar?
4. Does the analysis approach match what's needed?
5. Check execution parameters (if available) - can they be adjusted for this query?
6. Review example usage and workflow steps to understand what the analysis does

Return your decision in the exact JSON format specified in the system prompt."""

        return evaluation_prompt

# Factory function for easy initialization
def create_reuse_evaluator() -> ReuseEvaluatorService:
    """Create and return a ReuseEvaluatorService instance"""
    return ReuseEvaluatorService()