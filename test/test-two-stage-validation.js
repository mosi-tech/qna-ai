// Test two-stage validation: 1) Generate API requirements, 2) Match against available APIs
const fs = require('fs');

async function testTwoStageValidation() {
    try {
        console.log('🎯 Testing Two-Stage Validation System');
        console.log('=' .repeat(80));
        
        const testQuestion = "Which watchlist tickers had the highest 3-month Sharpe ratio?";
        
        // Load prompts and API specs
        console.log('📖 Loading validation assets...');
        const requirementPrompt = fs.readFileSync('./api-requirement-generator-prompt.txt', 'utf8');
        const matcherPrompt = fs.readFileSync('./api-availability-matcher-prompt.txt', 'utf8');
        
        const alpacaMarket = JSON.parse(fs.readFileSync('./alpaca-marketdata-extra-simple.json', 'utf8'));
        const alpacaTrading = JSON.parse(fs.readFileSync('./alpaca-trading-extra-simple.json', 'utf8'));
        const eodhd = JSON.parse(fs.readFileSync('./eodhd-extra-simple.json', 'utf8'));
        
        const availableApis = {
            'Alpaca Market Data API': alpacaMarket,
            'Alpaca Trading API': alpacaTrading,
            'EODHD API': eodhd
        };
        
        console.log(`✅ Requirement prompt: ${requirementPrompt.length} characters`);
        console.log(`✅ Matcher prompt: ${matcherPrompt.length} characters`);
        console.log(`✅ Available API specs: ${JSON.stringify(availableApis).length} characters`);
        console.log('');
        
        // STAGE 1: Generate API Requirements
        console.log('🔍 STAGE 1: Generating API Requirements');
        console.log('-' .repeat(50));
        console.log(`Question: "${testQuestion}"`);
        console.log('');
        
        const requirementSystemPrompt = requirementPrompt;
        const requirementUserPrompt = `Analyze this financial question and determine what APIs and data would be needed: "${testQuestion}"`;
        
        console.log('🤖 Sending to Ollama for requirement generation...');
        const startTime1 = Date.now();
        
        const requirementResponse = await fetch('http://localhost:11434/v1/chat/completions', {
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
                        content: requirementSystemPrompt
                    },
                    {
                        role: 'user',
                        content: requirementUserPrompt
                    }
                ],
                temperature: 0.1,
                max_tokens: 2000
            }),
        });

        const responseTime1 = Date.now() - startTime1;
        console.log(`⏱️  Stage 1 response time: ${(responseTime1 / 1000).toFixed(2)} seconds`);

        if (!requirementResponse.ok) {
            throw new Error(`Ollama API error: ${requirementResponse.status} ${requirementResponse.statusText}`);
        }

        const requirementData = await requirementResponse.json();
        const requirementContent = requirementData.choices[0].message.content;
        
        console.log('');
        console.log('📋 STAGE 1 RESULT - Generated Requirements:');
        console.log('-' .repeat(80));
        console.log(requirementContent);
        console.log('-' .repeat(80));

        let requirements;
        try {
            requirements = JSON.parse(requirementContent);
            console.log('');
            console.log('✅ Successfully parsed requirements JSON');
            console.log(`🔹 Data Requirements: ${requirements.data_requirements?.length || 0} items`);
            console.log(`🔹 Required Endpoints: ${requirements.required_endpoints?.length || 0} items`);
            console.log(`🔹 Calculation Steps: ${requirements.calculation_steps?.length || 0} steps`);
        } catch (parseError) {
            console.log('❌ Failed to parse requirements JSON:', parseError.message);
            return;
        }

        // Small delay between stages
        await new Promise(resolve => setTimeout(resolve, 2000));

        // STAGE 2: Match Against Available APIs
        console.log('');
        console.log('🔍 STAGE 2: Matching Against Available APIs');
        console.log('-' .repeat(50));
        
        const matcherSystemPrompt = `${matcherPrompt}

## Available API Specifications:
${JSON.stringify(availableApis, null, 2)}`;

        const matcherUserPrompt = `Match these generated requirements against available APIs:

**Generated Requirements:**
${JSON.stringify(requirements, null, 2)}

Determine if the original question "${testQuestion}" can be answered with the available APIs.`;

        console.log('🤖 Sending to Ollama for API matching...');
        const startTime2 = Date.now();
        
        const matcherResponse = await fetch('http://localhost:11434/v1/chat/completions', {
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
                        content: matcherSystemPrompt
                    },
                    {
                        role: 'user',
                        content: matcherUserPrompt
                    }
                ],
                temperature: 0.1,
                max_tokens: 3000
            }),
        });

        const responseTime2 = Date.now() - startTime2;
        console.log(`⏱️  Stage 2 response time: ${(responseTime2 / 1000).toFixed(2)} seconds`);

        if (!matcherResponse.ok) {
            throw new Error(`Ollama API error: ${matcherResponse.status} ${matcherResponse.statusText}`);
        }

        const matcherData = await matcherResponse.json();
        const matcherContent = matcherData.choices[0].message.content;
        
        console.log('');
        console.log('📋 STAGE 2 RESULT - API Matching:');
        console.log('-' .repeat(80));
        console.log(matcherContent);
        console.log('-' .repeat(80));

        let validationResult;
        try {
            validationResult = JSON.parse(matcherContent);
            console.log('');
            console.log('✅ Successfully parsed validation result JSON');
            console.log('');
            console.log('🎯 FINAL VALIDATION SUMMARY:');
            console.log('=' .repeat(80));
            console.log(`🔹 Result: ${validationResult.validation_result}`);
            console.log(`🔹 Feasibility Score: ${validationResult.feasibility_score}`);
            console.log(`🔹 Confidence Level: ${validationResult.confidence_level}`);
            console.log(`🔹 Matched Endpoints: ${validationResult.matched_endpoints?.length || 0}`);
            console.log(`🔹 Missing Capabilities: ${validationResult.missing_capabilities?.length || 0}`);
            console.log(`🔹 Implementation Steps: ${validationResult.recommended_implementation?.length || 0}`);
            
            if (validationResult.validation_notes) {
                console.log(`🔹 Notes: ${validationResult.validation_notes}`);
            }
            
            if (validationResult.suggested_question_refinement && 
                validationResult.suggested_question_refinement !== testQuestion) {
                console.log(`🔹 Suggested Refinement: ${validationResult.suggested_question_refinement}`);
            }
            
            console.log('');
            console.log('📊 PERFORMANCE SUMMARY:');
            console.log(`   Total time: ${((responseTime1 + responseTime2) / 1000).toFixed(2)}s`);
            console.log(`   Stage 1 (Requirements): ${(responseTime1 / 1000).toFixed(2)}s`);
            console.log(`   Stage 2 (Matching): ${(responseTime2 / 1000).toFixed(2)}s`);
            
            if (requirementData.usage && matcherData.usage) {
                console.log(`   Total tokens: ${requirementData.usage.total_tokens + matcherData.usage.total_tokens}`);
            }
            
            console.log('');
            console.log('🚀 TWO-STAGE VALIDATION COMPLETE!');
            console.log('   Benefits:');
            console.log('   - More thorough analysis of requirements');
            console.log('   - Better matching against available capabilities');  
            console.log('   - Clearer identification of limitations');
            console.log('   - More actionable implementation guidance');
            
        } catch (parseError) {
            console.log('❌ Failed to parse validation result JSON:', parseError.message);
            console.log('Raw content:', matcherContent);
        }

    } catch (error) {
        console.error('❌ Two-stage validation test failed:', error.message);
    }
}

testTwoStageValidation();