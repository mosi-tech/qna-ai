const fs = require('fs');

const path = 'invalid_questions.json';
const data = JSON.parse(fs.readFileSync(path, 'utf8'));
const today = '2025-09-09';

const additions = [
  {
    question: "What cognitive biases show up in my trading patterns?",
    rejection_reason: "Identifying cognitive biases requires psychological assessment beyond available trading and market APIs.",
    missing_data: ["Psychometric inputs", "Behavioral assessment framework"],
    suggested_alternatives: [
      "Do I buy more after recent price run-ups?",
      "Do I hold losers longer than winners?"
    ],
    validation_date: today,
    category: "behavioral_assessment"
  },
  {
    question: "How does my confidence level correlate with trading frequency?",
    rejection_reason: "Confidence level is a subjective input not captured by APIs; cannot quantify without external self-reports.",
    missing_data: ["Self-reported confidence metric", "Time-aligned survey data"],
    suggested_alternatives: [
      "How does my trading frequency vary with recent returns?",
      "Do winning streaks increase my trade count?"
    ],
    validation_date: today,
    category: "subjective_input_required"
  }
];

data.invalid_questions.push(...additions);
fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
console.log('Appended', additions.length, 'entries to invalid_questions.json');

