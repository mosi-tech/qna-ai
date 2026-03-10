#!/usr/bin/env python3
"""
LLM-based Sequential UI Planner using ui-planner-with-blocks.md agent

Processes 1813 questions from consolidated_questions.json sequentially,
one question at a time, using the exact ui-planner-with-blocks agent specification.
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import requests

# Paths
PROJECT_ROOT = Path("/Users/shivc/Documents/Workspace/JS/qna-ai-admin")
INPUT_FILE = PROJECT_ROOT / "all-questions/consolidated_questions.json"
OUTPUT_DIR = PROJECT_ROOT / "all-questions"
FINAL_OUTPUT = OUTPUT_DIR / "sub_questions_with_blocks.json"
AGENT_FILE = PROJECT_ROOT / ".claude/agents/ui-planner-with-blocks.md"
BLOCK_CATALOG = PROJECT_ROOT / "frontend/apps/base-ui/src/blocks/BLOCK_CATALOG.json"

# Ollama configuration
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "https://ollama.com/api")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "glm-4.7:cloud")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")

# Rate limiting
DELAY_BETWEEN_REQUESTS = 2.0


def load_block_catalog() -> str:
    """Load BLOCK_CATALOG.json and return condensed representation"""
    with open(BLOCK_CATALOG) as f:
        catalog: Dict[str, Any] = json.load(f)

    lines: List[str] = []
    for category, blocks in catalog.get("categories", {}).items():
        lines.append(f"\n### {category}")
        for block in blocks:
            block_id = block.get("id", "?")
            lines.append(f"\n**{block_id}** (category: {category})")
            best_for = block.get("bestFor", [])
            if best_for:
                lines.append(f"  bestFor: {str(best_for[0])[:120]}")
                if len(best_for) > 1:
                    lines.append(f"          {str(best_for[1])[:120]}")
            avoid_when = block.get("avoidWhen", "")
            if avoid_when:
                lines.append(f"  avoidWhen: {str(avoid_when)[:120]}")
            data_shape = block.get("dataShape", "")
            if data_shape:
                lines.append(f"  dataShape: {str(data_shape)[:200]}")
    return "\n".join(lines)


def build_system_prompt() -> str:
    """
    Build the system prompt from ui-planner-with-blocks.md agent specification
    with BLOCK_CATALOG injected.
    """
    with open(AGENT_FILE) as f:
        agent_content = f.read()

    # Extract the agent instruction (everything after the frontmatter)
    # Skip the frontmatter (lines starting with ---)
    lines = agent_content.split('\n')
    in_frontmatter = False
    prompt_lines = []

    for line in lines:
        if line.strip() == '---':
            in_frontmatter = not in_frontmatter
            continue
        if not in_frontmatter:
            prompt_lines.append(line)

    agent_prompt = '\n'.join(prompt_lines)

    # Load and inject BLOCK_CATALOG
    block_catalog = load_block_catalog()

    # Replace placeholder if it exists, or append catalog
    if '{{BLOCK_CATALOG}}' in agent_prompt:
        agent_prompt = agent_prompt.replace('{{BLOCK_CATALOG}}', block_catalog)
    else:
        # Find where to insert catalog (after BLOCK_CATALOG Categories section)
        catalog_section = f"\n\n## BLOCK_CATALOG\n\n{block_catalog}\n"
        agent_prompt = agent_prompt.replace(
            "## BLOCK_CATALOG Categories",
            f"## BLOCK_CATALOG Categories{catalog_section}## Rules"
        )

    return agent_prompt


def load_questions() -> List[Dict[str, Any]]:
    """Load questions from consolidated_questions.json"""
    with open(INPUT_FILE) as f:
        data = json.load(f)
    return data.get("questions", [])


def call_ollama_api(question: str, system_prompt: str) -> str:
    """Call Ollama API to generate a dashboard plan for a question"""
    # Use /v1/messages endpoint for Ollama Cloud
    # OLLAMA_BASE_URL is https://ollama.com/api, so we need to use just /v1/messages
    url = "https://ollama.com/v1/messages"

    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json"
    }

    user_message = f"Process this question and generate a dashboard plan: {question}"

    payload = {
        "model": OLLAMA_MODEL,
        "max_tokens": 2000,
        "temperature": 0.1,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)

            if response.status_code == 200:
                data = response.json()
                # Ollama Cloud /v1/messages returns { "content": [{"text": "..."}] }
                content = ""
                if "content" in data and isinstance(data["content"], list):
                    for block in data["content"]:
                        if "text" in block:
                            content += block["text"]
                return content
            elif response.status_code == 429:
                wait_time = (attempt + 1) * 5
                print(f"  [Rate limited, waiting {wait_time}s...]")
                time.sleep(wait_time)
                continue
            else:
                print(f"  ERROR: API returned status {response.status_code}: {response.text[:200]}")
                raise Exception(f"API error: {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"  ERROR: Request timeout, retrying...")
            time.sleep(5)
            continue
        except Exception as e:
            print(f"  ERROR calling API: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(5)

    raise Exception("Max retries exceeded")


def parse_json_response(raw_response: str, question: str) -> dict:
    """Parse JSON response with fallback on error"""
    try:
        clean_response = raw_response.strip()
        if clean_response.startswith("```"):
            lines = clean_response.split("\n")
            if lines[0].startswith("```json"):
                clean_response = "\n".join(lines[1:-1])
            elif lines[0].startswith("```"):
                clean_response = "\n".join(lines[1:-1])

        dashboard_plan = json.loads(clean_response)
        return dashboard_plan
    except json.JSONDecodeError as e:
        print(f"  ERROR parsing JSON: {e}")
        print(f"  Raw response: {raw_response[:500]}")
        return {
            "title": "Dashboard",
            "subtitle": "Analysis dashboard",
            "layout": "grid",
            "blocks": [
                {
                    "blockId": "kpi-card-01",
                    "category": "kpi-cards",
                    "title": "Key Metrics",
                    "dataContract": {
                        "type": "kpi",
                        "description": "Summary metrics",
                        "points": 2
                    },
                    "sub_question": question,
                    "canonical_params": {"metric": "summary"}
                }
            ]
        }


def process_question(question_data: Dict[str, Any], index: int, system_prompt: str) -> Dict[str, Any]:
    """Process a single question and return the result"""
    question = question_data["question"]
    normalized_text = question_data.get("normalized_text", question.lower())
    metadata = question_data.get("metadata", {})

    print(f"[{index+1}/{total_questions}] {question[:50]}...")

    # Call Ollama API
    raw_response = call_ollama_api(question, system_prompt)

    # Parse JSON response
    dashboard_plan = parse_json_response(raw_response, question)

    return {
        "original_question": question,
        "normalized_text": normalized_text,
        "metadata": metadata,
        "question_index": index,
        "dashboard_plan": dashboard_plan
    }


def save_checkpoint(results: List[Dict[str, Any]], output_file: Path):
    """Save current results as a checkpoint"""
    checkpoint_output = {
        "total_questions": len(results),
        "generated_at": datetime.now().isoformat(),
        "results": results
    }
    with open(output_file, 'w') as f:
        json.dump(checkpoint_output, f, indent=2)


def main():
    """Main orchestrator"""
    # Load .env file from backend/apiServer
    env_file = PROJECT_ROOT / "backend/apiServer/.env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

    print(f"Using Ollama API:")
    print(f"  URL: {OLLAMA_BASE_URL}")
    print(f"  Model: {OLLAMA_MODEL}")

    print(f"\nBuilding system prompt from {AGENT_FILE}")
    system_prompt = build_system_prompt()
    print(f"System prompt loaded ({len(system_prompt)} chars)")

    print(f"\nLoading questions from {INPUT_FILE}")
    questions = load_questions()
    global total_questions
    total_questions = len(questions)
    print(f"Loaded {total_questions} questions")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Check for existing checkpoint
    results = []
    start_index = 0
    checkpoint_file = OUTPUT_DIR / "sub_questions_with_blocks_checkpoint.json"

    if checkpoint_file.exists():
        try:
            with open(checkpoint_file) as f:
                checkpoint = json.load(f)
                results = checkpoint.get("results", [])
                start_index = len(results)
                print(f"\nResuming from checkpoint: {len(results)} questions already processed")
        except Exception as e:
            print(f"Warning: Could not load checkpoint: {e}")

    print(f"\n=== Processing {len(questions) - start_index} remaining questions ===")
    print(f"Delay between requests: {DELAY_BETWEEN_REQUESTS}s\n")

    total_errors = 0

    for i in range(start_index, len(questions)):
        try:
            result = process_question(questions[i], i, system_prompt)
            results.append(result)

            # Save checkpoint every 5 questions
            if (i + 1) % 5 == 0:
                save_checkpoint(results, checkpoint_file)
                print(f"  [Checkpoint saved: {i+1}/{total_questions}]")

            # Rate limiting delay
            if i < len(questions) - 1:
                time.sleep(DELAY_BETWEEN_REQUESTS)

        except Exception as e:
            total_errors += 1
            print(f"  [FAILED] Error processing question {i}: {e}")
            # Add fallback result
            results.append({
                "original_question": questions[i]["question"],
                "normalized_text": questions[i].get("normalized_text", questions[i]["question"].lower()),
                "metadata": questions[i].get("metadata", {}),
                "question_index": i,
                "dashboard_plan": {
                    "title": "Dashboard",
                    "subtitle": "Analysis dashboard",
                    "layout": "grid",
                    "blocks": [
                        {
                            "blockId": "kpi-card-01",
                            "category": "kpi-cards",
                            "title": "Key Metrics",
                            "dataContract": {
                                "type": "kpi",
                                "description": "Summary metrics",
                                "points": 2
                            },
                            "sub_question": questions[i]["question"],
                            "canonical_params": {"metric": "summary"}
                        }
                    ]
                }
            })
            # Save checkpoint on error
            save_checkpoint(results, checkpoint_file)

    # Final save
    save_checkpoint(results, FINAL_OUTPUT)

    print(f"\n=== Processing Complete ===")
    print(f"- Total questions processed: {len(results)}/{total_questions}")
    print(f"- Total errors: {total_errors}")
    print(f"- Output file: {FINAL_OUTPUT}")


if __name__ == "__main__":
    main()