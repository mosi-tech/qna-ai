"""
BlockCacheService — Phase 4

Before dispatching a block's sub-question to the execution pipeline, callers
can check whether an identical answered block already exists (cache HIT).

Cache key computation
---------------------
    cache_key = sha256[:16](json.dumps(canonical_params, sort_keys=True))

The key is computed *by the UIPlanner* during planning (Phase 2) and stored in
`BlockPlanModel.cache_key`.  BlockCacheService only reads it.

Cache invalidation
------------------
- **Default:** TTL-based — configurable `ttl_hours` (default 24 h).
- **Force refresh:** The orchestrator passes `force_refresh=True`, which skips
  `lookup()` entirely (caller's responsibility).
- **Manual bust:** `POST /api/dashboard/{id}/blocks/{block_id}/refresh` will
  delete the cached block's `result_data` (Phase 7 route).
"""

import hashlib
import json
import logging
from typing import Any, Dict, Optional

from ..db.dashboard_repository import DashboardRepository

logger = logging.getLogger("block_cache_service")


# ---------------------------------------------------------------------------
# Standalone utility — not an LLM service, no BaseService inheritance
# ---------------------------------------------------------------------------


def compute_cache_key(canonical_params: Dict[str, Any]) -> str:
    """
    Compute the canonical cache key for a block's parameters.

    Invariant: the same dict (regardless of insertion order) must always yield
    the same key.  ``sort_keys=True`` guarantees key-order independence.

    Returns the first 16 hex characters of the SHA-256 digest.

    >>> compute_cache_key({"ticker": "QQQ", "metric": "price"})
    '<16-char hex string>'
    """
    normalised = json.dumps(canonical_params, sort_keys=True)
    return hashlib.sha256(normalised.encode()).hexdigest()[:16]


class BlockCacheService:
    """
    Checks whether a block's ``canonical_params`` have already been answered
    recently enough to reuse.

    All reads delegate to ``DashboardRepository.find_cached_block``; this
    service adds TTL enforcement and logging.
    """

    def __init__(
        self,
        dashboard_repo: DashboardRepository,
        ttl_hours: int = 24,
    ) -> None:
        self.repo = dashboard_repo
        self.ttl_hours = ttl_hours

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def lookup(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Return ``result_data`` if a matching *complete* block exists within TTL.

        Returns ``None`` on cache miss (key not found, wrong status, or
        TTL exceeded).
        """
        cached_block = await self.repo.find_cached_block(cache_key, self.ttl_hours)
        if cached_block is None:
            logger.debug("Cache MISS for key=%s (ttl=%sh)", cache_key, self.ttl_hours)
            return None

        result_data = cached_block.get("resultData")
        if result_data is None:
            # Block document found but no payload — treat as miss.
            logger.debug(
                "Cache MISS for key=%s — block found but resultData is empty",
                cache_key,
            )
            return None

        logger.info("Cache HIT  for key=%s", cache_key)
        return result_data

    async def is_stale(self, cache_key: str) -> bool:
        """
        Return ``True`` when no fresh cached result exists for this key.

        A ``True`` result means a re-execution is needed; ``False`` means a
        valid cached answer is available.
        """
        cached_block = await self.repo.find_cached_block(cache_key, self.ttl_hours)
        stale = cached_block is None
        logger.debug(
            "is_stale key=%s → %s (ttl=%sh)", cache_key, stale, self.ttl_hours
        )
        return stale


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_block_cache_service(
    dashboard_repo: DashboardRepository,
    ttl_hours: int = 24,
) -> BlockCacheService:
    """
    Construct a ``BlockCacheService``.

    Usage (Phase 7 — app startup)::

        from shared.services.block_cache_service import create_block_cache_service
        block_cache = create_block_cache_service(repo_manager.dashboard)

    ``ttl_hours`` can be overridden per deployment (e.g. set to 1 for
    real-time tickers, 168 for weekly reports).
    """
    return BlockCacheService(dashboard_repo=dashboard_repo, ttl_hours=ttl_hours)
