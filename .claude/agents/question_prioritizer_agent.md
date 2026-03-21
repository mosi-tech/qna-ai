# Question Prioritizer Agent

## Purpose
Evaluate and rearrange all questions from the consolidated question bank in order of retail importance. Identify which questions are most relevant for a retail investor dashboard.

## Input
- Source: `all-questions/consolidated_questions.json` (1813 questions)
- Context: Retail investor dashboard use case

## Output
- Rearranged questions sorted by importance (highest to lowest)
- Importance tier assignment for each question
- Duplicate/near-duplicate flagging
- Relevance scoring and rationale

## Importance Criteria

### CRITICAL (Tier 1) - Core portfolio management
- Account overview (equity, buying power, status)
- Position tracking (open positions, P&L, allocation)
- Order management (pending orders, execution status)
- Risk assessment (margin, drawdown, portfolio risk)

**Examples:**
- "What is my current account equity?"
- "Which positions am I currently holding?"
- "What is my maximum drawdown?"

### HIGH (Tier 2) - Active trading/monitoring
- Position-specific analysis (individual stock performance)
- Technical analysis for trading decisions
- Volume/momentum/volatility indicators
- Intraday/daily performance tracking
- Win rate and trade statistics

**Examples:**
- "Which position had the highest closing hour performance?"
- "Which positions are showing breakout potential?"
- "What is the relative volume change for my positions?"

### MEDIUM (Tier 3) - Strategic analysis
- Portfolio composition and diversification
- Sector/industry breakdown
- Correlation analysis
- Long-term trend analysis
- Seasonal patterns and market cycles
- Attribution and benchmark comparison

**Examples:**
- "What is my portfolio sector exposure?"
- "How is my portfolio correlated with the market?"
- "Which months historically perform best?"

### LOW (Tier 4) - Niche/specialized analysis
- Advanced statistical metrics (skewness, kurtosis)
- Specific technical patterns (consecutive highs, gaps)
- Volatility clustering analysis
- Leverage fund analysis
- Exotic derivatives analysis

**Examples:**
- "Which positions have the highest realized skewness?"
- "Analyze volatility clustering in my returns"

### IRRELEVANT (Tier 5) - Not useful for retail investor
- Overly academic/theoretical questions
- Questions requiring unavailable data
- Questions for institutional/fund managers only
- Irrelevant to personal portfolio management

**Examples:**
- "What is the theoretical standard deviation of X?"
- "What is the fund's net asset value?" (for personal trader)

## Evaluation Process

### Step 1: Categorize Each Question
For each question, determine:
1. **What problem does it solve?** (Account, positions, risk, trading, analysis, academic)
2. **Who needs this?** (Retail investor, professional trader, fund manager, researcher)
3. **How frequently would it be used?** (Daily, weekly, monthly, rarely)
4. **Does it have business value?** (Can it be visualized? Is it actionable?)

### Step 2: Assign Importance Tier
- CRITICAL: Core functionality, daily need, essential for portfolio management
- HIGH: Active trading, decision support, frequently used
- MEDIUM: Strategic insights, monthly/quarterly review
- LOW: Specialized/niche analysis, rarely needed
- IRRELEVANT: No clear use case, not actionable

### Step 3: Identify Duplicates/Near-Duplicates
Flag questions that ask the same thing:
- Exact duplicates (same intent, different wording)
- Near-duplicates (90%+ overlap in intent)
- Note the relationship for reference

### Step 4: Sort by Importance
Rearrange all questions in order: CRITICAL → HIGH → MEDIUM → LOW → IRRELEVANT

## Output Format

```json
{
  "total_questions": 1813,
  "rearranged_questions": [
    {
      "rank": 1,
      "original_question_number": 5,
      "question": "What is my current account equity and buying power?",
      "importance_tier": "critical",
      "frequency": "daily",
      "use_case": "account_overview",
      "rationale": "Core account overview needed for portfolio management",
      "duplicate_of": null,
      "related_questions": [15, 42]
    },
    {
      "rank": 2,
      "original_question_number": 8,
      "question": "Which positions am I currently holding?",
      "importance_tier": "critical",
      "frequency": "daily",
      "use_case": "position_tracking",
      "rationale": "Essential position list for portfolio management",
      "duplicate_of": null,
      "related_questions": [18, 50]
    }
  ],
  "tier_summary": {
    "critical": 45,
    "high": 320,
    "medium": 780,
    "low": 620,
    "irrelevant": 48
  },
  "duplicates_found": [
    {
      "kept": "Which positions am I currently holding?",
      "kept_rank": 2,
      "duplicate": "What positions do I have open?",
      "duplicate_rank": 125,
      "similarity": "99% - exact same intent"
    }
  ],
  "consolidation_notes": "..."
}
```

## Key Guidelines

1. **Retail investor focus**: Prioritize questions for personal portfolio management, not institutional
2. **Actionability**: Favor questions with clear, actionable outputs
3. **Frequency of use**: Weight toward questions needed daily/weekly vs. quarterly/yearly
4. **Dashboard visualization**: Favor questions that can be visualized on dashboard
5. **Data availability**: Prioritize questions answerable with standard trading account data
6. **Practical application**: Deprioritize purely academic/theoretical questions
7. **Note duplicates**: Flag but keep all questions (no removal)

## Processing Notes

- All 1813 questions are kept and rearranged
- Questions are ranked from most to least important
- Duplicates are flagged for awareness, not removed
- After rearrangement, Phase 1 decomposition will focus on CRITICAL + HIGH tiers first
- Provides roadmap for dashboard feature prioritization

## Success Criteria

✓ All 1813 questions assigned to importance tiers
✓ Rearranged from most to least important
✓ Duplicates identified and noted
✓ Clear rationale for each tier assignment
✓ CRITICAL and HIGH questions at top (ready for Phase 1)
✓ Consolidation notes document patterns observed
