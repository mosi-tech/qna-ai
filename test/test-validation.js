// Test validation API with a sample question
const fs = require('fs');

async function testValidation() {
    try {
        // Test question
        const testQuestion = "Which watchlist tickers had the highest 3-month Sharpe ratio?";
        
        console.log('🔍 Testing validation for question:');
        console.log(`"${testQuestion}"`);
        console.log('');
        
        // Test API call to questions endpoint
        console.log('📊 Testing questions API...');
        const questionsResponse = await fetch('http://localhost:3000/api/questions');
        const questionsData = await questionsResponse.json();
        console.log(`✅ Questions API: ${questionsData.questions?.length || 0} questions loaded`);
        
        // Test API call to valid-questions endpoint
        console.log('📊 Testing valid-questions API...');
        const validResponse = await fetch('http://localhost:3000/api/valid-questions');
        const validData = await validResponse.json();
        console.log(`✅ Valid questions API: ${validData.valid_questions?.length || 0} valid questions`);
        
        // Test API call to invalid-questions endpoint
        console.log('📊 Testing invalid-questions API...');
        const invalidResponse = await fetch('http://localhost:3000/api/invalid-questions');
        const invalidData = await invalidResponse.json();
        console.log(`✅ Invalid questions API: ${invalidData.invalid_questions?.length || 0} invalid questions`);
        
        // Test Ollama connection
        console.log('🤖 Testing Ollama connection...');
        try {
            const ollamaResponse = await fetch('http://localhost:11434/api/tags');
            if (ollamaResponse.ok) {
                const ollamaData = await ollamaResponse.json();
                console.log(`✅ Ollama connected: ${ollamaData.models?.length || 0} models available`);
                if (ollamaData.models?.length > 0) {
                    console.log(`   Models: ${ollamaData.models.map(m => m.name).join(', ')}`);
                }
            } else {
                console.log('❌ Ollama connection failed');
            }
        } catch (error) {
            console.log('❌ Ollama not accessible:', error.message);
        }
        
        console.log('');
        console.log('🚀 Test complete! You can now:');
        console.log('1. Go to http://localhost:3000/validation');
        console.log('2. Click "Test Connection" to verify Ollama');
        console.log('3. Click "Validate All" to start processing questions');
        
    } catch (error) {
        console.error('❌ Test failed:', error);
    }
}

// Run the test
testValidation();