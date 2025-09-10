// Test OpenAI-compatible API with Ollama
async function testOpenAICompatible() {
    try {
        console.log('🔍 Testing OpenAI-compatible API with Ollama...');
        
        const testQuestion = "Which watchlist tickers had the highest 3-month Sharpe ratio?";
        
        const response = await fetch('http://localhost:11434/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ollama' // Dummy key
            },
            body: JSON.stringify({
                model: 'gpt-oss:20b',
                messages: [
                    {
                        role: 'system',
                        content: 'You are a financial API validation expert. Validate questions against available APIs and respond in JSON format only.'
                    },
                    {
                        role: 'user',
                        content: `Validate this financial question: "${testQuestion}"

Respond with a JSON object in this exact format:
{
  "status": "VALID",
  "original_question": "${testQuestion}",
  "validation_notes": "Your explanation here",
  "required_apis": ["api1", "api2"],
  "data_requirements": ["requirement1", "requirement2"]
}

Only respond with valid JSON, no other text.`
                    }
                ],
                temperature: 0.1,
                max_tokens: 1000
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        
        console.log('✅ OpenAI-compatible API response:');
        console.log('Raw response:', JSON.stringify(data, null, 2));
        
        if (data.choices && data.choices[0] && data.choices[0].message) {
            const content = data.choices[0].message.content;
            console.log('📝 Message content:');
            console.log(content);
            
            // Try to parse as JSON
            try {
                const validationResult = JSON.parse(content);
                console.log('✅ Parsed validation result:');
                console.log(JSON.stringify(validationResult, null, 2));
            } catch (parseError) {
                console.log('⚠️  Content is not valid JSON, raw content shown above');
            }
        }
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
    }
}

testOpenAICompatible();