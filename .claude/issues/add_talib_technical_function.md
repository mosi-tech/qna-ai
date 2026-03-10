# [Feature] Add `calculate_talib_technical` for remaining TA-Lib indicators

## Problem

The analytics server exposes only 40+ of 150+ available TA-Lib indicators. The remaining 110+ indicators (KAMA, TEMA, HT_TRENDLINE, SAR, etc.) are not available for the script building pipeline.

## Context

- **Current state**: 40+ TA-Lib indicators exposed as individual MCP functions
- **Gap**: 110+ indicators not exposed (adaptive MAs, advanced indicators, etc.)
- **Limitation**: Cannot expose all 150 individually (namespace clutter)
- **Requirement**: Script building pipeline needs function docstrings for LLM understanding

## Solution

Implement `calculate_talib_technical()` with pattern-mapping docstring approach.

### Design

```python
def calculate_talib_technical(
    indicator: str,
    data: Dict,
    **kwargs
) -> Dict:
    """
    Calculate TA-Lib technical indicators.

    === COMMONLY USED INDICATORS ===

    For ADAPTIVE trends: use KAMA (period=14)
    For SMOOTH trends: use TEMA (period=20) or HT_TRENDLINE (period=7)
    For STOPS: use SAR (step=0.02, max=0.2)

    === QUESTION PATTERNS TO INDICATOR MAPPING ===

    "adaptive moving average" → KAMA
    "triple exponential" → TEMA
    "Hilbert transform trend" → HT_TRENDLINE
    "parabolic sar" or "trailing stop" → SAR
    ...
    """
    import talib
    # Implementation
```

### Why This Approach

1. **Single function** - Clean MCP namespace
2. **Pattern-mapping docstring** - LLM can match questions to indicators
3. **Extensible** - Add more indicators/patterns easily
4. **Works with pipeline** - Docstring provides context for script generation

### Implementation Location

`backend/mcp-server/analytics/indicators/talib.py`

## Tasks

- [ ] Create `talib.py` module
- [ ] Implement `calculate_talib_technical()` with comprehensive docstring
- [ ] Add question pattern mappings for top 50 indicators
- [ ] Add to `analytics/__init__.py` for auto-discovery
- [ ] Test with common indicators (KAMA, TEMA, SAR, HT_TRENDLINE)
- [ ] Document usage in README

## Related

- Gap analysis found 36 missing atomic functions
- Some could be covered by additional TA-Lib indicators
- Issue: #xxx (atomic function gap analysis)