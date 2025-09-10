const fs = require('fs');

const pathValid = 'valid_questions.json';
const valid = JSON.parse(fs.readFileSync(pathValid, 'utf8'));
const today = '2025-09-09';

const additions = [
  {
    question: "Which stocks in my watchlist have positive sentiment shifts?",
    status: "VALID",
    original_question: "Which stocks in my watchlist have positive sentiment shifts?",
    validation_notes: "Use trading watchlists (or a configured list) and compute recent change in news sentiment.",
    required_apis: ["trading:/v2/watchlists", "eodhd:/sentiments"],
    data_requirements: ["Watchlist symbols", "Recent sentiment scores", "Delta vs prior period"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What earnings calendar events could impact my holdings?",
    status: "VALID",
    original_question: "What earnings calendar events could impact my holdings?",
    validation_notes: "Match portfolio symbols to upcoming earnings dates within chosen horizon.",
    required_apis: ["trading:/v2/positions", "eodhd:/calendar/earnings"],
    data_requirements: ["Portfolio symbols", "Upcoming earnings dates", "Window filter"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How do Federal Reserve announcements affect my positions?",
    status: "NEEDS_REFINEMENT",
    original_question: "How do Federal Reserve announcements affect my positions?",
    validation_notes: "Use FOMC announcement dates from economic calendar; compute pre/post returns for holdings or portfolio.",
    required_apis: ["eodhd:/economic-calendar", "trading:/v2/positions", "marketdata:/v2/stocks/bars"],
    data_requirements: ["FOMC dates", "Holdings returns around events", "Event window comparison"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which of my stocks have upcoming dividend dates?",
    status: "VALID",
    original_question: "Which of my stocks have upcoming dividend dates?",
    validation_notes: "Query dividend calendars for portfolio symbols and filter by upcoming ex-dividend dates.",
    required_apis: ["trading:/v2/positions", "eodhd:/dividends"],
    data_requirements: ["Portfolio symbols", "Ex-dividend and pay dates", "Upcoming window filter"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What analyst recommendations changed for my holdings this week?",
    status: "NEEDS_REFINEMENT",
    original_question: "What analyst recommendations changed for my holdings this week?",
    validation_notes: "List rating changes for holdings within the last 7 days, if available from ratings endpoint.",
    required_apis: ["trading:/v2/positions", "eodhd:/analyst-ratings"],
    data_requirements: ["Recent rating change events", "Symbol mapping", "Week filter"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How many round-trip trades have I completed this month?",
    status: "VALID",
    original_question: "How many round-trip trades have I completed this month?",
    validation_notes: "Count completed buy->sell cycles per symbol within the current month.",
    required_apis: ["trading:/v2/orders", "trading:/v2/account/activities"],
    data_requirements: ["Matched trade pairs", "Month date filter", "Cycle counting"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's my success rate on swing trades versus buy-and-hold?",
    status: "NEEDS_REFINEMENT",
    original_question: "What's my success rate on swing trades versus buy-and-hold?",
    validation_notes: "Define swing trade holding-period threshold; compute win rate for trades above/below that threshold.",
    required_apis: ["trading:/v2/orders", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Trade open/close matching", "Holding period classification", "Win rate per strategy"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How does my performance vary by time of day trading?",
    status: "NEEDS_REFINEMENT",
    original_question: "How does my performance vary by time of day trading?",
    validation_notes: "Compute realized P&L per trade and group by entry time buckets (open, mid-day, close).",
    required_apis: ["trading:/v2/orders", "trading:/v2/account/activities"],
    data_requirements: ["Trade timestamps", "Per-trade P&L (realized)", "Grouping and comparison"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's my average time between buy and sell decisions?",
    status: "VALID",
    original_question: "What's my average time between buy and sell decisions?",
    validation_notes: "Match buys and subsequent sells per symbol/lots to compute holding durations; average them.",
    required_apis: ["trading:/v2/orders"],
    data_requirements: ["Matched buy-sell pairs", "Duration calculation", "Average and distribution"],
    validation_date: today,
    implementation_ready: true
  }
];

valid.valid_questions.push(...additions);
fs.writeFileSync(pathValid, JSON.stringify(valid, null, 2) + '\n');
console.log('Appended', additions.length, 'entries to valid_questions.json');

