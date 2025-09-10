// Simple test of two-stage validation approach
const fs = require('fs');

async function testTwoStageSimple() {
    try {
        console.log('🎯 Two-Stage Validation Test');
        console.log('=' .repeat(50));
        
        const testQuestion = "What are my largest portfolio positions?";
        
        // Load requirement generation prompt
        const requirementPrompt = fs.readFileSync('./api-requirement-generator-prompt.txt', 'utf8');
        
        console.log(`Question: "${testQuestion}"`);
        console.log(`Prompt length: ${requirementPrompt.length} chars`);
        console.log('');
        
        // STAGE 1: Generate requirements
        console.log('🔍 STAGE 1: Generate API Requirements');
        console.log('-' .repeat(30));
        
        const userPrompt = `Analyze this financial question and determine what APIs and data would be needed: "${testQuestion}"`;
        
        const response = await fetch('http://localhost:11434/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ollama'
            },
            body: JSON.stringify({
                model: 'gpt-oss:20b',
                messages: [
                    { role: 'system', content: requirementPrompt },
                    { role: 'user', content: userPrompt }
                ],
                temperature: 0.1,
                max_tokens: 1500
            }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        const content = data.choices[0].message.content;
        
        console.log('Generated Requirements:');
        console.log(content);
        
        try {
            const requirements = JSON.parse(content);
            console.log('');
            console.log('✅ Parsed successfully!');
            console.log(`📊 Data requirements: ${requirements.data_requirements?.length || 0}`);
            console.log(`📊 Required endpoints: ${requirements.required_endpoints?.length || 0}`);
            console.log(`📊 Calculation steps: ${requirements.calculation_steps?.length || 0}`);
        } catch (e) {
            console.log('❌ JSON parsing failed');
        }
        
        console.log('');
        console.log('🎉 Stage 1 complete! Next step would be matching against available APIs.');
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
    }
}

testTwoStageSimple();