const fs = require('fs');

const today = '2025-09-09';

function appendValid(entries) {
  const path = 'valid_questions.json';
  const data = JSON.parse(fs.readFileSync(path, 'utf8'));
  data.valid_questions.push(...entries);
  fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
  console.log('Appended', entries.length, 'validated items to valid_questions.json');
}

const V = (q, notes, apis, reqs) => ({
  question: q,
  status: 'VALID',
  original_question: q,
  validation_notes: notes,
  required_apis: apis,
  data_requirements: reqs,
  validation_date: today,
  implementation_ready: true,
});

const R = (q, notes, apis, reqs) => ({
  question: q,
  status: 'NEEDS_REFINEMENT',
  original_question: q,
  validation_notes: notes,
  required_apis: apis,
  data_requirements: reqs,
  validation_date: today,
  implementation_ready: true,
});

const additions = [
  V(
    'Which sector ETFs have the lowest 21-day volatility right now?',
    'Compute 21-day realized volatility for sector ETFs and rank lowest.',
    ['marketdata:/v2/stocks/bars'],
    ['Sector ETF symbols', '21-day return std dev', 'Ranking by volatility']
  ),
  V(
    'Which of my holdings are most negatively correlated with TLT?',
    'Compute correlation of holdings returns vs TLT over a chosen window.',
    ['trading:/v2/positions', 'marketdata:/v2/stocks/bars'],
    ['Portfolio symbols', 'TLT return series', 'Correlation ranking (most negative)']
  ),
  R(
    'Which mega-cap stocks led upside on above-average volume today?',
    'Use market-cap filter for mega-caps and flag names with strong % change and volume > 1.5× 30-day avg.',
    ['eodhd:/screener', 'marketdata:/v2/stocks/snapshots', 'marketdata:/v2/stocks/bars'],
    ['Mega-cap universe filter', 'Today % change', 'Volume vs 30-day avg threshold']
  ),
  V(
    'Which tickers showed a breakout above their 100-day high?',
    'Detect new 100-day highs and list symbols breaking out.',
    ['marketdata:/v2/stocks/bars'],
    ['Historical highs over 100 days', 'Today high/close', 'Breakout condition']
  ),
  R(
    'Which of my positions had the most consistent weekly gains this quarter?',
    'Define consistency as highest fraction of up weeks or lowest variance of weekly returns; compute and rank.',
    ['trading:/v2/positions', 'marketdata:/v2/stocks/bars'],
    ['Weekly returns per holding', 'Up-week hit rate or variance', 'Quarter window']
  ),
  V(
    'Which industries saw the biggest breadth improvement this week?',
    'Compute industry-level advancers/decliners across constituents and compare WoW changes.',
    ['eodhd:/screener', 'marketdata:/v2/stocks/snapshots'],
    ['Constituents by industry', 'Advancers vs decliners counts', 'Week-over-week breadth delta']
  ),
  V(
    'Which semiconductors had the largest 3-day gain following earnings windows?',
    'Identify semiconductor names and calculate 3-day post-earnings returns; rank by gain.',
    ['eodhd:/screener', 'eodhd:/calendar/earnings', 'marketdata:/v2/stocks/bars'],
    ['Semiconductor universe', 'Earnings dates', '3-day post-event return ranking']
  ),
  R(
    'Which of my holdings showed increasing momentum for 4 straight weeks?',
    'Define momentum (e.g., weekly ROC) and test monotonic increase over 4 weeks.',
    ['trading:/v2/positions', 'marketdata:/v2/stocks/bars'],
    ['Weekly momentum metric', '4-week monotonicity check', 'Qualified holdings list']
  ),
  V(
    'Which symbols showed the steepest decline in realized volatility this month?',
    'Compute month-over-month change in realized vol and rank by largest decline.',
    ['marketdata:/v2/stocks/bars'],
    ['Two adjacent monthly windows', 'Realized vol per window', 'Delta ranking']
  ),
  V(
    'Which ETFs most closely tracked SPY over the past year (lowest tracking error proxy)?',
    'Compute std dev of active returns (ETF minus SPY) as tracking error proxy and rank.',
    ['marketdata:/v2/stocks/bars'],
    ['ETF list', 'SPY returns', 'Std dev of active returns']
  ),
  V(
    'Which of my holdings are most sensitive to market selloffs (worst on SPY down days)?',
    'Filter SPY down days and compute average/median holding return; rank worst performers.',
    ['trading:/v2/positions', 'marketdata:/v2/stocks/bars'],
    ['Identify SPY down days', 'Holding returns on those days', 'Sensitivity ranking']
  ),
  V(
    'Which tickers had five consecutive green closes?',
    'Detect sequences of five consecutive positive close-to-close returns.',
    ['marketdata:/v2/stocks/bars'],
    ['Daily close series', 'Consecutive positive return streak detection']
  ),
  V(
    'Which of my positions recovered fastest after the last 5% SPY drawdown?',
    'Detect last SPY 5% peak-to-trough drawdown; compute time-to-recover or % off low recovery for holdings.',
    ['marketdata:/v2/stocks/bars', 'trading:/v2/positions'],
    ['SPY drawdown window', 'Holding performance post-drawdown', 'Recovery speed ranking']
  ),
  V(
    'Which watchlist symbols have the strongest 12-week relative strength rank?',
    'Compute 12-week returns for watchlist tickers and rank by RS.',
    ['trading:/v2/watchlists', 'marketdata:/v2/stocks/bars'],
    ['Watchlist symbols', '12-week returns', 'RS ranking']
  ),
  V(
    'Which sector ETFs had the highest up/down capture ratio vs SPY YTD?',
    'Compute average returns on SPY up vs down days for sector ETFs; ratio vs SPY.',
    ['marketdata:/v2/stocks/bars'],
    ['SPY up/down day classification', 'Sector ETF returns per group', 'Capture ratio calculation']
  ),
  R(
    'Which of my holdings show negative momentum divergence (price up, momentum down)?',
    'Define divergence using price vs RSI/MACD slope; flag holdings with rising price and weakening momentum.',
    ['trading:/v2/positions', 'marketdata:/v2/stocks/bars', 'eodhd:/technical/{symbol}'],
    ['Price trend detection', 'Momentum indicator slope', 'Divergence flagging']
  ),
  V(
    'Which names posted the largest bullish outside day candles this week?',
    'Detect bullish outside days from OHLC bars and rank by range/close strength.',
    ['marketdata:/v2/stocks/bars'],
    ['Daily OHLC bars', 'Outside day condition', 'Bullish variant detection and ranking']
  ),
  V(
    'Which of my positions spent the most days above the 50-day MA this year?',
    'Count days closing above SMA(50) for each holding YTD and rank.',
    ['trading:/v2/positions', 'marketdata:/v2/stocks/bars', 'eodhd:/technical/{symbol}'],
    ['SMA(50) per day', 'Daily close vs SMA(50)', 'Count and ranking']
  ),
  R(
    'Which symbols in the S&P 500 had the largest 1-hour move after the open today?',
    'Use S&P 500 constituent list and 60-minute bars from market open to compute first-hour return; rank.',
    ['eodhd:/screener', 'marketdata:/v2/stocks/bars'],
    ['S&P 500 symbols', 'First-hour bar returns', 'Largest move ranking']
  ),
  V(
    'Which of my holdings lagged their industry peers the most last month?',
    'Compute last-month return by holding and compare to industry median/mean; rank laggards.',
    ['trading:/v2/positions', 'eodhd:/screener', 'marketdata:/v2/stocks/bars'],
    ['Industry classification', 'Monthly returns', 'Peer relative underperformance']
  ),
  V(
    'Which ETFs showed the steepest 3-month trend slope?',
    'Estimate 3-month trend slope via linear regression or ROC and rank.',
    ['marketdata:/v2/stocks/bars'],
    ['ETF symbols', '3-month price series', 'Trend slope calculation']
  ),
  V(
    'Which of my positions have the smallest average intraday range?',
    'Compute average (high - low)/midprice per day over a window and rank.',
    ['trading:/v2/positions', 'marketdata:/v2/stocks/bars'],
    ['Daily high/low', 'Average intraday range metric', 'Ranking']
  ),
  V(
    'Which tickers had the largest positive earnings-day drift over the next 3 sessions?',
    'Identify earnings day and compute cumulative return over next 3 sessions; rank by drift.',
    ['eodhd:/calendar/earnings', 'marketdata:/v2/stocks/bars'],
    ['Earnings calendar', 'Post-earnings 3-day cumulative return', 'Ranking']
  ),
  V(
    'Which of my holdings show the highest correlation with MTUM?',
    'Compute correlation between each holding and MTUM over a specified window.',
    ['trading:/v2/positions', 'marketdata:/v2/stocks/bars'],
    ['Holding return series', 'MTUM return series', 'Correlation ranking']
  ),
  R(
    'Which symbols showed repeated failed breakouts in the past month?',
    'Define failed breakout (e.g., close above prior high then closing back below within 3 days) and count occurrences.',
    ['marketdata:/v2/stocks/bars'],
    ['Prior high identification', 'Breakout then failure condition', 'Count repeats over a month']
  ),
];

appendValid(additions);

