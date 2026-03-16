#!/usr/bin/env python3
"""
Run Single Agent - Generic Runner

Execute any headless agent in isolation for testing and development.

Usage:
    python run_single_agent.py ui_planner \
        --input '{"question": "Show QQQ ETF price"}' \
        --output output.json

    python run_single_agent.py ui_planner \
        --input-file input.json \
        --prompt-file shared/config/agents/ui_planner_v2.txt

    python run_single_agent.py code_generator \
        --question "Show QQQ price" \
        --model glm-4.7:cloud
"""

import os
import sys
import argparse
import json
import logging
from typing import Optional, Dict, Any

# Add parent directory to path for imports
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.normpath(os.path.join(_CURRENT_DIR, "..", ".."))
sys.path.insert(0, _BACKEND)

from agent_base import get_agent_class, AgentResult


def load_input(args) -> Dict[str, Any]:
    """Load input from various sources"""
    if args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif args.input:
        return json.loads(args.input)
    elif args.question:
        return {"question": args.question}
    else:
        raise ValueError("Must provide --input, --input-file, or --question")


def save_output(result: AgentResult, output_file: Optional[str]):
    """Save result to file"""
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"✅ Output saved to: {output_file}")
    else:
        print(json.dumps(result.to_dict(), indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Run a single headless agent in isolation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run UI planner with inline input
    python run_single_agent.py ui_planner --input '{"question": "Show QQQ price"}'

    # Run with input file
    python run_single_agent.py code_generator --input-file input.json

    # Run with question shorthand
    python run_single_agent.py ui_planner --question "Show my portfolio P&L"

    # Use custom prompt
    python run_single_agent.py ui_planner --question "Show QQQ" \\
        --prompt-file shared/config/agents/ui_planner_v2.txt

    # Specify model
    python run_single_agent.py code_generator --question "Show AAPL" \\
        --model gpt-4 --provider openai

    # Save output
    python run_single_agent.py ui_planner --question "Show QQQ" -o result.json

Available agents:
    ui_planner, question_enhancer, reuse_evaluator, code_generator,
    script_validator, verification, script_executor, result_formatter
        """
    )

    # Agent name
    parser.add_argument("agent", help="Name of the agent to run (e.g., ui_planner, code_generator)")

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--input", "-i", help="JSON string as input")
    input_group.add_argument("--input-file", help="JSON file with input data")
    input_group.add_argument("--question", "-q", help="Shorthand for question input (creates {\"question\": ...})")

    # Output
    parser.add_argument("--output", "-o", help="Save output to file")

    # LLM options
    parser.add_argument("--model", help="Override LLM model")
    parser.add_argument("--provider", help="Override LLM provider (ollama, openai, anthropic)")
    parser.add_argument("--prompt-file", help="Override prompt file")

    # Other options
    parser.add_argument("--timeout", type=int, default=60, help="Request timeout in seconds")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--metrics", action="store_true", help="Show metrics after execution")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be executed without running")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s:%(name)s:%(message)s'
    )

    # Load input
    try:
        input_data = load_input(args)
        print(f"📥 Input loaded: {json.dumps(input_data, indent=2)[:200]}...")
    except Exception as e:
        print(f"❌ Failed to load input: {e}")
        sys.exit(1)

    # Get agent class
    agent_class = get_agent_class(args.agent)
    if agent_class is None:
        print(f"❌ Agent not found: {args.agent}")
        print(f"   Available agents: ui_planner, question_enhancer, reuse_evaluator, code_generator, script_validator, verification, script_executor, result_formatter")
        sys.exit(1)

    # Show execution plan
    print(f"\n🎯 Agent: {args.agent}")
    print(f"   Model: {args.model or 'default'}")
    print(f"   Provider: {args.provider or 'default'}")
    print(f"   Prompt file: {args.prompt_file or 'default'}")
    print(f"   Timeout: {args.timeout}s\n")

    if args.dry_run:
        print("🔍 Dry run - would execute with above configuration")
        sys.exit(0)

    # Create agent instance
    try:
        # Build kwargs for agent initialization
        init_kwargs = {}
        if args.model:
            init_kwargs["llm_model"] = args.model
        if args.provider:
            init_kwargs["llm_provider"] = args.provider

        # Try to create agent
        agent = agent_class(**init_kwargs)

        # Override prompt file if specified
        if args.prompt_file:
            agent._load_prompt(args.prompt_file)

    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        sys.exit(1)

    # Execute agent
    result = agent.execute(input_data)

    # Print output
    if result.success:
        print(f"\n✅ Agent {args.agent} succeeded")
    else:
        print(f"\n❌ Agent {args.agent} failed")
        if result.error:
            print(f"   Error: {result.error}")

    # Print data
    if result.data is not None:
        print(f"\n📤 Output:")
        print(json.dumps(result.data, indent=2))

    # Save output
    save_output(result, args.output)

    # Show metrics
    if args.metrics:
        agent.print_metrics()

    # Exit with appropriate code
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()