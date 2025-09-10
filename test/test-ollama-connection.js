// Test Ollama connection separately
async function testOllamaConnection() {
    try {
        console.log('🔍 Testing Ollama connection...');
        
        // Test 1: Check if Ollama is running
        console.log('1. Checking if Ollama is running...');
        const tagsResponse = await fetch('http://localhost:11434/api/tags');
        
        if (!tagsResponse.ok) {
            throw new Error(`Ollama not responding: ${tagsResponse.status} ${tagsResponse.statusText}`);
        }
        
        const tagsData = await tagsResponse.json();
        console.log('✅ Ollama is running');
        console.log(`📦 Available models: ${tagsData.models?.map(m => m.name).join(', ') || 'none'}`);
        
        if (!tagsData.models || tagsData.models.length === 0) {
            throw new Error('No models available in Ollama');
        }
        
        // Test 2: Simple generation test
        const testModel = tagsData.models[0].name;
        console.log(`\n2. Testing simple generation with model: ${testModel}`);
        
        const generateResponse = await fetch('http://localhost:11434/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: testModel,
                prompt: 'Say "Hello, I am working!" in exactly 5 words.',
                stream: false,
                options: {
                    temperature: 0.1,
                }
            }),
        });
        
        if (!generateResponse.ok) {
            throw new Error(`Generation failed: ${generateResponse.status} ${generateResponse.statusText}`);
        }
        
        const generateData = await generateResponse.json();
        console.log('✅ Generation test successful');
        console.log(`📝 Response: "${generateData.response?.trim()}"`);
        
        // Test 3: JSON response test
        console.log(`\n3. Testing JSON response capability...`);
        
        const jsonTestResponse = await fetch('http://localhost:11434/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: testModel,
                prompt: 'Respond with a valid JSON object containing: {"status": "VALID", "message": "Test successful"}',
                stream: false,
                options: {
                    temperature: 0.1,
                }
            }),
        });
        
        if (!jsonTestResponse.ok) {
            throw new Error(`JSON test failed: ${jsonTestResponse.status} ${jsonTestResponse.statusText}`);
        }
        
        const jsonTestData = await jsonTestResponse.json();
        console.log('✅ JSON test response received');
        console.log(`📝 Raw response: "${jsonTestData.response?.trim()}"`);
        
        // Try to extract and parse JSON
        const jsonMatch = jsonTestData.response?.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            try {
                const parsed = JSON.parse(jsonMatch[0]);
                console.log('✅ JSON parsing successful:', parsed);
            } catch (e) {
                console.log('⚠️  JSON parsing failed:', e.message);
            }
        } else {
            console.log('⚠️  No JSON found in response');
        }
        
        console.log('\n🎉 Ollama connection test complete!');
        console.log(`💡 Recommended model for validation: ${testModel}`);
        
    } catch (error) {
        console.error('❌ Ollama connection test failed:', error.message);
        console.log('\n🔧 Troubleshooting:');
        console.log('1. Make sure Ollama is running: ollama serve');
        console.log('2. Check if models are installed: ollama list');
        console.log('3. Install a model if needed: ollama pull llama3.1');
        console.log('4. Verify Ollama is on port 11434: curl http://localhost:11434/api/tags');
    }
}

// Run the test
testOllamaConnection();