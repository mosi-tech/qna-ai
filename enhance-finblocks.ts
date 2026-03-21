import fs from 'fs';
import path from 'path';

// Financial data enhancement templates for each category
const FINANCIAL_DATA = {
  portfolio: {
    'portfolio-kpi-summary': {
      metrics: [
        { name: 'Portfolio Value', stat: '$487,250', change: '+12.5%', changeType: 'positive' },
        { name: 'Unrealized P&L', stat: '$52,150', change: '+10.8%', changeType: 'positive' },
        { name: 'YTD Return', stat: '18.3%', change: '+4.2%', changeType: 'positive' },
        { name: 'Sharpe Ratio', stat: '1.64', change: '+0.12', changeType: 'positive' },
      ]
    },
    'holdings-table': {
      headers: ['Symbol', 'Shares', 'Price', 'Value', '%', 'Change'],
      holdings: [
        { symbol: 'AAPL', shares: 150, price: '$189.45', value: '$28,417.50', pct: '5.8%', change: '+8.2%' },
        { symbol: 'MSFT', shares: 75, price: '$424.00', value: '$31,800.00', pct: '6.5%', change: '+12.4%' },
        { symbol: 'GOOGL', shares: 45, price: '$152.30', value: '$6,853.50', pct: '1.4%', change: '+6.1%' },
        { symbol: 'TSLA', shares: 50, price: '$248.50', value: '$12,425.00', pct: '2.5%', change: '+15.3%' },
        { symbol: 'BRK.B', shares: 100, price: '$385.20', value: '$38,520.00', pct: '7.9%', change: '+5.2%' },
      ]
    },
    'sector-allocation-donut': {
      sectors: [
        { name: 'Technology', value: 35, color: 'blue' },
        { name: 'Healthcare', value: 18, color: 'green' },
        { name: 'Financials', value: 15, color: 'purple' },
        { name: 'Consumer', value: 12, color: 'orange' },
        { name: 'Other', value: 20, color: 'gray' },
      ]
    },
    'asset-class-allocation': {
      classes: [
        { name: 'Stocks', value: 65 },
        { name: 'Bonds', value: 20 },
        { name: 'Cash', value: 10 },
        { name: 'Alternatives', value: 5 },
      ]
    },
  },
  stock_research: {
    'stock-price-kpi': {
      metrics: [
        { name: 'Current Price', stat: '$189.45', change: '+2.3%', changeType: 'positive' },
        { name: '52W High', stat: '$199.62', change: '-5.1%', changeType: 'negative' },
        { name: '52W Low', stat: '$151.20', change: '+25.2%', changeType: 'positive' },
        { name: 'P/E Ratio', stat: '28.5', change: '+0.8', changeType: 'positive' },
      ]
    },
  },
  risk_management: {
    'risk-metrics-kpi': {
      metrics: [
        { name: 'Portfolio Beta', stat: '0.92', change: '-0.04', changeType: 'positive' },
        { name: 'Annual Volatility', stat: '14.2%', change: '-1.3%', changeType: 'positive' },
        { name: 'Max Drawdown', stat: '-18.5%', change: '-2.1%', changeType: 'positive' },
        { name: 'VaR (95%)', stat: '-$8,250', change: '-$1,200', changeType: 'positive' },
      ]
    },
  },
  income: {
    'dividend-income-kpi': {
      metrics: [
        { name: 'Annual Dividend Income', stat: '$12,450', change: '+8.3%', changeType: 'positive' },
        { name: 'Dividend Yield', stat: '2.56%', change: '+0.18%', changeType: 'positive' },
        { name: 'Payout Ratio', stat: '42%', change: '-2%', changeType: 'positive' },
        { name: 'Next Ex-Dividend', stat: 'Mar 15', change: 'Upcoming', changeType: 'neutral' },
      ]
    },
  },
  performance: {
    'annual-returns-bar': {
      years: [
        { year: '2020', return: '12.8%' },
        { year: '2021', return: '28.4%' },
        { year: '2022', return: '-16.2%' },
        { year: '2023', return: '24.1%' },
        { year: '2024', return: '18.3%' },
      ]
    },
  },
  technical: {
    'rsi-overbought-oversold': {
      metrics: [
        { name: 'RSI (14)', stat: '68.5', change: '+5.2', changeType: 'positive' },
        { name: 'Status', stat: 'Neutral', change: 'Approaching Overbought', changeType: 'neutral' },
        { name: '30-Day Avg RSI', stat: '52.1', change: '+1.8', changeType: 'positive' },
      ]
    },
  },
  fundamental: {
    'earnings-quality-score': {
      metrics: [
        { name: 'Quality Score', stat: '78/100', change: '+5', changeType: 'positive' },
        { name: 'FCF Growth', stat: '14.2%', change: '+3.1%', changeType: 'positive' },
        { name: 'Margin Trend', stat: 'Improving', change: '+220 bps', changeType: 'positive' },
        { name: 'Earnings Stability', stat: 'High', change: 'Consistent', changeType: 'positive' },
      ]
    },
  },
  tax: {
    'estimated-tax-liability': {
      metrics: [
        { name: 'Est. Tax Liability', stat: '$18,500', change: '+$2,150', changeType: 'negative' },
        { name: 'Realized Gains', stat: '$45,200', change: '+$5,800', changeType: 'neutral' },
        { name: 'Tax Loss Harvesting', stat: '$8,500', change: 'Available', changeType: 'positive' },
        { name: 'Effective Tax Rate', stat: '22.4%', change: '+1.2%', changeType: 'negative' },
      ]
    },
  },
  etf_analysis: {
    'etf-comparison-metrics': {
      metrics: [
        { name: 'Expense Ratio', stat: '0.03%', change: '-0.01%', changeType: 'positive' },
        { name: 'AUM', stat: '$85.2B', change: '+8.3%', changeType: 'positive' },
        { name: 'Daily Volume', stat: '$2.3B', change: '+12.5%', changeType: 'positive' },
        { name: 'Tracking Error', stat: '0.04%', change: 'Low', changeType: 'positive' },
      ]
    },
  },
  sector: {
    'sector-performance-bar': {
      sectors: [
        { name: 'Technology', return: '24.3%' },
        { name: 'Healthcare', return: '14.2%' },
        { name: 'Financials', return: '8.5%' },
        { name: 'Energy', return: '6.2%' },
        { name: 'Industrials', return: '12.8%' },
      ]
    },
  },
  monitoring: {
    'price-alert-setup': {
      alerts: [
        { symbol: 'AAPL', above: '$195', below: '$180', active: true },
        { symbol: 'MSFT', above: '$450', below: '$400', active: true },
        { symbol: 'GOOGL', above: '$165', below: '$145', active: false },
      ]
    },
  },
};

const baseDir = '/Users/shivc/Documents/Workspace/JS/qna-ai-admin/frontend/apps/base-ui/src/finBlocks/components';

function enhanceComponent(category: string, filePath: string, templateData: any): string {
  const content = fs.readFileSync(filePath, 'utf-8');

  // Build replacement for SAMPLE_DATA
  const dataString = JSON.stringify(templateData, null, 2);

  return content.replace(
    /const SAMPLE_DATA:[^;]*?}[^}]*?};?/s,
    `const SAMPLE_DATA: ${content.match(/interface (\w+Data)/)?.[1] || 'any'} = ${dataString};`
  );
}

// Process all categories
Object.entries(FINANCIAL_DATA).forEach(([category, components]) => {
  const categoryDir = path.join(baseDir, category);

  Object.entries(components).forEach(([blockId, data]) => {
    const fileName = blockId.replace(/-(\w)/g, (_, c) => c.toUpperCase()) + '.tsx';
    const filePath = path.join(categoryDir, fileName);

    if (fs.existsSync(filePath)) {
      try {
        const enhanced = enhanceComponent(category, filePath, { ...data, cols: 4 });
        fs.writeFileSync(filePath, enhanced);
        console.log(`✓ Enhanced ${category}/${blockId}`);
      } catch (error) {
        console.log(`✗ Failed to enhance ${category}/${blockId}: ${error}`);
      }
    }
  });
});

console.log('\nFinBlock enhancement complete!');
