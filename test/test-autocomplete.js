// Test script for autocomplete suggestions using simplified API specs and same validation prompt
const fs = require('fs');

async function testAutocomplete() {
  try {
    const input = process.argv.slice(2).join(' ') || 'Find ideas related to ETF performance analysis';

    console.log('🧪 Testing autocomplete suggestions...');
    console.log('🔎 Input:', input);

    // Load validation prompt and simplified API specs
    const validationPrompt = fs.readFileSync('./question-validator-prompt.txt', 'utf8');
    const alpacaMarket = JSON.parse(fs.readFileSync('./alpaca-marketdata-simple.json', 'utf8'));
    const alpacaTrading = JSON.parse(fs.readFileSync('./alpaca-trading-simple.json', 'utf8'));
    const eodhd = JSON.parse(fs.readFileSync('./eodhd-simple.json', 'utf8'));

    const specsObj = {
      'Alpaca Market Data API': alpacaMarket,
      'Alpaca Trading API': alpacaTrading,
      'EODHD API': eodhd,
    };
    const apiSpecs = JSON.stringify(specsObj, null, 2);

    const systemPrompt = `You are a financial API validation and suggestion assistant. 
Use the validation guidance and API specifications to determine what is feasible. 
Given a user question, propose 5 top alternative questions that are likely answerable using ONLY the available APIs.
Return strictly JSON, no extra text.

${validationPrompt}

## API Specifications:
${apiSpecs}`;

    const userPrompt = `User question: "${input}"

Produce exactly this JSON schema:
{
  "suggestions": [
    {
      "question": "string",
      "reason": "why this is answerable with available APIs",
      "required_apis": ["api1", "api2"]
    }
  ]
}
Rules:
- Provide exactly 5 suggestions.
- Avoid duplicates; be specific and practically queryable.
- Ensure each suggestion is feasible using the listed APIs.
- No prose outside the JSON.`;

    console.log('📝 System prompt length:', systemPrompt.length);

    const startTime = Date.now();
    const response = await fetch('http://localhost:11434/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ollama',
      },
      body: JSON.stringify({
        model: 'gpt-oss:20b',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
        temperature: 0.3,
        max_tokens: 1200,
      }),
    });

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`⏱️  Response time: ${elapsed}s`);

    if (!response.ok) {
      throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    const content = data?.choices?.[0]?.message?.content;
    if (!content) {
      throw new Error('Invalid response format from Ollama');
    }

    console.log('');
    console.log('📝 Raw Suggestions Response:');
    console.log('-'.repeat(80));
    console.log(content);
    console.log('-'.repeat(80));

    try {
      const parsed = JSON.parse(content);
      console.log('');
      console.log('✅ PARSED SUGGESTIONS:');
      console.log('='.repeat(80));
      console.log(JSON.stringify(parsed, null, 2));
      console.log('='.repeat(80));

      console.log('');
      console.log('📋 SUMMARY (Top 5):');
      (parsed.suggestions || []).slice(0, 5).forEach((s, i) => {
        console.log(` ${i + 1}. ${s.question}`);
        if (s.required_apis?.length) console.log(`    APIs: ${s.required_apis.join(', ')}`);
      });
    } catch (e) {
      console.log('❌ Failed to parse JSON. See raw content above.');
    }
  } catch (err) {
    console.error('❌ Autocomplete test failed:', err.message);
  }
}

testAutocomplete();

