// Robust test with JSON cleaning for two-stage validation
const fs = require('fs');
const MODEL = 'gpt-oss:20b';

// Helper function to clean JSON response from markdown or extra text
function cleanJsonResponse(content) {
    try {
        // First try direct parsing
        return JSON.parse(content);
    } catch (e) {
        // If it fails, try to extract JSON from markdown code blocks
        let cleaned = content;
        
        // Remove markdown code blocks
        cleaned = cleaned.replace(/```json\s*/g, '');
        cleaned = cleaned.replace(/```\s*/g, '');
        
        // Try to find JSON object boundaries
        const startIndex = cleaned.indexOf('{');
        const endIndex = cleaned.lastIndexOf('}');
        
        if (startIndex >= 0 && endIndex >= 0 && endIndex > startIndex) {
            cleaned = cleaned.substring(startIndex, endIndex + 1);
        }
        
        // Remove any leading/trailing whitespace or text
        cleaned = cleaned.trim();
        
        return JSON.parse(cleaned);
    }
}

async function testTwoStageRobust() {
    try {
        console.log('🎯 Robust Two-Stage Validation Test');
        console.log('=' .repeat(60));
        
        const testQuestion = "What is my account top position by returns?";
        
        // Load prompts
        const requirementPrompt = fs.readFileSync('./api-requirement-generator-prompt.txt', 'utf8');
        const matcherPrompt = fs.readFileSync('./api-availability-matcher-prompt.txt', 'utf8');
        
        console.log(`Question: "${testQuestion}"`);
        console.log('');
        
        // STAGE 1: Generate Requirements
        console.log('🔍 STAGE 1: Generate API Requirements');
        console.log('-' .repeat(40));
        
        const requirementUserPrompt = `Analyze this financial question and determine what APIs and data would be needed: "${testQuestion}"

IMPORTANT: Respond with ONLY a JSON object, no markdown formatting, no code blocks.`;

        console.log('🤖 Generating requirements...');
        const requirementResponse = await fetch('http://localhost:11434/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ollama'
            },
            body: JSON.stringify({
                model: MODEL,
                messages: [
                    { role: 'system', content: requirementPrompt },
                    { role: 'user', content: requirementUserPrompt }
                ],
                temperature: 0.1,
                max_tokens: 1500
            }),
        });

        if (!requirementResponse.ok) {
            throw new Error(`API error: ${requirementResponse.status} ${requirementResponse.statusText}`);
        }

        const requirementData = await requirementResponse.json();
        const requirementContent = requirementData.choices[0].message.content;
        
        console.log('Raw response length:', requirementContent.length);
        console.log('Raw response preview:', requirementContent.substring(0, 200) + '...');
        
        let requirements;
        try {
            requirements = cleanJsonResponse(requirementContent);
            console.log('✅ Successfully parsed requirements JSON!');
            console.log(`📊 Data requirements: ${requirements.data_requirements?.length || 0}`);
            console.log(`📊 Required endpoints: ${requirements.required_endpoints?.length || 0}`);
            console.log(`📊 Calculation steps: ${requirements.calculation_steps?.length || 0}`);
        } catch (parseError) {
            console.log('❌ Failed to parse requirements JSON:', parseError.message);
            console.log('Full content:', requirementContent);
            return;
        }
        
        // Small delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        // Load API specs
        const alpacaMarket = JSON.parse(fs.readFileSync('./alpaca-marketdata-extra-simple.json', 'utf8'));
        const alpacaTrading = JSON.parse(fs.readFileSync('./alpaca-trading-extra-simple.json', 'utf8'));
        const eodhd = JSON.parse(fs.readFileSync('./eodhd-extra-simple.json', 'utf8'));

        const availableApis = {
            'Alpaca Market Data API': alpacaMarket,
            'Alpaca Trading API': alpacaTrading,
            'EODHD API': eodhd
        };

        // STAGE 2: Match Against Available APIs
        console.log('');
        console.log('🔍 STAGE 2: Match Against Available APIs');  
        console.log(`Total API endpoints available: ${Object.values(availableApis).reduce((total, spec) => total + (spec.endpoints?.length || 0), 0)}`);
        console.log('-' .repeat(40));
        
        const matcherSystemPrompt = `${matcherPrompt}

## Available API Specifications:
${JSON.stringify(availableApis, null, 2)}`;

        const matcherUserPrompt = `Match these generated requirements against available APIs:

**Generated Requirements:**
${JSON.stringify(requirements, null, 2)}

Determine if the original question "${testQuestion}" can be answered with the available APIs.

IMPORTANT: Respond with ONLY a JSON object, no markdown formatting, no code blocks.`;

        console.log('🤖 Matching against available APIs...');
        const matcherResponse = await fetch('http://localhost:11434/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ollama'
            },
            body: JSON.stringify({
                model: MODEL,
                messages: [
                    { role: 'system', content: matcherSystemPrompt },
                    { role: 'user', content: matcherUserPrompt }
                ],
                temperature: 0.1,
                max_tokens: 2000
            }),
        });

        if (!matcherResponse.ok) {
            throw new Error(`API error: ${matcherResponse.status} ${matcherResponse.statusText}`);
        }

        const matcherData = await matcherResponse.json();
        const matcherContent = matcherData.choices[0].message.content;
        
        console.log('Raw response length:', matcherContent.length);
        
        let validationResult;
        try {
            validationResult = cleanJsonResponse(matcherContent);
            console.log('✅ Successfully parsed validation result JSON!');
            
            console.log('');
            console.log('🎯 FINAL VALIDATION SUMMARY:');
            console.log('=' .repeat(60));
            console.log(`🔹 Result: ${validationResult.validation_result}`);
            console.log(`🔹 Feasibility Score: ${validationResult.feasibility_score}`);
            console.log(`🔹 Confidence Level: ${validationResult.confidence_level}`);
            console.log(`🔹 Matched Endpoints: ${validationResult.matched_endpoints?.length || 0}`);
            console.log(`🔹 Missing Capabilities: ${validationResult.missing_capabilities?.length || 0}`);
            
            if (validationResult.validation_notes) {
                console.log(`🔹 Notes: ${validationResult.validation_notes.substring(0, 200)}...`);
            }
            
            console.log('');
            console.log('📋 IMPLEMENTATION PLAN:');
            if (validationResult.recommended_implementation) {
                validationResult.recommended_implementation.forEach((step, i) => {
                    console.log(`   ${i + 1}. ${step.action} (${step.endpoint})`);
                });
            }
            
            console.log('');
            console.log('🚀 TWO-STAGE VALIDATION COMPLETE!');
            console.log('✅ System successfully analyzed requirements and matched against APIs');
            
        } catch (parseError) {
            console.log('❌ Failed to parse validation result JSON:', parseError.message);
            console.log('Full content preview:', matcherContent.substring(0, 500));
        }

    } catch (error) {
        console.error('❌ Robust validation test failed:', error.message);
    }
}

testTwoStageRobust();