const fs = require('fs');
const path = require('path');

function writeJSON(p, obj) {
  const dir = path.dirname(p);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(p, JSON.stringify(obj, null, 2));
}

function readJSON(p, fallback) {
  try {
    if (!fs.existsSync(p)) return fallback;
    const raw = fs.readFileSync(p, 'utf-8');
    if (!raw.trim()) return fallback;
    const v = JSON.parse(raw);
    return v;
  } catch {
    return fallback;
  }
}

function main() {
  const count = Number(process.argv[2] || 100);
  const expMetaPath = path.join(process.cwd(), 'data', 'experimental.json');
  const existing = readJSON(expMetaPath, []);
  const baseIdPrefix = 'acct-';

  const topics = [
    // Core account
    { key: 'buying-power', q: 'What is my current buying power?', apis: ['trading:/v2/account'] },
    { key: 'cash-balance', q: 'What is my current cash balance?', apis: ['trading:/v2/account'] },
    { key: 'portfolio-value', q: 'What is my current portfolio value (equity)?', apis: ['trading:/v2/account'] },
    { key: 'dtbp', q: 'What is my day trading buying power?', apis: ['trading:/v2/account'] },
    { key: 'multiplier', q: 'What is my current margin multiplier?', apis: ['trading:/v2/account'] },
    { key: 'status', q: 'What is my account status?', apis: ['trading:/v2/account'] },
    // Positions
    { key: 'positions-count', q: 'How many open positions do I have?', apis: ['trading:/v2/positions'] },
    { key: 'largest-position', q: 'Which open position has the highest market value?', apis: ['trading:/v2/positions'] },
    { key: 'unrealized-total', q: 'What is my total unrealized P&L across positions?', apis: ['trading:/v2/positions'] },
    { key: 'realized-30d', q: 'What are my realized gains/losses over the past 30 days?', apis: ['trading:/v2/account', 'trading:/v2/orders'] },
    // Orders
    { key: 'orders-open-count', q: 'How many open orders do I currently have?', apis: ['trading:/v2/orders'] },
    { key: 'orders-filled-7d', q: 'How many orders were filled in the last 7 days?', apis: ['trading:/v2/orders'] },
    { key: 'win-rate-30d', q: 'What is my trade win rate over the last 30 days?', apis: ['trading:/v2/orders'] },
    { key: 'avg-hold-days', q: 'What is my average holding period for closed positions over the last quarter?', apis: ['trading:/v2/orders'] },
    // Risk
    { key: 'exposure-long-short', q: 'What is my current long vs short dollar exposure?', apis: ['trading:/v2/positions'] },
    { key: 'margin-used', q: 'How much margin am I currently using?', apis: ['trading:/v2/account'] },
    { key: 'largest-drawdown-30d', q: 'What was my largest daily drawdown in the last 30 days?', apis: ['trading:/v2/account'] },
    // Misc
    { key: 'pdt-flag', q: 'Am I currently flagged as a pattern day trader?', apis: ['trading:/v2/account'] },
    { key: 'withdrawable-cash', q: 'How much cash is withdrawable right now?', apis: ['trading:/v2/account'] },
  ];

  // Expand to N by adding indexed variants (periods, slices)
  const horizons = [7, 14, 30, 60, 90];
  const items = [];
  for (let i = 0; items.length < count; i++) {
    const base = topics[i % topics.length];
    const h = horizons[Math.floor(i / topics.length) % horizons.length];
    const key = `${base.key}-${h}d`;
    const id = `${baseIdPrefix}${key}`;
    const name = `Account: ${base.key.replace(/-/g, ' ')} (${h}d)`;
    const question = base.q.replace('last 7 days', `last ${h} days`).replace('past 30 days', `past ${h} days`).replace('last quarter', `${h} days`).replace('currently', 'currently');
    const file = `experimental/${id}.json`;
    const output = `/${file}`;
    const description = `Account-focused metric: ${question}`;
    const workflow = [];
    // Build workflow per primary endpoint
    if (base.apis.includes('trading:/v2/account')) {
      workflow.push({ type: 'fetch', description: `Step 1: Fetch account snapshot via trading:/v2/account.` });
      if (/drawdown/i.test(question)) {
        workflow.push({ type: 'engine', description: `Step 2: Compute daily equity changes over ${h} days and find max drawdown.` });
      } else if (/realized/i.test(question)) {
        workflow.push({ type: 'fetch', description: `Step 2: Fetch closed orders via trading:/v2/orders with status=closed over ${h} days.` });
        workflow.push({ type: 'engine', description: `Step 3: Aggregate fills to compute realized P&L over ${h} days.` });
      } else {
        workflow.push({ type: 'compute', description: `Step 2: Extract and format the relevant field(s) from account.` });
      }
    }
    if (base.apis.includes('trading:/v2/positions')) {
      workflow.push({ type: 'fetch', description: `Step 1: Retrieve open positions via trading:/v2/positions.` });
      if (/unrealized/i.test(question)) {
        workflow.push({ type: 'compute', description: `Step 2: Sum unrealized_pl across positions to get the total.` });
      } else if (/largest market value/i.test(question)) {
        workflow.push({ type: 'compute', description: `Step 2: Identify the position with the highest market_value.` });
      } else if (/exposure/i.test(question)) {
        workflow.push({ type: 'engine', description: `Step 2: Aggregate market value by side (long/short) to get exposures.` });
      } else {
        workflow.push({ type: 'compute', description: `Step 2: Compute requested summary from positions.` });
      }
    }
    if (base.apis.includes('trading:/v2/orders')) {
      workflow.push({ type: 'fetch', description: `Step 1: Fetch orders via trading:/v2/orders filtered to the last ${h} days.` });
      if (/win rate/i.test(question)) {
        workflow.push({ type: 'engine', description: `Step 2: Label filled orders as win/loss from fills and compute win rate.` });
      } else if (/filled/i.test(question)) {
        workflow.push({ type: 'compute', description: `Step 2: Count orders with status=filled.` });
      } else if (/holding period/i.test(question)) {
        workflow.push({ type: 'engine', description: `Step 2: Match buy/sell pairs to compute holding days; average across positions.` });
      } else {
        workflow.push({ type: 'compute', description: `Step 2: Summarize requested metric from orders.` });
      }
    }

    const body = [
      { key: 'primary_value', value: 'to_be_computed', description: 'Primary metric answering the question.' },
      { key: 'context_1', value: 'to_be_computed', description: 'Supporting value for context.' },
      { key: 'data_sources', value: base.apis, description: 'APIs used for this analysis.' },
    ];

    items.push({ id, name, file, output, question, description, apis: base.apis, workflow, body });
  }

  // Write files and update metadata
  const newMeta = [...items.map(({ id, name, file, output, question, description, apis, workflow }) => ({ id, name, file, output, question, description, apis, workflow })), ...existing];
  writeJSON(expMetaPath, newMeta);

  // Create JSON files under experimental
  for (const it of items) {
    const jsonPath = path.join(process.cwd(), it.file);
    const jsonObj = {
      description: it.description,
      body: it.body,
    };
    writeJSON(jsonPath, jsonObj);
  }

  console.log(`Generated ${items.length} experimental account questions.`);
}

main();

