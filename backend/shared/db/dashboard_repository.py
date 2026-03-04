"""
DashboardRepository — persistence layer for DashboardPlanModel / BlockPlanModel.

All operations target the `dashboard_plans` MongoDB collection.
The collection is accessed directly via the raw Motor database object
(`MongoDBClient.db`) because the block-level nested-document queries are
specialised enough that adding them to MongoDBClient would increase clutter.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .mongodb_client import MongoDBClient
from .schemas import BlockStatus, DashboardPlanModel

logger = logging.getLogger("dashboard_repository")

COLLECTION = "dashboard_plans"


class DashboardRepository:
    """Persistence operations for dashboard plans and their blocks."""

    def __init__(self, db: MongoDBClient):
        self.db = db

    @property
    def _col(self):
        """Return the raw Motor collection (lazy — valid after db.connect())."""
        return self.db.db[COLLECTION]

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    async def create(self, plan: DashboardPlanModel) -> str:
        """
        Persist a new DashboardPlanModel.

        Returns the `dashboard_id` string (uuid, set by the model's
        default_factory, NOT the MongoDB _id).
        """
        doc = plan.model_dump(by_alias=True)
        await self._col.insert_one(doc)
        logger.info("Created dashboard plan %s", plan.dashboard_id)
        return plan.dashboard_id

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    async def get_by_id(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Return the raw document for the given dashboard_id, or None."""
        return await self._col.find_one(
            {"dashboardId": dashboard_id},
            {"_id": 0},
        )

    async def get_by_message_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Return the dashboard plan associated with a chat message, or None."""
        return await self._col.find_one(
            {"messageId": message_id},
            {"_id": 0},
        )

    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Return recent dashboard plans for a user (newest first)."""
        cursor = (
            self._col.find({"userId": user_id}, {"_id": 0})
            .sort("createdAt", -1)
            .skip(skip)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    # ------------------------------------------------------------------
    # Block status updates
    # ------------------------------------------------------------------

    async def update_block_status(
        self,
        dashboard_id: str,
        block_id: str,
        status: BlockStatus,
        *,
        analysis_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        result_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> bool:
        """
        Update a single block's status (and optional payload fields) in-place
        using MongoDB's positional-filtered update operator.

        Returns True if the document was modified.
        """
        now = datetime.utcnow()
        set_fields: Dict[str, Any] = {
            "blocks.$[elem].status": status.value,
            "blocks.$[elem].updatedAt": now,
            "updatedAt": now,
        }
        if analysis_id is not None:
            set_fields["blocks.$[elem].analysisId"] = analysis_id
        if execution_id is not None:
            set_fields["blocks.$[elem].executionId"] = execution_id
        if result_data is not None:
            set_fields["blocks.$[elem].resultData"] = result_data
        if error is not None:
            set_fields["blocks.$[elem].error"] = error

        result = await self._col.update_one(
            {"dashboardId": dashboard_id},
            {"$set": set_fields},
            array_filters=[{"elem.block_id": block_id}],
        )
        modified = result.modified_count > 0
        if modified:
            logger.debug(
                "Dashboard %s block %s → %s", dashboard_id, block_id, status.value
            )
        else:
            logger.warning(
                "update_block_status: no doc modified for dashboard=%s block=%s",
                dashboard_id,
                block_id,
            )
        return modified

    async def update_dashboard_status(
        self, dashboard_id: str, status: str
    ) -> bool:
        """Update the top-level status field of a dashboard plan."""
        result = await self._col.update_one(
            {"dashboardId": dashboard_id},
            {"$set": {"status": status, "updatedAt": datetime.utcnow()}},
        )
        return result.modified_count > 0

    # ------------------------------------------------------------------
    # Cache lookup
    # ------------------------------------------------------------------

    async def find_cached_block(
        self,
        cache_key: str,
        max_age_hours: int = 24,
    ) -> Optional[Dict[str, Any]]:
        """
        Search *all* dashboard plans for a completed block whose cache_key
        matches and whose updatedAt is within `max_age_hours`.

        Returns the matching block sub-document (plain dict) or None.

        The query uses an aggregation pipeline so we can $filter the blocks
        array and apply the TTL constraint in one round-trip.
        """
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)

        pipeline = [
            # 1. Only consider documents that have at least one matching block
            {
                "$match": {
                    "blocks": {
                        "$elemMatch": {
                            "cache_key": cache_key,
                            "status": BlockStatus.COMPLETE.value,
                            "updatedAt": {"$gte": cutoff},
                        }
                    }
                }
            },
            # 2. Extract matching blocks
            {
                "$project": {
                    "_id": 0,
                    "matchedBlock": {
                        "$filter": {
                            "input": "$blocks",
                            "as": "b",
                            "cond": {
                                "$and": [
                                    {"$eq": ["$$b.cache_key", cache_key]},
                                    {"$eq": ["$$b.status", BlockStatus.COMPLETE.value]},
                                    {"$gte": ["$$b.updatedAt", cutoff]},
                                ]
                            },
                        }
                    },
                }
            },
            # 3. Unwind so each matched block becomes its own document
            {"$unwind": "$matchedBlock"},
            # 4. Sort: most-recently updated first so we get the freshest result
            {"$sort": {"matchedBlock.updatedAt": -1}},
            # 5. Return only the first (best) hit
            {"$limit": 1},
        ]

        async for doc in self._col.aggregate(pipeline):
            return doc.get("matchedBlock")

        return None
