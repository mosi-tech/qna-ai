const fs = require('fs');

const pathValid = 'valid_questions.json';
const valid = JSON.parse(fs.readFileSync(pathValid, 'utf8'));
const today = '2025-09-09';

const additions = [
  {
    question: "Which stocks have the strongest price momentum right now?",
    status: "VALID",
    original_question: "Which stocks have the strongest price momentum right now?",
    validation_notes: "Rank by short/medium-term returns or RSI using market bars and/or screeners.",
    required_apis: ["marketdata:/v1beta1/screener/stocks/movers", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Universe of candidates", "Momentum metric (1M/3M/RSI)", "Ranking"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What sectors are outperforming the broader market?",
    status: "VALID",
    original_question: "What sectors are outperforming the broader market?",
    validation_notes: "Compare sector ETF returns vs SPY over selected window.",
    required_apis: ["marketdata:/v2/stocks/bars"],
    data_requirements: ["Sector ETF symbols", "Return calculation", "Outperformance vs SPY"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How does market breadth look for today's session?",
    status: "NEEDS_REFINEMENT",
    original_question: "How does market breadth look for today's session?",
    validation_notes: "Approximate breadth via advancers/decliners among screener universe and volume leaders; full exchange-wide breadth may be limited.",
    required_apis: ["marketdata:/v1beta1/screener/stocks/movers", "marketdata:/v2/stocks/snapshots"],
    data_requirements: ["Advancers/decliners counts", "Volume confirmation", "Intraday snapshot data"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which stocks are making new highs with volume confirmation?",
    status: "NEEDS_REFINEMENT",
    original_question: "Which stocks are making new highs with volume confirmation?",
    validation_notes: "Define volume confirmation threshold (e.g., >1.5x 30-day avg volume) alongside new 52-week high.",
    required_apis: ["marketdata:/v2/stocks/bars", "marketdata:/v2/stocks/snapshots"],
    data_requirements: ["52-week highs", "Current/average volume", "Threshold filter"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's the advance-decline ratio telling us about market health?",
    status: "NEEDS_REFINEMENT",
    original_question: "What's the advance-decline ratio telling us about market health?",
    validation_notes: "Compute A/D ratio from available screener universe; interpret as breadth signal with caveats.",
    required_apis: ["marketdata:/v1beta1/screener/stocks/movers", "marketdata:/v2/stocks/snapshots"],
    data_requirements: ["Advancers vs decliners counts", "Intraday change data", "Ratio calculation"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How does my portfolio's alpha generation compare to the market?",
    status: "NEEDS_REFINEMENT",
    original_question: "How does my portfolio's alpha generation compare to the market?",
    validation_notes: "Estimate alpha as excess return vs SPY or via CAPM regression; specify window and risk-free assumption.",
    required_apis: ["trading:/v2/account/portfolio/history", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Portfolio and SPY returns", "Risk-free rate (assumed/constant)", "Excess return or regression alpha"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's my information ratio for active management decisions?",
    status: "VALID",
    original_question: "What's my information ratio for active management decisions?",
    validation_notes: "Information ratio = mean active return / tracking error vs benchmark over a specified window.",
    required_apis: ["trading:/v2/account/portfolio/history", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Active return series", "Tracking error (std dev of active returns)", "Window selection"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which holdings have the highest correlation with market volatility?",
    status: "NEEDS_REFINEMENT",
    original_question: "Which holdings have the highest correlation with market volatility?",
    validation_notes: "Use SPY realized volatility as a proxy for market vol; correlate holding returns with that series.",
    required_apis: ["trading:/v2/positions", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Holding return series", "SPY realized vol series", "Correlation calculation"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How does my portfolio perform during market stress periods?",
    status: "NEEDS_REFINEMENT",
    original_question: "How does my portfolio perform during market stress periods?",
    validation_notes: "Define stress as SPY drawdowns > X% over Y days; compute portfolio returns during those windows.",
    required_apis: ["trading:/v2/account/portfolio/history", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Drawdown window detection", "Portfolio returns in stress windows", "Comparison to baseline"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What's my upside versus downside capture ratio?",
    status: "VALID",
    original_question: "What's my upside versus downside capture ratio?",
    validation_notes: "Compute portfolio average returns on SPY up days vs down days relative to SPY's averages.",
    required_apis: ["trading:/v2/account/portfolio/history", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Classification of market up/down days", "Portfolio returns per group", "Capture ratio calculation"],
    validation_date: today,
    implementation_ready: true
  }
];

valid.valid_questions.push(...additions);
fs.writeFileSync(pathValid, JSON.stringify(valid, null, 2) + '\n');
console.log('Appended', additions.length, 'entries to valid_questions.json');

