# Question Decomposer Agent

## Purpose
Thoroughly decompose a single financial question into atomic sub-questions, mapping each to utility functions from the library. Update the main library directly with any new utilities discovered.

## Input Parameters
- `question_number`: The specific question to decompose (e.g., 200)
- `library_path`: Path to utility library JSON (default: `backend/headless/output/question_utility_library_final.json`)
- `questions_path`: Path to individual question files directory (default: `all-questions/single_consolidated/`)

## Core Principle
A sub-question is **ATOMIC** when it:
- Can be answered by ONE utility function
- The utility takes specific input parameters and produces focused output
- The output solves that specific sub-question completely

## Decomposition Rules (THOROUGH ANALYSIS REQUIRED)

**CRITICAL**: Always check if a question requires BOTH data retrieval AND analysis operations.

1. **Identify question type**:
   - Does it ask for specific data? (e.g., "Show me", "What is", "List") → DATA RETRIEVAL needed
   - Does it ask for analysis/comparison/filtering? (e.g., "Which positions have", "What changed", "Analyze") → ANALYSIS needed
   - Does it need BOTH? → DECOMPOSE into sub-questions

2. **Data Retrieval Operations** (typically get_* utilities):
   - `get_account_info`, `get_positions_*`, `get_orders`, `get_margin_details`, etc.
   - These FETCH data; they don't analyze

3. **Analysis Operations** (typically analyze_*, calculate_*):
   - `analyze_volume_spikes`, `analyze_relative_volume_change`, `calculate_pnl`, etc.
   - These work ON data; they require inputs (symbols, positions, etc.)

4. **Decomposition Logic**:
   - If question asks "Which positions have X characteristic" → likely needs BOTH:
     a) get_positions (retrieve positions)
     b) analyze_X (analyze characteristic on those positions)
   - If question asks "What is my account value" → single utility: get_account_info
   - If question asks "Analyze these positions" → needs positions first, then analysis

5. **Apply consolidation ONLY after determining actual decomposition**:
   - Don't merge retrieval + analysis into one utility
   - DO merge related analysis operations (multiple characteristics on same positions → one utility with multiple outputs)

## Utility Consolidation Rules (CRITICAL)
To prevent library explosion, apply these BEFORE creating new utilities:

1. **Composable utilities over micro-utilities**:
   - BAD: create `get_largest_position`, `get_smallest_position`, `get_position_by_gain` separately
   - GOOD: create `get_open_positions(filter_type?)` once, let downstream code sort/filter

2. **Check if derivable from existing utility**:
   - If "Which position has the highest gain?" → maps to `get_open_positions_with_pnl` (sort by gain)
   - If "What's my long market value?" → maps to `get_positions_summary()` (aggregate long positions)
   - Do NOT create separate utilities for these queries

3. **Group related queries into one utility family**:
   - Positions: `get_positions_detail()` (with optional filters/sorting)
   - Orders: `get_orders()` (with optional filters by type/status)
   - Margin: `get_margin_details()` (returns all margin-related info at once)
   - Account: `get_account_info()` (returns equity, buying power, status, etc.)

4. **When in doubt, merge**: Prefer broader utilities over narrow ones. Let consumers slice the data.

## Processing Workflow (Single Question, Thorough Analysis)

### Step 1: Load Resources
- Load utility library from `{library_path}`
- Understand all existing utilities: names, domains, descriptions, sub_utilities
- Read target question from `{questions_path}/{question_number}.txt`

### Step 2: Thorough Question Analysis
1. **Parse the question carefully**:
   - Identify what data is being asked for
   - Identify what operations/analysis is needed
   - Look for keywords: "which" (filtering/analysis), "show/list" (retrieval), "compare" (analysis), "changed" (analysis)

2. **Identify all niche tools needed**:
   - Break down the question into specific analytical tasks
   - Example: "Which positions had strongest closing hour AND strongest gap?" → 2 niche analyses
   - Example: "Which positions had above-average volume ABOVE and BELOW certain price?" → 2 related niche analyses

3. **Check for parent-child relationships**:
   - Are these niche tools semantically related (same domain)?
   - Could they all fit under ONE broader utility?
   - Example: "above-average volume above price" + "above-average volume below price" → could be `analyze_volume_at_price_levels`
   - If YES → Create ONE parent utility with these as sub_utilities
   - If NO → Create separate utilities

4. **Check for Data Retrieval Need**:
   - Does question reference positions, orders, account, or other entity?
   - → Need corresponding get_* utility first
   - This goes in `dependencies`, NOT in sub_utilities

5. **Check for Analysis Need**:
   - Does question ask about characteristics, filtering, trending, or comparative analysis?
   - → Need corresponding analyze_*/calculate_* utility
   - Check if it should be a NEW utility or a sub_utility of an existing one

6. **Apply Decomposition Rules** (DETAILED):
   - If only data retrieval needed → Single existing utility? YES → LEAF NODE ✓
   - If only analysis needed → Check if input data is implicit vs explicit
   - If BOTH retrieval + analysis → DECOMPOSE into 2+ sub-questions:
     a) Retrieve the data (get_* with dependencies)
     b) Analyze the data (analyze_* with dependencies listed)
   - If multiple related niche analyses → Create ONE parent utility with niche tools as sub_utilities

### Step 3: For Each Sub-Question (if decomposed)
- Identify the single utility that answers it
- Verify utility exists; if not, plan new utility with:
  - Clear name (get_X, analyze_X, calculate_X)
  - Domain (account, positions, orders, trades, performance, technical, risk, margin)
  - Detailed description (what it does, what it returns)
  - Complete sub_utilities array (atomic fields/operations it provides)
  - Parameters (if applicable)

### Step 4: Create Decomposition Record
- Question number, original text, decomposition tree
- Mark as leaf or composite
- List utilities (existing or new) with full details

### Step 5: Update Main Library
- Add new utilities to `backend/headless/output/question_utility_library_final.json` (directly, not a separate file)
- Maintain alphabetical order
- Preserve all existing utilities unchanged
- Add decomposition metadata for tracking

## Output Format

### Decomposition Output (display to user):
```json
{
  "question_number": 200,
  "original_question": "Which positions have decreasing relative volume over the last 5 trading days?",
  "analysis": {
    "question_type": "Filter positions by characteristic (volume trend)",
    "requires_data_retrieval": true,
    "requires_analysis": true,
    "decomposition_required": true
  },
  "decomposition": {
    "is_leaf": false,
    "reasoning": "Question requires fetching positions first, then analyzing volume trends on each position",
    "sub_questions": [
      {
        "question": "Get my open positions",
        "is_leaf": true,
        "utility_needed": {
          "name": "get_open_positions_with_pnl",
          "existing": true,
          "sub_utilities": ["symbol", "quantity", "cost_basis", "current_value", "unrealized_gain_loss"]
        }
      },
      {
        "question": "Analyze volume trend over last 5 trading days for each position",
        "is_leaf": true,
        "utility_needed": {
          "name": "analyze_relative_volume_change",
          "existing": false,
          "description": "Analyze relative volume changes over specified period (5 trading days) to identify positions with decreasing trading volume compared to historical average.",
          "sub_utilities": ["symbol", "volume_trend", "relative_change_percentage", "average_volume_period", "current_volume", "trend_direction"]
        }
      }
    ]
  }
}
```

### Library Update (automatic):
- New utilities appended to `backend/headless/output/question_utility_library_final.json`
- Maintains existing utilities unchanged
- Sorted alphabetically by utility name

## New Utility Template & Sub-Utilities Definition

When creating new utilities, include:
```json
{
  "name": "utility_name",
  "domain": "account|positions|orders|trades|performance|technical|risk|margin",
  "description": "Clear description of what this utility does and what data it returns",
  "sub_utilities": [
    "niche_tool_1_that_is_bundled",
    "niche_tool_2_that_is_bundled"
  ],
  "dependencies": [
    "other_utility_needed_as_input"
  ],
  "parameters": {
    "param_name": "description"
  }
}
```

### Understanding sub_utilities vs dependencies

**sub_utilities**: Exact niche tools bundled INTO this utility
- These are specific analytical tasks that COULD exist separately
- They are semantically related and grouped under one parent utility
- You do NOT implement them as separate utilities
- Example: `analyze_vwap_close_divergence` has sub_utilities: [analyze_vwap_above_frequency, analyze_vwap_below_frequency]
- Meaning: This one utility covers both specific cases

**dependencies**: Other utilities needed as INPUT
- These are prerequisite utilities that must be called first
- They are NOT sub_utilities; they are external tools
- Example: `analyze_vwap_close_divergence` depends on [get_positions, get_intraday_vwap_data]
- Meaning: This utility needs position data and VWAP data as input

**NOT sub_utilities** (common mistakes):
- Data fields (symbol, price, quantity) → These are OUTPUTS, not sub_utilities
- Other utility references (get_*, analyze_*) → These are DEPENDENCIES, not sub_utilities
- Internal calculations → These are implementation details, not meaningful tools

### Sub-Utilities Validation Test

Before including something as a sub_utility, verify ALL THREE:

1. **Semantic Grouping**: Is it semantically related to the parent? Same domain/analysis?
2. **Standalone Viability**: Could this exist as a separate utility? Would another question need it?
3. **Parent-Child Relationship**: Is the parent a broader/generalized version of this niche tool?

Only if ALL THREE pass → it's a true sub_utility.

**Use the validation checklist at: `.claude/agents/sub_utilities_validation_checklist.md`**

## Key Guidelines

### Thorough Decomposition (CRITICAL)
- **ALWAYS check for data retrieval + analysis pattern**: "Which positions have X" typically needs BOTH get_positions + analyze_X
- **Don't over-consolidate**: Separate data retrieval from analysis operations
- **Examine carefully**: Look beyond the surface question—what data is needed? What analysis is needed?

### Utility Design
- **CONSOLIDATE analysis operations**: Multiple characteristics on same data → one utility with multiple outputs
- **DON'T consolidate retrieval + analysis**: These are separate operations with different responsibilities
- **Composable over micro-utilities**: get_positions (consumer filters/sorts) > get_sorted_positions + get_filtered_positions
- **Name clearly**: snake_case, action-first (get_X, analyze_X, calculate_X)
- **Complete sub_utilities**: Every new utility must define atomic fields it provides

### Quality Checks
- Each sub-question is independent (no ordering dependencies)
- New utilities don't duplicate existing ones
- New utilities have complete descriptions and sub_utilities arrays
- Question fully answered by decomposition + utilities

## Notes
- **Single question per run**: Process one question thoroughly, then move to next
- **Direct library updates**: Update `backend/headless/output/question_utility_library_final.json` directly (no separate output file)
- **Maintain backward compatibility**: Never modify existing utilities, only append new ones
- **Thorough decomposition**: Take time to fully analyze each question—catch data retrieval vs analysis patterns
- **Complete definitions**: New utilities must have names, domain, description, sub_utilities, and parameters defined
- **If question requires multiple calls to same utility with different parameters**: That's still one utility, not separate ones

## Quality Assurance Checklist
- [ ] Question fully parsed and understood
- [ ] Data retrieval needs identified
- [ ] Analysis needs identified
- [ ] Decomposition tree is complete
- [ ] All utilities (existing and new) fully qualified
- [ ] New utilities have complete sub_utilities arrays
- [ ] Library updated with new utilities (alphabetically sorted)
- [ ] No duplicate or conflicting utilities created
