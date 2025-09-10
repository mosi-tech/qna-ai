const fs = require('fs');

const pathValid = 'valid_questions.json';
const valid = JSON.parse(fs.readFileSync(pathValid, 'utf8'));
const today = '2025-09-09';

const additions = [
  {
    question: "Am I making investment decisions based on recent news?",
    status: "NEEDS_REFINEMENT",
    original_question: "Am I making investment decisions based on recent news?",
    validation_notes: "Refine to measure fraction of trades executed within N hours after major news for traded symbols.",
    required_apis: ["eodhd:/news", "trading:/v2/orders"],
    data_requirements: ["Trade timestamps and symbols", "News timestamps and importance", "Proximity window match and ratio"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How does my performance change during volatile markets?",
    status: "NEEDS_REFINEMENT",
    original_question: "How does my performance change during volatile markets?",
    validation_notes: "Use SPY realized volatility as proxy for market volatility; compare portfolio returns on high-vol vs normal days.",
    required_apis: ["trading:/v2/account/portfolio/history", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Portfolio daily returns", "SPY daily returns/volatility", "Subsample comparison stats"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Do I tend to chase momentum or buy dips?",
    status: "NEEDS_REFINEMENT",
    original_question: "Do I tend to chase momentum or buy dips?",
    validation_notes: "Classify buys based on prior N-day returns of the asset to determine buy-on-strength vs buy-on-weakness.",
    required_apis: ["trading:/v2/orders", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Buy trade timestamps and symbols", "Pre-trade return windows", "Classification and summary"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's my current day trading buying power?",
    status: "VALID",
    original_question: "What's my current day trading buying power?",
    validation_notes: "Directly available from account fields.",
    required_apis: ["trading:/v2/account"],
    data_requirements: ["Account day trading buying power field"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How many day trades have I used this week?",
    status: "VALID",
    original_question: "How many day trades have I used this week?",
    validation_notes: "Count same-day round trips from activities/orders within current week.",
    required_apis: ["trading:/v2/account/activities", "trading:/v2/orders"],
    data_requirements: ["Order fills with timestamps", "Same-day buy/sell pairing logic", "Week filter"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's my account maintenance requirement?",
    status: "VALID",
    original_question: "What's my account maintenance requirement?",
    validation_notes: "Available from trading account details (maintenance requirement/margin).",
    required_apis: ["trading:/v2/account"],
    data_requirements: ["Maintenance requirement fields"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which positions are on margin versus cash?",
    status: "VALID",
    original_question: "Which positions are on margin versus cash?",
    validation_notes: "Determine margin usage using account margin status and position marginability; flag if margin used and position contributes.",
    required_apis: ["trading:/v2/positions", "trading:/v2/account", "alpaca.trading:/v2/assets"],
    data_requirements: ["Position list", "Asset marginable flag", "Account margin used"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How much interest am I paying on margin loans?",
    status: "VALID",
    original_question: "How much interest am I paying on margin loans?",
    validation_notes: "Sum interest charge activities over selected period.",
    required_apis: ["trading:/v2/account/activities"],
    data_requirements: ["Interest charge entries", "Date range filter", "Aggregation"],
    validation_date: today,
    implementation_ready: true
  }
];

valid.valid_questions.push(...additions);
fs.writeFileSync(pathValid, JSON.stringify(valid, null, 2) + '\n');
console.log('Appended', additions.length, 'entries to valid_questions.json');

