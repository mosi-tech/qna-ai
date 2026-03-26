#!/usr/bin/env python3
"""
Tool Result Reducer

Intercepts large MCP tool results and reduces them before they enter the LLM
context window — without making any assumptions about what the data means.

Two-pass reduction:
  1. Field projection — strip each row to only the keys the block actually needs
     (dataContract.fields + date/identifier keys). Can shrink by 3–10x alone.
  2. Row truncation — if still over the character budget, trim rows from the tail
     and record _total_rows so the LLM knows data was cut.

No analytics, no metric computation, no domain assumptions.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Maximum chars a single tool result may occupy in the LLM context
CHAR_BUDGET = 8_000

# Keys that are always kept regardless of dataContract.fields
# (dates, identifiers — the LLM needs these to make sense of the rows)
_ALWAYS_KEEP: Set[str] = {
    "date", "timestamp", "t", "time", "Date", "datetime",
    "ticker", "symbol", "name", "label", "id", "sector",
}


# ─── Public entry point ───────────────────────────────────────────────────────

def reduce_tool_result(
    raw: Any,
    data_contract: Dict,
    function_name: str = "",
) -> Any:
    """
    Reduce a large tool result to fit within CHAR_BUDGET chars.
    Returns unchanged if already within budget.
    """
    if not isinstance(raw, dict):
        return _budget_cap_scalar(raw, function_name)

    # Fast path: already small
    if _char_size(raw) <= CHAR_BUDGET:
        return raw

    data_array = _find_data_array(raw)
    if data_array is None:
        # No array found — hard-truncate the serialised form
        return _hard_truncate_dict(raw, function_name)

    original_len = len(data_array)
    fields = set(data_contract.get("fields") or [])

    logger.info(
        f"  🔀 Reducing [{function_name}]: {original_len} rows, "
        f"{_char_size(raw):,} chars → budget {CHAR_BUDGET:,}"
    )

    # ── Pass 1: field projection ──────────────────────────────────────────────
    keep_keys = (_ALWAYS_KEEP | fields) if fields else None
    projected = _project_fields(data_array, keep_keys)

    # ── Pass 2: row truncation to fit budget ──────────────────────────────────
    array_key  = _find_data_array_key(raw)
    overhead   = _char_size({k: v for k, v in raw.items() if k != array_key})
    row_budget = CHAR_BUDGET - overhead - 200  # 200 char buffer for metadata

    trimmed = _trim_to_budget(projected, row_budget)

    result = {
        **{k: v for k, v in raw.items() if k != array_key},
        array_key:       trimmed,
        "_total_rows":   original_len,
        "_returned_rows": len(trimmed),
    }

    if len(trimmed) < original_len:
        result["_note"] = (
            f"Result truncated from {original_len} to {len(trimmed)} rows "
            f"to fit context budget. Rows are ordered as returned by the API."
        )

    logger.info(
        f"  🔀 Done: {original_len} → {len(trimmed)} rows, "
        f"{_char_size(result):,} chars"
    )
    return result


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _project_fields(data_array: List[Dict], keep_keys: Optional[Set[str]]) -> List[Dict]:
    """Strip each row to only keep_keys. No-op if keep_keys is None."""
    if not keep_keys or not data_array or not isinstance(data_array[0], dict):
        return data_array
    return [
        {k: v for k, v in row.items() if k in keep_keys}
        for row in data_array
    ]


def _trim_to_budget(data_array: List, budget: int) -> List:
    """Binary-search for the largest prefix that fits within budget chars."""
    if budget <= 0:
        return data_array[:10]

    # Fast path: everything fits
    if _char_size(data_array) <= budget:
        return data_array

    # Binary search for largest prefix that fits
    lo, hi = 1, len(data_array)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if _char_size(data_array[:mid]) <= budget:
            lo = mid
        else:
            hi = mid - 1
    return data_array[:max(lo, 1)]


def _find_data_array(raw: Dict) -> Optional[List]:
    for key in ("data", "bars", "results", "quotes", "trades", "history", "records", "items"):
        val = raw.get(key)
        if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
            return val
    return None


def _find_data_array_key(raw: Dict) -> str:
    for key in ("data", "bars", "results", "quotes", "trades", "history", "records", "items"):
        val = raw.get(key)
        if isinstance(val, list) and len(val) > 0:
            return key
    return "data"


def _char_size(obj: Any) -> int:
    try:
        return len(json.dumps(obj, default=str))
    except Exception:
        return 0


def _hard_truncate_dict(raw: Dict, function_name: str) -> Dict:
    """Last resort: serialise, truncate string, return with a warning."""
    serialised = json.dumps(raw, default=str)
    if len(serialised) <= CHAR_BUDGET:
        return raw
    logger.warning(f"  [{function_name}] No array found — hard-truncating dict to {CHAR_BUDGET} chars")
    return {
        "_truncated": True,
        "_note": f"Result too large ({len(serialised):,} chars), truncated to first {CHAR_BUDGET} chars",
        "_raw_prefix": serialised[:CHAR_BUDGET],
    }


def _budget_cap_scalar(raw: Any, function_name: str) -> Any:
    """Cap non-dict results (strings, lists) by char budget."""
    size = _char_size(raw)
    if size <= CHAR_BUDGET:
        return raw
    if isinstance(raw, list):
        trimmed = _trim_to_budget(raw, CHAR_BUDGET)
        return trimmed
    logger.warning(f"  [{function_name}] Scalar result too large ({size:,} chars)")
    return raw
