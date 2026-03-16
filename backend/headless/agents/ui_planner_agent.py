#!/usr/bin/env python3
"""
UI Planner Agent

Given a user question, plans a dashboard by selecting appropriate blocks
from the BLOCK_CATALOG and assigning sub-questions to each block.

Input:
    {"question": "Show QQQ ETF price and YTD return"}

Output:
    {
        "title": "QQQ ETF Performance Dashboard",
        "blocks": [
            {"blockId": "kpi-card-01", "title": "QQQ Price", "category": "kpi-cards", ...},
            ...
        ],
        "metadata": {...}
    }
"""

import os
import json
from typing import Dict, Any, List

from agent_base import AgentBase, AgentResult


class UIPlannerAgent(AgentBase):
    """Agent that plans dashboards based on user questions"""

    def __init__(
        self,
        prompt_file: str = "../../shared/config/system-prompt-ui-planner.txt",
        llm_model: str = None,  # Use task-based config by default
        llm_provider: str = None  # Use task-based config by default
    ):
        super().__init__(
            name="ui_planner",
            task="UI_PLANNER",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

        # Load block catalog
        self.catalog = self._load_catalog()

    def _load_catalog(self) -> Dict[str, Any]:
        """Load BLOCK_CATALOG.json"""
        # Go up from agents/ to headless/ to backend/ to frontend/
        catalog_path = os.path.normpath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..", "frontend", "apps", "base-ui", "src", "blocks", "BLOCK_CATALOG.json"
        ))

        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                catalog = json.load(f)
            self.logger.info(f"✅ Loaded block catalog: {catalog_path}")
            return catalog
        except FileNotFoundError:
            self.logger.warning(f"⚠️ BLOCK_CATALOG not found: {catalog_path}")
            return {"categories": {}}

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
                "title": {"type": "string"},
                "subtitle": {"type": "string"},
                "layout": {"type": "string"},
                "blocks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "blockId": {"type": "string"},
                            "category": {"type": "string"},
                            "title": {"type": "string"},
                            "dataContract": {"type": "object"}
                        }
                    }
                }
            },
            "required": ["title", "blocks"]
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Process question and generate dashboard plan"""
        question = input_data["question"]

        # Build prompt with catalog
        catalog_prompt = self._build_catalog_prompt()

        user_message = f"""
User Question: {question}

Please plan a dashboard that answers this question.

Return ONLY a JSON object with:
- title: Dashboard title
- subtitle: Brief description
- layout: "grid" or "wide"
- blocks: Array of 3-7 block objects with:
  - blockId: Block ID from catalog
  - category: Block category
  - title: Block title
  - dataContract: Object with type, description, points, categories

No markdown, no code blocks, just JSON.
"""

        try:
            # Make LLM request
            response = self._make_llm_request(
                messages=[{"role": "user", "content": user_message}],
                system_prompt=f"{self.system_prompt}\n\n{catalog_prompt}"
            )

            content = response.get("content", "").strip()
            result_data = self._safe_parse_json(content)

            # Validate result structure
            if "blocks" not in result_data:
                raise Exception("Missing 'blocks' field in response")

            if not isinstance(result_data["blocks"], list):
                raise Exception("'blocks' must be an array")

            if len(result_data["blocks"]) < 3:
                self.logger.warning("⚠️ Less than 3 blocks in plan")

            # Add metadata
            result_data["metadata"] = {
                "question": question,
                "block_count": len(result_data["blocks"]),
                "block_ids": [b.get("blockId") for b in result_data["blocks"]]
            }

            self.logger.info(f"✅ Planned dashboard '{result_data.get('title')}' with {len(result_data['blocks'])} blocks")

            return AgentResult(success=True, data=result_data)

        except Exception as e:
            self.logger.error(f"❌ Failed to plan dashboard: {e}")
            return AgentResult(success=False, error=str(e))

    def _build_catalog_prompt(self) -> str:
        """Build condensed catalog representation for prompt"""
        if not self.catalog or not self.catalog.get("categories"):
            return "(Block catalog not available)"

        lines = ["Available Blocks:"]
        for category, blocks in self.catalog.get("categories", {}).items():
            lines.append(f"\n{category}:")
            for block in blocks:
                block_id = block.get("id", "?")
                lines.append(f"  - {block_id}")
                if block.get("bestFor"):
                    lines.append(f"    Best for: {block['bestFor'][0][:80]}")
                if block.get("avoidWhen"):
                    lines.append(f"    Avoid when: {block['avoidWhen'][:80]}")

        return "\n".join(lines)


# Factory function for easy creation
def create_ui_planner_agent(**kwargs) -> UIPlannerAgent:
    """Create UI Planner agent with optional overrides"""
    return UIPlannerAgent(**kwargs)


# For direct execution
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        question = sys.argv[1]
        agent = UIPlannerAgent()
        result = agent.execute({"question": question})
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Usage: python ui_planner_agent.py \"Your question here\"")