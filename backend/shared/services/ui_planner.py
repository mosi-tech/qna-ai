"""
UIPlanner — Dashboard Decomposition Service

Given a user question, decomposes it into a DashboardSpec:
  - Selects 3–6 base-ui blocks from BLOCK_CATALOG.json
  - Assigns an atomic sub_question per block
  - Emits canonical_params for deterministic cache fingerprinting
  - Computes cache_key = sha256[:16](json.dumps(canonical_params, sort_keys=True))
"""

import hashlib
import json
import logging
import os
from typing import Any, Dict, List, Optional, TypedDict

from .base_service import BaseService
from ..llm import LLMService, create_ui_planner_llm
from ..utils.json_utils import safe_json_loads

logger = logging.getLogger("ui-planner")

# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

class DataContract(TypedDict, total=False):
    type: str
    description: str
    points: int
    categories: List[str]


class BlockPlanOutput(TypedDict, total=False):
    blockId: str
    category: str
    title: str
    dataContract: DataContract
    sub_question: str
    canonical_params: Dict[str, str]
    cache_key: str


class DashboardPlanOutput(TypedDict, total=False):
    title: str
    subtitle: str
    layout: str          # "grid" | "wide"
    blocks: List[BlockPlanOutput]


# ---------------------------------------------------------------------------
# Catalog helper
# ---------------------------------------------------------------------------

_CATALOG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..",                           # services → shared → backend → root
    "frontend", "apps", "base-ui", "src", "blocks", "BLOCK_CATALOG.json",
)

# Only include these fields in the condensed prompt representation
_CATALOG_BLOCK_FIELDS = ("id", "category", "bestFor", "avoidWhen", "dataShape")


def _load_condensed_catalog() -> str:
    """
    Load BLOCK_CATALOG.json and return a condensed, human-readable
    representation suitable for injection into the system prompt.
    """
    catalog_path = os.path.normpath(_CATALOG_PATH)
    try:
        with open(catalog_path) as f:
            catalog: Dict[str, Any] = json.load(f)
    except FileNotFoundError:
        logger.warning(f"BLOCK_CATALOG.json not found at {catalog_path}; using empty catalog")
        return "(catalog unavailable — use blocks from memory)"

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


# ---------------------------------------------------------------------------
# UIPlanner
# ---------------------------------------------------------------------------

class UIPlanner(BaseService):
    """
    Decomposes a user question into a DashboardSpec with sub-questions
    and cache keys.  Uses a fast/cheap LLM — planning only, not execution.
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(llm_service=llm_service, service_name="ui-planner")

    # ------------------------------------------------------------------
    # BaseService overrides
    # ------------------------------------------------------------------

    def _create_default_llm(self) -> LLMService:
        return create_ui_planner_llm()

    def _get_system_prompt_filename(self) -> str:
        return "system-prompt-ui-planner.txt"

    def _initialize_service_specific(self):
        """Pre-load condensed block catalog for prompt injection."""
        self._block_catalog_text = _load_condensed_catalog()
        self.logger.info(
            f"📦 BLOCK_CATALOG loaded ({len(self._block_catalog_text)} chars)"
        )

    async def load_system_prompt(self) -> str:
        """
        Override to inject the live BLOCK_CATALOG into the system prompt
        before returning it.  Replaces the {{BLOCK_CATALOG}} placeholder.
        """
        raw = await super().load_system_prompt()
        return raw.replace("{{BLOCK_CATALOG}}", self._block_catalog_text)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def plan(self, question: str) -> DashboardPlanOutput:
        """
        Decompose *question* into a DashboardSpec with 3–6 blocks.

        Each block has:
          - blockId, category, title, dataContract
          - sub_question   (atomic, standalone question for that block)
          - canonical_params  (flat dict for cache fingerprinting)
          - cache_key      (sha256[:16] of canonical_params)

        Returns a DashboardPlanOutput dict.
        Raises ValueError if the LLM response cannot be parsed / validated.
        """
        system_prompt = await self.get_system_prompt()
        user_message = self._build_user_message(question)

        self.logger.info(f"🗺  Planning dashboard for: {question[:80]}…")

        response = await self.llm_service.make_request(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.1,
        )

        content = response.get("content", "")
        if not content:
            raise ValueError("UIPlanner: LLM returned empty response")

        raw = safe_json_loads(content)
        if not raw or not isinstance(raw, dict):
            raise ValueError(
                f"UIPlanner: Could not parse LLM response as JSON.\n"
                f"Raw response (first 400 chars): {content[:400]}"
            )

        result = self._validate_and_enrich(raw, question)
        self.logger.info(
            f"✅ Dashboard planned: '{result.get('title')}' "
            f"with {len(result.get('blocks', []))} blocks"
        )
        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_user_message(self, question: str) -> str:
        return (
            f"Question: {question}\n\n"
            "Build a dashboard for this question. "
            "Follow all rules. Respond with JSON only."
        )

    def _validate_and_enrich(
        self, raw: Dict[str, Any], question: str
    ) -> DashboardPlanOutput:
        """
        Validate the raw LLM output and enrich each block with a cache_key.
        Raises ValueError on fatal schema problems.
        """
        required_top = ("title", "subtitle", "layout", "blocks")
        for field in required_top:
            if field not in raw:
                raise ValueError(
                    f"UIPlanner: LLM response missing required field '{field}'"
                )

        blocks = raw.get("blocks", [])
        if not isinstance(blocks, list) or len(blocks) < 1:
            raise ValueError("UIPlanner: 'blocks' must be a non-empty list")

        enriched_blocks: List[BlockPlanOutput] = []
        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                self.logger.warning(f"Block {i} is not a dict — skipping")
                continue

            # Require core fields
            for f in ("blockId", "category", "title", "dataContract", "sub_question"):
                if f not in block:
                    self.logger.warning(
                        f"Block {i} ({block.get('blockId', '?')}) missing '{f}' — skipping"
                    )
                    continue

            canonical_params: Dict[str, str] = block.get("canonical_params") or {}
            cache_key = self._compute_cache_key(canonical_params)

            enriched: BlockPlanOutput = {
                "blockId":          block["blockId"],
                "category":         block["category"],
                "title":            block["title"],
                "dataContract":     block["dataContract"],
                "sub_question":     block["sub_question"],
                "canonical_params": canonical_params,
                "cache_key":        cache_key,
            }
            enriched_blocks.append(enriched)

        if not enriched_blocks:
            raise ValueError("UIPlanner: No valid blocks after validation")

        result: DashboardPlanOutput = {
            "title":    raw["title"],
            "subtitle": raw.get("subtitle", ""),
            "layout":   raw.get("layout", "grid"),
            "blocks":   enriched_blocks,
        }
        return result

    def _compute_cache_key(self, canonical_params: Dict[str, Any]) -> str:
        """
        Deterministic cache key: sha256[:16] of the JSON serialisation of
        canonical_params with keys sorted.  Must match the invariant in
        DASHBOARD_PLAN.md section "Invariants".
        """
        normalised = json.dumps(canonical_params, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(normalised.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_ui_planner(llm_service: Optional[LLMService] = None) -> UIPlanner:
    """Create a UIPlanner instance, optionally with a custom LLM service."""
    return UIPlanner(llm_service=llm_service)
