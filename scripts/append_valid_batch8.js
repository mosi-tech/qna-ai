const fs = require('fs');

const pathValid = 'valid_questions.json';
const valid = JSON.parse(fs.readFileSync(pathValid, 'utf8'));
const today = '2025-09-09';

const additions = [
  {
    question: "Am I more successful with larger or smaller position sizes?",
    status: "VALID",
    original_question: "Am I more successful with larger or smaller position sizes?",
    validation_notes: "Group trades by notional size buckets and compare win rate/average P&L.",
    required_apis: ["trading:/v2/orders", "trading:/v2/account/activities"],
    data_requirements: ["Per-trade notional and realized P&L", "Bucketization by size", "Win rate and P&L stats"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What patterns show up in my profitable versus unprofitable trades?",
    status: "NEEDS_REFINEMENT",
    original_question: "What patterns show up in my profitable versus unprofitable trades?",
    validation_notes: "Summarize differences by holding period, time of day, sector, and instrument; highlight statistically notable gaps.",
    required_apis: ["trading:/v2/orders", "trading:/v2/account/activities", "eodhd:/fundamentals/{symbol}"],
    data_requirements: ["Per-trade realized P&L", "Derived features (holding time, entry time, sector)", "Group comparisons"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's my current account equity value?",
    status: "VALID",
    original_question: "What's my current account equity value?",
    validation_notes: "Direct from account endpoint.",
    required_apis: ["trading:/v2/account"],
    data_requirements: ["Account equity field"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How much settled cash do I have available for trading?",
    status: "VALID",
    original_question: "How much settled cash do I have available for trading?",
    validation_notes: "Use settled cash or cash fields from account details.",
    required_apis: ["trading:/v2/account"],
    data_requirements: ["Settled cash / cash fields"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's my account's net liquidation value?",
    status: "VALID",
    original_question: "What's my account's net liquidation value?",
    validation_notes: "Direct from account fields (net liquidation value).",
    required_apis: ["trading:/v2/account"],
    data_requirements: ["NLV field"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which positions are approaching margin calls?",
    status: "NEEDS_REFINEMENT",
    original_question: "Which positions are approaching margin calls?",
    validation_notes: "Estimate by comparing maintenance margin requirement vs equity and simulating haircut; flag low headroom positions.",
    required_apis: ["trading:/v2/account", "trading:/v2/positions", "alpaca.trading:/v2/assets"],
    data_requirements: ["Maintenance requirement", "Position marginability and risk", "Headroom threshold"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How much dividend income did I receive this quarter?",
    status: "VALID",
    original_question: "How much dividend income did I receive this quarter?",
    validation_notes: "Sum dividend activity amounts within current quarter.",
    required_apis: ["trading:/v2/account/activities"],
    data_requirements: ["Dividend activity entries", "Quarter date range", "Aggregation"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's the all-in cost of my investment strategy?",
    status: "NEEDS_REFINEMENT",
    original_question: "What's the all-in cost of my investment strategy?",
    validation_notes: "Combine platform/broker fees from activities with TER-based expense estimates for held funds.",
    required_apis: ["trading:/v2/account/activities", "trading:/v2/positions", "eodhd:/fundamentals/{symbol}"],
    data_requirements: ["Fee entries aggregation", "Expense ratio weighted costs", "Annualized total"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How much am I paying in management fees across all accounts?",
    status: "VALID",
    original_question: "How much am I paying in management fees across all accounts?",
    validation_notes: "Sum management/advisory fee activities across accounts over a year.",
    required_apis: ["trading:/v2/account/activities"],
    data_requirements: ["Management fee entries", "12-month date range", "Aggregation"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which investments offer the best value for their expense ratios?",
    status: "NEEDS_REFINEMENT",
    original_question: "Which investments offer the best value for their expense ratios?",
    validation_notes: "Rank funds by performance-to-fee metric within categories using historical returns and TER.",
    required_apis: ["eodhd:/screener", "marketdata:/v2/stocks/bars", "eodhd:/fundamentals/{symbol}"],
    data_requirements: ["Fund categories", "Historical returns", "Expense ratios", "Value metric computation"],
    validation_date: today,
    implementation_ready: true
  }
];

valid.valid_questions.push(...additions);
fs.writeFileSync(pathValid, JSON.stringify(valid, null, 2) + '\n');
console.log('Appended', additions.length, 'entries to valid_questions.json');

