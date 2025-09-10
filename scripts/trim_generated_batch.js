const fs = require('fs');

const path = 'generated_questions.json';
const data = JSON.parse(fs.readFileSync(path, 'utf8'));

// Remove first N questions from queue
const N = parseInt(process.argv[2] || '0', 10);
if (!Number.isFinite(N) || N <= 0) {
  console.error('Provide a positive integer N to trim.');
  process.exit(1);
}

data.questions = data.questions.slice(N);
fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
console.log('Trimmed', N, 'questions. Remaining:', data.questions.length);

