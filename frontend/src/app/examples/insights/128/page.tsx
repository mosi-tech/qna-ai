'use client';

import Headline from '@/components/insights/Headline';
import Subheadline from '@/components/insights/Subheadline';
import RankedList from '@/components/insights/RankedList';
import KeyValueTable from '@/components/insights/KeyValueTable';
import StatGroup from '@/components/insights/StatGroup';
import BadgeList from '@/components/insights/BadgeList';
import SummaryConclusion from '@/components/insights/SummaryConclusion';

export default function MorningReversalAnalysis() {
  const handleApprove = (component: string) => {
    console.log(`Approved: ${component}`);
  };

  const handleDisapprove = (component: string) => {
    console.log(`Disapproved: ${component}`);
  };

  // Mock data for morning reversal analysis
  const reversalRankings = [
    {
      id: 'AAPL',
      name: 'Apple Inc',
      value: '87.3%',
      change: '+12.4%',
      changeType: 'positive' as const,
      subtitle: 'Technology sector'
    },
    {
      id: 'MSFT', 
      name: 'Microsoft Corp',
      value: '84.1%',
      change: '+8.7%',
      changeType: 'positive' as const,
      subtitle: 'Software/Cloud sector'
    },
    {
      id: 'GOOGL',
      name: 'Alphabet Inc',
      value: '81.6%',
      change: '+5.2%',
      changeType: 'positive' as const,
      subtitle: 'Technology/Search sector'
    },
    {
      id: 'META',
      name: 'Meta Platforms Inc',
      value: '78.9%',
      change: '+3.1%',
      changeType: 'positive' as const,
      subtitle: 'Social Media sector'
    },
    {
      id: 'NVDA',
      name: 'NVIDIA Corp',
      value: '76.4%',
      change: '-2.3%',
      changeType: 'negative' as const,
      subtitle: 'AI/Semiconductor sector'
    },
    {
      id: 'AMZN',
      name: 'Amazon.com Inc',
      value: '74.2%',
      change: '-1.8%',
      changeType: 'negative' as const,
      subtitle: 'E-commerce/Cloud sector'
    },
    {
      id: 'TSLA',
      name: 'Tesla Inc',
      value: '69.7%',
      change: '-4.6%',
      changeType: 'negative' as const,
      subtitle: 'Electric Vehicle sector'
    },
    {
      id: 'NFLX',
      name: 'Netflix Inc',
      value: '67.3%',
      change: '-6.2%',
      changeType: 'negative' as const,
      subtitle: 'Streaming/Media sector'
    }
  ];

  const reversalMetrics = [
    { 
      symbol: 'AAPL', 
      selloffDays: 67, 
      reversalDays: 58, 
      successRate: 87.3, 
      avgReversalMagnitude: 2.8, 
      avgSelloffMagnitude: -3.1
    },
    { 
      symbol: 'MSFT', 
      selloffDays: 62, 
      reversalDays: 52, 
      successRate: 84.1, 
      avgReversalMagnitude: 2.4, 
      avgSelloffMagnitude: -2.7
    },
    { 
      symbol: 'GOOGL', 
      selloffDays: 59, 
      reversalDays: 48, 
      successRate: 81.6, 
      avgReversalMagnitude: 2.6, 
      avgSelloffMagnitude: -2.9
    },
    { 
      symbol: 'META', 
      selloffDays: 71, 
      reversalDays: 56, 
      successRate: 78.9, 
      avgReversalMagnitude: 3.2, 
      avgSelloffMagnitude: -3.4
    },
    { 
      symbol: 'NVDA', 
      selloffDays: 73, 
      reversalDays: 55, 
      successRate: 76.4, 
      avgReversalMagnitude: 4.1, 
      avgSelloffMagnitude: -4.7
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        <Headline 
          text="Morning Selloff Reversal Analysis"
          onApprove={() => handleApprove('Headline')}
        />
        
        <Subheadline 
          text="Identification of symbols most likely to reverse higher after morning weakness in 2024"
          onApprove={() => handleApprove('Subheadline')}
        />

        <StatGroup 
          title="Key Reversal Statistics"
          stats={[
            { value: 87.3, label: "Highest Success Rate", change: "AAPL", format: "percentage" },
            { value: 77.8, label: "Average Success Rate", change: "all symbols", format: "percentage" },
            { value: 394, label: "Total Selloff Days", change: "analyzed", format: "number" },
            { value: 306, label: "Successful Reversals", change: "confirmed", format: "number" }
          ]}
          columns={4}
          onApprove={() => handleApprove('Reversal Stats')}
        />

        <RankedList 
          title="Morning Reversal Success Rankings"
          items={reversalRankings}
          showValues={true}
          onApprove={() => handleApprove('Reversal Rankings')}
        />

        <KeyValueTable 
          title="Detailed Reversal Analysis"
          data={reversalMetrics}
          columns={[
            { key: 'symbol', label: 'Symbol', align: 'left' },
            { key: 'selloffDays', label: 'Morning Selloffs', align: 'right', format: 'number' },
            { key: 'reversalDays', label: 'Successful Reversals', align: 'right', format: 'number' },
            { key: 'successRate', label: 'Success Rate (%)', align: 'right', format: 'percentage' },
            { key: 'avgSelloffMagnitude', label: 'Avg Selloff (%)', align: 'right', format: 'percentage' },
            { key: 'avgReversalMagnitude', label: 'Avg Reversal (%)', align: 'right', format: 'percentage' }
          ]}
          onApprove={() => handleApprove('Reversal Metrics')}
        />

        <BadgeList 
          title="Reversal Pattern Characteristics"
          badges={[
            { text: "Technology Sector Leadership", type: "positive" },
            { text: "Large Cap Stability", type: "info" },
            { text: "High Volume Confirmation", type: "positive" },
            { text: "Institutional Support", type: "info" },
            { text: "Mean Reversion Pattern", type: "neutral" },
            { text: "Morning Weakness Fade", type: "positive" }
          ]}
          layout="grid"
          onApprove={() => handleApprove('Pattern Characteristics')}
        />

        <SummaryConclusion 
          keyFindings={[
            "Apple (AAPL) leads with 87.3% morning reversal success rate",
            "Technology and large-cap stocks dominate top reversal rankings", 
            "Average reversal magnitude of 2.8% following morning weakness",
            "Pattern most pronounced in high-volume, liquid names with institutional support"
          ]}
          conclusion="Large-cap technology stocks demonstrate consistent ability to reverse morning selloffs, with Apple, Microsoft, and Alphabet showing superior mean reversion characteristics. The pattern suggests institutional buying on temporary weakness creates reliable reversal opportunities in quality growth names."
          nextSteps={[
            "Monitor for morning weakness in top-ranked symbols",
            "Consider reversal trades during oversold morning conditions",
            "Focus on high-volume confirmation for entry signals"
          ]}
          confidence="high"
          onApprove={() => handleApprove('Conclusion')}
        />

      </div>
    </div>
  );
}