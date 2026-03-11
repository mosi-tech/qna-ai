#!/usr/bin/env python3
"""
UI Planner Agent Runner

Runs the ui-planner-system agent on the consolidated questions file,
sending one question at a time to the LLM and generating dashboard structures.

Note: This script uses the Anthropic SDK for headless batch processing.
The Agent SDK (claude_agent_sdk) is designed for interactive sessions and
spawns CLI subprocesses, which is not suitable for batch processing.

Usage:
    python run_ui_planner_agent.py [options]

Options:
    --input PATH          Input JSON file with questions (default: all-questions/consolidated_questions.json)
    --output PATH         Output JSON file for results (default: all-questions/sub_questions_ui_planner_system.json)
    --start N            Start from question N (default: 1)
    --end N              End at question N (default: all)
    --agent-file PATH     Path to the ui-planner-system agent file
    --help               Show this help message

Environment Variables:
    ANTHROPIC_AUTH_TOKEN Anthropic API auth token (required)
    ANTHROPIC_BASE_URL   Custom API base URL (optional)
    MODEL                Claude model to use (default: glm-4.7:cloud)
"""

import json
import os
import sys
import argparse
import time
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


# Try to import Anthropic SDK for headless batch processing
# Note: The Agent SDK (claude_agent_sdk) is designed for interactive sessions
# and spawns CLI subprocesses. For headless batch processing, we use the
# Anthropic SDK directly which provides programmatic API access.
try:
    from anthropic import Anthropic
except ImportError:
    print("Error: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)


@dataclass
class UIPlannerConfig:
    """Configuration for the UI planner runner."""
    input_file: str = "all-questions/consolidated_questions.json"
    output_file: str = "all-questions/sub_questions_ui_planner_system.json"
    start_index: int = 1
    end_index: int = None  # None means process all
    agent_file: str = ".claude/agents/ui-planner-system.md"
    model: str = "glm-4.7:cloud"
    max_retries: int = 3
    retry_delay: float = 2.0
    max_tokens: int = 8192


def parse_arguments() -> UIPlannerConfig:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run ui-planner-system agent on consolidated questions using Agent SDK"
    )
    parser.add_argument(
        "--input",
        default="all-questions/consolidated_questions.json",
        help="Input JSON file with questions"
    )
    parser.add_argument(
        "--output",
        default="all-questions/sub_questions_ui_planner_system.json",
        help="Output JSON file for results"
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Start from question N (1-indexed)"
    )
    parser.add_argument(
        "--end",
        type=int,
        help="End at question N (1-indexed, inclusive)"
    )
    parser.add_argument(
        "--agent-file",
        default=".claude/agents/ui-planner-system.md",
        help="Path to the ui-planner-system agent file"
    )
    parser.add_argument(
        "--model",
        default=os.getenv("MODEL", "glm-4.7:cloud"),
        help="Claude model to use"
    )

    args = parser.parse_args()

    return UIPlannerConfig(
        input_file=args.input,
        output_file=args.output,
        start_index=args.start,
        end_index=args.end,
        agent_file=args.agent_file,
        model=args.model
    )


def load_questions(config: UIPlannerConfig) -> List[Dict[str, Any]]:
    """Load questions from the input file."""
    input_path = Path(config.input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {config.input_file}")

    with open(input_path, "r") as f:
        data = json.load(f)

    # Handle different input formats
    if isinstance(data, list):
        questions = [{"question_id": i + 1, **q} for i, q in enumerate(data)]
    elif isinstance(data, dict) and "questions" in data:
        questions = data["questions"]
        # Add question_id if not present
        for i, q in enumerate(questions):
            if "question_id" not in q:
                q["question_id"] = i + 1
    else:
        raise ValueError("Unexpected input format")

    # Apply start/end filters
    if config.start_index > 1:
        questions = [q for q in questions if q.get("question_id", 0) >= config.start_index]
    if config.end_index is not None:
        questions = [q for q in questions if q.get("question_id", 0) <= config.end_index]

    print(f"Loaded {len(questions)} questions from {config.input_file}")
    if config.start_index > 1 or config.end_index is not None:
        print(f"  Filtering: questions {config.start_index} to {config.end_index if config.end_index else 'end'}")

    return questions


def load_agent_prompt(config: UIPlannerConfig) -> str:
    """Load the agent prompt from the agent file."""
    agent_path = Path(config.agent_file)

    if not agent_path.exists():
        raise FileNotFoundError(f"Agent file not found: {config.agent_file}")

    with open(agent_path, "r") as f:
        return f.read()


def create_user_message(question: str, question_id: int) -> str:
    """Create the user message for a single question."""

    return f"""Question #{question_id}:

"{question}"

Return ONLY valid JSON for the dashboard structure with 3-6 blocks using block categories from BLOCK_CATALOG: kpi-cards, bar-charts, bar-lists, donut-charts, line-charts, status-monitoring, tables, spark-charts, treemaps, heatmaps.

Output schema:
{{
  "title": "Dashboard title (5–8 words)",
  "subtitle": "One-sentence description",
  "layout": "grid",
  "blocks": [
    {{
      "blockId": "kpi-card-01",
      "category": "kpi-cards",
      "title": "Concise Title",
      "dataContract": {{
        "type": "kpi",
        "description": "Brief description",
        "points": 4
      }},
      "sub_question": "What is the specific metric or data?",
      "output_format": {{
        "type": "kpi",
        "fields": ["metric1", "metric2", "metric3"]
      }},
      "canonical_params": {{"ticker": "ABC", "metric": "metric_name"}}
    }}
  ]
}}

Requirements:
- Select 3–6 blocks total. ALWAYS start with at least one kpi-cards block
- sub_question: Specific, self-contained question. This is what gets cached in vector DB.
- output_format: Tells query solver what format to return (kpi, table, timeseries, bar, pie, bar_list)
  - For kpi-cards: use {{"type": "kpi", "fields": ["metric1", "metric2"]}}
  - For tables: use {{"type": "table", "columns": ["col1", "col2"]}}
  - For charts: use {{"type": "timeseries"/"bar"/"pie", "x_field": "x", "y_field": "y"}}
- canonical_params: Use only these keys: ticker, tickers, metric, period, benchmark, strategy, sector, exchange, threshold
- Choose blocks suited to the question. Prefer variety: at minimum use 1 kpi-cards block and 1 chart block

DO NOT include any markdown code blocks or backticks. Return ONLY the JSON object.
"""


def process_question_with_api(
    question: str,
    question_id: int,
    config: UIPlannerConfig,
    agent_prompt: str
) -> Dict[str, Any]:
    """Process a single question using the Anthropic API."""
    # Create user message
    user_message = create_user_message(question, question_id)

    # Get API auth token
    api_key = os.getenv("ANTHROPIC_AUTH_TOKEN") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY environment variable not set")

    # Create Anthropic client with optional custom base URL
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    if base_url and "ollama.com" in base_url:
        # Use httpx for custom auth header
        import httpx
        client = Anthropic(
            api_key=api_key,
            base_url=base_url,
            http_client=httpx.Client(
                headers={"Authorization": f"Bearer {api_key}"},
                verify=False
            )
        )
    elif base_url:
        client = Anthropic(api_key=api_key, base_url=base_url)
    else:
        client = Anthropic(api_key=api_key)

    # Retry logic
    for attempt in range(config.max_retries):
        try:
            # Call the API
            response = client.messages.create(
                model=config.model,
                max_tokens=8192,
                temperature=0,
                system=agent_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # Extract the response text
            response_text = None
            for content_block in response.content:
                if hasattr(content_block, 'type') and content_block.type == 'text':
                    response_text = content_block.text
                    break

            if not response_text:
                raise ValueError("No text block found in response")

            # Parse JSON from response
            json_pattern = r'\{[\s\S]*\}'
            json_matches = re.findall(json_pattern, response_text)

            if json_matches:
                result_data = json.loads(max(json_matches, key=len))
                return result_data
            else:
                raise ValueError("Could not find JSON in agent response")

        except Exception as e:
            if attempt < config.max_retries - 1:
                print(f"  Attempt {attempt + 1} failed: {e}, retrying in {config.retry_delay}s...")
                time.sleep(config.retry_delay)
            else:
                print(f"  Error processing question #{question_id}: {type(e).__name__}: {e}")
                # Return minimal structure on error
                return {
                    "question_id": question_id,
                    "original_question": question,
                    "title": "Error Processing Question",
                    "subtitle": "Unable to generate dashboard structure",
                    "layout": "grid",
                    "blocks": [],
                    "error": str(e)
                }


def save_checkpoint(
    results: List[Dict[str, Any]],
    config: UIPlannerConfig,
    checkpoint_num: int = None
) -> None:
    """Save results to file (with optional checkpoint number)."""
    output_dir = Path(config.output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = Path(config.output_file)
    if checkpoint_num is not None:
        base_name = output_file.stem
        checkpoint_file = output_dir / f"{base_name}_checkpoint_{checkpoint_num}.json"
    else:
        checkpoint_file = output_file

    with open(checkpoint_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"  Saved: {checkpoint_file} ({len(results)} results)")


def generate_summary_report(
    results: List[Dict[str, Any]],
    config: UIPlannerConfig,
    start_time: float
) -> None:
    """Generate a summary report of all processing."""
    elapsed_time = time.time() - start_time

    # Count successful vs failed
    successful = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]

    # Count blocks per question
    total_blocks = sum(len(r.get("blocks", [])) for r in results)
    avg_blocks = total_blocks / len(results) if results else 0

    # Count block categories
    category_counts = {}
    for result in successful:
        for block in result.get("blocks", []):
            category = block.get("category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1

    print(f"\n{'='*60}")
    print("UI PLANNER AGENT - SUMMARY REPORT")
    print(f"{'='*60}")
    print(f"Total questions processed: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Success rate: {len(successful)/len(results)*100:.1f}%")
    print(f"\nElapsed time: {elapsed_time:.1f}s ({elapsed_time/60:.1f} minutes)")
    print(f"Average time per question: {elapsed_time/len(results):.2f}s")
    print(f"\nBlocks generated:")
    print(f"  Total: {total_blocks}")
    print(f"  Average per question: {avg_blocks:.1f}")
    print(f"\nBlock category distribution:")
    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {category}: {count}")
    print(f"\nOutput file: {config.output_file}")
    print(f"{'='*60}\n")


def main():
    """Main entry point."""
    config = parse_arguments()

    print(f"UI Planner Agent Runner")
    print(f"{'='*60}")
    print(f"Input file: {config.input_file}")
    print(f"Output file: {config.output_file}")
    print(f"Model: {config.model}")
    print(f"{'='*60}\n")

    start_time = time.time()

    try:
        # Load questions
        questions = load_questions(config)

        # Load agent prompt
        agent_prompt = load_agent_prompt(config)
        print(f"Loaded agent prompt from {config.agent_file}\n")

        # Process each question
        results = []
        total = len(questions)

        for i, question_obj in enumerate(questions):
            question_id = question_obj.get("question_id", i + 1)
            question_text = question_obj.get("question", "")

            print(f"Processing question {question_id}/{total} ({i+1}/{len(questions)}): {question_text[:60]}...")

            # Process question
            result = process_question_with_api(question_text, question_id, config, agent_prompt)

            # Add question metadata to result
            result["question_id"] = question_id
            result["original_question"] = question_text
            if "metadata" in question_obj:
                result["metadata"] = question_obj["metadata"]

            results.append(result)

            # Save checkpoint every 10 questions
            if (i + 1) % 10 == 0:
                save_checkpoint(results, config, checkpoint_num=i + 1)

        # Save final results
        save_checkpoint(results, config)

        # Generate summary report
        generate_summary_report(results, config, start_time)

        print("Processing complete!")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()