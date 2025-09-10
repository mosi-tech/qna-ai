const fs = require('fs');

const path = 'valid_questions.json';
const data = JSON.parse(fs.readFileSync(path, 'utf8'));

const additions = [
  {
    question: "How much am I paying in total trading fees annually?",
    status: "VALID",
    original_question: "How much am I paying in total trading fees annually?",
    validation_notes: "Compute sum of broker-recorded fees/commissions from account activities for a given year.",
    required_apis: ["trading:/v2/account/activities"],
    data_requirements: [
      "Account activities filtered by type (FEE, COMMISSION, REG_FEE, etc.)",
      "Date range filter for current or specified year",
      "Aggregation of fee amounts by activity type"
    ],
    validation_date: "2025-09-09",
    implementation_ready: true
  },
  {
    question: "What's the expense ratio impact across my ETF holdings?",
    status: "VALID",
    original_question: "What's the expense ratio impact across my ETF holdings?",
    validation_notes: "Estimate annual expense drag by multiplying each ETF's expense ratio by its market value; sum for portfolio impact.",
    required_apis: ["trading:/v2/positions", "eodhd:/fundamentals/{symbol}"],
    data_requirements: [
      "Identify ETF holdings in positions",
      "Expense ratio (TER) per ETF",
      "Position market value per ETF",
      "Per-ETF and total annualized expense cost"
    ],
    validation_date: "2025-09-09",
    implementation_ready: true
  },
  {
    question: "Which funds have the lowest cost basis in my portfolio?",
    status: "NEEDS_REFINEMENT",
    original_question: "Which funds have the lowest cost basis in my portfolio?",
    validation_notes: "Refine to use average entry price from positions as proxy for cost basis per share; lot-level tax basis may be unavailable.",
    required_apis: ["trading:/v2/positions"],
    data_requirements: [
      "Fund/ETF positions only",
      "Average entry price per position",
      "Ranking by lowest average cost per share"
    ],
    validation_date: "2025-09-09",
    implementation_ready: true
  },
  {
    question: "How do commission costs affect my small position trades?",
    status: "NEEDS_REFINEMENT",
    original_question: "How do commission costs affect my small position trades?",
    validation_notes: "Analyze per-trade fees/commissions from activities relative to trade notional for small positions; some brokers are zero-commission.",
    required_apis: ["trading:/v2/account/activities", "trading:/v2/orders"],
    data_requirements: [
      "Per-trade fees/commissions from activities",
      "Identify small trades by notional/quantity",
      "Fee as % of trade notional impact analysis"
    ],
    validation_date: "2025-09-09",
    implementation_ready: true
  },
  {
    question: "What's the fee drag on my long-term investment returns?",
    status: "NEEDS_REFINEMENT",
    original_question: "What's the fee drag on my long-term investment returns?",
    validation_notes: "Estimate fee drag using expense ratios and historical returns; provide scenario analysis rather than precise forecasting.",
    required_apis: ["trading:/v2/positions", "eodhd:/fundamentals/{symbol}", "marketdata:/v2/stocks/bars"],
    data_requirements: [
      "Expense ratios for funds",
      "Portfolio value/weights",
      "Historical returns to estimate compounding impact",
      "Projected fee drag over multi-year horizon"
    ],
    validation_date: "2025-09-09",
    implementation_ready: true
  }
];

data.valid_questions.push(...additions);

fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
console.log('Appended', additions.length, 'entries to valid_questions.json');

