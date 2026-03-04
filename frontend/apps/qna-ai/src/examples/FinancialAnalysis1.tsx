'use client';

export default function FinancialAnalysis1() {
  const analysisData = {
    company: "TechFlow Solutions Inc.",
    ticker: "TFSI",
    reportDate: "Q3 2024",
    summary: {
      overallRating: "Strong Buy",
      targetPrice: "$142.50",
      currentPrice: "$118.75",
      upside: "20.0%",
      riskLevel: "Medium"
    },
    highlights: [
      {
        category: "Revenue Growth",
        value: "+28.4% YoY",
        description: "Sustained growth driven by cloud services expansion and enterprise software adoption"
      },
      {
        category: "Profitability",
        value: "EBITDA: 32.1%",
        description: "Improved operational efficiency and cost management initiatives showing results"
      },
      {
        category: "Market Position", 
        value: "#3 in SaaS",
        description: "Gained 2.3% market share through strategic acquisitions and product innovation"
      },
      {
        category: "Cash Flow",
        value: "$245M FCF",
        description: "Strong free cash flow generation supporting dividend growth and R&D investment"
      }
    ],
    keyMetrics: [
      { metric: "Revenue (TTM)", value: "$1.89B", change: "+28.4%", trend: "positive" },
      { metric: "Gross Margin", value: "68.2%", change: "+1.8pp", trend: "positive" },
      { metric: "Operating Margin", value: "24.7%", change: "+3.2pp", trend: "positive" },
      { metric: "ROE", value: "18.9%", change: "+2.1pp", trend: "positive" },
      { metric: "Debt/Equity", value: "0.31", change: "-0.08", trend: "positive" },
      { metric: "P/E Ratio", value: "24.6x", change: "-1.2x", trend: "positive" }
    ],
    riskFactors: [
      "Increasing competition from established tech giants",
      "Regulatory uncertainty in key international markets",
      "Dependency on subscription revenue model",
      "Potential economic slowdown affecting enterprise spending"
    ],
    catalysts: [
      "Launch of AI-powered analytics platform in Q4 2024",
      "Expansion into European markets scheduled for Q1 2025", 
      "Strategic partnership with major cloud provider",
      "Potential acquisition of complementary fintech startup"
    ]
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">{analysisData.company}</h1>
              <p className="text-gray-600 mt-1">
                {analysisData.ticker} • Financial Analysis • {analysisData.reportDate}
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">Target Price</div>
              <div className="text-2xl font-semibold text-green-700">{analysisData.summary.targetPrice}</div>
              <div className="text-sm text-green-600">+{analysisData.summary.upside} upside</div>
            </div>
          </div>
        </div>

        {/* Executive Summary */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Executive Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Rating</div>
              <div className="text-lg font-semibold text-green-700">{analysisData.summary.overallRating}</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Current Price</div>
              <div className="text-lg font-semibold text-gray-900">{analysisData.summary.currentPrice}</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Target Price</div>
              <div className="text-lg font-semibold text-gray-900">{analysisData.summary.targetPrice}</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Risk Level</div>
              <div className="text-lg font-semibold text-yellow-600">{analysisData.summary.riskLevel}</div>
            </div>
          </div>
        </div>

        {/* Key Highlights */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Key Highlights</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analysisData.highlights.map((highlight, index) => (
              <div key={index} className="border border-gray-100 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-medium text-gray-900">{highlight.category}</h3>
                  <span className="text-sm font-semibold text-green-700">{highlight.value}</span>
                </div>
                <p className="text-sm text-gray-600">{highlight.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Financial Metrics */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Key Financial Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {analysisData.keyMetrics.map((item, index) => (
              <div key={index} className="border border-gray-100 rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-1">{item.metric}</div>
                <div className="flex items-center justify-between">
                  <span className="text-lg font-semibold text-gray-900">{item.value}</span>
                  <span className={`text-sm font-medium ${
                    item.trend === 'positive' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {item.change}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Risk Factors */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Factors</h2>
            <div className="space-y-3">
              {analysisData.riskFactors.map((risk, index) => (
                <div key={index} className="flex items-start">
                  <div className="w-2 h-2 bg-red-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <p className="text-sm text-gray-700">{risk}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Growth Catalysts */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Growth Catalysts</h2>
            <div className="space-y-3">
              {analysisData.catalysts.map((catalyst, index) => (
                <div key={index} className="flex items-start">
                  <div className="w-2 h-2 bg-green-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <p className="text-sm text-gray-700">{catalyst}</p>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Investment Thesis */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Investment Thesis</h2>
          <div className="bg-gray-50 border border-gray-100 rounded-lg p-4">
            <p className="text-gray-800 leading-relaxed">
              TechFlow Solutions presents a compelling investment opportunity with strong fundamentals and clear growth trajectory. 
              The company's 28.4% revenue growth, expanding margins, and dominant position in the SaaS market provide a solid foundation. 
              Key strengths include recurring revenue model, strong cash generation, and strategic market positioning. 
              While competitive pressures and economic uncertainties pose risks, the upcoming AI platform launch and international 
              expansion should drive continued outperformance. We maintain a Strong Buy rating with a 12-month price target of $142.50.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-gray-500 pt-4 border-t border-gray-200">
          <p>This analysis is for illustrative purposes only and does not constitute investment advice.</p>
          <p>Generated on {new Date().toLocaleDateString()}</p>
        </div>

      </div>
    </div>
  );
}