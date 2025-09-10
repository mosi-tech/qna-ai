const fs = require('fs');

const path = 'invalid_questions.json';
const data = JSON.parse(fs.readFileSync(path, 'utf8'));
const today = '2025-09-09';

const additions = [
  {
    question: "Which trading strategies work best for my risk profile?",
    rejection_reason: "Requires explicit risk profile definition and strategy taxonomy beyond available APIs; subjective selection needed.",
    missing_data: ["Risk profile measurement", "Strategy definitions and labeling of trades"],
    suggested_alternatives: ["What's my win rate by holding period?", "How does my P&L vary by time of day?"],
    validation_date: today,
    category: "subjective_assessment"
  }
];

data.invalid_questions.push(...additions);
fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
console.log('Appended', additions.length, 'entries to invalid_questions.json');

