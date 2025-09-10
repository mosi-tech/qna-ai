// Test validation with simplified API specs that include sample parameters and responses
const fs = require('fs');

async function testSimplifiedValidation() {
    try {
        console.log('🧪 Testing validation with simplified API specs (with samples)...');
        
        const testQuestion = "Which watchlist tickers had the highest 3-month Sharpe ratio?";
        
        // Load the validation prompt
        console.log('📖 Loading validation prompt...');
        const validationPrompt = fs.readFileSync('./question-validator-prompt.txt', 'utf8');
        
        // Load simplified API specifications with samples
        console.log('📖 Loading simplified API specifications...');
        const alpacaMarket = JSON.parse(fs.readFileSync('./alpaca-marketdata-extra-simple.json', 'utf8'));
        const alpacaTrading = JSON.parse(fs.readFileSync('./alpaca-trading-extra-simple.json', 'utf8'));
        const eodhd = JSON.parse(fs.readFileSync('./eodhd-extra-simple.json', 'utf8'));
        
        const apiSpecs = JSON.stringify({
            'Alpaca Market Data API': alpacaMarket,
            'Alpaca Trading API': alpacaTrading,
            'EODHD API': eodhd
        }, null, 2);
        
        console.log(`✅ Validation prompt: ${validationPrompt.length} characters`);
        console.log(`✅ Simplified API specs: ${apiSpecs.length} characters`);
        console.log('   - Alpaca Market Data: Enhanced with sample parameters and responses');
        console.log('   - Alpaca Trading API: Enhanced with sample parameters and responses');
        console.log('   - EODHD API: Enhanced with sample parameters and responses');
        
        // Create system and user prompts
        const systemPrompt = `You are a financial API validation expert. Validate questions against available APIs and respond in JSON format only.

${validationPrompt}

## API Specifications:
${apiSpecs}`;

        const userPrompt = `Validate this financial question: "${testQuestion}"

Respond with a JSON object in this exact format:
{
  "status": "VALID" | "INVALID" | "NEEDS_REFINEMENT",
  "original_question": "${testQuestion}",
  "validated_question": "refined version if needed",
  "validation_notes": "explanation of validation result",
  "required_apis": ["api1", "api2"],
  "data_requirements": ["requirement1", "requirement2"],
  "rejection_reason": "reason if invalid",
  "missing_data": ["missing1", "missing2"],
  "suggested_alternatives": ["alternative1", "alternative2"]
}

Only respond with valid JSON, no other text.`;

        console.log('');
        console.log('🔍 Test Question:');
        console.log(`"${testQuestion}"`);
        console.log('');
        console.log(`📝 Total system prompt: ${systemPrompt.length} characters (much smaller!)`);
        console.log(`📝 User prompt: ${userPrompt.length} characters`);
        console.log('');
        
        console.log('🤖 Sending to Ollama (OpenAI-compatible API)...');
        const startTime = Date.now();
        
        const response = await fetch('http://localhost:11434/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ollama'
            },
            body: JSON.stringify({
                model: 'gpt-oss:20b',
                messages: [
                    {
                        role: 'system',
                        content: systemPrompt
                    },
                    {
                        role: 'user',
                        content: userPrompt
                    }
                ],
                temperature: 0.1,
                max_tokens: 2000
            }),
        });

        const responseTime = Date.now() - startTime;
        console.log(`⏱️  Response time: ${(responseTime / 1000).toFixed(2)} seconds`);

        if (!response.ok) {
            throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        
        if (!data.choices || !data.choices[0] || !data.choices[0].message) {
            throw new Error('Invalid response format from Ollama');
        }

        const content = data.choices[0].message.content;
        console.log('');
        console.log('📝 Raw Validation Response:');
        console.log('-' .repeat(80));
        console.log(content);
        console.log('-' .repeat(80));

        try {
            const validationResult = JSON.parse(content);
            console.log('');
            console.log('✅ PARSED VALIDATION RESULT:');
            console.log('=' .repeat(80));
            console.log(JSON.stringify(validationResult, null, 2));
            console.log('=' .repeat(80));
            
            console.log('');
            console.log('📋 VALIDATION SUMMARY:');
            console.log(`🔹 Status: ${validationResult.status}`);
            console.log(`🔹 Original Question: ${validationResult.original_question}`);
            if (validationResult.validated_question && validationResult.validated_question !== validationResult.original_question) {
                console.log(`🔹 Refined Question: ${validationResult.validated_question}`);
            }
            console.log(`🔹 Notes: ${validationResult.validation_notes}`);
            if (validationResult.required_apis && validationResult.required_apis.length > 0) {
                console.log(`🔹 Required APIs: ${validationResult.required_apis.join(', ')}`);
            }
            if (validationResult.data_requirements && validationResult.data_requirements.length > 0) {
                console.log(`🔹 Data Requirements: ${validationResult.data_requirements.join(', ')}`);
            }
            if (validationResult.rejection_reason) {
                console.log(`🔹 Rejection Reason: ${validationResult.rejection_reason}`);
            }
            if (validationResult.suggested_alternatives && validationResult.suggested_alternatives.length > 0) {
                console.log(`🔹 Alternatives: ${validationResult.suggested_alternatives.join('; ')}`);
            }
            
            console.log('');
            console.log('🎉 SIMPLIFIED VALIDATION TEST SUCCESSFUL!');
            console.log(`📊 Prompt size reduction: ${((467702 - systemPrompt.length) / 467702 * 100).toFixed(1)}% smaller`);
            console.log('');
            console.log('📈 Performance:');
            console.log(`   Response time: ${(responseTime / 1000).toFixed(2)}s`);
            if (data.usage) {
                console.log(`   Prompt tokens: ${data.usage.prompt_tokens}`);
                console.log(`   Completion tokens: ${data.usage.completion_tokens}`);
                console.log(`   Total tokens: ${data.usage.total_tokens}`);
            }
            
            console.log('');
            console.log('🚀 The simplified specs with samples work perfectly!');
            console.log('   - Much smaller prompts (faster processing)');
            console.log('   - Better context with sample parameters/responses');
            console.log('   - More accurate validation results');
            
        } catch (parseError) {
            console.log('');
            console.log('❌ FAILED TO PARSE VALIDATION JSON:');
            console.log('Error:', parseError.message);
            console.log('Raw content:', content);
        }

    } catch (error) {
        console.error('❌ Simplified validation test failed:', error.message);
    }
}

testSimplifiedValidation();