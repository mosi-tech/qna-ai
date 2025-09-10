const fs = require('fs');

const path = 'invalid_questions.json';
const data = JSON.parse(fs.readFileSync(path, 'utf8'));

const today = '2025-09-09';

const additions = [
  {
    question: "Am I saving enough for my retirement goals?",
    rejection_reason: "Requires personalized financial planning assumptions (income, spending, target retirement age, returns) beyond available APIs.",
    missing_data: [
      "Personal income and expense projections",
      "Retirement goal parameters and constraints",
      "Long-term return and inflation assumptions"
    ],
    suggested_alternatives: [
      "What's my portfolio's historical annualized return?",
      "What's my current savings rate relative to my income?"
    ],
    validation_date: today,
    category: "personal_financial_planning"
  },
  {
    question: "How much should I allocate to my emergency fund?",
    rejection_reason: "Emergency fund sizing is a financial planning guideline and needs personal expense data not available via APIs.",
    missing_data: [
      "Monthly living expenses",
      "Job stability and income volatility",
      "Desired months of coverage"
    ],
    suggested_alternatives: [
      "What's my average monthly spending inferred from cash flows?",
      "What's my current cash balance as a percentage of portfolio?"
    ],
    validation_date: today,
    category: "personal_financial_planning"
  },
  {
    question: "What's my target allocation for my age group?",
    rejection_reason: "Target allocations by age are planning heuristics, not derivable from market/trading APIs.",
    missing_data: [
      "Age and risk profile",
      "Financial goals and time horizon",
      "Planning rule selection (e.g., 110-age heuristic)"
    ],
    suggested_alternatives: [
      "What's my current equity/bond/cash allocation?",
      "How does my allocation compare to a chosen benchmark?"
    ],
    validation_date: today,
    category: "planning_guidelines"
  },
  {
    question: "Should I rebalance my portfolio quarterly or annually?",
    rejection_reason: "Requires policy design and personal constraints; APIs provide data but not prescriptive policy recommendations.",
    missing_data: [
      "Policy preferences and tax constraints",
      "Transaction cost tolerance",
      "Tracking error tolerance"
    ],
    suggested_alternatives: [
      "How far is my current allocation from targets?",
      "What are the transaction costs to rebalance today?"
    ],
    validation_date: today,
    category: "policy_recommendation"
  },
  {
    question: "How does my risk tolerance align with my time horizon?",
    rejection_reason: "Needs subjective risk tolerance inputs and life planning data not available in APIs.",
    missing_data: [
      "Risk tolerance assessment",
      "Time horizon and liquidity needs",
      "Income and liability profile"
    ],
    suggested_alternatives: [
      "What's my portfolio volatility and max drawdown?",
      "How concentrated is my portfolio in risky assets?"
    ],
    validation_date: today,
    category: "subjective_assessment"
  }
];

data.invalid_questions.push(...additions);
fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
console.log('Appended', additions.length, 'entries to invalid_questions.json');

