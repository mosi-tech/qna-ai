'use client';

import Headline from '@/components/insights/Headline';
import Subheadline from '@/components/insights/Subheadline';
import QueryRestatement from '@/components/insights/QueryRestatement';
import RankedList from '@/components/insights/RankedList';
import KeyValueTable from '@/components/insights/KeyValueTable';
import StatGroup from '@/components/insights/StatGroup';
import Section from '@/components/insights/Section';
import Grid from '@/components/insights/Grid';
import TimelineList from '@/components/insights/TimelineList';
import DistributionSummary from '@/components/insights/DistributionSummary';
import TrendDescription from '@/components/insights/TrendDescription';
import BadgeList from '@/components/insights/BadgeList';
import MethodologyBlock from '@/components/insights/MethodologyBlock';
import LimitationsNote from '@/components/insights/LimitationsNote';
import SummaryConclusion from '@/components/insights/SummaryConclusion';
import CalloutNote from '@/components/insights/CalloutNote';
import Divider from '@/components/insights/Divider';
import TimeProgressIndicator from '@/components/insights/TimeProgressIndicator';
import ComparisonCard from '@/components/insights/ComparisonCard';
import VelocityIndicator from '@/components/insights/VelocityIndicator';
import EventImpactBlock from '@/components/insights/EventImpactBlock';

export default function ReboundSpeedAnalysis() {
  const handleApprove = (component: string) => {
    console.log(`Approved: ${component}`);
  };

  const handleDisapprove = (component: string) => {
    console.log(`Disapproved: ${component}`);
  };

  // Mock data for fastest rebound analysis
  const fastestRebounds = [
    {
      id: 'NVDA',
      name: 'NVIDIA Corp',
      value: '2.3 days',
      change: '-87% faster',
      changeType: 'positive' as const,
      subtitle: 'AI/Semiconductor sector'
    },
    {
      id: 'TSLA', 
      name: 'Tesla Inc',
      value: '3.1 days',
      change: '-76% faster',
      changeType: 'positive' as const,
      subtitle: 'Electric Vehicle sector'
    },
    {
      id: 'AMZN',
      name: 'Amazon.com Inc',
      value: '4.2 days',
      change: '-68% faster', 
      changeType: 'positive' as const,
      subtitle: 'E-commerce/Cloud sector'
    },
    {
      id: 'META',
      name: 'Meta Platforms Inc',
      value: '5.8 days',
      change: '-55% faster',
      changeType: 'positive' as const,
      subtitle: 'Social Media sector'
    },
    {
      id: 'GOOGL',
      name: 'Alphabet Inc',
      value: '6.4 days', 
      change: '-51% faster',
      changeType: 'positive' as const,
      subtitle: 'Technology/Search sector'
    },
    {
      id: 'MSFT',
      name: 'Microsoft Corp',
      value: '7.9 days',
      change: '-39% faster',
      changeType: 'positive' as const,
      subtitle: 'Software/Cloud sector'
    },
    {
      id: 'AAPL',
      name: 'Apple Inc',
      value: '9.2 days',
      change: '-29% faster',
      changeType: 'positive' as const,
      subtitle: 'Consumer Technology sector'
    },
    {
      id: 'NFLX',
      name: 'Netflix Inc',
      value: '11.7 days',
      change: '-10% faster',
      changeType: 'positive' as const,
      subtitle: 'Streaming/Media sector'
    }
  ];

  const reboundMetrics = [
    { symbol: 'NVDA', declineDate: '2024-07-15', reboundDays: 2.3, volume: '156M', sector: 'Semiconductor' },
    { symbol: 'TSLA', declineDate: '2024-08-22', reboundDays: 3.1, volume: '89M', sector: 'Automotive' },
    { symbol: 'AMZN', declineDate: '2024-09-05', reboundDays: 4.2, volume: '67M', sector: 'E-commerce' },
    { symbol: 'META', declineDate: '2024-06-18', reboundDays: 5.8, volume: '45M', sector: 'Social Media' }
  ];

  const reboundEvents = [
    {
      id: '1',
      date: '2024-07-15',
      title: 'NVDA 10% Decline Event',
      description: 'Semiconductor selloff triggered by AI bubble concerns. Stock recovered 5% within 2.3 days on renewed institutional buying.',
      type: 'negative' as const,
      impact: 'high' as const
    },
    {
      id: '2', 
      date: '2024-07-17',
      title: 'NVDA 5% Recovery Complete',
      description: 'Fastest recovery in analysis period. Strong volume surge and options flow indicated institutional confidence.',
      type: 'positive' as const,
      impact: 'high' as const
    },
    {
      id: '3',
      date: '2024-08-22',
      title: 'TSLA Earnings Miss Decline',
      description: 'Tesla fell 10% on delivery disappointment. Quick recovery driven by autonomous driving optimism.',
      type: 'negative' as const,
      impact: 'medium' as const
    },
    {
      id: '4',
      date: '2024-08-25', 
      title: 'TSLA Rebound Completion',
      description: 'Second fastest recovery at 3.1 days. Elon Musk timeline announcements catalyzed buying interest.',
      type: 'positive' as const,
      impact: 'medium' as const
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        <Headline 
          text="Fastest 5% Rebound Analysis After 10% Declines"
          onApprove={() => handleApprove('Headline')}
        />
        
        <Subheadline 
          text="Analysis of recovery speed for symbols experiencing significant drawdowns in 2024"
          onApprove={() => handleApprove('Subheadline')}
        />

        <QueryRestatement 
          originalQuery="Which symbols had the fastest 5% rebound after a 10% decline?"
          interpretation="Identification and ranking of stocks by recovery speed following major selloff events"
          scope="Major US equities with 10%+ declines in 2024, measuring time to 5% recovery from trough"
          onApprove={() => handleApprove('QueryRestatement')}
        />

        <Section title="Recovery Speed Rankings" onApprove={() => handleApprove('Recovery Rankings')}>
          
          <StatGroup 
            title="Key Rebound Statistics"
            stats={[
              { value: 2.3, label: "Fastest Recovery", change: "NVDA", format: "number" },
              { value: 6.4, label: "Average Recovery Time", change: "days", format: "number" },
              { value: 87, label: "Speed Advantage", change: "vs average", format: "percentage" }
            ]}
            columns={3}
            onApprove={() => handleApprove('Rebound Stats')}
          />

          <RankedList 
            title="Fastest Recovery Rankings"
            items={fastestRebounds}
            showValues={true}
            onApprove={() => handleApprove('Recovery Rankings')}
          />

          <KeyValueTable 
            title="Detailed Rebound Metrics"
            data={reboundMetrics}
            columns={[
              { key: 'symbol', label: 'Symbol', align: 'left' },
              { key: 'declineDate', label: 'Decline Date', align: 'center' },
              { key: 'reboundDays', label: 'Recovery Time (Days)', align: 'right', format: 'number' },
              { key: 'volume', label: 'Avg Daily Volume', align: 'right' },
              { key: 'sector', label: 'Sector', align: 'left' }
            ]}
            onApprove={() => handleApprove('Rebound Metrics')}
          />

        </Section>

        <Section title="Recovery Analysis" onApprove={() => handleApprove('Recovery Analysis')}>
          
          <Grid columns={2}>
            <ComparisonCard 
              value={2.3}
              comparisonValue={6.4}
              label="NVDA Recovery Speed"
              comparisonLabel="Market Average"
              format="days"
              variant="detailed"
              onApprove={() => handleApprove('Comparison Card')}
            />

            <VelocityIndicator 
              velocity={2.3}
              maxVelocity={12}
              label="Recovery Velocity"
              unit="days"
              comparison={{ value: 6.4, label: "Average Recovery" }}
              direction="lower-is-better"
              onApprove={() => handleApprove('Velocity Indicator')}
            />
          </Grid>

          <TimeProgressIndicator 
            title="NVDA Recovery Timeline"
            stages={[
              { id: 'decline', label: 'Market Decline', duration: 0, type: 'start', description: '10% drop initiated' },
              { id: 'bottom', label: 'Trough Reached', duration: 0.8, type: 'event', description: 'Maximum drawdown' },
              { id: 'recovery', label: '5% Recovery', duration: 2.3, type: 'end', description: 'Target achieved' }
            ]}
            unit="days"
            variant="detailed"
            onApprove={() => handleApprove('Time Progress')}
          />

          <EventImpactBlock 
            event={{
              title: "AI Sector Selloff",
              date: "July 15, 2024",
              description: "Broad semiconductor selloff triggered by concerns over AI bubble and geopolitical tensions affecting chip manufacturing.",
              type: "negative",
              category: "Market Event"
            }}
            beforeValue={485.50}
            afterValue={437.25}
            recoveryValue={462.80}
            metric="NVDA Stock Price"
            format="currency"
            timeToRecovery="2.3 days"
            variant="detailed"
            onApprove={() => handleApprove('Event Impact')}
          />

          <Grid columns={2}>
            <TrendDescription 
              trend="Technology and growth stocks demonstrate significantly faster recovery times compared to traditional sectors. High-beta names with strong institutional support show quickest mean reversion patterns."
              direction="up"
              magnitude="strong"
              timeframe="2024 YTD"
              confidence="high"
              onApprove={() => handleApprove('Recovery Trend')}
            />

            <DistributionSummary 
              title="Recovery Time Distribution"
              data={{
                min: 2.3,
                max: 11.7,
                mean: 6.4,
                median: 5.8,
                count: 8,
                stdDev: 3.2
              }}
              format="number"
              onApprove={() => handleApprove('Distribution Summary')}
            />
          </Grid>

          <TimelineList 
            title="Key Rebound Events"
            events={reboundEvents}
            onApprove={() => handleApprove('Rebound Timeline')}
          />

          <BadgeList 
            title="Recovery Characteristics"
            badges={[
              { text: "High Volume Surge", type: "positive" },
              { text: "Institutional Buying", type: "info" },
              { text: "Options Activity Spike", type: "positive" },
              { text: "Momentum Continuation", type: "neutral" },
              { text: "Mean Reversion Pattern", type: "info" }
            ]}
            onApprove={() => handleApprove('Recovery Characteristics')}
          />

        </Section>

        <Divider label="Analysis Framework" />

        <Grid columns={2}>
          <MethodologyBlock 
            methodology="Rebound analysis identifies 10% decline events from recent highs, then measures trading days required for 5% recovery from the decline trough. Analysis excludes gaps and after-hours movements."
            dataSource="Daily OHLC data from Bloomberg, Volume from exchange feeds"
            timeframe="January 1, 2024 to November 15, 2024"
            approach="Event-driven analysis with statistical ranking"
            onApprove={() => handleApprove('Methodology')}
          />

          <LimitationsNote 
            limitations={[
              "Analysis limited to major cap US equities with adequate liquidity",
              "Excludes corporate actions, dividends, and stock splits during measurement periods", 
              "Recovery measurement based on closing prices only",
              "Does not account for intraday volatility or trading halts"
            ]}
            onApprove={() => handleApprove('Limitations')}
          />
        </Grid>

        <CalloutNote 
          type="info"
          title="Key Insight"
          content="Technology stocks demonstrate superior rebound velocity, with NVIDIA leading at 2.3 days recovery time. This pattern suggests strong institutional support and momentum-driven buying in high-growth names during temporary selloffs."
          onApprove={() => handleApprove('Key Insight')}
        />

        <SummaryConclusion 
          keyFindings={[
            "NVIDIA showed fastest 5% rebound at 2.3 days after 10% decline",
            "Technology sector dominates top recovery rankings with 6 of top 8 positions",
            "Average recovery time across all symbols was 6.4 days",
            "High-beta growth stocks consistently outperformed defensive names in rebound speed"
          ]}
          conclusion="Growth and technology stocks demonstrate superior mean reversion characteristics during selloff events. The combination of institutional support, high liquidity, and momentum trading creates faster recovery patterns compared to traditional value sectors."
          nextSteps={[
            "Monitor for similar decline patterns in current market environment", 
            "Consider rebound speed as factor in tactical allocation decisions",
            "Update analysis quarterly with new decline/recovery events"
          ]}
          confidence="high"
          onApprove={() => handleApprove('Conclusion')}
        />

      </div>
    </div>
  );
}