'use client';

export default function QuantAnalysis2() {
  const analysisData = {
    strategy: "Mean Reversion Momentum Strategy",
    asset: "NVDA (NVIDIA Corporation)",
    timeframe: "1-Month Analysis",
    lastUpdated: "November 15, 2024",
    summary: {
      signal: "STRONG BUY",
      confidence: "87.3%",
      expectedReturn: "+12.4%",
      maxDrawdown: "-8.7%",
      sharpeRatio: "2.41"
    },
    highlights: [
      {
        title: "Technical Momentum",
        value: "Bullish",
        confidence: "92%",
        description: "RSI oversold bounce with volume confirmation. 20-day MA breakout with strong momentum divergence."
      },
      {
        title: "Options Flow Analysis", 
        value: "Heavy Call Activity",
        confidence: "88%",
        description: "$470-$480 strike concentrations expiring in 2 weeks. Put/call ratio at 0.23 indicating bullish sentiment."
      },
      {
        title: "Volatility Assessment",
        value: "IV Expansion Expected",
        confidence: "76%",
        description: "Historical volatility (14.2%) below implied volatility (18.7%). Earnings catalyst approaching."
      },
      {
        title: "Risk-Adjusted Returns",
        value: "Superior Alpha",
        confidence: "91%",
        description: "3-month rolling alpha of 4.2% vs SPY. Beta-adjusted returns outperforming sector by 280bps."
      }
    ],
    technicalIndicators: [
      { indicator: "RSI (14)", value: "34.2", signal: "Oversold Bounce", strength: "Strong" },
      { indicator: "MACD", value: "Bullish Cross", signal: "Buy Signal", strength: "Moderate" },
      { indicator: "Bollinger Bands", value: "Lower Band Test", signal: "Support Hold", strength: "Strong" },
      { indicator: "Volume Profile", value: "+47% Above Avg", signal: "Accumulation", strength: "Very Strong" },
      { indicator: "ADX", value: "28.4", signal: "Trending Market", strength: "Moderate" },
      { indicator: "Stochastic", value: "18.3", signal: "Oversold", strength: "Strong" }
    ],
    quantMetrics: [
      { metric: "1-Month Volatility", value: "28.4%", benchmark: "SPY: 12.1%", status: "elevated" },
      { metric: "Beta (252d)", value: "1.67", benchmark: "Sector: 1.23", status: "high" },
      { metric: "Correlation to QQQ", value: "0.84", benchmark: "Historical: 0.78", status: "increased" },
      { metric: "Average Daily Volume", value: "47.2M", benchmark: "30d Avg: 31.8M", status: "elevated" },
      { metric: "Bid-Ask Spread", value: "0.08%", benchmark: "Sector Avg: 0.12%", status: "tight" },
      { metric: "Price Momentum (5d)", value: "+3.7%", benchmark: "SPY: +0.8%", status: "outperforming" }
    ],
    riskFactors: [
      "High correlation to tech sector selloffs (0.84 to QQQ)",
      "Elevated implied volatility ahead of earnings announcement", 
      "Concentration risk from AI bubble concerns",
      "Options gamma exposure creating price instability",
      "Regulatory concerns around semiconductor exports"
    ],
    entryStrategy: [
      "Scale into position on 2-3% pullbacks from current levels",
      "Use $465-$468 as primary entry zone with volume confirmation",
      "Stop loss placement below $455 (2.8% risk per position)",
      "Target 1: $485 (4.2% gain) • Target 2: $495 (7.8% gain)",
      "Position sizing: 2.5% of portfolio maximum due to volatility"
    ],
    backtestResults: {
      period: "Jan 2023 - Nov 2024",
      totalReturn: "+127.4%",
      annualizedReturn: "+58.2%", 
      maxDrawdown: "-23.1%",
      winRate: "67.3%",
      profitFactor: "2.87",
      averageWin: "+8.4%",
      averageLoss: "-3.2%",
      tradingDays: "487",
      totalTrades: "23"
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">{analysisData.strategy}</h1>
              <p className="text-gray-600 mt-1">
                {analysisData.asset} • {analysisData.timeframe} • Updated {analysisData.lastUpdated}
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">Signal Strength</div>
              <div className="text-2xl font-semibold text-green-700">{analysisData.summary.signal}</div>
              <div className="text-sm text-green-600">{analysisData.summary.confidence} confidence</div>
            </div>
          </div>
        </div>

        {/* Strategy Summary */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Strategy Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Signal</div>
              <div className="text-lg font-semibold text-green-700">{analysisData.summary.signal}</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Expected Return</div>
              <div className="text-lg font-semibold text-green-700">{analysisData.summary.expectedReturn}</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Max Drawdown</div>
              <div className="text-lg font-semibold text-red-600">{analysisData.summary.maxDrawdown}</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Sharpe Ratio</div>
              <div className="text-lg font-semibold text-gray-900">{analysisData.summary.sharpeRatio}</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Confidence</div>
              <div className="text-lg font-semibold text-blue-700">{analysisData.summary.confidence}</div>
            </div>
          </div>
        </div>

        {/* Analysis Highlights */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Analysis Highlights</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analysisData.highlights.map((highlight, index) => (
              <div key={index} className="border border-gray-100 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-medium text-gray-900">{highlight.title}</h3>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-blue-700">{highlight.value}</div>
                    <div className="text-xs text-gray-500">{highlight.confidence} confidence</div>
                  </div>
                </div>
                <p className="text-sm text-gray-600">{highlight.description}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Technical Indicators */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Technical Indicators</h2>
            <div className="space-y-3">
              {analysisData.technicalIndicators.map((indicator, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900">{indicator.indicator}</div>
                    <div className="text-sm text-gray-600">{indicator.signal}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900">{indicator.value}</div>
                    <div className={`text-xs px-2 py-1 rounded-full ${
                      indicator.strength === 'Very Strong' ? 'bg-green-200 text-green-800' :
                      indicator.strength === 'Strong' ? 'bg-green-100 text-green-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {indicator.strength}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quantitative Metrics */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quantitative Metrics</h2>
            <div className="space-y-3">
              {analysisData.quantMetrics.map((metric, index) => (
                <div key={index} className="border border-gray-100 rounded-lg p-3">
                  <div className="flex justify-between items-start mb-1">
                    <span className="font-medium text-gray-900">{metric.metric}</span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      metric.status === 'elevated' || metric.status === 'outperforming' ? 'bg-blue-100 text-blue-700' :
                      metric.status === 'high' || metric.status === 'increased' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {metric.status}
                    </span>
                  </div>
                  <div className="text-lg font-semibold text-gray-900">{metric.value}</div>
                  <div className="text-sm text-gray-500">{metric.benchmark}</div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Entry Strategy */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Entry Strategy</h2>
          <div className="space-y-3">
            {analysisData.entryStrategy.map((strategy, index) => (
              <div key={index} className="flex items-start">
                <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium mr-3 mt-0.5 flex-shrink-0">
                  {index + 1}
                </div>
                <p className="text-gray-700">{strategy}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Risk Assessment */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Assessment</h2>
            <div className="space-y-3">
              {analysisData.riskFactors.map((risk, index) => (
                <div key={index} className="flex items-start">
                  <div className="w-2 h-2 bg-red-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <p className="text-sm text-gray-700">{risk}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Backtest Performance */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Backtest Results</h2>
            <div className="text-sm text-gray-600 mb-4">{analysisData.backtestResults.period}</div>
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="text-xs text-gray-500">Total Return</div>
                <div className="font-semibold text-green-700">{analysisData.backtestResults.totalReturn}</div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="text-xs text-gray-500">Annualized</div>
                <div className="font-semibold text-green-700">{analysisData.backtestResults.annualizedReturn}</div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="text-xs text-gray-500">Max Drawdown</div>
                <div className="font-semibold text-red-600">{analysisData.backtestResults.maxDrawdown}</div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="text-xs text-gray-500">Win Rate</div>
                <div className="font-semibold text-blue-700">{analysisData.backtestResults.winRate}</div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="text-xs text-gray-500">Profit Factor</div>
                <div className="font-semibold text-gray-900">{analysisData.backtestResults.profitFactor}</div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="text-xs text-gray-500">Total Trades</div>
                <div className="font-semibold text-gray-900">{analysisData.backtestResults.totalTrades}</div>
              </div>
            </div>
          </div>

        </div>

        {/* Disclaimer */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Important Disclaimers</h2>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-gray-800 leading-relaxed">
              This analysis is for educational and informational purposes only. Past performance does not guarantee future results. 
              All trading involves substantial risk of loss. The strategies discussed may not be suitable for all investors. 
              Please conduct your own research and consult with a qualified financial advisor before making investment decisions.
              Options trading involves significant risk and is not appropriate for all investors.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-gray-500 pt-4 border-t border-gray-200">
          <p>Quantitative Analysis Engine v2.1 • Generated on {new Date().toLocaleDateString()}</p>
        </div>

      </div>
    </div>
  );
}