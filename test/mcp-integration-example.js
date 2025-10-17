// Example of how to integrate MCP Financial Server with the validation system
const { generateMockData } = await import('./mcp-financial-server/mockDataGenerator.js');

// Sample questions that can now be answered with real mock data
const testQuestions = [
  {
    question: "What are my top 5 positions by value?",
    requiredAPIs: ["alpaca-trading_positions", "alpaca-market_stocks-quotes-latest"],
    workflow: [
      { step: 1, action: "Get all positions", api: "alpaca-trading_positions" },
      { step: 2, action: "Get current prices", api: "alpaca-market_stocks-quotes-latest" },
      { step: 3, action: "Calculate market values and sort", api: "computation" }
    ]
  },
  {
    question: "Which stocks have the highest volatility in my watchlist?",
    requiredAPIs: ["alpaca-trading_watchlists", "alpaca-market_stocks-bars"],
    workflow: [
      { step: 1, action: "Get watchlist symbols", api: "alpaca-trading_watchlists" },
      { step: 2, action: "Get 30-day price history", api: "alpaca-market_stocks-bars" },
      { step: 3, action: "Calculate daily returns and volatility", api: "computation" }
    ]
  },
  {
    question: "What's my portfolio's performance over the last 3 months?",
    requiredAPIs: ["alpaca-trading_portfolio-history"],
    workflow: [
      { step: 1, action: "Get portfolio history", api: "alpaca-trading_portfolio-history" },
      { step: 2, action: "Calculate returns and metrics", api: "computation" }
    ]
  },
  {
    question: "Show me dividend yields for tech stocks",
    requiredAPIs: ["eodhd_screener", "eodhd_fundamentals"],
    workflow: [
      { step: 1, action: "Screen tech sector stocks", api: "eodhd_screener" },
      { step: 2, action: "Get fundamental data", api: "eodhd_fundamentals" },
      { step: 3, action: "Extract dividend yields", api: "computation" }
    ]
  }
];

// Function to execute a workflow using MCP mock data
async function executeWorkflow(question, workflow) {
  console.log(`\n🔍 Executing: "${question}"`);
  console.log('-' .repeat(50));
  
  const results = {};
  
  for (const step of workflow) {
    console.log(`Step ${step.step}: ${step.action}`);
    
    if (step.api === 'computation') {
      console.log('  ⚡ Performing calculations...');
      continue;
    }
    
    // Parse API call
    const [api, endpoint] = step.api.split('_');
    const apiMap = {
      'alpaca-trading': 'alpaca-trading',
      'alpaca-market': 'alpaca-market', 
      'eodhd': 'eodhd'
    };
    
    const endpointMap = {
      'positions': '/v2/positions',
      'watchlists': '/v2/watchlists',
      'portfolio-history': '/v2/portfolio/history',
      'stocks-quotes-latest': '/v2/stocks/quotes/latest',
      'stocks-bars': '/v2/stocks/bars',
      'screener': '/api/screener',
      'fundamentals': '/api/fundamentals/{symbol}'
    };
    
    try {
      const mockData = generateMockData(
        apiMap[api], 
        endpointMap[endpoint] || endpoint,
        { symbols: 'AAPL,TSLA,MSFT,GOOGL,NVDA', period: '3M' }
      );
      
      results[step.api] = mockData;
      
      // Show preview of data
      if (Array.isArray(mockData)) {
        console.log(`  ✅ Retrieved ${mockData.length} records`);
      } else if (typeof mockData === 'object' && mockData !== null) {
        const keys = Object.keys(mockData);
        if (keys.includes('bars') || keys.includes('quotes') || keys.includes('snapshots')) {
          const dataKeys = Object.keys(mockData[keys[0]] || {});
          console.log(`  ✅ Retrieved data for ${dataKeys.length} symbols`);
        } else {
          console.log(`  ✅ Retrieved ${keys.length} data fields`);
        }
      }
      
    } catch (error) {
      console.log(`  ❌ Error: ${error.message}`);
    }
  }
  
  return results;
}

// Function to generate JSON output using the mock data
function generateJSONOutput(question, workflowResults) {
  const description = `Analysis answering: ${question}`;
  const body = [];
  
  // Generate realistic output based on the mock data
  if (workflowResults['alpaca-trading_positions']) {
    const positions = workflowResults['alpaca-trading_positions'];
    positions.forEach((pos, i) => {
      if (i < 5) { // Top 5
        body.push({
          key: `position_${i + 1}`,
          value: `${pos.symbol}: $${pos.market_value} (${pos.qty} shares)`,
          description: `Position ${i + 1} by market value, showing ${pos.unrealized_pl > 0 ? 'gain' : 'loss'} of $${Math.abs(pos.unrealized_pl)}`
        });
      }
    });
  }
  
  if (workflowResults['alpaca-trading_portfolio-history']) {
    const history = workflowResults['alpaca-trading_portfolio-history'];
    const startValue = history.equity[0];
    const endValue = history.equity[history.equity.length - 1];
    const totalReturn = ((endValue - startValue) / startValue * 100).toFixed(2);
    
    body.push({
      key: "total_return_3m",
      value: `${totalReturn}%`,
      description: `Total portfolio return over 3-month period, from $${startValue.toLocaleString()} to $${endValue.toLocaleString()}`
    });
  }
  
  if (workflowResults['eodhd_screener']) {
    const stocks = workflowResults['eodhd_screener'];
    stocks.slice(0, 3).forEach((stock, i) => {
      body.push({
        key: `tech_dividend_${i + 1}`,
        value: `${stock.code}: ${(stock.dividend_yield * 100).toFixed(2)}%`,
        description: `Technology stock with dividend yield, market cap $${(stock.market_cap / 1000000000).toFixed(1)}B`
      });
    });
  }
  
  return {
    description,
    body: body.length > 0 ? body : [
      {
        key: "mock_data_ready",
        value: "Mock data successfully generated",
        description: "MCP server provided realistic financial data for analysis"
      }
    ]
  };
}

// Demo the complete system
async function demonstrateMCPIntegration() {
  console.log('🎯 MCP Financial Server Integration Demo');
  console.log('=' .repeat(60));
  console.log('This demonstrates how validated questions can be answered with real mock data');
  
  for (const testCase of testQuestions) {
    try {
      // Execute the workflow
      const results = await executeWorkflow(testCase.question, testCase.workflow);
      
      // Generate JSON output
      const jsonOutput = generateJSONOutput(testCase.question, results);
      
      console.log('\n📋 Generated JSON Output:');
      console.log(JSON.stringify(jsonOutput, null, 2));
      
    } catch (error) {
      console.error(`❌ Error processing "${testCase.question}":`, error.message);
    }
    
    console.log('\n' + '='.repeat(60));
  }
  
  console.log('\n🎉 MCP Integration Demo Complete!');
  console.log('\n🚀 Next Steps:');
  console.log('  1. Add MCP server to Claude Desktop configuration');
  console.log('  2. Use validated questions to query real mock data');
  console.log('  3. Generate JSON outputs for the QnA system');
  console.log('  4. Test complete end-to-end workflow');
}

// Run the demonstration
demonstrateMCPIntegration().catch(console.error);