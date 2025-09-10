// Test single question validation with Ollama
const fs = require('fs');

async function testSingleValidation() {
    try {
        // Test question
        const testQuestion = "Which watchlist tickers had the highest 3-month Sharpe ratio?";
        
        console.log('🔍 Testing validation for:');
        console.log(`"${testQuestion}"`);
        console.log('');
        
        // Load validation prompt
        const validationPrompt = fs.readFileSync('./question-validator-prompt.txt', 'utf8');
        
        // Load API specs
        const alpacaMarket = JSON.parse(fs.readFileSync('./alpaca.marketdata.spec.json', 'utf8'));
        const alpacaTrading = JSON.parse(fs.readFileSync('./alpaca.trading.spec.json', 'utf8'));
        const eodhd = JSON.parse(fs.readFileSync('./EODHD.spec.json', 'utf8'));
        
        const apiSpecs = JSON.stringify({
            'Alpaca Market Data API': alpacaMarket,
            'Alpaca Trading API': alpacaTrading,
            'EODHD API': eodhd
        }, null, 2);
        
        // Create the prompt for Ollama
        const fullPrompt = `${validationPrompt}

## API Specifications:
${apiSpecs}

## Question to Validate:
"${testQuestion}"

Please validate this question and respond with a JSON object in the exact format specified in the prompt. Ensure the response is valid JSON.`;

        console.log('🤖 Sending to Ollama...');
        
        // Call Ollama API
        const response = await fetch('http://localhost:11434/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: 'gpt-oss:latest',
                prompt: fullPrompt,
                stream: false,
                options: {
                    temperature: 0.1,
                    top_p: 0.9,
                }
            }),
        });

        if (!response.ok) {
            throw new Error(`Ollama API error: ${response.statusText}`);
        }

        const data = await response.json();
        let resultText = data.response;

        console.log('📝 Raw Ollama Response:');
        console.log('=' .repeat(50));
        console.log(resultText);
        console.log('=' .repeat(50));
        console.log('');

        // Extract JSON from the response
        const jsonMatch = resultText.match(/\{[\s\S]*\}/);
        if (!jsonMatch) {
            console.log('❌ No JSON found in response');
            return;
        }

        try {
            const validationResult = JSON.parse(jsonMatch[0]);
            console.log('✅ Parsed Validation Result:');
            console.log(JSON.stringify(validationResult, null, 2));
            
            console.log('');
            console.log('📊 Summary:');
            console.log(`Status: ${validationResult.status}`);
            console.log(`Question: ${validationResult.original_question}`);
            if (validationResult.validated_question && validationResult.validated_question !== validationResult.original_question) {
                console.log(`Refined: ${validationResult.validated_question}`);
            }
            console.log(`Notes: ${validationResult.validation_notes}`);
            if (validationResult.required_apis) {
                console.log(`APIs: ${validationResult.required_apis.join(', ')}`);
            }
            if (validationResult.rejection_reason) {
                console.log(`Rejection: ${validationResult.rejection_reason}`);
            }
            if (validationResult.suggested_alternatives) {
                console.log(`Alternatives: ${validationResult.suggested_alternatives.join('; ')}`);
            }
        } catch (parseError) {
            console.log('❌ Failed to parse JSON:', parseError.message);
            console.log('Raw JSON:', jsonMatch[0]);
        }

    } catch (error) {
        console.error('❌ Validation test failed:', error.message);
    }
}

// Run the test
testSingleValidation();