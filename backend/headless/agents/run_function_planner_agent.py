#!/usr/bin/env python3
"""
Function Planner Agent Runner

Runs the function-planner agent on batches of financial questions to create
a function registry and question-to-function mappings.

This version uses the Anthropic API directly.

Usage:
    python run_function_planner_agent.py [options]

Options:
    --input PATH          Input JSON file with questions (default: all-questions/sub_questions_ui_planner_system_v2.json)
    --batch-size N        Number of questions per batch (default: 20)
    --output-dir PATH     Output directory for results (default: all-questions)
    --question-field PATH    JSON path to question field (default: $.original_question)
    --help               Show this help message

Environment Variables:
    ANTHROPIC_AUTH_TOKEN Anthropic API auth token (required)
    ANTHROPIC_BASE_URL   Custom API base URL (optional)
    MODEL                Claude model to use (default: claude-sonnet-4-6)
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
import re

# Load .env file from agents directory
agents_dir = Path(__file__).parent
env_file = agents_dir / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)


# Try to import Anthropic SDK
try:
    from anthropic import Anthropic
except ImportError:
    print("Error: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)


@dataclass
class FunctionPlannerConfig:
    """Configuration for the function planner runner."""
    input_file: str = "all-questions/sub_questions_ui_planner_system_v2.json"
    output_dir: str = "all-questions"
    batch_size: int = 20
    question_field: str = "original_question"
    agent_file: str = ".claude/agents/function-planner.md"
    model: str = "claude-sonnet-4-6"


def parse_arguments() -> FunctionPlannerConfig:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run function-planner agent on batches of financial questions"
    )
    parser.add_argument(
        "--input",
        default="all-questions/sub_questions_ui_planner_system_v2.json",
        help="Input JSON file with questions"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Number of questions per batch"
    )
    parser.add_argument(
        "--output-dir",
        default="all-questions",
        help="Output directory for results"
    )
    parser.add_argument(
        "--question-field",
        default="original_question",
        help="JSON path to question field"
    )
    parser.add_argument(
        "--agent-file",
        default=".claude/agents/function-planner.md",
        help="Path to the function-planner agent file"
    )
    parser.add_argument(
        "--model",
        default=os.getenv("MODEL", "claude-sonnet-4-6"),
        help="Claude model to use"
    )

    args = parser.parse_args()

    return FunctionPlannerConfig(
        input_file=args.input,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        question_field=args.question_field,
        agent_file=args.agent_file,
        model=args.model
    )


def load_questions(config: FunctionPlannerConfig) -> List[Dict[str, Any]]:
    """Load questions from the input file."""
    input_path = Path(config.input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {config.input_file}")

    with open(input_path, "r") as f:
        data = json.load(f)

    # Extract questions based on the question_field path
    questions = []
    for item in data:
        # Handle both array of objects and array of question strings
        if isinstance(item, str):
            questions.append({"question": item, "original_question": item})
        else:
            # Try to extract the question field
            question_field = config.question_field
            if question_field in item:
                questions.append(item)
            elif "question" in item:
                questions.append(item)
            elif "original_question" in item:
                questions.append(item)
            else:
                # Use the whole item as is
                questions.append(item)

    print(f"Loaded {len(questions)} questions from {config.input_file}")
    return questions


def create_batches(
    questions: List[Dict[str, Any]],
    batch_size: int
) -> List[List[Dict[str, Any]]]:
    """Split questions into batches."""
    batches = []
    for i in range(0, len(questions), batch_size):
        batch = questions[i:i + batch_size]
        batches.append(batch)

    print(f"Created {len(batches)} batches (batch_size={batch_size})")
    return batches


def load_agent_prompt(config: FunctionPlannerConfig) -> str:
    """Load the agent prompt from the agent file."""
    agent_path = Path(config.agent_file)

    if not agent_path.exists():
        raise FileNotFoundError(f"Agent file not found: {config.agent_file}")

    with open(agent_path, "r") as f:
        return f.read()


def create_batch_prompt(
    batch: List[Dict[str, Any]],
    batch_index: int,
    agent_prompt: str,
    question_field: str
) -> str:
    """Create the prompt for processing a batch of questions."""
    # Extract question texts
    question_texts = []
    for idx, item in enumerate(batch):
        start_idx = batch_index * len(batch) + idx + 1
        question_text = item.get(question_field, item.get("question", str(item)))
        question_texts.append(f"{start_idx}. \"{question_text}\"")

    questions_block = "\n".join(question_texts)

    prompt = f"""{agent_prompt}

You are processing batch {batch_index + 1}. Here are the questions to process:

{questions_block}

CRITICAL INSTRUCTIONS:
1. Process ALL {len(batch)} questions in this batch
2. For each question, determine the appropriate mapping type (MCP_DIRECT, MCP_PARAMETERIZED, CUSTOM_REUSE, CUSTOM_NEW, CUSTOM_SPECIFIC)
3. Create custom functions only when patterns emerge across multiple questions in this batch
4. Track which custom function handles which questions
5. Use MCP functions directly whenever possible
6. Respond ONLY with valid JSON in the following format:

{{
  "function_registry": {{
    "get_stock_fundamental": {{
      "function_id": "get_stock_fundamental",
      "name": "Get Stock Fundamental",
      "description": "Retrieve fundamental metrics for a stock",
      "parameters": {{
        "symbol": {{"type": "string", "required": true, "description": "Stock ticker symbol"}},
        "metric": {{
          "type": "enum",
          "required": true,
          "description": "Fundamental metric to retrieve",
          "enum": ["pe_ratio", "pb_ratio", "dividend_yield", "market_cap", "revenue", "net_income", "eps", "roe", "debt_to_equity"]
        }}
      }},
      "returns": {{"type": "number", "description": "Value of the requested fundamental metric"}},
      "implementation": {{
        "type": "mcp_wrapped",
        "mcp_function": "get_fundamentals",
        "mcp_params": {{"symbol": "{{symbol}}"}},
        "data_extraction": "{{metric}}"
      }},
      "questions": [1, 2, 5, 8]
    }}
  }},
  "question_function_mapping": [
    {{"question_id": 1, "question": "...", "mapping_type": "...", ...}},
    ...
  ],
  "summary": {{
    "total_questions": {len(batch)},
    "breakdown": {{"MCP_DIRECT": 0, "MCP_PARAMETERIZED": 0, "CUSTOM_REUSE": 0, "CUSTOM_NEW": 0, "CUSTOM_SPECIFIC": 0}},
    "unique_functions_created": 0,
    "reuse_rate": 0,
    "average_questions_per_function": 0
  }}
}}

DO NOT include any markdown code blocks or backticks. Return ONLY the JSON object.
"""

    return prompt


def process_batch_with_api(
    batch: List[Dict[str, Any]],
    batch_index: int,
    config: FunctionPlannerConfig
) -> Dict[str, Any]:
    """Process a batch of questions using the Anthropic API."""
    # Get API auth token (support both ANTHROPIC_AUTH_TOKEN and ANTHROPIC_API_KEY)
    api_key = os.getenv("ANTHROPIC_AUTH_TOKEN") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY environment variable not set")

    # Load agent prompt
    agent_prompt = load_agent_prompt(config)

    # Create batch prompt
    batch_prompt = create_batch_prompt(
        batch,
        batch_index,
        agent_prompt,
        config.question_field
    )

    print(f"\n{'='*60}")
    print(f"Processing batch {batch_index + 1} (questions {batch_index * config.batch_size + 1} - {batch_index * config.batch_size + len(batch)})")
    print(f"{'='*60}")

    # Create Anthropic client with optional custom base URL
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    # For ollama.com endpoint, use Authorization: Bearer format
    if base_url and "ollama.com" in base_url:
        # Use httpx for custom auth header
        import httpx
        client = Anthropic(
            api_key=api_key,
            base_url=base_url,
            http_client=httpx.Client(
                headers={
                    "Authorization": f"Bearer {api_key}"
                },
                verify=False  # For self-signed certificates if needed
            )
        )
        print(f"  Using custom base URL with Bearer auth: {base_url}")
    elif base_url:
        client = Anthropic(api_key=api_key, base_url=base_url)
        print(f"  Using custom base URL: {base_url}")
    else:
        client = Anthropic(api_key=api_key)

    # Call the API
    try:
        print(f"  Calling API with model: {config.model}")
        response = client.messages.create(
            model=config.model,
            max_tokens=8192,
            temperature=0,
            messages=[
                {"role": "user", "content": batch_prompt}
            ]
        )

        # Extract the response text
        print(f"  Response content length: {len(response.content)}")

        # Find the text block (skip thinking blocks)
        response_text = None
        for content_block in response.content:
            if hasattr(content_block, 'type'):
                print(f"  Content block type: {content_block.type}")
                if content_block.type == 'text' and hasattr(content_block, 'text') and content_block.text:
                    response_text = content_block.text
                    break

        if not response_text:
            print(f"  Error: No text block found in response")
            print(f"  Response content: {response.content}")
            raise ValueError("No text block found in response")

        # Parse JSON from response
        # The response might have markdown code blocks, so extract the JSON
        json_pattern = r'\{[\s\S]*\}'
        json_matches = re.findall(json_pattern, response_text)

        if json_matches:
            # Use the largest JSON block
            result_data = json.loads(max(json_matches, key=len))
        else:
            raise ValueError("Could not find JSON in agent response")

        return result_data

    except Exception as e:
        print(f"  Error processing batch: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        # Return empty result on error
        return {
            "function_registry": {},
            "question_function_mapping": [],
            "summary": {
                "total_questions": len(batch),
                "breakdown": {"MCP_DIRECT": 0, "MCP_PARAMETERIZED": 0, "CUSTOM_REUSE": 0, "CUSTOM_NEW": 0, "CUSTOM_SPECIFIC": 0},
                "unique_functions_created": 0,
                "reuse_rate": 0,
                "average_questions_per_function": 0
            },
            "error": str(e)
        }


def save_batch_result(
    batch: List[Dict[str, Any]],
    batch_index: int,
    result: Dict[str, Any],
    config: FunctionPlannerConfig
) -> None:
    """Save batch result to files."""
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    batch_num = batch_index + 1
    start_idx = batch_index * config.batch_size + 1
    end_idx = batch_index * config.batch_size + len(batch)

    # Add metadata
    function_registry = result.get("function_registry", {})
    function_registry["metadata"] = {
        "batch_index": batch_index,
        "batch_number": batch_num,
        "question_range": [start_idx, end_idx],
        "question_count": len(batch)
    }

    question_mappings = result.get("question_function_mapping", [])
    mapping_data = {
        "mappings": question_mappings,
        "summary": result.get("summary", {}),
        "metadata": {
            "batch_index": batch_index,
            "batch_number": batch_num,
            "question_range": [start_idx, end_idx],
            "question_count": len(batch)
        }
    }

    # Save function registry
    registry_file = output_dir / f"function_registry_batch_{batch_num}.json"
    with open(registry_file, "w") as f:
        json.dump(function_registry, f, indent=2)
    print(f"  Saved: {registry_file}")

    # Save question mappings
    mapping_file = output_dir / f"question_function_mapping_batch_{batch_num}.json"
    with open(mapping_file, "w") as f:
        json.dump(mapping_data, f, indent=2)
    print(f"  Saved: {mapping_file}")


def merge_results(
    all_results: List[Dict[str, Any]],
    config: FunctionPlannerConfig,
    total_questions: int
) -> None:
    """Merge all batch results into consolidated output files."""
    output_dir = Path(config.output_dir)

    # Merge function registries
    consolidated_registry = {"custom_functions": {}, "metadata": {}}

    for result in all_results:
        registry = result.get("function_registry", {})
        # Skip metadata when merging
        for func_id, func_data in registry.items():
            if func_id == "metadata":
                continue
            if func_id in consolidated_registry["custom_functions"]:
                # Merge questions list
                existing_questions = consolidated_registry["custom_functions"][func_id].get("questions", [])
                new_questions = func_data.get("questions", [])
                consolidated_registry["custom_functions"][func_id]["questions"] = list(set(existing_questions + new_questions))
            else:
                consolidated_registry["custom_functions"][func_id] = func_data

    consolidated_registry["metadata"] = {
        "total_custom_functions": len(consolidated_registry["custom_functions"]),
        "total_batches": len(all_results),
        "total_questions": total_questions
    }

    # Save consolidated registry
    registry_file = output_dir / "function_registry.json"
    with open(registry_file, "w") as f:
        json.dump(consolidated_registry, f, indent=2)
    print(f"\nConsolidated function registry saved: {registry_file}")

    # Merge question mappings
    all_mappings = []
    for result in all_results:
        all_mappings.extend(result.get("question_function_mapping", []))

    consolidated_mapping = {
        "mappings": all_mappings,
        "metadata": {
            "total_mappings": len(all_mappings),
            "total_batches": len(all_results),
            "total_questions": total_questions
        }
    }

    # Save consolidated mapping
    mapping_file = output_dir / "question_function_mapping.json"
    with open(mapping_file, "w") as f:
        json.dump(consolidated_mapping, f, indent=2)
    print(f"Consolidated question mapping saved: {mapping_file}")


def generate_summary_report(
    all_results: List[Dict[str, Any]],
    total_questions: int,
    config: FunctionPlannerConfig
) -> None:
    """Generate a summary report of all processing."""
    # Aggregate summary stats
    total_direct = 0
    total_parameterized = 0
    total_reuse = 0
    total_new = 0
    total_specific = 0

    for result in all_results:
        breakdown = result.get("summary", {}).get("breakdown", {})
        total_direct += breakdown.get("MCP_DIRECT", 0)
        total_parameterized += breakdown.get("MCP_PARAMETERIZED", 0)
        total_reuse += breakdown.get("CUSTOM_REUSE", 0)
        total_new += breakdown.get("CUSTOM_NEW", 0)
        total_specific += breakdown.get("CUSTOM_SPECIFIC", 0)

    # Count unique functions
    all_functions = set()
    for result in all_results:
        registry = result.get("function_registry", {})
        for func_id in registry.keys():
            if func_id != "metadata":
                all_functions.add(func_id)

    print(f"\n{'='*60}")
    print("FINAL SUMMARY REPORT")
    print(f"{'='*60}")
    print(f"Total questions processed: {total_questions}")
    print(f"Total batches processed: {len(all_results)}")
    print(f"Batch size: {config.batch_size}")
    print(f"\nMapping Type Breakdown:")
    print(f"  MCP_DIRECT: {total_direct} ({total_direct/total_questions*100:.1f}%)")
    print(f"  MCP_PARAMETERIZED: {total_parameterized} ({total_parameterized/total_questions*100:.1f}%)")
    print(f"  CUSTOM_REUSE: {total_reuse} ({total_reuse/total_questions*100:.1f}%)")
    print(f"  CUSTOM_NEW: {total_new} ({total_new/total_questions*100:.1f}%)")
    print(f"  CUSTOM_SPECIFIC: {total_specific} ({total_specific/total_questions*100:.1f}%)")
    print(f"\nUnique Custom Functions Created: {len(all_functions)}")
    if total_questions > 0:
        print(f"Reusability Rate: {total_reuse/total_questions*100:.1f}%")
        print(f"Average Questions per Function: {total_questions/len(all_functions):.1f}" if all_functions else "N/A")
    print(f"\nOutput Files:")
    print(f"  - all-questions/function_registry.json")
    print(f"  - all-questions/question_function_mapping.json")
    print(f"{'='*60}\n")


def main():
    """Main entry point."""
    config = parse_arguments()

    print(f"Function Planner Agent Runner")
    print(f"{'='*60}")
    print(f"Input file: {config.input_file}")
    print(f"Output directory: {config.output_dir}")
    print(f"Batch size: {config.batch_size}")
    print(f"Model: {config.model}")
    print(f"{'='*60}\n")

    try:
        # Load questions
        questions = load_questions(config)

        # Create batches
        batches = create_batches(questions, config.batch_size)

        # Process each batch
        all_results = []
        for i, batch in enumerate(batches):
            result = process_batch_with_api(batch, i, config)
            save_batch_result(batch, i, result, config)
            all_results.append(result)

        # Merge results
        merge_results(all_results, config, len(questions))

        # Generate summary report
        generate_summary_report(all_results, len(questions), config)

        print("Processing complete!")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()