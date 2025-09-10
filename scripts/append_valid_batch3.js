const fs = require('fs');

const path = 'valid_questions.json';
const data = JSON.parse(fs.readFileSync(path, 'utf8'));

const today = '2025-09-09';

const additions = [
  {
    question: "Which news events moved my holdings the most this month?",
    status: "NEEDS_REFINEMENT",
    original_question: "Which news events moved my holdings the most this month?",
    validation_notes: "Refine to attribute price moves around news timestamps for portfolio holdings; report largest post-news returns.",
    required_apis: ["trading:/v2/positions", "eodhd:/news", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Portfolio symbols", "News timestamps per symbol", "Event-window return calculation (e.g., 1d/3d)", "Ranking by magnitude"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What earnings announcements are coming up for my stocks?",
    status: "VALID",
    original_question: "What earnings announcements are coming up for my stocks?",
    validation_notes: "Cross portfolio symbols with earnings calendar for upcoming dates.",
    required_apis: ["trading:/v2/positions", "eodhd:/calendar/earnings"],
    data_requirements: ["Portfolio symbols", "Earnings dates in forward window", "Symbol-date mapping"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How do analyst upgrades correlate with my stock performance?",
    status: "NEEDS_REFINEMENT",
    original_question: "How do analyst upgrades correlate with my stock performance?",
    validation_notes: "Refine to show recent rating changes for holdings and subsequent short-horizon returns (e.g., 1w/1m).",
    required_apis: ["trading:/v2/positions", "eodhd:/analyst-ratings", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Recent rating changes per symbol", "Return calculation post-change", "Correlation/association summary"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which of my stocks have recent insider buying activity?",
    status: "VALID",
    original_question: "Which of my stocks have recent insider buying activity?",
    validation_notes: "Filter insider transactions to buys for portfolio symbols within recent period.",
    required_apis: ["trading:/v2/positions", "eodhd:/insider-transactions"],
    data_requirements: ["Portfolio symbols", "Recent insider buy transactions", "Issuer, insider, date, size"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What market sentiment indicators suggest about current trends?",
    status: "NEEDS_REFINEMENT",
    original_question: "What market sentiment indicators suggest about current trends?",
    validation_notes: "Refine to news sentiment for portfolio/watchlist over last week with average sentiment score trend.",
    required_apis: ["eodhd:/sentiments", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Recent news sentiment scores", "Time-window aggregation", "Trend indication"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How many trades have I made this month?",
    status: "VALID",
    original_question: "How many trades have I made this month?",
    validation_notes: "Count fills or orders with status filled in current month.",
    required_apis: ["trading:/v2/account/activities", "trading:/v2/orders"],
    data_requirements: ["Date range filter for current month", "Filled orders or trade activity count"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's my average trade size compared to my account value?",
    status: "VALID",
    original_question: "What's my average trade size compared to my account value?",
    validation_notes: "Compute average notional per filled order and compare to current equity.",
    required_apis: ["trading:/v2/orders", "trading:/v2/account"],
    data_requirements: ["Filled orders with notional/qty*price", "Account equity value", "Average trade size as % of equity"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which stocks do I trade most frequently?",
    status: "VALID",
    original_question: "Which stocks do I trade most frequently?",
    validation_notes: "Aggregate filled orders by symbol and rank by count in selected period.",
    required_apis: ["trading:/v2/orders"],
    data_requirements: ["Filled orders by symbol", "Date range filter", "Frequency ranking"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How long do I typically hold losing positions?",
    status: "NEEDS_REFINEMENT",
    original_question: "How long do I typically hold losing positions?",
    validation_notes: "Refine to closed positions with realized losses; compute holding period between opening and closing trades.",
    required_apis: ["trading:/v2/orders", "trading:/v2/account/activities"],
    data_requirements: ["Match buys to sells per symbol/lots", "Identify losing closures", "Holding period statistics"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's my profit and loss by sector allocation?",
    status: "NEEDS_REFINEMENT",
    original_question: "What's my profit and loss by sector allocation?",
    validation_notes: "Refine to current unrealized P&L by sector using positions' market value vs cost and sector classification.",
    required_apis: ["trading:/v2/positions", "eodhd:/fundamentals/{symbol}"],
    data_requirements: ["Positions with cost basis/avg entry and market value", "Sector classification", "Aggregate P&L by sector"],
    validation_date: today,
    implementation_ready: true
  }
];

data.valid_questions.push(...additions);
fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
console.log('Appended', additions.length, 'entries to valid_questions.json');

