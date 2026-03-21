#!/usr/bin/env python3
"""
Question Decomposer Agent

Recursively breaks down financial questions into atomic sub-questions that map
to individual utility functions. Identifies existing utilities and flags needed ones.

Usage:
    python3 question_decomposer.py --questions path/to/questions.json --output output/utility_library.json

Input:
    all-questions/consolidated_questions.json

Output:
    headless/output/question_decompositions.json - decomposition tree for each question
    headless/output/utility_library.json - aggregated utility requirements
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_base import AgentBase, AgentResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuestionDecomposer(AgentBase):
    """Agent that recursively decomposes questions into utility-sized chunks"""

    def __init__(
        self,
        prompt_file: str = "../../../shared/config/agents/question_decomposer.txt",
        llm_model: str = "glm-4.7:cloud",
        llm_provider: str = "ollama",
        utility_library: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(
            name="question_decomposer",
            task="QUESTION_DECOMPOSER",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )
        self.utility_library = utility_library or []

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "utility_library": {"type": "array", "default": []}
            },
            "required": ["question"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "decomposition": {"type": "object"},
                "utilities_found": {"type": "array"},
                "utilities_needed": {"type": "array"}
            },
            "required": ["decomposition"]
        }

    def set_utility_library(self, utilities: List[Dict[str, Any]]):
        """Set the library of existing utilities"""
        self.utility_library = utilities
        self.logger.info(f"📚 Loaded utility library with {len(utilities)} utilities")

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Decompose a single question"""
        question = input_data.get("question", "").strip()

        if not question:
            return AgentResult(success=False, error="Question is required")

        try:
            # Format utility library for prompt
            utilities_json = json.dumps(
                [{"name": u.get("name"), "description": u.get("description", "")}
                 for u in self.utility_library],
                indent=2
            )

            # Update system prompt with utilities
            system_prompt = self.system_prompt.replace(
                "{EXISTING_UTILITIES_JSON}",
                utilities_json
            )

            # Build user message
            user_message = f"Decompose this question into atomic sub-questions that map to utilities:\n\n{question}"

            # Make LLM request
            response = self._make_llm_request(
                messages=[{"role": "user", "content": user_message}],
                system_prompt=system_prompt,
                tools=None
            )

            self.logger.debug(f"Response: {response}")

            # Handle response structure
            if response is None:
                return AgentResult(success=False, error="LLM returned None")

            if response.get("success") is False:
                return AgentResult(success=False, error=f"LLM error: {response.get('error', 'Unknown error')}")

            # Extract content - handle different response formats
            if isinstance(response.get("data"), dict):
                content = response["data"].get("content", "") or response["data"].get("text", "")
            elif isinstance(response.get("data"), str):
                content = response.get("data", "")
            else:
                content = response.get("content", "") or response.get("text", "")

            if not content:
                self.logger.error(f"No content in response: {response}")
                return AgentResult(success=False, error=f"No content in LLM response: {json.dumps(response)}")

            content = content.strip()
            decomposition = self._safe_parse_json(content)

            if not isinstance(decomposition, dict):
                return AgentResult(
                    success=False,
                    error=f"Expected decomposition object, got {type(decomposition)}"
                )

            # Extract utilities found and needed
            utilities_found, utilities_needed = self._extract_utilities(decomposition)

            self.logger.info(
                f"✅ Decomposed: {question[:60]}... "
                f"({len(utilities_found)} found, {len(utilities_needed)} needed)"
            )

            return AgentResult(
                success=True,
                data={
                    "question": question,
                    "decomposition": decomposition,
                    "utilities_found": utilities_found,
                    "utilities_needed": utilities_needed
                }
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to decompose question: {e}")
            return AgentResult(success=False, error=str(e))

    def _extract_utilities(self, node: Dict[str, Any]) -> tuple:
        """Recursively extract utilities from decomposition tree"""
        utilities_found = []
        utilities_needed = []

        if node.get("is_leaf"):
            utility = node.get("utility_needed", {})
            if utility:
                extracted_util = {
                    "name": utility.get("name"),
                    "description": utility.get("description", "")
                }
                # Preserve sub_utilities from LLM if provided
                if "sub_utilities" in utility:
                    extracted_util["sub_utilities"] = utility.get("sub_utilities", [])

                if utility.get("existing"):
                    utilities_found.append(extracted_util)
                else:
                    utilities_needed.append(extracted_util)

        # Recurse into sub-questions
        for sub_q in node.get("sub_questions", []):
            found, needed = self._extract_utilities(sub_q)
            utilities_found.extend(found)
            utilities_needed.extend(needed)

        return utilities_found, utilities_needed

    def _extract_conceptual_sub_utilities(self, node: Dict[str, Any]) -> List[str]:
        """
        Extract all conceptual sub-utilities from a decomposition tree.
        This captures what atomic utilities were identified during decomposition,
        even if they were consolidated into a broader utility.
        Returns list of utility names (both found and needed).
        """
        sub_utilities = []

        if node.get("is_leaf"):
            utility = node.get("utility_needed", {})
            if utility:
                sub_utilities.append(utility.get("name"))

        # Recurse into sub-questions
        for sub_q in node.get("sub_questions", []):
            sub_utilities.extend(self._extract_conceptual_sub_utilities(sub_q))

        return sub_utilities

    def _consolidate_utility(self, new_utility: Dict[str, Any], existing_utilities: List[Dict[str, Any]]) -> tuple:
        """
        Check if a new utility can be consolidated with existing ones.
        Returns tuple: (consolidated_utility_or_new, consolidated_into_name_or_none)
        consolidated_into_name will be the name of the existing utility it was merged into, if any.
        """
        new_name = new_utility.get("name", "").lower()
        new_desc = new_utility.get("description", "").lower()

        # Keywords that indicate a utility can be derived from a broader one
        derivative_patterns = {
            "largest": "positions",
            "smallest": "positions",
            "highest": "positions",
            "lowest": "positions",
            "best": "positions",
            "worst": "positions",
            "long": "positions",
            "short": "positions",
            "gained": "positions",
            "lost": "positions",
            "stop": "orders",
            "bracket": "orders",
            "day order": "orders",
        }

        # Check if new utility matches derivative patterns
        for pattern, family in derivative_patterns.items():
            if pattern in new_name or pattern in new_desc:
                # Find if a broad family utility exists
                for existing in existing_utilities:
                    existing_name = existing.get("name", "").lower()
                    if family in existing_name:
                        self.logger.info(
                            f"  🔄 Consolidation: '{new_name}' is derivable from '{existing_name}' "
                            f"(pattern: {pattern})"
                        )
                        return None, existing_name  # Don't add as separate utility, but track it

        # Check for semantic similarity with existing utilities
        for existing in existing_utilities:
            existing_name = existing.get("name", "").lower()
            existing_desc = existing.get("description", "").lower()

            # Simple overlap check: if names/descriptions share key terms
            new_terms = set(new_name.split("_"))
            existing_terms = set(existing_name.split("_"))

            overlap = new_terms & existing_terms
            if len(overlap) >= 2:  # Significant overlap
                self.logger.info(
                    f"  🔄 Consolidation: '{new_name}' overlaps with '{existing_name}' "
                    f"(shared terms: {overlap})"
                )
                return None, existing_name  # Flag for consolidation, track the existing utility

        # No consolidation needed - this is a truly new utility
        return new_utility, None


def load_questions(questions_path: str) -> List[str]:
    """Load questions from consolidated questions file"""
    try:
        with open(questions_path, 'r') as f:
            data = json.load(f)

        questions = data.get('questions', [])

        # Extract question strings
        result = []
        for item in questions:
            if isinstance(item, dict):
                q = item.get("question")
                if q:
                    result.append(q.strip())
            elif isinstance(item, str):
                result.append(item.strip())

        # Remove duplicates while preserving order
        seen = set()
        unique_questions = []
        for q in result:
            if q and q not in seen:
                seen.add(q)
                unique_questions.append(q)

        return unique_questions
    except Exception as e:
        logger.error(f"❌ Failed to load questions: {e}")
        return []


def load_utility_library(library_path: str) -> List[Dict[str, Any]]:
    """Load existing utility library"""
    if not os.path.exists(library_path):
        return []

    try:
        with open(library_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to load utility library: {e}")
        return []


def save_decompositions(decompositions: List[Dict[str, Any]], output_path: str):
    """Save decompositions to file"""
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(decompositions, f, indent=2)

    logger.info(f"💾 Saved {len(decompositions)} decompositions to {output_path}")


def aggregate_utilities(decompositions: List[Dict[str, Any]], utility_library: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate all utilities from decompositions and final library"""
    all_discovered = {}  # name -> description

    for item in decompositions:
        for utility in item.get("utilities_needed", []):
            name = utility.get("name")
            if name:
                all_discovered[name] = utility.get("description", "")

    # utilities in the final library
    utilities_in_library = [u.get("name") for u in utility_library if u.get("name")]

    # utilities consolidated as sub_utilities (discovered but not in final library)
    utilities_consolidated = [u for u in all_discovered.keys() if u not in utilities_in_library]

    return {
        "summary": {
            "total_decompositions": len(decompositions),
            "utilities_in_final_library": len(utilities_in_library),
            "utilities_discovered_as_new": len(all_discovered),
            "utilities_consolidated_as_sub": len(utilities_consolidated)
        },
        "utilities_in_final_library": sorted(utilities_in_library),
        "utilities_discovered_as_new": [
            {"name": name, "description": desc}
            for name, desc in sorted(all_discovered.items())
        ],
        "utilities_consolidated_as_sub": sorted(utilities_consolidated)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Decompose questions into atomic utilities"
    )
    parser.add_argument(
        "--questions",
        default="all-questions/consolidated_questions_prioritized.json",
        help="Path to questions file"
    )
    parser.add_argument(
        "--output",
        default="output/question_decompositions.json",
        help="Output path for decompositions (relative to backend/headless)"
    )
    parser.add_argument(
        "--utility-lib",
        default="output/utility_library.json",
        help="Path to existing utility library (relative to backend/headless)"
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
        help="Start processing from this question index"
    )

    args = parser.parse_args()

    # Resolve paths
    script_dir = os.path.dirname(os.path.abspath(__file__))  # .../backend/headless/agents
    headless_dir = os.path.dirname(script_dir)  # .../backend/headless
    backend_dir = os.path.dirname(headless_dir)  # .../backend
    project_root = os.path.dirname(backend_dir)  # .../qna-ai-admin

    output_path = os.path.join(headless_dir, args.output)
    utility_lib_path = os.path.join(headless_dir, args.utility_lib)
    final_lib_path = output_path.replace("decompositions.json", "utility_library_final.json")

    # Resolve questions path (relative to project root)
    questions_path = os.path.join(project_root, args.questions)

    # Load questions
    logger.info(f"📖 Loading questions from: {questions_path}")
    questions = load_questions(questions_path)
    logger.info(f"✅ Loaded {len(questions)} questions")

    if not questions:
        logger.error("❌ No questions loaded. Exiting.")
        sys.exit(1)

    # Load existing utility library (prefer final consolidated version if available)
    if os.path.exists(final_lib_path):
        logger.info(f"📚 Loading utility library from: {final_lib_path}")
        utility_library = load_utility_library(final_lib_path)
    else:
        logger.info(f"📚 Loading utility library from: {utility_lib_path}")
        utility_library = load_utility_library(utility_lib_path)
    logger.info(f"✅ Loaded {len(utility_library)} existing utilities")

    # Initialize decomposer
    decomposer = QuestionDecomposer()

    # Process questions - ITERATIVELY UPDATE UTILITY LIBRARY
    # Load existing decompositions if resuming (for aggregation)
    output_path = os.path.join(headless_dir, args.output)
    aggregation_path = output_path.replace("decompositions.json", "utility_requirements.json")

    if os.path.exists(output_path) and args.start_at > 0:
        try:
            with open(output_path, 'r') as f:
                decompositions = json.load(f)
            logger.info(f"📂 Loaded {len(decompositions)} existing decompositions for aggregation")
        except Exception as e:
            logger.warning(f"⚠️ Could not load existing decompositions: {e}")
            decompositions = []
    else:
        decompositions = []

    start_idx = args.start_at
    end_idx = len(questions)

    if args.max_questions:
        end_idx = min(start_idx + args.max_questions, len(questions))

    total = end_idx - start_idx

    for idx in range(start_idx, end_idx):
        question = questions[idx]
        progress = idx - start_idx + 1

        logger.info(f"\n[{progress}/{total}] Decomposing: {question[:70]}... (Library: {len(utility_library)} utilities)")

        # Update decomposer with current utility library
        decomposer.set_utility_library(utility_library)

        result = decomposer.process({
            "question": question,
            "utility_library": utility_library
        })

        if result.success:
            decompositions.append(result.data)

            # Extract all conceptual sub-utilities from the decomposition tree
            decomposition = result.data.get("decomposition", {})
            conceptual_subs = decomposer._extract_conceptual_sub_utilities(decomposition)

            # ✨ KEY: Add newly identified utilities to library for next question
            utilities_needed = result.data.get("utilities_needed", [])
            for util in utilities_needed:
                # Check if utility already exists
                existing_util = next(
                    (u for u in utility_library if u.get("name") == util.get("name")),
                    None
                )
                if existing_util:
                    # Update sub_utilities if the new utility provides additional ones
                    if "sub_utilities" in util and util.get("sub_utilities"):
                        if "sub_utilities" not in existing_util:
                            existing_util["sub_utilities"] = []
                        # Add any new sub_utilities that aren't already there
                        for sub in util.get("sub_utilities", []):
                            if sub not in existing_util["sub_utilities"]:
                                existing_util["sub_utilities"].append(sub)
                    continue

                # 🔄 CONSOLIDATION: Check if this utility can be derived from existing ones
                new_util, consolidated_into = decomposer._consolidate_utility(util, utility_library)

                if consolidated_into:
                    # Utility was consolidated - add to sub_utilities of existing utility
                    target_util = next(
                        (u for u in utility_library if u.get("name").lower() == consolidated_into.lower()),
                        None
                    )
                    if target_util:
                        if "sub_utilities" not in target_util:
                            target_util["sub_utilities"] = []
                        target_util["sub_utilities"].append(util.get("name"))
                        logger.info(f"  ⊘ Skipped (consolidated into '{consolidated_into}'): {util.get('name')}")
                else:
                    # Truly new utility - add to library
                    # Preserve sub_utilities from LLM (don't overwrite with conceptual_subs)
                    # The LLM provides the actual data fields, conceptual_subs is for consolidation tracking
                    utility_library.append(new_util)
                    logger.info(f"  ✨ Added utility: {new_util.get('name')}")

            # Show reuse stats and attach conceptual sub-utilities to existing utilities
            utilities_found = result.data.get("utilities_found", [])
            if utilities_found:
                logger.info(f"  ♻️  Reused {len(utilities_found)} utilities")
                # Attach sub-utilities to existing utilities
                for found_util in utilities_found:
                    found_util_name = found_util.get("name") if isinstance(found_util, dict) else found_util
                    target = next(
                        (u for u in utility_library if u.get("name") == found_util_name),
                        None
                    )
                    if target:
                        # Update with sub_utilities from LLM response (actual data fields)
                        if isinstance(found_util, dict) and "sub_utilities" in found_util:
                            if "sub_utilities" not in target:
                                target["sub_utilities"] = []
                            for sub in found_util.get("sub_utilities", []):
                                if sub not in target["sub_utilities"]:
                                    target["sub_utilities"].append(sub)
                        # Also attach conceptual sub-utilities (avoid duplicates)
                        if conceptual_subs:
                            if "sub_utilities" not in target:
                                target["sub_utilities"] = []
                            for sub in conceptual_subs:
                                if sub not in target["sub_utilities"] and sub != found_util_name:
                                    target["sub_utilities"].append(sub)

            # 💾 SAVE LIBRARY AFTER EACH QUESTION (checkpoint)
            final_lib_path = output_path.replace("decompositions.json", "utility_library_final.json")
            with open(final_lib_path, 'w') as f:
                json.dump(utility_library, f, indent=2)
            logger.info(f"  💾 Saved library checkpoint ({len(utility_library)} utilities total)")

            # 💾 SAVE AGGREGATION AFTER EACH QUESTION (checkpoint)
            current_aggregation = aggregate_utilities(decompositions, utility_library)
            with open(aggregation_path, 'w') as f:
                json.dump(current_aggregation, f, indent=2)
            logger.info(f"  💾 Saved aggregation checkpoint ({current_aggregation['summary']['utilities_in_final_library']} in library, {current_aggregation['summary']['utilities_consolidated_as_sub']} consolidated)")
        else:
            logger.warning(f"⚠️ Failed: {result.error}")

    # Save decompositions
    logger.info(f"\n📊 Saving results...")
    save_decompositions(decompositions, output_path)

    # Aggregate utilities
    aggregation = aggregate_utilities(decompositions, utility_library)

    with open(aggregation_path, 'w') as f:
        json.dump(aggregation, f, indent=2)

    logger.info(f"📊 Saved aggregation to {aggregation_path}")

    # Note: Final utility library is saved after each question (see loop above)
    final_lib_path = output_path.replace("decompositions.json", "utility_library_final.json")
    logger.info(f"📚 Final utility library saved at: {final_lib_path}")

    # Print summary
    print("\n" + "="*60)
    print("DECOMPOSITION SUMMARY (ITERATIVE)")
    print("="*60)
    print(f"Questions processed: {len(decompositions)}")
    print(f"Utilities in final library: {aggregation['summary']['utilities_in_final_library']}")
    print(f"Utilities discovered as new: {aggregation['summary']['utilities_discovered_as_new']}")
    print(f"Utilities consolidated as sub: {aggregation['summary']['utilities_consolidated_as_sub']}")
    print(f"Final library size: {len(utility_library)}")
    print(f"\nOutput files:")
    print(f"  - {output_path}")
    print(f"  - {aggregation_path}")
    print(f"  - {final_lib_path}")
    print("="*60)


if __name__ == "__main__":
    main()
