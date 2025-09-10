const fs = require('fs');

const path = 'invalid_questions.json';
const data = JSON.parse(fs.readFileSync(path, 'utf8'));
const today = '2025-09-09';

const additions = [
  {
    question: "Do I perform better when I follow my trading plan?",
    rejection_reason: "Requires explicit tagging of plan adherence per trade, which is not available via APIs.",
    missing_data: ["Trade-level plan adherence tags", "Defined trading plan criteria"],
    suggested_alternatives: ["How does my win rate change after rule-based entries?", "What is my P&L by holding-period buckets?"],
    validation_date: today,
    category: "missing_annotations"
  },
  {
    question: "How does my emotional state correlate with trading outcomes?",
    rejection_reason: "Emotional state is not captured by APIs; correlation requires external self-reported data.",
    missing_data: ["Time-stamped sentiment/mood logs", "Mapping to trades"],
    suggested_alternatives: ["Do winning streaks change my position sizes?", "How does trade frequency vary after losses?"],
    validation_date: today,
    category: "subjective_input_required"
  },
  {
    question: "How does my confidence level change after winning or losing streaks?",
    rejection_reason: "Confidence is subjective and not measured in the available data.",
    missing_data: ["Self-reported confidence logs", "Time alignment with activity"],
    suggested_alternatives: ["Do my position sizes change after streaks?", "Does trade frequency change after streaks?"],
    validation_date: today,
    category: "subjective_input_required"
  },
  {
    question: "What tax implications should I consider for my trading activity?",
    rejection_reason: "Tax advice requires jurisdiction-specific rules and personal tax data not provided by APIs.",
    missing_data: ["Tax residency and bracket", "Lot level tax data", "Tax rules for instruments"],
    suggested_alternatives: ["What's my realized short-term vs long-term gains this year?", "How many wash sale-flagged trades did I have?"],
    validation_date: today,
    category: "tax_advice"
  },
  {
    question: "How can I optimize my asset location across taxable and tax-advantaged accounts?",
    rejection_reason: "Asset location optimization requires tax constraints and multi-account modeling beyond API scope.",
    missing_data: ["Account tax status and rules", "Expected returns/yields by asset", "Optimization objectives"],
    suggested_alternatives: ["What's my income yield in taxable accounts?", "Which holdings generate most dividends/interest?"],
    validation_date: today,
    category: "tax_planning"
  }
];

data.invalid_questions.push(...additions);
fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
console.log('Appended', additions.length, 'entries to invalid_questions.json');

