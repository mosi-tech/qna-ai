"""
BlockCacheService — Script Cache

Caches the *generated Python scripts* produced for dashboard blocks so that
the same analysis logic can be reused across different tickers, periods, and
date ranges without a round-trip to the LLM.

Two keys are used:
    cache_key   = sha256[:16](json.dumps(canonical_params, sort_keys=True))
                  Full-params fingerprint — uniquely identifies one block's
                  complete parameters (ticker + metric + period + …).
                  Stored on BlockPlanModel for block identity.

    script_key  = sha256[:16](json.dumps(template_params, sort_keys=True))
                  where template_params = canonical_params − RUNTIME_ARG_KEYS
                  (ticker, period, dates, etc. removed)

                  This is the *function identity* — it answers "what kind of
                  computation does this script perform?"  Scripts for QQQ/6m
                  and SPY/1y with the same metric share an identical script_key
                  because they are the same function with different arguments.

Script vs argument separation (like function caching):
    function  ←→  script_key  (metric + any non-runtime params)
    arguments ←→  canonical_params  (ticker, period, dates — injected at run)

Script cache flow:
    1. UIPlanner emits script_key on each block.
    2. Orchestrator passes script_key + canonical_params in job metadata.
    3. Reconciler, on block completion, tags the AnalysisModel with script_key
       via BlockCacheService.store_script() so future lookups find it.
    4. Analysis pipeline checks script_key before calling LLM — HIT means
       load the existing script and inject the new canonical_params as args.
"""

import hashlib
import json
import logging
from typing import Any, Dict, Optional

from ..db.dashboard_repository import DashboardRepository

logger = logging.getLogger("block_cache_service")

# ── Runtime argument keys — substituted at execution time ─────────────────────
# These are "arguments" to the script function, not part of its identity.
# A script that fetches "price 6m for QQQ" and "price 1y for SPY" is the
# *same function* — only the arguments differ.
#
# script_key = hash(canonical_params - RUNTIME_ARG_KEYS)
#            = hash of the pure metric/analysis identity
#
# canonical_params (full set) are still passed to the execution worker as
# arguments so the script runs against the right ticker and time range.
_RUNTIME_ARG_KEYS: frozenset = frozenset({
    # ticker-like
    "ticker", "symbol", "tickers", "symbols",
    # time range — the script logic is identical regardless of window
    "period", "start_date", "end_date", "date_range", "interval",
    "lookback", "lookback_days", "lookback_months",
})


# ---------------------------------------------------------------------------
# Standalone utility — not an LLM service, no BaseService inheritance
# ---------------------------------------------------------------------------


def compute_cache_key(canonical_params: Dict[str, Any]) -> str:
    """
    Full-params fingerprint (ticker-inclusive).

    Used as block identity — stored on ``BlockPlanModel.cache_key``.
    Two blocks with the same ticker+metric+period share this key.

    Returns the first 16 hex characters of the SHA-256 digest.

    >>> compute_cache_key({"ticker": "QQQ", "metric": "price"})
    '<16-char hex string>'
    """
    normalised = json.dumps(canonical_params, sort_keys=True)
    return hashlib.sha256(normalised.encode()).hexdigest()[:16]


def compute_script_key(canonical_params: Dict[str, Any]) -> str:
    """
    Script-identity fingerprint — the cache key for the *function*, not its
    arguments.

    Strip all runtime arguments (ticker, period, dates…) from canonical_params
    and hash the remainder.  What's left are the params that define *what the
    script computes* (e.g. metric="price_trend"), not *what data it runs on*.

    Examples — these all share the same script_key because the script logic
    is identical; only the arguments differ:
        {"ticker": "QQQ", "metric": "price", "period": "6m"}
        {"ticker": "SPY", "metric": "price", "period": "1y"}
        {"ticker": "AAPL","metric": "price", "period": "30d"}

    Returns the first 16 hex characters of the SHA-256 digest.
    """
    template_params = {
        k: v for k, v in canonical_params.items()
        if k not in _RUNTIME_ARG_KEYS
    }
    normalised = json.dumps(template_params, sort_keys=True)
    return hashlib.sha256(normalised.encode()).hexdigest()[:16]


def extract_script_params(canonical_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract the runtime *arguments* from canonical_params — the complement of
    compute_script_key().

    These are the values that change per execution (ticker, period, dates…)
    and are injected into a cached script at run time instead of re-generating
    it from the LLM.

    Together, script_key + script_params fully describe a block execution:
        script_key    → which script to use (function identity)
        script_params → what to run it with (runtime arguments)

    Example:
        canonical_params = {"ticker": "SPY", "metric": "price", "period": "1y"}
        script_key    = hash({"metric": "price"})          # function id
        script_params = {"ticker": "SPY", "period": "1y"}  # arguments
    """
    return {
        k: v for k, v in canonical_params.items()
        if k in _RUNTIME_ARG_KEYS
    }


class BlockCacheService:
    """
    Script-level cache for dashboard blocks.

    Looks up and stores *AnalysisModel IDs* (which point to reusable
    generated scripts) keyed by ``script_key`` (ticker-agnostic).

    This allows SPY to reuse a QQQ script for the same metric/period without
    an LLM round-trip.  The ticker is substituted at execution time via the
    ``canonical_params`` passed to the execution worker.
    """

    def __init__(self, dashboard_repo: DashboardRepository) -> None:
        self.repo = dashboard_repo

    # ------------------------------------------------------------------
    # Script cache API
    # ------------------------------------------------------------------

    async def lookup_script(
        self,
        script_key: str,
        analysis_repo: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Return the most-recently-created ``AnalysisModel`` doc whose
        ``script_key`` matches, or ``None`` on miss.

        The caller can use ``doc['analysisId']`` and ``doc['scriptUrl']``
        to skip LLM generation and re-execute the cached script with
        the new ticker's ``canonical_params``.
        """
        doc = await analysis_repo.find_by_script_key(script_key)
        if doc:
            logger.info("Script cache HIT  key=%s → analysis_id=%s", script_key, doc.get("analysisId"))
        else:
            logger.debug("Script cache MISS key=%s", script_key)
        return doc

    async def store_script(
        self,
        script_key: str,
        analysis_id: str,
        analysis_repo: Any,
    ) -> None:
        """
        Tag an ``AnalysisModel`` document with its ``script_key`` so future
        ``lookup_script()`` calls can find it.

        Called by the reconciler after a block's analysis completes.
        """
        await analysis_repo.set_script_key(analysis_id, script_key)
        logger.info("Script cache WRITE key=%s → analysis_id=%s", script_key, analysis_id)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_block_cache_service(
    dashboard_repo: DashboardRepository,
    ttl_hours: int = 24,  # kept for backwards-compat; unused now
) -> BlockCacheService:
    """
    Construct a ``BlockCacheService``.

    Usage::

        from shared.services.block_cache_service import create_block_cache_service
        block_cache = create_block_cache_service(repo_manager.dashboard)
    """
    return BlockCacheService(dashboard_repo=dashboard_repo)

