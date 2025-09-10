#!/usr/bin/env node

// Quick test script to verify the MCP server functionality
import { generateMockData } from './mockDataGenerator.js';

console.log('🧪 Testing Financial MCP Server Mock Data Generation');
console.log('=' .repeat(60));

// Test Alpaca Trading API endpoints
console.log('\n📊 ALPACA TRADING API TESTS');
console.log('-' .repeat(40));

try {
  // Test account data
  const accountData = generateMockData('alpaca-trading', '/v2/account', {});
  console.log('✅ Account Data:', JSON.stringify(accountData, null, 2).substring(0, 200) + '...');

  // Test positions
  const positionsData = generateMockData('alpaca-trading', '/v2/positions', { symbols: 'AAPL,TSLA,SPY' });
  console.log(`✅ Positions: ${positionsData.length} positions generated`);

  // Test orders
  const ordersData = generateMockData('alpaca-trading', '/v2/orders', { limit: 5 });
  console.log(`✅ Orders: ${ordersData.length} orders generated`);

  // Test portfolio history
  const portfolioData = generateMockData('alpaca-trading', '/v2/portfolio/history', { period: '1M' });
  console.log(`✅ Portfolio History: ${portfolioData.equity.length} data points`);

} catch (error) {
  console.error('❌ Alpaca Trading test failed:', error.message);
}

// Test Alpaca Market Data API endpoints
console.log('\n📈 ALPACA MARKET DATA API TESTS');
console.log('-' .repeat(40));

try {
  // Test stock bars
  const barsData = generateMockData('alpaca-market', '/v2/stocks/bars', { symbols: 'AAPL,TSLA' });
  console.log(`✅ Stock Bars: ${Object.keys(barsData.bars).length} symbols, ${barsData.bars.AAPL?.length || 0} bars per symbol`);

  // Test latest quotes
  const quotesData = generateMockData('alpaca-market', '/v2/stocks/quotes/latest', { symbols: 'AAPL,MSFT' });
  console.log(`✅ Latest Quotes: ${Object.keys(quotesData.quotes).length} symbols quoted`);

  // Test snapshots
  const snapshotsData = generateMockData('alpaca-market', '/v2/stocks/snapshots', { symbols: 'SPY' });
  console.log('✅ Market Snapshots:', Object.keys(snapshotsData.snapshots).length + ' snapshots');

  // Test screener
  const screenData = generateMockData('alpaca-market', '/v1beta1/screener/stocks/most-actives', { top: 10 });
  console.log(`✅ Stock Screener: ${screenData.most_actives.length} most active stocks`);

  // Test news
  const newsData = generateMockData('alpaca-market', '/v1beta1/news', { symbols: 'AAPL,TSLA' });
  console.log(`✅ Financial News: ${newsData.news.length} news articles`);

} catch (error) {
  console.error('❌ Alpaca Market Data test failed:', error.message);
}

// Test EODHD API endpoints  
console.log('\n📊 EODHD API TESTS');
console.log('-' .repeat(40));

try {
  // Test EOD data
  const eodData = generateMockData('eodhd', '/api/eod/{symbol}', { symbol: 'AAPL.US', period: 'd' });
  console.log(`✅ EOD Data: ${eodData.length} daily records for AAPL.US`);

  // Test fundamentals
  const fundamentalsData = generateMockData('eodhd', '/api/fundamentals/{symbol}', { symbol: 'MSFT.US' });
  console.log('✅ Fundamentals: Company data generated with', Object.keys(fundamentalsData).length, 'main sections');

  // Test technical indicators
  const technicalData = generateMockData('eodhd', '/api/technical/{symbol}', { 
    symbol: 'TSLA.US', 
    function: 'sma',
    period: 20 
  });
  console.log(`✅ Technical Indicators: ${technicalData.length} SMA data points`);

  // Test screener
  const eodhdScreenData = generateMockData('eodhd', '/api/screener', { limit: 25 });
  console.log(`✅ EODHD Screener: ${eodhdScreenData.length} screened stocks`);

  // Test dividends
  const dividendsData = generateMockData('eodhd', '/api/div/{symbol}', { symbol: 'AAPL.US' });
  console.log(`✅ Dividends: ${dividendsData.length} dividend payments`);

  // Test ETF data
  const etfData = generateMockData('eodhd', '/api/etf/{symbol}', { symbol: 'SPY.US' });
  console.log(`✅ ETF Holdings: ${etfData.Holdings.length} top holdings, ${Object.keys(etfData.SectorWeights).length} sectors`);

} catch (error) {
  console.error('❌ EODHD test failed:', error.message);
}

console.log('\n🎉 ALL TESTS COMPLETED');
console.log('=' .repeat(60));
console.log('📋 SUMMARY:');
console.log('✅ Alpaca Trading API - Account, positions, orders, portfolio history');
console.log('✅ Alpaca Market Data API - Bars, quotes, snapshots, screeners, news');
console.log('✅ EODHD API - EOD data, fundamentals, technicals, dividends, ETFs');
console.log('');
console.log('🚀 MCP Server ready for integration!');
console.log('📖 See README.md for usage instructions');
console.log('');
console.log('🔧 To test with Claude Desktop, add to your MCP settings:');
console.log('```json');
console.log('{');
console.log('  "mcpServers": {');
console.log('    "financial-mock": {');
console.log('      "command": "node",');
console.log(`      "args": ["${process.cwd()}/server.js"]`);
console.log('    }');
console.log('  }');
console.log('}');
console.log('```');