'use client';

interface MetricData {
  label: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
}

interface InsightData {
  title: string;
  content: string;
  priority: 'high' | 'medium' | 'low';
}

interface AnalysisInsightsProps {
  title?: string;
  metrics?: MetricData[];
  insights?: InsightData[];
  summary?: string;
}

export default function AnalysisInsights({ 
  title = "Analysis Report",
  metrics,
  insights,
  summary
}: AnalysisInsightsProps) {
  
  const defaultMetrics: MetricData[] = [
    { label: "Revenue Growth", value: "12.4%", change: "+2.1%", changeType: "positive" },
    { label: "Operating Margin", value: "18.7%", change: "-0.3%", changeType: "negative" },
    { label: "Market Share", value: "23.1%", change: "stable", changeType: "neutral" },
    { label: "Customer Retention", value: "94.2%", change: "+1.8%", changeType: "positive" },
    { label: "EBITDA", value: "$2.4M", change: "+8.5%", changeType: "positive" },
    { label: "Debt-to-Equity", value: "0.34", change: "-0.05", changeType: "positive" }
  ];

  const defaultInsights: InsightData[] = [
    {
      title: "Revenue Performance",
      content: "Strong quarterly performance with revenue growth of 12.4% year-over-year. Growth driven by strategic expansion into emerging markets and successful product diversification initiatives.",
      priority: "high"
    },
    {
      title: "Operational Efficiency", 
      content: "Operating margins remain healthy at 18.7%, though slightly down from previous quarter due to increased R&D investments and market expansion costs.",
      priority: "medium"
    },
    {
      title: "Market Position",
      content: "Maintained stable market position at 23.1% share. Competitive landscape remains challenging but company shows resilience through innovation and customer focus.",
      priority: "medium"
    },
    {
      title: "Financial Health",
      content: "Improved debt-to-equity ratio indicates stronger financial position. Cash flow generation remains robust, supporting continued investment in growth initiatives.",
      priority: "low"
    }
  ];

  const defaultSummary = "The analysis indicates a company in a strong financial position with sustainable growth prospects. Key performance indicators show positive trends across revenue, customer retention, and debt management. While operating margins face pressure from strategic investments, the overall trajectory remains favorable. Recommended focus areas include optimizing operational efficiency and monitoring competitive dynamics in core markets.";

  const displayMetrics = metrics || defaultMetrics;
  const displayInsights = insights || defaultInsights;
  const displaySummary = summary || defaultSummary;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="bg-white border border-gray-200 rounded-lg p-8">
          <h1 className="text-3xl font-semibold text-gray-900 mb-2">{title}</h1>
          <p className="text-gray-600">Generated on {new Date().toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}</p>
        </div>

        {/* Key Metrics */}
        <div className="bg-white border border-gray-200 rounded-lg p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Key Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {displayMetrics.map((metric, index) => (
              <div key={index} className="border border-gray-100 rounded-lg p-6 bg-gray-50">
                <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
                  {metric.label}
                </div>
                <div className="text-2xl font-semibold text-gray-900 mb-1">
                  {metric.value}
                </div>
                {metric.change && (
                  <div className={`text-sm ${
                    metric.changeType === 'positive' ? 'text-green-700' :
                    metric.changeType === 'negative' ? 'text-red-700' : 'text-gray-600'
                  }`}>
                    {metric.change}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Analysis Insights */}
        <div className="bg-white border border-gray-200 rounded-lg p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Analysis Insights</h2>
          <div className="space-y-6">
            {displayInsights.map((insight, index) => (
              <div key={index} className="border-l-4 border-gray-300 pl-6">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-medium text-gray-900">{insight.title}</h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    insight.priority === 'high' ? 'bg-red-100 text-red-800' :
                    insight.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {insight.priority.toUpperCase()}
                  </span>
                </div>
                <p className="text-gray-700 leading-relaxed">{insight.content}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Executive Summary */}
        <div className="bg-white border border-gray-200 rounded-lg p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Executive Summary</h2>
          <div className="bg-gray-50 border border-gray-100 rounded-lg p-6">
            <p className="text-gray-800 leading-relaxed text-lg">{displaySummary}</p>
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white border border-gray-200 rounded-lg p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Key Recommendations</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border border-gray-200 rounded-lg p-6">
              <h4 className="font-medium text-gray-900 mb-3">Short-term Actions</h4>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-gray-400 mr-2">•</span>
                  Monitor operational efficiency metrics closely
                </li>
                <li className="flex items-start">
                  <span className="text-gray-400 mr-2">•</span>
                  Optimize R&D investment allocation
                </li>
                <li className="flex items-start">
                  <span className="text-gray-400 mr-2">•</span>
                  Review competitive positioning strategies
                </li>
              </ul>
            </div>
            <div className="border border-gray-200 rounded-lg p-6">
              <h4 className="font-medium text-gray-900 mb-3">Long-term Strategy</h4>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-gray-400 mr-2">•</span>
                  Continue market expansion initiatives
                </li>
                <li className="flex items-start">
                  <span className="text-gray-400 mr-2">•</span>
                  Strengthen financial position through cash flow optimization
                </li>
                <li className="flex items-start">
                  <span className="text-gray-400 mr-2">•</span>
                  Invest in technology and innovation capabilities
                </li>
              </ul>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}