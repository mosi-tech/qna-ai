#!/usr/bin/env python3
"""
Orchestrator Agent

Chains multiple agents together to process financial analysis requests end-to-end.

Usage:
    python orchestrator.py --question "Show QQQ ETF price and YTD return"
    python orchestrator.py --question "..." --skip-verification
    python orchestrator.py --question "..." --skip-execution
    python orchestrator.py --question "..." --skip-enhancement
    python orchestrator.py --question "..." --no-code  # Use direct MCP tool calling (faster)
    python orchestrator.py --question "..." --mock  # Mock v1: Single-shot planning + mock data
    python orchestrator.py --question "..." --mock --mock-v2  # Mock v2: Decompose into sub-Qs + mock data per sub-Q

Pipeline (default - with code generation):
    1. question_enhancer (optional, skipped via --skip-enhancement)
    2. ui_planner
    3. reuse_evaluator
    4. code_prompt_builder
    5. [UNIFIED RETRY LOOP] code_script_generator → script_validator → verification_agent
       - If validation fails: retry generation with validation feedback
       - If verification fails: retry generation with verification feedback
       - Max 3 generation attempts (configurable)
    6. script_executor (skipped via --skip-execution)

Pipeline (with --no-code flag):
    1. question_enhancer (optional)
    2. ui_planner
    3. code_prompt_builder (selects relevant MCP functions)
    4. mcp_direct_agent (answers via direct MCP tool calling)

Pipeline (with --mock flag, v1 single-shot):
    1. question_enhancer (optional)
    2. ui_planner (plan blocks directly from question)
    3. mock_reuse_evaluator (checks ChromaDB for existing mock data)
    4. mock_data_generator (generates mock data for all blocks together)

Pipeline (with --mock --mock-v2 flags, hierarchical decomposition):
    1. question_enhancer (optional)
    2. ui_planner_batch_v2 (decompose question into atomic sub-questions)
    3. mock_v2_generator (generate mock data for each sub-question independently)

Skipped in no-code mode: reuse_evaluator, code_script_generator,
                         script_validator, verification_agent, script_executor

Skipped in mock v1 mode: code_script_generator, script_validator,
                         verification_agent, script_executor

Skipped in mock v2 mode: ui_planner (uses hierarchical decomposition instead), mock_reuse_evaluator,
                         code_script_generator, script_validator, verification_agent, script_executor
"""

import argparse
import json
import logging
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import agents and base class
from agent_base import AgentResult
from ui_planner_agent import create_ui_planner_agent
from ui_planner_batch_v2_agent import create_ui_planner_batch_v2
from question_enhancer_agent import create_question_enhancer_agent
from reuse_evaluator_agent import create_reuse_evaluator_agent
from code_prompt_builder_agent import create_code_prompt_builder_agent
from code_script_generator_agent import create_code_script_generator_agent
from script_validator_agent import create_script_validator_agent
from verification_agent import create_verification_agent
from script_executor_agent import create_script_executor_agent
from mcp_direct_agent import create_mcp_direct_agent
from mock.mock_reuse_evaluator import create_mock_reuse_evaluator
from mock.mock_data_generator import create_mock_data_generator
from mock.mock_v2_generator import create_mock_v2_generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnalysisOrchestrator:
    """Orchestrates multiple agents for end-to-end analysis"""

    def __init__(
        self,
        skip_verification: bool = False,
        skip_execution: bool = False,
        skip_enhancement: bool = False,
        skip_reuse: bool = False,
        no_code: bool = False,
        mock_mode: bool = False,
        mock_v2_mode: bool = False,
        max_generation_attempts: int = 3,
        verbose: bool = False,
        output_dir: str = None
    ):
        self.skip_verification = skip_verification
        self.skip_execution = skip_execution
        self.skip_enhancement = skip_enhancement
        self.skip_reuse = skip_reuse
        self.no_code = no_code
        self.mock_mode = mock_mode
        self.mock_v2_mode = mock_v2_mode
        self.max_generation_attempts = max_generation_attempts
        self.verbose = verbose
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), "..", "output")

        # Initialize agents
        self.ui_planner = create_ui_planner_agent()
        self.ui_planner_batch_v2 = create_ui_planner_batch_v2() if mock_v2_mode else None
        self.question_enhancer = create_question_enhancer_agent()
        self.reuse_evaluator = create_reuse_evaluator_agent()
        self.code_prompt_builder = create_code_prompt_builder_agent()
        self.code_script_generator = create_code_script_generator_agent()
        self.script_validator = create_script_validator_agent()
        self.verification = create_verification_agent()
        self.script_executor = create_script_executor_agent()
        self.mcp_direct = create_mcp_direct_agent()

        # Mock mode agents (v1 - single-shot)
        self.mock_reuse_evaluator = create_mock_reuse_evaluator()
        self.mock_data_generator = create_mock_data_generator()

        # Mock mode agents (v2 - batch decomposition)
        self.mock_v2_generator = create_mock_v2_generator() if mock_v2_mode else None

        # Track execution steps
        self.steps = []

    def process_question(self, question: str, existing_analyses: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Process a question through the full pipeline"""
        self.steps = []
        # Create question ID from question (safe filename)
        self.question_id = question.replace(" ", "_").replace("/", "_").replace("?", "").lower()[:50]
        start_time = datetime.now()

        try:
            # Step 1: Question Enhancer - Expand short questions (optional, skip via --skip-enhancement)
            enhanced_question = question  # Default to original if skipped
            if not self.skip_enhancement:
                step_result = self._run_step(
                    "question_enhancer",
                    self.question_enhancer.execute,
                    {
                        "question": question,
                        "original_question": question
                    }
                )
                if step_result["success"]:
                    enhanced_question = step_result["data"].get("enhanced_question", question)
                    self._log(f"📝 Enhanced: {enhanced_question[:100]}...")
                else:
                    self._log("⚠️  Question enhancer failed, using original question")

            # Mock V2 mode flow (batch decomposition): Skip normal UI planner
            if self.mock_mode and self.mock_v2_mode:
                self._log(f"🧪 Mock V2 mode enabled (batch decomposition)")

                # Step 2b: UI Planner Batch V2 - Decompose into sub-questions
                step_result = self._run_step(
                    "ui_planner_batch_v2",
                    self.ui_planner_batch_v2.execute,
                    {"question": enhanced_question}
                )
                if not step_result["success"]:
                    return self._error_result("UI Planner Batch V2 failed", step_result)

                decomposition = step_result["data"]
                title = decomposition.get("dashboard_title", enhanced_question)

                # Step 3 (V2): Mock V2 Generator - Generate data for each sub-question
                step_result = self._run_step(
                    "mock_v2_generator",
                    self.mock_v2_generator.execute,
                    decomposition
                )
                if not step_result["success"]:
                    return self._error_result("Mock V2 Generator failed", step_result)

                mock_v2_data = step_result["data"]
                blocks = mock_v2_data.get("blocks", [])
                blocks_data = mock_v2_data.get("blocks_data", [])

                total_time = (datetime.now() - start_time).total_seconds()

                self._log(f"✅ Mock V2 complete: {len(blocks)} blocks, {len(blocks_data)} data items")

                return {
                    "success": True,
                    "action": "mock_generated",
                    "title": title,
                    "blocks": blocks,
                    "blocks_data": blocks_data,
                    "total_time": total_time,
                    "steps": self.steps,
                    "timestamp": datetime.now().isoformat()
                }

            # Step 2: UI Planner - Plan dashboard layout (v1 flow)
            step_result = self._run_step(
                "ui_planner",
                self.ui_planner.execute,
                {"question": enhanced_question}
            )
            if not step_result["success"]:
                return self._error_result("UI Planner failed", step_result)

            blocks = step_result["data"].get("blocks", [])
            title = step_result["data"].get("title", enhanced_question)
            layout = step_result["data"].get("layout")  # Grid layout with slot assignments
            ui_output = step_result["data"]

            # Mock v1 mode flow: Skip script generation, use mock data
            if self.mock_mode:
                self._log(f"🧪 Mock mode enabled (skip_reuse={self.skip_reuse})")

                mock_data_file = None
                similarity = None

                # Step 3 (Mock): Mock Reuse Evaluator - Check for existing mock data (unless skipped)
                if not self.skip_reuse:
                    step_result = self._run_step(
                        "mock_reuse_evaluator",
                        self.mock_reuse_evaluator.execute,
                        {"question": enhanced_question}
                    )

                    if step_result["success"] and step_result["data"].get("reused"):
                        # Reuse existing mock data
                        self._log("🔄 Reusing existing mock data")
                        reuse_data = step_result["data"]
                        mock_data_file = reuse_data.get("mock_data_file")
                        similarity = reuse_data.get("similarity")

                # Step 4 (Mock): Load and validate reused mock data, OR generate fresh
                blocks_data = []
                validation_passed = False

                # First, try to load and validate reused data if available
                if mock_data_file:
                    try:
                        if os.path.exists(mock_data_file):
                            with open(mock_data_file, 'r') as f:
                                mock_file_content = json.load(f)

                            # Validate that reused mock data matches current UI layout
                            mock_block_ids = {b.get("block_id") for b in mock_file_content.get("blocks", [])}
                            ui_block_ids = {b.get("blockId") for b in blocks}

                            if mock_block_ids != ui_block_ids:
                                self._log(f"⚠️  Reused mock data blockIds don't match current UI layout")
                                self._log(f"   UI expects: {ui_block_ids}")
                                self._log(f"   Mock data has: {mock_block_ids}")
                                mock_data_file = None  # Force regeneration
                                similarity = None
                            else:
                                # Extract blocks from mock data and format for UI
                                for mock_block in mock_file_content.get("blocks", []):
                                    blocks_data.append({
                                        "blockId": mock_block.get("block_id"),
                                        "data": mock_block.get("data")
                                    })
                                self._log(f"✅ Loaded reused mock data with {len(blocks_data)} blocks")
                                validation_passed = True
                        else:
                            self._log(f"⚠️  Mock data file not found: {mock_data_file}")
                            mock_data_file = None
                            similarity = None
                    except Exception as e:
                        self._log(f"⚠️  Failed to load mock data file: {e}")
                        mock_data_file = None
                        similarity = None

                # If reused data failed validation or wasn't available, generate fresh data
                if not validation_passed:
                    self._log("🧪 Generating new mock data")
                    step_result = self._run_step(
                        "mock_data_generator",
                        self.mock_data_generator.execute,
                        {
                            "question": enhanced_question,
                            "ui_planner_output": ui_output,
                            "question_id": self.question_id
                        }
                    )

                    if not step_result["success"]:
                        return self._error_result("Mock data generator failed", step_result)

                    mock_data = step_result["data"]
                    mock_data_file = mock_data.get("mock_data_file")
                    similarity = None

                    # Load the freshly generated mock data
                    try:
                        if mock_data_file and os.path.exists(mock_data_file):
                            with open(mock_data_file, 'r') as f:
                                mock_file_content = json.load(f)
                            for mock_block in mock_file_content.get("blocks", []):
                                blocks_data.append({
                                    "blockId": mock_block.get("block_id"),
                                    "data": mock_block.get("data")
                                })
                            self._log(f"✅ Generated mock data with {len(blocks_data)} blocks")
                    except Exception as e:
                        self._log(f"⚠️  Failed to load freshly generated mock data: {e}")

                total_time = (datetime.now() - start_time).total_seconds()

                return {
                    "success": True,
                    "action": "mock_reused" if similarity is not None else "mock_generated",
                    "title": title,
                    "blocks": blocks,
                    "blocks_data": blocks_data,
                    "layout": layout,  # Grid layout with slot assignments
                    "mock_data_file": mock_data_file,
                    "similarity": similarity,
                    "total_time": total_time,
                    "steps": self.steps,
                    "timestamp": datetime.now().isoformat()
                }

            # Step 3: Reuse Evaluator - Check if we can reuse existing analysis (skip in no-code mode)
            if not self.no_code:
                step_result = self._run_step(
                    "reuse_evaluator",
                    self.reuse_evaluator.execute,
                    {
                        "question": enhanced_question,
                        "existing_analyses": existing_analyses or []
                    }
                )

                if step_result["success"] and step_result["data"].get("should_reuse"):
                    # Reuse existing analysis
                    self._log("🔄 Reusing existing analysis")
                    reuse_data = step_result["data"]
                    return {
                        "success": True,
                        "action": "reused",
                        "analysis_id": reuse_data.get("analysis_id"),
                        "script_name": reuse_data.get("script_name"),
                        "execution": reuse_data.get("execution"),
                        "total_time": (datetime.now() - start_time).total_seconds(),
                        "steps": self.steps
                    }

            # Step 4: Code Prompt Builder - Build enriched prompt and select functions
            step_result = self._run_step(
                "code_prompt_builder",
                self.code_prompt_builder.execute,
                {
                    "question": enhanced_question,
                    "blocks": blocks,
                    "context": {}
                }
            )

            if not step_result["success"]:
                return self._error_result("Code Prompt Builder failed", step_result)

            enriched_prompt = step_result["data"].get("enriched_prompt")
            selected_functions = step_result["data"].get("selected_functions", [])

            # No-code path: Use direct MCP tool calling instead of script generation
            if self.no_code:
                self._log("🚀 Using no-code path (direct MCP tool calling)")

                step_result = self._run_step(
                    "mcp_direct",
                    self.mcp_direct.execute,
                    {
                        "question": question,
                        "blocks": blocks,
                        "selected_functions": selected_functions
                    }
                )
                if not step_result["success"]:
                    return self._error_result("MCP Direct agent failed", step_result)

                mcp_data = step_result["data"].get("blocks_data", [])
                total_time = (datetime.now() - start_time).total_seconds()

                return {
                    "success": True,
                    "action": "mcp_direct",
                    "title": title,
                    "blocks": blocks,
                    "blocks_data": mcp_data,
                    "layout": layout,  # Grid layout with slot assignments
                    "total_time": total_time,
                    "steps": self.steps,
                    "timestamp": datetime.now().isoformat()
                }

            # Code path: Script generation with validation and verification
            # Unified retry loop: Generation → Validation → Verification
            # Any failure in validation or verification triggers regeneration with feedback
            generation_passed = False
            all_validation_messages = []
            all_verification_messages = []

            for gen_attempt in range(self.max_generation_attempts):
                gen_step_name = f"code_script_generator_{gen_attempt + 1}" if gen_attempt > 0 else "code_script_generator"

                # Step 5: Code Script Generator - Generate Python script
                if gen_attempt == 0:
                    # First attempt - no feedback
                    gen_input = {
                        "enriched_prompt": enriched_prompt,
                        "selected_functions": selected_functions,
                        "question": question,
                        "context": {"blocks": blocks}
                    }
                else:
                    # Retry with feedback from previous failures
                    self._log(f"🔄 Generation attempt {gen_attempt + 1} with feedback...")
                    gen_input = {
                        "enriched_prompt": enriched_prompt,
                        "selected_functions": selected_functions,
                        "question": question,
                        "context": {
                            "blocks": blocks,
                            "validation_feedback": all_validation_messages,
                            "verification_feedback": all_verification_messages
                        }
                    }

                step_result = self._run_step(
                    gen_step_name,
                    self.code_script_generator.execute,
                    gen_input
                )
                if not step_result["success"]:
                    return self._error_result("Code Script Generator failed", step_result)

                script = step_result["data"].get("script")
                script_name = step_result["data"].get("script_name")

                # Step 6: Script Validator - Validate script
                step_result = self._run_step(
                    "script_validator",
                    self.script_validator.execute,
                    {"script": script}
                )

                validation_data = step_result["data"] if step_result["success"] else {"valid": False}
                validation_messages = {
                    "attempt": gen_attempt + 1,
                    "errors": validation_data.get("errors", []),
                    "warnings": validation_data.get("warnings", []),
                    "valid": validation_data.get("valid", False)
                }
                all_validation_messages.append(validation_messages)

                if not validation_data.get("valid"):
                    self._log(f"⚠️  Validation failed on gen attempt {gen_attempt + 1}, will retry...")
                    # Validation failed - will retry generation in next loop iteration
                    continue

                # Step 7: Verification - Verify script with multiple models (if not skipped)
                if not self.skip_verification:
                    step_result = self._run_step(
                        "verification",
                        self.verification.execute,
                        {
                            "question": question,
                            "script": script,
                            "context": {"blocks": blocks}
                        }
                    )

                    verification_data = step_result["data"] if step_result["success"] else {"approved": False}
                    verification_messages = {
                        "attempt": gen_attempt + 1,
                        "approved": verification_data.get("approved", False),
                        "issues": verification_data.get("issues", []),
                        "suggestions": verification_data.get("suggestions", []),
                        "model_votes": verification_data.get("model_votes", {})
                    }
                    all_verification_messages.append(verification_messages)

                    if not verification_data.get("approved"):
                        self._log(f"⚠️  Verification failed on gen attempt {gen_attempt + 1}, will retry...")
                        # Verification failed - will retry generation in next loop iteration
                        continue

                # If we get here, both validation and verification passed
                generation_passed = True
                self._log(f"✅ Generation attempt {gen_attempt + 1} passed all checks")
                break

            if not generation_passed:
                # Determine what caused the final failure
                if all_validation_messages and not all_validation_messages[-1].get("valid"):
                    return self._error_result(
                        f"Script validation failed after {self.max_generation_attempts} generation attempts",
                        step_result,
                        details=[m["errors"] for m in all_validation_messages if m["errors"]]
                    )
                elif all_verification_messages and not all_verification_messages[-1].get("approved"):
                    return self._error_result(
                        f"Script verification failed after {self.max_generation_attempts} generation attempts",
                        step_result,
                        details=[m["issues"] for m in all_verification_messages if m["issues"]]
                    )
                else:
                    return self._error_result(
                        f"Generation failed after {self.max_generation_attempts} attempts",
                        {}
                    )

            # Step 8: Script Executor - Execute script
            if not self.skip_execution:
                step_result = self._run_step(
                    "script_executor",
                    self.script_executor.execute,
                    {
                        "script_content": script,
                        "parameters": {}
                    }
                )
                if not step_result["success"]:
                    return self._error_result("Script execution failed", step_result)

                script_results = step_result["data"].get("results")
            else:
                script_results = {"skipped": True, "message": "Execution skipped by request"}

            # Success!
            total_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "action": "generated",
                "title": title,
                "blocks": blocks,
                "layout": layout,  # Grid layout with slot assignments
                "script_name": script_name,
                "script": script if self.verbose else f"<{len(script)} characters>",
                "validation": validation_data,
                "results": script_results,
                "total_time": total_time,
                "steps": self.steps,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.exception(f"Orchestrator error: {e}")
            return self._error_result(f"Unexpected error: {e}", {})

    def _run_step(self, step_name: str, agent_method, input_data: Dict) -> Dict[str, Any]:
        """Run a single step and track metrics"""
        step_start = datetime.now()

        try:
            result = agent_method(input_data)

            step_time = (datetime.now() - step_start).total_seconds()

            step_info = {
                "step": step_name,
                "success": result.success,
                "duration": step_time,
                "timestamp": datetime.now().isoformat()
            }

            if result.data:
                step_info["output_size"] = len(json.dumps(result.data))

            self.steps.append(step_info)

            # Save step output to file
            if hasattr(self, 'question_id') and self.output_dir:
                self._save_step_output(step_name, input_data, result, step_time)

            self._log(f"✅ {step_name}: {'SUCCESS' if result.success else 'FAILED'} ({step_time:.2f}s)")

            return result.to_dict()

        except Exception as e:
            step_time = (datetime.now() - step_start).total_seconds()
            self.steps.append({
                "step": step_name,
                "success": False,
                "error": str(e),
                "duration": step_time,
                "timestamp": datetime.now().isoformat()
            })
            raise

    def _save_step_output(self, step_name: str, input_data: Dict, result: AgentResult, duration: float):
        """Save step output to file"""
        try:
            import os

            output_path = os.path.join(self.output_dir, self.question_id)
            os.makedirs(output_path, exist_ok=True)

            step_timestamp = datetime.now().isoformat()
            step_file = os.path.join(output_path, f"{step_name}.json")

            step_data = {
                "step": step_name,
                "input": input_data,
                "output": result.to_dict(),
                "duration": duration,
                "timestamp": step_timestamp
            }

            with open(step_file, 'w') as f:
                json.dump(step_data, f, indent=2)

            self._log(f"💾 Saved: {step_file}")

            # Also save a debug log entry
            debug_log_file = os.path.join(output_path, "_debug.log")
            debug_entry = f"[{step_timestamp}] {step_name}: {duration:.2f}s - {'SUCCESS' if result.success else 'FAILED'}\n"
            with open(debug_log_file, 'a') as f:
                f.write(debug_entry)

        except Exception as e:
            self._log(f"⚠️  Failed to save step output: {e}")

    def _error_result(self, message: str, step_result: Dict, details: Optional[List] = None) -> Dict[str, Any]:
        """Return an error result"""
        return {
            "success": False,
            "error": message,
            "details": details,
            "step_error": step_result.get("error"),
            "steps": self.steps
        }

    def _log(self, message: str):
        """Log message"""
        if self.verbose:
            logger.info(message)
        else:
            print(message)


def main():
    parser = argparse.ArgumentParser(
        description="Orchestrate multiple agents for financial analysis"
    )
    parser.add_argument(
        "--question", "-q",
        required=True,
        help="User's financial question"
    )
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Skip script verification step"
    )
    parser.add_argument(
        "--skip-execution",
        action="store_true",
        help="Skip script execution step"
    )
    parser.add_argument(
        "--skip-enhancement",
        action="store_true",
        help="Skip question enhancement step (for testing with well-formed questions)"
    )
    parser.add_argument(
        "--skip-reuse",
        action="store_true",
        help="Skip reuse evaluation and always generate fresh data (useful for testing without caching)"
    )
    parser.add_argument(
        "--no-code",
        action="store_true",
        help="Skip code generation and use direct MCP tool calling (faster for simple queries)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Mock mode: Skip script generation/execution, use mock data for testing UI Planner and Reuse Evaluator"
    )
    parser.add_argument(
        "--mock-v2",
        action="store_true",
        help="Mock V2 mode (batch decomposition): Requires --mock. Breaks questions into sub-questions and generates data per sub-question"
    )
    parser.add_argument(
        "--max-generation-attempts",
        type=int,
        default=3,
        help="Max number of generation retry attempts (default: 3)"
    )
    parser.add_argument(
        "--existing-analyses",
        help="Path to JSON file with existing analyses"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=None,
        help="Output directory for step outputs (default: backend/headless/output)"
    )
    parser.add_argument(
        "--output-file",
        help="Output file for final results"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose logging"
    )

    args = parser.parse_args()

    # Load existing analyses if provided
    existing_analyses = None
    if args.existing_analyses:
        try:
            with open(args.existing_analyses, 'r') as f:
                existing_analyses = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load existing analyses: {e}")

    # Create orchestrator
    orchestrator = AnalysisOrchestrator(
        skip_verification=args.skip_verification,
        skip_execution=args.skip_execution,
        skip_enhancement=args.skip_enhancement,
        skip_reuse=args.skip_reuse,
        no_code=args.no_code,
        mock_mode=args.mock,
        mock_v2_mode=args.mock_v2,
        max_generation_attempts=args.max_generation_attempts,
        verbose=args.verbose,
        output_dir=args.output_dir
    )

    # Process question
    print(f"\n{'='*60}")
    print(f"Processing: {args.question}")
    print(f"{'='*60}\n")

    result = orchestrator.process_question(args.question, existing_analyses)

    # Output results
    print(f"\n{'='*60}")
    if result.get("success"):
        print(f"✅ Analysis complete!")
        print(f"   Action: {result.get('action')}")
        print(f"   Total time: {result.get('total_time', 0):.2f}s")
        print(f"   Steps: {len(result.get('steps', []))}")

        # Print final plan details
        if result.get("title"):
            print(f"\n📋 Final Plan: {result.get('title')}")
        if result.get("blocks"):
            print(f"   Blocks selected: {len(result.get('blocks'))}")
            for i, block in enumerate(result.get("blocks", []), 1):
                print(f"      {i}. {block.get('blockId')} - {block.get('title')} ({block.get('category')})")

        # Print layout details
        if result.get("layout"):
            layout = result.get("layout")
            print(f"\n📐 Grid Layout: {layout.get('templateId')}")
            slots = layout.get("slots", {})
            for slot_id, slot_config in slots.items():
                print(f"      {slot_id}: {slot_config.get('blockId')} - {slot_config.get('title')}")
    else:
        print(f"❌ Analysis failed: {result.get('error')}")
    print(f"{'='*60}\n")

    # Save final result to question directory
    try:
        import os
        output_dir = args.output_dir or orchestrator.output_dir
        question_output_dir = os.path.join(output_dir, orchestrator.question_id)
        os.makedirs(question_output_dir, exist_ok=True)
        final_result_file = os.path.join(question_output_dir, "final_result.json")

        # Add debug info to result
        result["_debug"] = {
            "timestamp": datetime.now().isoformat(),
            "blocks_count": len(result.get("blocks", [])),
            "blocks_data_count": len(result.get("blocks_data", [])),
            "blocks_ids": [b.get("blockId") for b in result.get("blocks", [])],
            "blocks_data_ids": [b.get("blockId") for b in result.get("blocks_data", [])],
            "success": result.get("success"),
            "action": result.get("action"),
        }

        with open(final_result_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"💾 Final result saved to: {final_result_file}")
        print(f"   Blocks: {result['_debug']['blocks_count']}, BlocksData: {result['_debug']['blocks_data_count']}")
    except Exception as e:
        logger.error(f"Failed to save final result: {e}")

    # Print JSON to stdout for API parsing
    print(json.dumps(result))

    # Write output file if specified
    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results also written to: {args.output_file}")

    # Also print full result if verbose
    if args.verbose:
        print(json.dumps(result, indent=2))

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())