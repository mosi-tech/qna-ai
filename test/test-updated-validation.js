// Test the updated validation logic
async function testUpdatedValidation() {
    try {
        console.log('🧪 Testing updated validation logic...');
        
        const question = "Which watchlist tickers had the highest 3-month Sharpe ratio?";
        
        // Call our questions API to verify it's working
        const questionsResponse = await fetch('http://localhost:3000/api/questions');
        const questionsData = await questionsResponse.json();
        console.log(`📊 API check: ${questionsData.questions?.length || 0} questions available`);
        
        // Test adding a validation result to valid questions
        const testValidationResult = {
            question: question,
            status: "VALID",
            original_question: question,
            validation_notes: "Test validation using OpenAI-compatible API",
            required_apis: ["watchlist_api", "performance_api"],
            data_requirements: ["list_of_tickers", "historical_price_data_3_months", "risk_free_rate_data"],
            validation_date: new Date().toISOString().split('T')[0],
            implementation_ready: true
        };
        
        console.log('📝 Test validation result:');
        console.log(JSON.stringify(testValidationResult, null, 2));
        
        // Test adding to valid questions via API
        const addResponse = await fetch('http://localhost:3000/api/valid-questions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testValidationResult)
        });
        
        if (addResponse.ok) {
            console.log('✅ Successfully added test validation to valid questions');
            
            // Verify it was added
            const validResponse = await fetch('http://localhost:3000/api/valid-questions');
            const validData = await validResponse.json();
            console.log(`📈 Valid questions count: ${validData.valid_questions?.length || 0}`);
            
            // Show the last few valid questions
            if (validData.valid_questions && validData.valid_questions.length > 0) {
                const recent = validData.valid_questions.slice(-3);
                console.log('📋 Recent valid questions:');
                recent.forEach((q, i) => {
                    console.log(`  ${i + 1}. ${q.question}`);
                    console.log(`     Status: ${q.status}, APIs: ${q.required_apis?.join(', ') || 'none'}`);
                });
            }
        } else {
            console.log('❌ Failed to add test validation');
        }
        
        console.log('');
        console.log('🚀 Ready to test! Now you can:');
        console.log('1. Go to http://localhost:3000/validation');
        console.log('2. Model should be set to "gpt-oss:20b"');
        console.log('3. Click "Test Connection" - should work');
        console.log('4. Click "Validate All" to process questions with OpenAI-compatible API');
        console.log('5. Right panel should show validation results in real-time');
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
    }
}

testUpdatedValidation();