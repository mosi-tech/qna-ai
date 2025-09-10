const fs = require('fs');

const path = 'invalid_questions.json';
const data = JSON.parse(fs.readFileSync(path, 'utf8'));
const today = '2025-09-09';

const additions = [
  {
    question: "Am I on track to meet my college savings goals?",
    rejection_reason: "Requires personal goals, future contributions, tuition inflation assumptions beyond API scope.",
    missing_data: ["Savings goal amount and date", "Contribution plan", "Tuition inflation assumptions"],
    suggested_alternatives: ["What's my current 529/education account balance and return?", "What are lower-cost ETFs to reduce fees?"],
    validation_date: today,
    category: "personal_financial_planning"
  },
  {
    question: "How should I adjust my portfolio as I approach retirement?",
    rejection_reason: "Asset allocation advice requires individualized planning and risk preferences not provided by APIs.",
    missing_data: ["Risk tolerance", "Income needs", "Time horizon and constraints"],
    suggested_alternatives: ["What's my current equity/bond/cash allocation?", "How concentrated is my portfolio?"],
    validation_date: today,
    category: "advice_policy"
  },
  {
    question: "What's the optimal contribution to my 401k versus IRA?",
    rejection_reason: "Tax optimization and eligibility rules vary and require personal tax data beyond APIs.",
    missing_data: ["Tax bracket and deductions", "Employer match details", "IRA eligibility and limits"],
    suggested_alternatives: ["What's my current contribution rate?", "How much could I save by lowering fund expenses?"],
    validation_date: today,
    category: "tax_planning"
  },
  {
    question: "How much house can I afford with my current savings rate?",
    rejection_reason: "Home affordability requires income, debt, credit, mortgage rates, and expenses not available via these APIs.",
    missing_data: ["Income and debts", "Credit score and rates", "Housing expenses"],
    suggested_alternatives: ["What's my current savings rate?", "How have my savings grown over the last year?"],
    validation_date: today,
    category: "external_data_required"
  },
  {
    question: "What's my projected portfolio value at retirement?",
    rejection_reason: "Long-term projections require assumptions and forecasting beyond conservative API-based analysis.",
    missing_data: ["Expected returns and volatility", "Contribution schedule", "Withdrawal plans"],
    suggested_alternatives: ["What's my portfolio's historical annualized return?", "What's my fee drag based on current holdings?"],
    validation_date: today,
    category: "forecasting_assumptions"
  }
];

data.invalid_questions.push(...additions);
fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
console.log('Appended', additions.length, 'entries to invalid_questions.json');

