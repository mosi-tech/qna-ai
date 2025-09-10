const fs = require('fs');

const today = '2025-09-09';

function appendValid(entries) {
  const path = 'valid_questions.json';
  const data = JSON.parse(fs.readFileSync(path, 'utf8'));
  data.valid_questions.push(...entries);
  fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
  console.log('Appended', entries.length, 'validated items to valid_questions.json');
}

const additions = [
  {
    question: "Which of my holdings showed the strongest 3-month momentum?",
    status: "VALID",
    original_question: "Which of my holdings showed the strongest 3-month momentum?",
    validation_notes: "Compute 3-month total return for each holding and rank.",
    required_apis: ["trading:/v2/positions", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Portfolio symbols and weights", "3-month price history", "Return calculation and ranking"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which sector ETF outperformed SPY over the last 4 weeks?",
    status: "VALID",
    original_question: "Which sector ETF outperformed SPY over the last 4 weeks?",
    validation_notes: "Compare 4-week returns of sector ETFs vs SPY.",
    required_apis: ["marketdata:/v2/stocks/bars"],
    data_requirements: ["Sector ETF symbols (XLK, XLE, XLF, etc.)", "SPY bars", "4-week return comparison"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What is the rolling 30-day volatility of AAPL versus MSFT?",
    status: "VALID",
    original_question: "What is the rolling 30-day volatility of AAPL versus MSFT?",
    validation_notes: "Compute rolling standard deviation of daily returns over 30 trading days.",
    required_apis: ["marketdata:/v2/stocks/bars"],
    data_requirements: ["AAPL and MSFT daily bars", "Return series", "30-day rolling volatility"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which of my positions has the lowest correlation with SPY over the past year?",
    status: "VALID",
    original_question: "Which of my positions has the lowest correlation with SPY over the past year?",
    validation_notes: "Compute correlations between each holding's returns and SPY over 252 trading days.",
    required_apis: ["trading:/v2/positions", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Portfolio symbols", "SPY daily bars", "Correlation ranking"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What were the biggest intraday movers in the NASDAQ 100 today?",
    status: "NEEDS_REFINEMENT",
    original_question: "What were the biggest intraday movers in the NASDAQ 100 today?",
    validation_notes: "Refine to a supported universe (e.g., predefined NDX list or 'top NASDAQ movers') depending on screener capabilities.",
    required_apis: ["marketdata:/v1beta1/screener/stocks/movers", "marketdata:/v2/stocks/snapshots"],
    data_requirements: ["Universe filter (NDX constituents or NASDAQ exchange)", "Intraday % change", "Top movers selection"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which stocks had unusual volume today relative to their 30-day average?",
    status: "VALID",
    original_question: "Which stocks had unusual volume today relative to their 30-day average?",
    validation_notes: "Compute today's volume vs 30-day average volume and flag outliers.",
    required_apis: ["marketdata:/v2/stocks/bars", "marketdata:/v2/stocks/snapshots"],
    data_requirements: ["Today volume", "30-day avg volume", "Unusual volume threshold (e.g., >2×)"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How did my portfolio perform on the last three FOMC announcement days?",
    status: "NEEDS_REFINEMENT",
    original_question: "How did my portfolio perform on the last three FOMC announcement days?",
    validation_notes: "Use economic calendar FOMC dates and compute portfolio return on those dates; exact timing granularity may vary.",
    required_apis: ["eodhd:/economic-calendar", "trading:/v2/account/portfolio/history"],
    data_requirements: ["FOMC event dates", "Portfolio daily returns", "Event-day return extraction"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which of my holdings gapped up at the market open this week?",
    status: "VALID",
    original_question: "Which of my holdings gapped up at the market open this week?",
    validation_notes: "Detect open price > prior close for each day in the week for portfolio symbols.",
    required_apis: ["trading:/v2/positions", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Daily O/H/L/C per symbol", "Gap detection logic", "Week date range"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What is my portfolio’s 6-month exposure to the momentum factor (vs MTUM)?",
    status: "NEEDS_REFINEMENT",
    original_question: "What is my portfolio’s 6-month exposure to the momentum factor (vs MTUM)?",
    validation_notes: "Approximate exposure via correlation/regression between portfolio returns and MTUM over 6 months.",
    required_apis: ["trading:/v2/account/portfolio/history", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Portfolio return series", "MTUM return series", "Correlation/regression estimate"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which symbols in my watchlist have the highest 14-day RSI right now?",
    status: "VALID",
    original_question: "Which symbols in my watchlist have the highest 14-day RSI right now?",
    validation_notes: "Compute RSI(14) for each watchlist symbol and rank.",
    required_apis: ["trading:/v2/watchlists", "marketdata:/v2/stocks/bars", "eodhd:/technical/{symbol}"],
    data_requirements: ["Watchlist symbols", "Price history or technical endpoint", "RSI ranking"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which industries led performance within the S&P 500 this month?",
    status: "VALID",
    original_question: "Which industries led performance within the S&P 500 this month?",
    validation_notes: "Aggregate industry-level returns using constituents and rank leaders.",
    required_apis: ["eodhd:/screener", "marketdata:/v2/stocks/bars"],
    data_requirements: ["S&P 500 constituents with industries", "Monthly returns by industry", "Ranking"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What are the top gainers and losers in the Dow today?",
    status: "NEEDS_REFINEMENT",
    original_question: "What are the top gainers and losers in the Dow today?",
    validation_notes: "Use a maintained Dow 30 symbol list or screener filter; compute today's % change and rank.",
    required_apis: ["marketdata:/v2/stocks/snapshots", "marketdata:/v1beta1/screener/stocks/movers"],
    data_requirements: ["Dow 30 universe", "Intraday % change", "Top/bottom sorting"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which ETFs showed the strongest 1-week relative strength vs SPY?",
    status: "VALID",
    original_question: "Which ETFs showed the strongest 1-week relative strength vs SPY?",
    validation_notes: "Compute 1-week return for ETFs minus SPY and rank.",
    required_apis: ["marketdata:/v2/stocks/bars"],
    data_requirements: ["ETF list", "1-week returns", "Relative strength vs SPY rank"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which of my holdings has the highest beta to QQQ?",
    status: "VALID",
    original_question: "Which of my holdings has the highest beta to QQQ?",
    validation_notes: "Estimate beta via regression of holding returns vs QQQ returns.",
    required_apis: ["trading:/v2/positions", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Holding return series", "QQQ return series", "Beta estimation"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "How does my portfolio’s daily volatility compare to SPY this quarter?",
    status: "VALID",
    original_question: "How does my portfolio’s daily volatility compare to SPY this quarter?",
    validation_notes: "Compute standard deviation of daily returns for portfolio and SPY for the quarter.",
    required_apis: ["trading:/v2/account/portfolio/history", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Portfolio returns", "SPY returns", "Volatility comparison"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which tickers are above their 50-day but below their 200-day moving average?",
    status: "VALID",
    original_question: "Which tickers are above their 50-day but below their 200-day moving average?",
    validation_notes: "Compute 50DMA and 200DMA and filter for condition.",
    required_apis: ["marketdata:/v2/stocks/bars", "eodhd:/technical/{symbol}"],
    data_requirements: ["Historical prices", "SMA(50) and SMA(200)", "Screening condition"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "What was the average intraday range (ATR) of TSLA over the last 20 days?",
    status: "VALID",
    original_question: "What was the average intraday range (ATR) of TSLA over the last 20 days?",
    validation_notes: "Compute ATR(14/20) from OHLC bars over last 20 days.",
    required_apis: ["marketdata:/v2/stocks/bars", "eodhd:/technical/{symbol}"],
    data_requirements: ["TSLA OHLC bars", "ATR calculation", "20-day average"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which sector rotated from underperforming to outperforming in the past 2 weeks?",
    status: "VALID",
    original_question: "Which sector rotated from underperforming to outperforming in the past 2 weeks?",
    validation_notes: "Compare sector vs SPY relative returns week-over-week.",
    required_apis: ["marketdata:/v2/stocks/bars"],
    data_requirements: ["Sector ETF returns", "SPY returns", "Relative performance trend change"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which of my positions had the largest drawdown in the last 90 days?",
    status: "VALID",
    original_question: "Which of my positions had the largest drawdown in the last 90 days?",
    validation_notes: "Compute max peak-to-trough decline for each holding.",
    required_apis: ["trading:/v2/positions", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Holding price history", "Max drawdown per symbol", "Ranking"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which NASDAQ stocks printed new 20-day highs today?",
    status: "VALID",
    original_question: "Which NASDAQ stocks printed new 20-day highs today?",
    validation_notes: "Filter NASDAQ-listed symbols for new 20-day highs.",
    required_apis: ["eodhd:/screener", "marketdata:/v2/stocks/bars"],
    data_requirements: ["NASDAQ exchange filter", "20-day high detection", "Today filter"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which of my holdings are most correlated with USMV (low volatility)?",
    status: "VALID",
    original_question: "Which of my holdings are most correlated with USMV (low volatility)?",
    validation_notes: "Compute correlation between holdings' returns and USMV.",
    required_apis: ["trading:/v2/positions", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Holdings return series", "USMV return series", "Correlation ranking"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which symbols show persistent positive returns over the last 5 Mondays?",
    status: "VALID",
    original_question: "Which symbols show persistent positive returns over the last 5 Mondays?",
    validation_notes: "Filter daily bars by weekday and compute Monday returns sequence.",
    required_apis: ["marketdata:/v2/stocks/bars"],
    data_requirements: ["Daily bars for last 10 weeks", "Weekday filtering", "Return streak analysis"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which large-cap tech stocks had the biggest gap between open and close today?",
    status: "VALID",
    original_question: "Which large-cap tech stocks had the biggest gap between open and close today?",
    validation_notes: "Define large-cap tech via screener and compute |close-open| / open ranking.",
    required_apis: ["eodhd:/screener", "marketdata:/v2/stocks/snapshots"],
    data_requirements: ["Sector/market-cap filters", "Today OHLC or snapshots", "Gap magnitude ranking"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which of my holdings underperformed SPY in 8 of the last 10 weeks?",
    status: "VALID",
    original_question: "Which of my holdings underperformed SPY in 8 of the last 10 weeks?",
    validation_notes: "Compute weekly returns by holding vs SPY and count underperformance events.",
    required_apis: ["trading:/v2/positions", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Weekly return series", "SPY weekly returns", "Underperformance count threshold (>=8/10)"],
    validation_date: today,
    implementation_ready: true
  },
  {
    question: "Which watchlist names had the largest premarket volume spike today?",
    status: "NEEDS_REFINEMENT",
    original_question: "Which watchlist names had the largest premarket volume spike today?",
    validation_notes: "If premarket feed is limited, approximate using first minutes after open vs 30-day avg; otherwise use extended-hours data.",
    required_apis: ["trading:/v2/watchlists", "marketdata:/v2/stocks/snapshots", "marketdata:/v2/stocks/bars"],
    data_requirements: ["Premarket or early session volume", "Baseline 30-day avg volume", "Spike threshold and ranking"],
    validation_date: today,
    implementation_ready: true
  }
];

appendValid(additions);

