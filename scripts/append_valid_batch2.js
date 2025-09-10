const fs = require('fs');

const path = 'valid_questions.json';
const data = JSON.parse(fs.readFileSync(path, 'utf8'));

const today = '2025-09-09';

const additions = [
  {
    question: "What stocks are hitting their 52-week highs today?",
    status: "VALID",
    original_question: "What stocks are hitting their 52-week highs today?",
    validation_notes: "Use screener/movers with historical 52-week range check and current prices.",
    required_apis: ["marketdata:/v1beta1/screener/stocks/movers", "marketdata:/v2/stocks/snapshots", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Current prices", "52-week high values", "New-high identification logic"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which companies reported earnings beats this week?",
    status: "VALID",
    original_question: "Which companies reported earnings beats this week?",
    validation_notes: "Filter earnings calendar by date and compare actual vs estimate to flag beats.",
    required_apis: ["eodhd:/calendar/earnings"],
    data_requirements: ["Earnings events for current week", "Actual vs estimate EPS", "Beat/miss classification"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How volatile has TSLA been compared to other EV stocks?",
    status: "VALID",
    original_question: "How volatile has TSLA been compared to other EV stocks?",
    validation_notes: "Compute realized volatility over a window for TSLA and peer EV set, then compare.",
    required_apis: ["marketdata:/v2/stocks/bars", "eodhd:/screener"],
    data_requirements: ["Peer set of EV stocks", "Historical daily bars", "Volatility (stdev of returns) comparison"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's the price momentum on semiconductor stocks?",
    status: "VALID",
    original_question: "What's the price momentum on semiconductor stocks?",
    validation_notes: "Define momentum (e.g., 1M/3M/6M returns or RSI) across semiconductor sector and rank.",
    required_apis: ["eodhd:/screener", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Semiconductor sector symbols", "Historical bars", "Momentum metric calculation and ranking"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which stocks have the strongest technical breakouts?",
    status: "NEEDS_REFINEMENT",
    original_question: "Which stocks have the strongest technical breakouts?",
    validation_notes: "Refine to a specific breakout definition (e.g., price crossing 52-week high with volume > 1.5x avg).",
    required_apis: ["marketdata:/v1beta1/screener/stocks/movers", "marketdata:/v2/stocks/bars", "marketdata:/v2/stocks/snapshots"],
    data_requirements: ["Historical highs", "Current price and volume", "Average volume baseline and threshold"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How does my portfolio's Sharpe ratio compare to benchmarks?",
    status: "VALID",
    original_question: "How does my portfolio's Sharpe ratio compare to benchmarks?",
    validation_notes: "Compute portfolio Sharpe and compare to SPY or a selected benchmark over same period.",
    required_apis: ["trading:/v2/account/portfolio/history", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Portfolio returns", "Benchmark (e.g., SPY) returns", "Risk-free rate and Sharpe calculation"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's my maximum drawdown over the past year?",
    status: "VALID",
    original_question: "What's my maximum drawdown over the past year?",
    validation_notes: "Use portfolio value history to compute peak-to-trough max drawdown for trailing 1Y.",
    required_apis: ["trading:/v2/account/portfolio/history"],
    data_requirements: ["Daily portfolio value series", "Peak/trough tracking", "Max drawdown metric"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which positions contribute most to my portfolio risk?",
    status: "NEEDS_REFINEMENT",
    original_question: "Which positions contribute most to my portfolio risk?",
    validation_notes: "Approximate risk contribution using weights × volatility or beta due to limited covariance data.",
    required_apis: ["trading:/v2/positions", "marketdata:/v2/stocks/bars", "eodhd:/fundamentals/{symbol}"],
    data_requirements: ["Position weights", "Per-asset volatility or beta", "Contribution scoring and ranking"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How correlated are my top 5 holdings?",
    status: "VALID",
    original_question: "How correlated are my top 5 holdings?",
    validation_notes: "Select top 5 by weight, compute pairwise correlation of returns over a window.",
    required_apis: ["trading:/v2/positions", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Top holdings by weight", "Historical returns time series", "Correlation matrix"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's my portfolio's tracking error versus the S&P 500?",
    status: "VALID",
    original_question: "What's my portfolio's tracking error versus the S&P 500?",
    validation_notes: "Tracking error is std dev of active returns vs S&P 500; compute from portfolio and SPY returns over same window.",
    required_apis: ["trading:/v2/account/portfolio/history", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Portfolio return series", "SPY return series", "Std dev of differences (active returns)"],
    validation_date: today,
    implementation_ready: true
  }
];

data.valid_questions.push(...additions);
fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
console.log('Appended', additions.length, 'entries to valid_questions.json');

