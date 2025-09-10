const fs = require('fs');

const pathValid = 'valid_questions.json';
const valid = JSON.parse(fs.readFileSync(pathValid, 'utf8'));
const today = '2025-09-09';

const additions = [
  {
    question: "What's the total cost of ownership for my mutual funds?",
    status: "NEEDS_REFINEMENT",
    original_question: "What's the total cost of ownership for my mutual funds?",
    validation_notes: "Estimate using expense ratios (TER) and known broker/platform fees from activities; exclude undisclosed trading costs.",
    required_apis: ["trading:/v2/positions", "eodhd:/fundamentals/{symbol}", "trading:/v2/account/activities"],
    data_requirements: ["Identify mutual fund positions", "Expense ratio per fund", "Platform/broker fee entries", "Annualized cost estimate"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How do expense ratios vary across my portfolio?",
    status: "VALID",
    original_question: "How do expense ratios vary across my portfolio?",
    validation_notes: "Join positions with expense ratios for funds/ETFs and summarize distribution by holding and weight.",
    required_apis: ["trading:/v2/positions", "eodhd:/fundamentals/{symbol}"],
    data_requirements: ["Portfolio holdings", "Expense ratio per holding", "Weighted averages and range"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which investments have hidden fees I should know about?",
    status: "NEEDS_REFINEMENT",
    original_question: "Which investments have hidden fees I should know about?",
    validation_notes: "Highlight investments with higher TERs and list any recorded platform/advisory fees; true hidden costs may be unavailable.",
    required_apis: ["trading:/v2/positions", "eodhd:/fundamentals/{symbol}", "trading:/v2/account/activities"],
    data_requirements: ["Expense ratios by holding", "Fee activities by symbol/account", "Flag high-cost holdings"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What platform fees am I paying annually?",
    status: "VALID",
    original_question: "What platform fees am I paying annually?",
    validation_notes: "Sum platform/advisory/maintenance fee entries in activities over trailing year.",
    required_apis: ["trading:/v2/account/activities"],
    data_requirements: ["Fee-type filtering", "12-month date window", "Aggregation and categorization"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How much could I save by switching to lower-cost funds?",
    status: "NEEDS_REFINEMENT",
    original_question: "How much could I save by switching to lower-cost funds?",
    validation_notes: "Estimate savings by comparing current TERs to category lower-TER alternatives; uses screeners to find comparable funds.",
    required_apis: ["trading:/v2/positions", "eodhd:/screener", "eodhd:/fundamentals/{symbol}"],
    data_requirements: ["Identify fund categories", "Find lower-TER alternatives", "Compute fee difference on current market values"],
    validation_date: today,
    implementation_ready: true
  }
];

valid.valid_questions.push(...additions);
fs.writeFileSync(pathValid, JSON.stringify(valid, null, 2) + '\n');
console.log('Appended', additions.length, 'entries to valid_questions.json');

