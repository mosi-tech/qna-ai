# Sub-Utilities Validation Checklist

## Purpose
Validate that sub_utilities have true parent-child or subset-superset relationships with their parent utility.

## Validation Test (3-Part)

For each potential sub_utility, answer ALL THREE questions:

### 1. **Semantic Grouping Test**
- Is the sub_utility semantically related to the parent utility?
- Do they analyze/operate on the same domain?
- Would they naturally belong together in a user's mind?

**Examples:**
- ✓ `analyze_vwap_above_frequency` → sub_utility of `analyze_vwap_close_divergence` (both VWAP-close analysis)
- ✗ `calculate_bollinger_bands` → NOT sub_utility of `analyze_volume_spikes` (different domains)

### 2. **Standalone Viability Test**
- Could this sub_utility meaningfully exist as a separate utility?
- Would another question ask for just this niche tool?
- Does it solve a distinct analytical problem?

**Examples:**
- ✓ `analyze_vwap_above_frequency` could be useful separately ("How often does this close above VWAP?")
- ✗ `calculate_divergence` is just math, not a standalone query

### 3. **Parent-Child Relationship Test**
- Is the parent utility a broader/generalized version of the sub_utility?
- Does the parent encompass this as one of several related analyses?
- Is the sub_utility a specific instance of the parent's capability?

**Examples:**
- ✓ `analyze_vwap_close_divergence` (parent) encompasses `analyze_vwap_above` (specific case)
- ✗ `get_account_info` is NOT a parent of `calculate_daily_pnl` (no parent-child relationship)

---

## Checklist Format

For each utility:

```
Utility: analyze_vwap_close_divergence

Sub_utility: analyze_vwap_above_frequency
- Semantic grouping: ✓ YES (both VWAP-close analysis)
- Standalone viability: ✓ YES (could be separate query)
- Parent-child relationship: ✓ YES (specific case of broader divergence analysis)
- VERDICT: ✓ KEEP as sub_utility

Sub_utility: symbol
- Semantic grouping: ✗ NO (this is a data field, not a tool)
- VERDICT: ✗ REMOVE (not a sub_utility)

Sub_utility: get_intraday_vwap_data
- Semantic grouping: ✓ YES (needed for VWAP analysis)
- Standalone viability: ✓ YES (separate retrieval utility)
- Parent-child relationship: ✗ NO (this is a dependency, not a child analysis)
- VERDICT: ✗ MOVE to dependencies field
```

---

## Common False Positives (Remove These)

1. **Data fields** (symbol, price, quantity, date, etc.)
   - These are outputs, not sub_utilities
   - Remove from sub_utilities

2. **Dependencies/other utilities** (get_*, analyze_*, calculate_*)
   - These are prerequisites, not sub_utilities
   - Move to dependencies field

3. **Internal calculations** (calculate_divergence, sum_volumes, etc.)
   - These are implementation details, not meaningful standalone queries
   - Remove from sub_utilities

4. **Duplicates/redundant names** (same concept with different names)
   - Keep one canonical name, remove others

---

## Common True Cases (Keep These)

1. **Specific instances of broader analysis**
   - `analyze_vwap_above` is a sub_utility of `analyze_vwap_divergence`
   - `analyze_upper_band_breakout` is a sub_utility of `analyze_bollinger_breakouts`

2. **Variant analyses on same data**
   - `analyze_volume_increase` and `analyze_volume_decrease` as sub_utilities of `analyze_volume_changes`

3. **Related metrics from same domain**
   - `calculate_win_rate` and `calculate_loss_rate` as sub_utilities of `calculate_trade_statistics`

---

## Decision Tree

```
Is it a utility/function reference (starts with get_, analyze_, calculate_)?
  ├─ YES → Move to dependencies field (not a sub_utility)
  └─ NO → Continue

Is it a data field (symbol, price, date, quantity)?
  ├─ YES → Remove (not a sub_utility)
  └─ NO → Continue

Could it meaningfully exist as a separate utility?
  ├─ NO → Remove (internal implementation only)
  └─ YES → Continue

Is it semantically related to parent utility?
  ├─ NO → Remove (different domain)
  └─ YES → KEEP as sub_utility
```

---

## Output Format After Validation

```json
{
  "name": "utility_name",
  "description": "...",
  "sub_utilities": [
    "specific_niche_analysis_1",
    "specific_niche_analysis_2"
  ],
  "dependencies": [
    "get_prerequisite_utility",
    "analyze_prerequisite_utility"
  ]
}
```

**Key:**
- `sub_utilities`: Only niche analyses that pass all 3 tests
- `dependencies`: Utilities that must be called first (other utilities)
- Both arrays should be non-empty if applicable, empty if none exist
