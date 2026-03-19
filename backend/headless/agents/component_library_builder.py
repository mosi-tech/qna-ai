#!/usr/bin/env python3
"""
Component Library Builder

Builds a library of reusable financial data components by analyzing questions.

Usage:
    python3 component_library_builder.py

Input:
    all-questions/consolidated_questions.json

Output:
    headless/output/component_library.json
"""

import argparse
import json
import logging
import os
import sys
import random
from typing import Dict, Any, List, Tuple
from datetime import datetime
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_base import AgentBase, AgentResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComponentLibraryBuilder(AgentBase):
    """Agent that builds a component library from questions"""

    def __init__(
        self,
        prompt_file: str = "../../shared/config/agents/component_library_builder.txt",
        llm_model: str = "glm-4.7:cloud",  # Use fast model for this task
        llm_provider: str = "ollama"
    ):
        super().__init__(
            name="component_library_builder",
            task="COMPONENT_LIBRARY",  # Can use default model config
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "existing_library": {"type": "array"}
            },
            "required": ["question"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "components": {"type": "array"}
            },
            "required": ["components"]
        }

    def _compute_embedding(self, text: str) -> np.ndarray:
        """Compute embedding for text using Ollama embeddings"""
        import requests

        # Get API key from environment
        api_key = os.environ.get("OLLAMA_API_KEY") or os.environ.get("ANALYSIS_LLM_API_KEY")

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.post(
            "https://ollama.com/api/embeddings",
            json={
                "model": "qwen3-embedding:8b",
                "input": text
            },
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        embedding = response.json().get("embeddings", [[]])[0]
        return np.array(embedding)

    def _find_similar_components(
        self,
        question: str,
        library: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Find most similar components in library to the question"""
        if not library:
            return []

        # Compute question embedding
        question_emb = self._compute_embedding(question)

        # Compute embeddings for all components
        # For efficiency, cache these in production
        library_embeddings = []
        for comp in library:
            # Combine name, description, usage for better matching
            text = f"{comp.get('name', '')} {comp.get('description', '')} {comp.get('usage', '')}"
            emb = self._compute_embedding(text)
            library_embeddings.append(emb)

        library_embeddings = np.array(library_embeddings)

        # Compute cosine similarity
        similarities = np.dot(library_embeddings, question_emb) / (
            np.linalg.norm(library_embeddings, axis=1) * np.linalg.norm(question_emb)
        )

        # Get top-k indices
        top_indices = similarities.argsort()[-top_k:][::-1]

        # Return similar components (full details, simplified for prompt)
        similar_components = []
        for idx in top_indices:
            comp = library[idx]
            similar_components.append({
                "name": comp.get("name"),
                "description": comp.get("description"),
                "usage": comp.get("usage"),
                "similarity": float(similarities[idx])
            })

        self.logger.info(f"Found {len(similar_components)} similar components (threshold > 0.3)")
        return [c for c in similar_components if c["similarity"] > 0.3]

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Process a question and extract new components"""
        question = input_data.get("question", "")
        existing_library = input_data.get("existing_library", [])

        if not question:
            return AgentResult(success=False, error="Question is required")

        # Find similar components
        similar_components = self._find_similar_components(question, existing_library, top_k=10)

        # Format similar components for prompt (prominent section)
        similar_json = json.dumps(similar_components, indent=2)

        # Sample of full library for context (abbreviated to save tokens)
        # Limit to 50 random components to give broad context
        sample_size = min(50, len(existing_library))
        sample_indices = random.sample(range(len(existing_library)), sample_size) if len(existing_library) > sample_size else range(sample_size)
        library_sample = [
            {
                "name": existing_library[i].get("name"),
                "description": existing_library[i].get("description"),
                "usage": existing_library[i].get("usage")
            }
            for i in sample_indices
        ]
        library_sample_json = json.dumps(library_sample, indent=2)

        # Build user message with new format
        user_message = f"""SIMILAR EXISTING COMPONENTS:
{similar_json}

CURRENT LIBRARY (sample of {sample_size} components):
{library_sample_json}

USER QUESTION:
{question}

TASK:
What NEW components would help answer this question?
First, carefully review the SIMILAR EXISTING COMPONENTS - can any of them answer this question?
Only create new components if similar components cannot satisfy the need.
Return 1-4 components in JSON array format (or empty array [] if none needed).
"""

        try:
            # Make LLM request (no tools needed)
            response = self._make_llm_request(
                messages=[{"role": "user", "content": user_message}],
                tools=None  # No tools needed for this task
            )

            content = response.get("content", "").strip()

            # Parse JSON response
            components = self._safe_parse_json(content)

            if not isinstance(components, list):
                return AgentResult(success=False, error=f"Expected array of components, got {type(components)}")

            # Empty array is valid (means no new components needed)
            if len(components) == 0:
                self.logger.info(f"✅ No new components needed for: {question[:60]}...")
            else:
                self.logger.info(f"✅ Extracted {len(components)} new components from: {question[:60]}...")

            return AgentResult(success=True, data={"components": components})

        except Exception as e:
            self.logger.error(f"❌ Failed to extract components: {e}")
            return AgentResult(success=False, error=str(e))


def load_questions(questions_path: str) -> List[str]:
    """Load questions from consolidated questions file"""
    with open(questions_path, 'r') as f:
        data = json.load(f)

    # The consolidated_questions.json format has a 'questions' key
    questions = data.get('questions', [])

    # Extract question strings
    result = []
    for item in questions:
        if isinstance(item, dict):
            # Format: {"question": "...", "normalized_text": "...", "metadata": {...}}
            q = item.get("question")
            if q:
                result.append(q)
        elif isinstance(item, str):
            result.append(item)

    return result


def load_library(library_path: str) -> List[Dict[str, Any]]:
    """Load existing component library"""
    if not os.path.exists(library_path):
        return []

    with open(library_path, 'r') as f:
        return json.load(f)


def save_library(library: List[Dict[str, Any]], library_path: str):
    """Save component library to file"""
    with open(library_path, 'w') as f:
        json.dump(library, f, indent=2)


def deduplicate_components(components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate components based on name"""
    seen_names = set()
    deduplicated = []

    for comp in components:
        name = comp.get("name", "").lower()
        if name not in seen_names:
            seen_names.add(name)
            deduplicated.append(comp)

    return deduplicated


def main():
    parser = argparse.ArgumentParser(
        description="Build a library of reusable financial data components"
    )
    parser.add_argument(
        "--questions",
        default="/Users/shivc/Documents/Workspace/JS/qna-ai-admin/all-questions/consolidated_questions.json",
        help="Path to questions file"
    )
    parser.add_argument(
        "--output",
        default="output/component_library.json",
        help="Output path for component library (relative to backend/headless)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing library instead of starting fresh"
    )
    parser.add_argument(
        "--max-questions",
        type=int,
        help="Maximum number of questions to process (for testing)"
    )
    parser.add_argument(
        "--start-at",
        type=int,
        default=0,
        help="Start processing from this question index (for resuming)"
    )

    args = parser.parse_args()

    # Resolve paths
    script_dir = os.path.dirname(os.path.abspath(__file__))  # .../backend/headless/agents
    headless_dir = os.path.dirname(script_dir)  # .../backend/headless
    output_path = os.path.join(headless_dir, args.output)  # .../backend/headless/output/component_library.json

    # Resolve questions path (relative to backend directory)
    backend_dir = os.path.dirname(headless_dir)  # .../backend
    questions_path = os.path.abspath(os.path.join(backend_dir, args.questions.replace("backend/", "")))

    # Load questions
    logger.info(f"Loading questions from: {questions_path}")
    questions = load_questions(questions_path)
    logger.info(f"Loaded {len(questions)} questions")

    # Load or initialize library
    if args.resume:
        library = load_library(output_path)
        logger.info(f"Resumed with {len(library)} existing components")
    else:
        library = []
        logger.info("Starting with empty library")

    # Create builder agent
    builder = ComponentLibraryBuilder()

    # Process questions
    total_questions = len(questions)
    start_index = args.start_at
    max_index = len(questions) if args.max_questions is None else start_index + args.max_questions

    logger.info(f"\nProcessing questions {start_index} to {max_index - 1}...")

    for i in range(start_index, min(max_index, total_questions)):
        question = questions[i]

        if not question:
            continue

        # Format existing library for prompt
        existing_json = json.dumps(library, indent=2)

        # Call agent
        result = builder.execute({
            "question": question,
            "existing_library": library
        })

        if result.success:
            new_components = result.data.get("components", [])

            if new_components:
                # Add to library
                library.extend(new_components)
                # Deduplicate
                library = deduplicate_components(library)
                # Save progress
                save_library(library, output_path)
                logger.info(f"  [{i+1}/{total_questions}] Added {len(new_components)} components. Total: {len(library)}")
            else:
                logger.info(f"  [{i+1}/{total_questions}] No new components")
        else:
            logger.error(f"  [{i+1}/{total_questions}] Failed: {result.error}")

    # Final save
    save_library(library, output_path)

    logger.info(f"\n✅ Complete! Built library with {len(library)} components")
    logger.info(f"Saved to: {output_path}")

    # Print summary
    print("\n=== COMPONENT LIBRARY SUMMARY ===")
    for comp in library:
        print(f"\n• {comp.get('name')}")
        print(f"  {comp.get('description')}")


if __name__ == "__main__":
    main()