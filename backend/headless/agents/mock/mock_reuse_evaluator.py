#!/usr/bin/env python3
"""
Mock Reuse Evaluator Agent

Evaluates if existing mock data can be reused for new financial questions.
Uses ChromaDB to store question -> mock_data_file mappings.

Input:
    {
        "question": "Show QQQ ETF price"
    }

Output:
    {
        "reused": true/false,
        "mock_data_file": "mock_data/q001.json" (if found),
        "similarity": 0.89 (if found)
    }
"""

import json
import logging
import os
from typing import Dict, Any
from datetime import datetime

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../..")

from agent_base import AgentBase, AgentResult
from shared.analyze.search.library import get_analysis_library

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_reuse_evaluator")


class MockReuseEvaluator(AgentBase):
    """Agent that evaluates whether existing mock data can be reused"""

    def __init__(
        self,
        prompt_file: str = None,  # Not needed for this agent
        llm_model: str = None,
        llm_provider: str = None
    ):
        super().__init__(
            name="mock_reuse_evaluator",
            task="MOCK_REUSE_EVALUATOR",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

        # ChromaDB collection for mock data reuse
        self.collection_name = "mock_reuse"
        self.mock_data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "output", "mock_data")

        # Initialize ChromaDB library
        try:
            self.library = get_analysis_library()
            self._ensure_mock_collection()
            logger.info("✅ Mock Reuse Evaluator initialized with ChromaDB")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ChromaDB: {e}")
            self.library = None

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "User's question"}
            },
            "required": ["question"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "reused": {"type": "boolean"},
                "mock_data_file": {"type": "string"},
                "similarity": {"type": "number"}
            },
            "required": ["reused"]
        }

    def _ensure_mock_collection(self):
        """Ensure the mock reuse collection exists in ChromaDB"""
        if not self.library:
            return

        try:
            # Get or create collection
            # Note: We're using the existing financial_analyses collection
            # but filtering by metadata for mock data
            pass
        except Exception as e:
            logger.warning(f"⚠️ Could not ensure collection: {e}")

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Evaluate reuse potential for mock data"""
        question = input_data.get("question", "")

        if not self.library:
            self.logger.warning("ChromaDB not available, skipping reuse evaluation")
            return AgentResult(success=True, data={"reused": False})

        try:
            # Search for similar questions in ChromaDB
            search_result = self.library.search_similar(
                query=question,
                top_k=3,
                similarity_threshold=0.85  # High threshold for reuse (must be very similar)
            )

            if search_result.get("success") and search_result.get("analyses"):
                # Filter for mock data entries
                for analysis in search_result["analyses"]:
                    # Check if this is a mock data entry
                    if analysis.get("is_mock_data"):
                        mock_file = analysis.get("mock_file")
                        similarity = analysis.get("similarity", 0)

                        # Verify the file exists
                        if mock_file and os.path.exists(mock_file):
                            self.logger.info(f"✅ Found reusable mock data: {mock_file} (similarity: {similarity:.2f})")
                            return AgentResult(success=True, data={
                                "reused": True,
                                "mock_data_file": mock_file,
                                "similarity": similarity
                            })
                        else:
                            # File doesn't exist or mock_file is None - log and skip
                            self.logger.warning(f"⚠️  Mock data entry found but file missing/invalid: {mock_file} (similarity: {similarity:.2f})")
                            continue

            # No reusable mock data found
            self.logger.info(f"✅ No reusable mock data found for: {question[:50]}...")
            return AgentResult(success=True, data={"reused": False})

        except Exception as e:
            self.logger.error(f"❌ Failed to evaluate mock reuse: {e}")
            return AgentResult(success=False, error=str(e))

    def save_mock_data_reference(
        self,
        question: str,
        mock_data_file: str,
        analysis_id: str = None
    ) -> Dict[str, Any]:
        """
        Save a question -> mock_data_file mapping to ChromaDB
        Call this after generating new mock data
        """
        if not self.library:
            return {"success": False, "error": "ChromaDB not available"}

        try:
            import hashlib
            if analysis_id is None:
                # Generate ID from question and timestamp
                combined = f"{question}_{datetime.now().isoformat()}"
                analysis_id = hashlib.md5(combined.encode()).hexdigest()[:12]

            # Prepare metadata
            metadata = {
                "is_mock_data": True,
                "mock_file": mock_data_file,
                "question": question,
                "description": f"Mock data for: {question}",
                "created_date": datetime.now().isoformat()
            }

            # Save to ChromaDB
            result = self.library.save_analysis(
                analysis_id=analysis_id,
                question=question,
                metadata=metadata
            )

            self.logger.info(f"✅ Saved mock data reference: {question[:50]}... -> {mock_data_file}")
            return result

        except Exception as e:
            self.logger.error(f"❌ Failed to save mock data reference: {e}")
            return {"success": False, "error": str(e)}


# Factory function
def create_mock_reuse_evaluator(**kwargs) -> MockReuseEvaluator:
    """Create Mock Reuse Evaluator agent with optional overrides"""
    return MockReuseEvaluator(**kwargs)


# For direct execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        question = sys.argv[1]
        evaluator = create_mock_reuse_evaluator()

        # Test reuse evaluation
        result = evaluator.execute({"question": question})
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Usage: python mock_reuse_evaluator.py \"Your question here\"")