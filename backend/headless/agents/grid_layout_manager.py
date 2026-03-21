#!/usr/bin/env python3
"""
Grid Layout Manager

Manages grid templates and approval constraints to ensure blocks are placed
only in slots where they're approved for that width.

This bridges the frontend CreativeGrids and approvals.json with the backend
UI planner to generate valid dashboard layouts.
"""

import json
import os
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class GridLayoutManager:
    """Manages grid templates and approval-aware block assignment"""

    def __init__(self):
        self.grids = self._load_grids()
        self.approvals = self._load_approvals()

    def _load_grids(self) -> Dict[str, Any]:
        """Load grid templates from frontend CreativeGrids"""
        grid_path = os.path.normpath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..", "frontend", "apps", "base-ui", "src", "dashboardComposer", "CreativeGrids.ts"
        ))

        # Grid templates matching frontend CreativeGrids
        return {
            "single-col": {
                "id": "single-col",
                "name": "Single Column",
                "cols": 1,
                "slots": [{"id": "slot-1", "colSpan": 1, "width": "full"}],
            },
            "two-col": {
                "id": "two-col",
                "name": "Two Equal",
                "cols": 2,
                "slots": [
                    {"id": "slot-1", "colSpan": 1, "width": "1/2"},
                    {"id": "slot-2", "colSpan": 1, "width": "1/2"},
                ],
            },
            "two-col-wide-narrow": {
                "id": "two-col-wide-narrow",
                "name": "Wide + Narrow",
                "cols": 3,
                "slots": [
                    {"id": "slot-1", "colSpan": 2, "width": "2/3"},
                    {"id": "slot-2", "colSpan": 1, "width": "1/3"},
                ],
            },
            "three-col": {
                "id": "three-col",
                "name": "Three Equal",
                "cols": 3,
                "slots": [
                    {"id": "slot-1", "colSpan": 1, "width": "1/3"},
                    {"id": "slot-2", "colSpan": 1, "width": "1/3"},
                    {"id": "slot-3", "colSpan": 1, "width": "1/3"},
                ],
            },
            "three-col-wide": {
                "id": "three-col-wide",
                "name": "3Col Large",
                "cols": 3,
                "slots": [
                    {"id": "slot-1", "colSpan": 2, "width": "2/3"},
                    {"id": "slot-2", "colSpan": 1, "width": "1/3"},
                    {"id": "slot-3", "colSpan": 1, "width": "1/3"},
                    {"id": "slot-4", "colSpan": 1, "width": "1/3"},
                ],
            },
            "three-col-hero": {
                "id": "three-col-hero",
                "name": "3Col Hero",
                "cols": 3,
                "slots": [
                    {"id": "slot-1", "colSpan": 3, "width": "full"},
                    {"id": "slot-2", "colSpan": 1, "width": "1/3"},
                    {"id": "slot-3", "colSpan": 1, "width": "1/3"},
                    {"id": "slot-4", "colSpan": 1, "width": "1/3"},
                ],
            },
            "quad-balance": {
                "id": "quad-balance",
                "name": "Quad Balance",
                "cols": 2,
                "slots": [
                    {"id": "slot-1", "colSpan": 1, "width": "1/2"},
                    {"id": "slot-2", "colSpan": 1, "width": "1/2"},
                    {"id": "slot-3", "colSpan": 1, "width": "1/2"},
                    {"id": "slot-4", "colSpan": 1, "width": "1/2"},
                ],
            },
            "four-col": {
                "id": "four-col",
                "name": "Four Col",
                "cols": 4,
                "slots": [
                    {"id": "slot-1", "colSpan": 1, "width": "1/4"},
                    {"id": "slot-2", "colSpan": 1, "width": "1/4"},
                    {"id": "slot-3", "colSpan": 1, "width": "1/4"},
                    {"id": "slot-4", "colSpan": 1, "width": "1/4"},
                ],
            },
            "flowing-rows": {
                "id": "flowing-rows",
                "name": "Flowing",
                "cols": 3,
                "slots": [
                    {"id": "slot-1", "colSpan": 3, "width": "full"},
                    {"id": "slot-2", "colSpan": 1, "width": "1/3"},
                    {"id": "slot-3", "colSpan": 1, "width": "1/3"},
                    {"id": "slot-4", "colSpan": 1, "width": "1/3"},
                    {"id": "slot-5", "colSpan": 3, "width": "full"},
                ],
            },
        }

    def _load_approvals(self) -> Dict[str, List[str]]:
        """Load block approvals from frontend approvals.json"""
        approvals_path = os.path.normpath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..", "frontend", "apps", "base-ui", "approvals.json"
        ))

        try:
            with open(approvals_path, 'r', encoding='utf-8') as f:
                approvals = json.load(f)
            logger.info(f"✅ Loaded approvals: {len(approvals)} blocks approved")
            return approvals
        except FileNotFoundError:
            logger.warning(f"⚠️ Approvals not found: {approvals_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse approvals: {e}")
            return {}

    def select_grid(self, block_count: int) -> Optional[str]:
        """Select best grid template for number of blocks"""
        # Prefer more compact, visually balanced layouts
        if block_count == 1:
            return "single-col"
        elif block_count == 2:
            return "two-col"
        elif block_count == 3:
            return "three-col"
        elif block_count == 4:
            return "quad-balance"
        elif block_count == 5:
            return "flowing-rows"  # full + 3 below + 1 more
        elif block_count <= 7:
            return "four-col"
        else:
            return "quad-balance"  # Fallback for many blocks

    def get_slot_width(self, grid_id: str, slot_id: str) -> Optional[str]:
        """Get width constraint for a specific slot"""
        grid = self.grids.get(grid_id)
        if not grid:
            return None

        for slot in grid["slots"]:
            if slot["id"] == slot_id:
                return slot.get("width", "full")

        return None

    def get_slots_for_grid(self, grid_id: str) -> List[Dict[str, Any]]:
        """Get all slots for a grid template"""
        grid = self.grids.get(grid_id)
        return grid.get("slots", []) if grid else []

    def is_block_approved_for_slot(self, block_id: str, grid_id: str, slot_id: str) -> bool:
        """Check if block is approved for this slot's width"""
        slot_width = self.get_slot_width(grid_id, slot_id)
        if not slot_width:
            return False

        block_approvals = self.approvals.get(block_id, [])
        return slot_width in block_approvals

    def assign_blocks_to_slots(
        self,
        grid_id: str,
        block_ids: List[str],
    ) -> Tuple[Dict[str, str], List[str]]:
        """
        Assign blocks to slots respecting approval constraints.

        Returns:
            (slot_assignments, unplaced_blocks)
            slot_assignments: {"slot-1": "block-id-1", ...}
            unplaced_blocks: blocks that couldn't be placed
        """
        slots = self.get_slots_for_grid(grid_id)
        assignments = {}
        remaining_blocks = list(block_ids)

        # Try to place each block in a slot
        for slot in slots:
            slot_id = slot["id"]

            # Find first remaining block approved for this slot
            for i, block_id in enumerate(remaining_blocks):
                if self.is_block_approved_for_slot(block_id, grid_id, slot_id):
                    assignments[slot_id] = block_id
                    remaining_blocks.pop(i)
                    break

        return assignments, remaining_blocks

    def generate_layout_config(
        self,
        dashboard_title: str,
        blocks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate complete layout configuration for a dashboard.

        Input blocks: [{"blockId": "kpi-01", "category": "kpi", ...}, ...]
        Output: {
            "title": "...",
            "layout": {
                "templateId": "two-col",
                "slots": {
                    "slot-1": {"blockId": "kpi-01", ...},
                    ...
                }
            }
        }
        """
        block_ids = [b.get("blockId") for b in blocks]
        grid_id = self.select_grid(len(block_ids))

        assignments, unplaced = self.assign_blocks_to_slots(grid_id, block_ids)

        # Build slot config with block metadata
        slot_blocks = {}
        for slot_id, block_id in assignments.items():
            block_data = next((b for b in blocks if b.get("blockId") == block_id), {})
            slot_blocks[slot_id] = {
                "blockId": block_id,
                "category": block_data.get("category"),
                "title": block_data.get("title"),
                "dataContract": block_data.get("dataContract"),
            }

        logger.info(f"✅ Generated layout '{grid_id}': {len(assignments)} blocks placed, {len(unplaced)} unplaced")

        if unplaced:
            logger.warning(f"⚠️ Unplaced blocks: {unplaced}")

        return {
            "title": dashboard_title,
            "layout": {
                "templateId": grid_id,
                "slots": slot_blocks,
            },
            "metadata": {
                "slot_count": len(self.get_slots_for_grid(grid_id)),
                "placed_count": len(assignments),
                "unplaced_blocks": unplaced,
            },
        }


# Factory
def create_grid_manager() -> GridLayoutManager:
    """Create grid layout manager"""
    return GridLayoutManager()
