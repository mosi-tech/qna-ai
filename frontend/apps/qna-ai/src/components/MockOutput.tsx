interface MockOutputProps {
  moduleKey: string;
}

export default function MockOutput({ moduleKey }: MockOutputProps) {
  // Generate mock data based on module type
  const getMockData = () => {
    switch (moduleKey) {
      case 'rebalance':
        return {
          title: 'Rebalancing Impact Analysis',
          metrics: [
            { metric: 'Annualized Return', value: '12.4%', description: 'Portfolio return with quarterly rebalancing', trend: '+0.8%' },
            { metric: 'Max Drawdown', value: '-8.2%', description: 'Maximum peak-to-trough decline', trend: '-1.3%' },
            { metric: 'Sharpe Ratio', value: '1.34', description: 'Risk-adjusted return measure', trend: '+0.12' },
            { metric: 'Transaction Costs', value: '$2,450', description: 'Total rebalancing costs (2 years)', trend: '' },
            { metric: 'Tracking Error', value: '2.1%', description: 'Volatility vs benchmark', trend: '+0.3%' }
          ]
        };
      case 'backtest':
        return {
          title: 'Visual Strategy Backtest Results',
          metrics: [
            { metric: 'Strategy Performance', value: '+28.7%', description: 'Total return vs 18.3% buy-and-hold', trend: '+10.4%' },
            { metric: 'Sharpe Ratio', value: '1.89', description: 'Risk-adjusted performance measure', trend: '+0.31' },
            { metric: 'Win Rate', value: '62%', description: 'Percentage of profitable trades', trend: '+2%' },
            { metric: 'Max Drawdown', value: '-6.4%', description: 'Largest peak-to-trough decline', trend: '-0.8%' },
            { metric: 'Total Trades', value: '52', description: 'Entry and exit signals generated', trend: '' },
            { metric: 'Avg Trade Duration', value: '7.2 days', description: 'Average holding period per trade', trend: '' }
          ]
        };
      case 'regression':
        return {
          title: 'Factor Exposure Analysis',
          metrics: [
            { metric: 'Market Beta', value: '1.12', description: 'Sensitivity to broad market (SPY)', trend: '' },
            { metric: 'Size Factor (SMB)', value: '-0.23', description: 'Large cap bias vs small cap', trend: '' },
            { metric: 'Value Factor (HML)', value: '0.18', description: 'Growth tilt vs value stocks', trend: '' },
            { metric: 'R-Squared', value: '0.87', description: 'Model explains 87% of variance', trend: '' },
            { metric: 'Jensen\'s Alpha', value: '2.4%', description: 'Excess return after risk adjustment', trend: '' }
          ]
        };
      case 'risk':
        return {
          title: 'Portfolio Risk Assessment',
          metrics: [
            { metric: '95% VaR (30-day)', value: '-$8,750', description: 'Maximum expected loss (95% confidence)', trend: '' },
            { metric: 'Expected Shortfall', value: '-$12,300', description: 'Average loss beyond VaR threshold', trend: '' },
            { metric: 'Portfolio Beta', value: '1.08', description: 'Systematic risk vs market', trend: '' },
            { metric: 'Volatility (Annual)', value: '18.2%', description: 'Annualized standard deviation', trend: '+2.1%' },
            { metric: 'Correlation to SPY', value: '0.89', description: 'Correlation with S&P 500', trend: '' }
          ]
        };
      case 'screening':
        return {
          title: 'Stock Screening Results',
          metrics: [
            { metric: 'Matches Found', value: '47 stocks', description: 'Stocks meeting all criteria', trend: '' },
            { metric: 'Avg P/E Ratio', value: '18.3x', description: 'Price-to-earnings of results', trend: '' },
            { metric: 'Avg Revenue Growth', value: '12.8%', description: 'YoY revenue growth rate', trend: '' },
            { metric: 'Top Sector', value: 'Technology', description: '32% of results', trend: '' },
            { metric: 'Market Cap Range', value: '$2.1B - $847B', description: 'Range of company sizes', trend: '' }
          ]
        };
      case 'correlation':
        return {
          title: 'Asset Correlation Matrix',
          metrics: [
            { metric: 'Highest Correlation', value: 'AAPL-MSFT: 0.78', description: 'Strongest positive relationship', trend: '' },
            { metric: 'Lowest Correlation', value: 'TSLA-SPY: 0.23', description: 'Most diversified pair', trend: '' },
            { metric: 'Portfolio Diversity', value: '6.2/10', description: 'Diversification score', trend: '+0.8' },
            { metric: 'Avg Correlation', value: '0.54', description: 'Mean pairwise correlation', trend: '' },
            { metric: 'Risk Concentration', value: '34%', description: 'Risk from top 2 holdings', trend: '-3%' }
          ]
        };
      case 'strategy_builder':
        return {
          title: 'Visual Strategy Builder Results',
          metrics: [
            { metric: 'Strategy Performance', value: '+24.7%', description: 'Total return vs 18.3% buy-and-hold', trend: '+6.4%' },
            { metric: 'Sharpe Ratio', value: '1.58', description: 'Risk-adjusted performance measure', trend: '+0.23' },
            { metric: 'Win Rate', value: '68%', description: 'Percentage of profitable trades', trend: '+3%' },
            { metric: 'Max Drawdown', value: '-7.8%', description: 'Largest peak-to-trough decline', trend: '-1.2%' },
            { metric: 'Total Trades', value: '47', description: 'Entry and exit signals generated', trend: '' },
            { metric: 'Avg Trade Duration', value: '8.3 days', description: 'Average holding period per trade', trend: '' }
          ]
        };
      default:
        return {
          title: 'Analysis Results',
          metrics: [
            { metric: 'Status', value: 'Complete', description: 'Analysis finished successfully', trend: '' }
          ]
        };
    }
  };

  const mockData = getMockData();

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">{mockData.title}</h3>
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
            ✓ Complete
          </span>
        </div>
      </div>
      
      {/* Mock Chart with more realistic placeholder */}
      <div className="mb-8">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg p-8 text-center border border-blue-200 relative overflow-hidden">
          <div className="absolute inset-0 opacity-10">
            <svg className="w-full h-full" viewBox="0 0 400 200">
              <path d="M50,150 Q100,100 150,120 T250,80 T350,90" stroke="rgb(59, 130, 246)" strokeWidth="3" fill="none"/>
              <path d="M50,170 Q100,140 150,150 T250,120 T350,130" stroke="rgb(34, 197, 94)" strokeWidth="2" fill="none" opacity="0.7"/>
            </svg>
          </div>
          <div className="relative z-10">
            <div className="text-blue-600 text-2xl mb-3">📈</div>
            <div className="text-gray-700 font-medium">Interactive Chart</div>
            <div className="text-sm text-gray-600 mt-1">
              Performance visualization, correlation heatmap, or risk metrics would be displayed here
            </div>
            <div className="mt-3 inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
              Live data visualization
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Results Table */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h4 className="font-semibold text-gray-900">Key Metrics & Insights</h4>
          <div className="text-xs text-gray-500">
            ✨ Generated {new Date().toLocaleDateString()}
          </div>
        </div>
        
        <div className="space-y-3">
          {mockData.metrics.map((row, index) => (
            <div key={index} className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h5 className="font-medium text-gray-900">{row.metric}</h5>
                    {row.trend && (
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        row.trend.startsWith('+') ? 'bg-green-100 text-green-700' : 
                        row.trend.startsWith('-') ? 'bg-red-100 text-red-700' : 
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {row.trend}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{row.description}</p>
                </div>
                <div className="text-right ml-4">
                  <div className="text-lg font-semibold text-gray-900">{row.value}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Action buttons */}
        <div className="mt-6 flex gap-3">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
            📊 Export Results
          </button>
          <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium">
            📋 Save to Dashboard
          </button>
          <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium">
            🔄 Rerun Analysis
          </button>
        </div>
      </div>
    </div>
  );
}