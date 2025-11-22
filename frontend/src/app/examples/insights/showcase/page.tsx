'use client';

// Tier 1 - Core Insight Components
// import Headline from '@/components/insights/Headline';
// import Subheadline from '@/components/insights/Subheadline';
// import NarrativeParagraph from '@/components/insights/NarrativeParagraph';
import BulletList from '@/components/insights/BulletList';
// import KeyValueTable from '@/components/insights/KeyValueTable';
import ComparisonTable from '@/components/insights/ComparisonTable';
// import BadgeList from '@/components/insights/BadgeList';
import StatCard from '@/components/insights/helper/StatCard';
import StatGroup from '@/components/insights/StatGroup';
// import CalloutNote from '@/components/insights/CalloutNote';

// Tier 2 - Structural Layout Components
// import Section from '@/components/insights/Section';
// import Subsection from '@/components/insights/Subsection';
// import Grid from '@/components/insights/Grid';
// import Divider from '@/components/insights/Divider';
// import Accordion from '@/components/insights/Accordion';
// import Tabs from '@/components/insights/Tabs';

// Tier 3 - Data & Insight Visualization
import RankedList from '@/components/insights/RankedList';
// import TrendDescription from '@/components/insights/TrendDescription';
// import DistributionSummary from '@/components/insights/DistributionSummary';
// import ChangeIndicator from '@/components/insights/ChangeIndicator';
// import MatrixTable from '@/components/insights/MatrixTable';
// import TimelineList from '@/components/insights/TimelineList';
// import ThresholdIndicator from '@/components/insights/ThresholdIndicator';
// import HeatmapText from '@/components/insights/HeatmapText';

// Tier 6 - Advanced Analytics Components  
// import TimeProgressIndicator from '@/components/insights/TimeProgressIndicator';
// import ComparisonCard from '@/components/insights/ComparisonCard';
// import EventImpactBlock from '@/components/insights/EventImpactBlock';
// import VelocityIndicator from '@/components/insights/VelocityIndicator';
// import PeriodComparisonTable from '@/components/insights/PeriodComparisonTable';
// import SignificanceIndicator from '@/components/insights/SignificanceIndicator';
// import TimeSeriesBreakdown from '@/components/insights/TimeSeriesBreakdown';
// import ConfirmationIndicator from '@/components/insights/ConfirmationIndicator';
// import StatWithConfidence from '@/components/insights/StatWithConfidence';
// import SignalStrengthGauge from '@/components/insights/SignalStrengthGauge';

// Tier 4 - Action & Decision Support
// import ActionList from '@/components/insights/ActionList';
// import DecisionBlock from '@/components/insights/DecisionBlock';
// import OptionComparison from '@/components/insights/OptionComparison';
// import ScenarioBlock from '@/components/insights/ScenarioBlock';
// import Checklist from '@/components/insights/Checklist';
import SummaryConclusion from '@/components/insights/SummaryConclusion';

// Tier 5 - Metadata, Context, and Queries
// import QueryRestatement from '@/components/insights/QueryRestatement';
// import AssumptionList from '@/components/insights/AssumptionList';
// import LimitationsNote from '@/components/insights/LimitationsNote';
// import MethodologyBlock from '@/components/insights/MethodologyBlock';
import SectionedInsightCard from '@/components/insights/SectionedInsightCard';
// import MultiMetricComparisonCard from '@/components/insights/MultiMetricComparisonCard';

export default function ComponentShowcase() {
  const handleApprove = (componentName: string) => {
    console.log(`Approved: ${componentName}`);
  };

  const handleDisapprove = (componentName: string) => {
    console.log(`Disapproved: ${componentName}`);
  };

  // Sample data for demonstrations
  const keyValueData = [
    { metric: 'Revenue', value: 1250000, change: '+12.4%', period: 'Q3 2024' },
    { metric: 'EBITDA', value: 187500, change: '+8.7%', period: 'Q3 2024' },
    { metric: 'Margin', value: 15.0, change: '-0.8%', period: 'Q3 2024' }
  ];

  const comparisonData = {
    'AAPL': { revenue: 123.5, margin: 25.2, growth: 8.4 },
    'MSFT': { revenue: 98.3, margin: 32.1, growth: 12.1 },
    'GOOGL': { revenue: 89.7, margin: 28.8, growth: 15.2 }
  };

  const rankedItems = [
    { id: '1', name: 'Apple Inc.', value: 2.8, changeType: 'positive' as const, change: '+0.3' },
    { id: '2', name: 'Microsoft Corp.', value: 2.3, changeType: 'positive' as const, change: '+0.1' },
    { id: '3', name: 'Amazon.com Inc.', value: 1.9, changeType: 'negative' as const, change: '-0.2' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        
        <Headline 
          text="Analysis Component Library Showcase" 
          onApprove={() => handleApprove('Headline')}
          onDisapprove={() => handleDisapprove('Headline')}
        />
        
        <Subheadline 
          text="Comprehensive demonstration of all 44 professional analysis components for financial and business insights"
          onApprove={() => handleApprove('Subheadline')}
        />

        {/* Tier 1 - Core Insight Components */}
        <Section title="Tier 1 - Core Insight Components" onApprove={() => handleApprove('Tier 1')}>
          
          <Subsection title="Text Components" onApprove={() => handleApprove('Text Components')}>
            <NarrativeParagraph 
              content="This showcase demonstrates the complete analysis component library, featuring 34 professionally designed components across 5 tiers. Each component follows consistent design principles with approve/disapprove functionality."
              onApprove={() => handleApprove('NarrativeParagraph')}
            />
            
            <BulletList 
              title="Key Features"
              items={[
                "Professional financial styling with subtle colors",
                { text: "Interactive approve/disapprove buttons on every component", emphasis: "strong" },
                "TypeScript interfaces and comprehensive documentation",
                "Responsive design for all screen sizes"
              ]}
              onApprove={() => handleApprove('BulletList')}
            />

            <BadgeList 
              title="Component Status"
              badges={[
                { text: "Production Ready", type: "positive" },
                { text: "TypeScript", type: "info" },
                { text: "Responsive", type: "positive" },
                { text: "Beta Testing", type: "warning" }
              ]}
              onApprove={() => handleApprove('BadgeList')}
            />
          </Subsection>

          <Subsection title="Data Display Components">
            <KeyValueTable 
              title="Sample Financial Metrics"
              data={keyValueData}
              columns={[
                { key: 'metric', label: 'Metric', align: 'left' },
                { key: 'value', label: 'Value', align: 'right', format: 'currency' },
                { key: 'change', label: 'Change', align: 'center' },
                { key: 'period', label: 'Period', align: 'center' }
              ]}
              onApprove={() => handleApprove('KeyValueTable')}
            />

            <ComparisonTable 
              title="Stock Comparison Analysis"
              entities={[
                { id: 'AAPL', name: 'AAPL', subtitle: 'Apple Inc.' },
                { id: 'MSFT', name: 'MSFT', subtitle: 'Microsoft' },
                { id: 'GOOGL', name: 'GOOGL', subtitle: 'Alphabet' }
              ]}
              metrics={[
                { id: 'revenue', name: 'Revenue', format: 'currency' },
                { id: 'margin', name: 'Margin %', format: 'percentage' },
                { id: 'growth', name: 'Growth %', format: 'percentage' }
              ]}
              data={comparisonData}
              onApprove={() => handleApprove('ComparisonTable')}
            />
          </Subsection>

          <div className="space-y-4">
            <h4 className="text-lg font-medium text-gray-900">StatCard - Versatile Use Cases</h4>
            
            <Grid columns={3}>
              <StatCard 
                value={2847.32}
                label="Portfolio Value"
                change={"+12.4%"}
                changeType="positive"
                format="currency"
                onApprove={() => handleApprove('Financial Stat')}
              />
              <StatCard 
                value={156789}
                label="Website Visitors"
                change={"+24.1%"}
                changeType="positive"
                format="number"
                onApprove={() => handleApprove('Traffic Stat')}
              />
              <StatCard 
                value={94.2}
                label="System Uptime"
                change={"-0.8%"}
                changeType="negative"
                format="percentage"
                onApprove={() => handleApprove('Performance Stat')}
              />
            </Grid>

            <Grid columns={3}>
              <StatCard 
                value="Excellent"
                label="Credit Rating"
                change="Upgraded"
                changeType="positive"
                format="text"
                onApprove={() => handleApprove('Text Stat')}
              />
              <StatCard 
                value={3.2}
                label="Response Time"
                change={"+0.4s"}
                changeType="negative"
                format="number"
                onApprove={() => handleApprove('Time Stat')}
              />
              <StatCard 
                value={42.7}
                label="Conversion Rate"
                change={"+5.1%"}
                changeType="positive"
                format="percentage"
                onApprove={() => handleApprove('Conversion Stat')}
              />
            </Grid>
          </div>

          <StatGroup 
            title="Key Performance Indicators"
            stats={[
              { value: 142.5, label: "Stock Price", change: "+3.2%", changeType: "positive", format: "currency" },
              { value: 24.8, label: "P/E Ratio", change: "-1.1", changeType: "negative", format: "number" },
              { value: 2.1, label: "Dividend Yield", change: "+0.1%", changeType: "positive", format: "percentage" }
            ]}
            columns={3}
            onApprove={() => handleApprove('StatGroup')}
          />

          <CalloutNote 
            type="warning"
            title="Important Disclaimer"
            content="This component library is for demonstration purposes. All financial data shown is simulated and should not be used for actual investment decisions."
            onApprove={() => handleApprove('CalloutNote')}
          />

        </Section>

        {/* Tier 2 - Structural Layout Components */}
        <Section title="Tier 2 - Structural Layout Components" onApprove={() => handleApprove('Tier 2')}>
          
          <Divider label="Layout Demonstration" onApprove={() => handleApprove('Divider')} />

          <Accordion 
            sections={[
              {
                id: 'financial',
                title: 'Financial Analysis Details',
                content: <NarrativeParagraph content="Detailed financial analysis would go here, including balance sheet analysis, cash flow statements, and profitability metrics." />
              },
              {
                id: 'risk',
                title: 'Risk Assessment',
                content: <BulletList items={["Market risk exposure", "Credit risk factors", "Operational risk analysis"]} />
              }
            ]}
            onApprove={() => handleApprove('Accordion')}
          />

          <Tabs 
            tabs={[
              {
                id: 'overview',
                title: 'Overview',
                badge: '5',
                content: <NarrativeParagraph content="Portfolio overview with key metrics and performance indicators." />
              },
              {
                id: 'holdings',
                title: 'Holdings',
                badge: '23',
                content: <BulletList items={["AAPL - 15.2%", "MSFT - 12.8%", "GOOGL - 9.4%"]} />
              }
            ]}
            onApprove={() => handleApprove('Tabs')}
          />

        </Section>

        {/* Tier 3 - Data & Insight Visualization */}
        <Section title="Tier 3 - Data & Insight Visualization" onApprove={() => handleApprove('Tier 3')}>
          
          <div className="space-y-4">
            <h4 className="text-lg font-medium text-gray-900">RankedList - Versatile Use Cases</h4>
            
            <Grid columns={2}>
              <RankedList 
                title="Top Stock Performers"
                items={[
                  { id: '1', name: 'Apple Inc.', value: '2.8%', changeType: 'positive' as const, change: '+0.3%' },
                  { id: '2', name: 'Microsoft Corp.', value: '2.3%', changeType: 'positive' as const, change: '+0.1%' },
                  { id: '3', name: 'Amazon.com Inc.', value: '1.9%', changeType: 'negative' as const, change: '-0.2%' }
                ]}
                onApprove={() => handleApprove('Stock Rankings')}
              />
              
              <RankedList 
                title="Sales Team Performance"
                items={[
                  { id: '1', name: 'Sarah Johnson', value: '$147K', changeType: 'positive' as const, change: '+$23K', subtitle: 'West Region' },
                  { id: '2', name: 'Mike Chen', value: '$132K', changeType: 'positive' as const, change: '+$18K', subtitle: 'East Region' },
                  { id: '3', name: 'Lisa Rodriguez', value: '$128K', changeType: 'neutral' as const, change: '+$2K', subtitle: 'Central Region' }
                ]}
                onApprove={() => handleApprove('Sales Rankings')}
              />
            </Grid>

            <Grid columns={2}>
              <RankedList 
                title="Website Pages by Traffic"
                items={[
                  { id: '1', name: 'Homepage', value: '45.2K', changeType: 'positive' as const, change: '+12%', subtitle: 'visits/month' },
                  { id: '2', name: 'Product Catalog', value: '38.7K', changeType: 'positive' as const, change: '+8%', subtitle: 'visits/month' },
                  { id: '3', name: 'About Us', value: '21.4K', changeType: 'negative' as const, change: '-3%', subtitle: 'visits/month' }
                ]}
                onApprove={() => handleApprove('Traffic Rankings')}
              />
              
              <RankedList 
                title="Customer Satisfaction Scores"
                items={[
                  { id: '1', name: 'Premium Support', value: '9.8/10', changeType: 'positive' as const, change: '+0.2', subtitle: 'Tier 1' },
                  { id: '2', name: 'Standard Support', value: '8.4/10', changeType: 'neutral' as const, change: '0.0', subtitle: 'Tier 2' },
                  { id: '3', name: 'Basic Support', value: '7.1/10', changeType: 'negative' as const, change: '-0.3', subtitle: 'Tier 3' }
                ]}
                onApprove={() => handleApprove('Satisfaction Rankings')}
              />
            </Grid>
          </div>

          <Grid columns={2}>
            <TrendDescription 
              trend="Strong upward momentum in technology sector with increasing institutional investment and positive earnings revisions across major holdings."
              direction="up"
              magnitude="strong"
              timeframe="Q3 2024"
              confidence="high"
              onApprove={() => handleApprove('TrendDescription')}
            />

            <DistributionSummary 
              title="Portfolio Returns Distribution"
              data={{
                min: -8.2,
                max: 23.4,
                mean: 12.7,
                median: 11.3,
                count: 252,
                stdDev: 5.8
              }}
              format="percentage"
              variant="detailed"
              onApprove={() => handleApprove('DistributionSummary')}
            />
          </Grid>

          <Grid columns={4}>
            <ChangeIndicator 
              value={12.4}
              format="percentage"
              label="YTD"
              onApprove={() => handleApprove('ChangeIndicator')}
            />
            <ChangeIndicator 
              value={-2.1}
              format="percentage"
              label="1M"
              onApprove={() => handleApprove('ChangeIndicator')}
            />
            <ChangeIndicator 
              value={847}
              format="currency"
              label="Daily P&L"
              onApprove={() => handleApprove('ChangeIndicator')}
            />
            <ThresholdIndicator 
              value={18.5}
              threshold={20}
              label="Risk Limit"
              type="below"
              format="percentage"
              onApprove={() => handleApprove('ThresholdIndicator')}
            />
          </Grid>

          <MatrixTable 
            title="Correlation Matrix"
            matrix={[
              [1.00, 0.72, 0.45],
              [0.72, 1.00, 0.38],
              [0.45, 0.38, 1.00]
            ]}
            rowLabels={['Tech', 'Finance', 'Healthcare']}
            columnLabels={['Tech', 'Finance', 'Healthcare']}
            format="correlation"
            colorScale={true}
            onApprove={() => handleApprove('MatrixTable')}
          />

          <TimelineList 
            title="Recent Portfolio Events"
            events={[
              {
                id: '1',
                date: '2024-11-15',
                title: 'Technology Rebalancing',
                description: 'Increased allocation to AI and cloud computing sectors',
                type: 'positive',
                impact: 'medium'
              },
              {
                id: '2',
                date: '2024-11-10',
                title: 'Dividend Distribution',
                description: 'Quarterly dividend payments received from equity holdings',
                type: 'milestone',
                impact: 'low'
              },
              {
                id: '3',
                date: '2024-11-05',
                title: 'Risk Assessment Update',
                description: 'Updated risk parameters following market volatility increase',
                type: 'neutral',
                impact: 'high'
              }
            ]}
            onApprove={() => handleApprove('TimelineList')}
          />

          <HeatmapText 
            title="Risk Assessment Matrix"
            data={[
              [8.5, 6.2, 3.1],
              [7.3, 9.1, 4.8],
              [5.9, 7.7, 8.3]
            ]}
            rowLabels={['Equity', 'Fixed Income', 'Alternatives']}
            columnLabels={['Market Risk', 'Credit Risk', 'Liquidity Risk']}
            scale="risk"
            onApprove={() => handleApprove('HeatmapText')}
          />

        </Section>

        {/* Tier 4 - Action & Decision Support */}
        <Section title="Tier 4 - Action & Decision Support" onApprove={() => handleApprove('Tier 4')}>
          
          <ActionList 
            title="Recommended Actions"
            actions={[
              {
                id: '1',
                title: 'Rebalance Technology Allocation',
                description: 'Current tech allocation exceeds target by 3.2%. Consider reducing positions in overweight holdings.',
                priority: 'high',
                timeline: 'short-term',
                impact: 'medium',
                category: 'Portfolio Management'
              },
              {
                id: '2',
                title: 'Review ESG Compliance',
                description: 'Quarterly ESG review due for all holdings to ensure alignment with sustainability criteria.',
                priority: 'medium',
                timeline: 'medium-term',
                impact: 'low',
                category: 'Compliance'
              }
            ]}
            groupByPriority={true}
            variant="detailed"
            onApprove={() => handleApprove('ActionList')}
          />

          <div className="space-y-6">
            <h4 className="text-lg font-medium text-gray-900">DecisionBlock - Versatile Use Cases</h4>
            
            <DecisionBlock 
              decision="Should we increase exposure to emerging markets?"
              pros={[
                { text: "Higher expected returns in developing economies", weight: "high" },
                "Portfolio diversification benefits",
                "Undervalued relative to developed markets"
              ]}
              cons={[
                { text: "Increased volatility and political risk", weight: "high" },
                "Currency risk exposure",
                "Lower liquidity in some markets"
              ]}
              recommendation="Moderate increase with gradual implementation"
              rationale="The potential for higher returns outweighs the risks when implemented gradually with proper risk management controls."
              confidence="medium"
              onApprove={() => handleApprove('Investment Decision')}
            />

            <DecisionBlock 
              decision="Should we migrate to cloud infrastructure?"
              pros={[
                { text: "Reduced infrastructure costs ($120K annually)", weight: "high" },
                "Improved scalability and flexibility",
                "Enhanced disaster recovery capabilities",
                "Faster deployment cycles"
              ]}
              cons={[
                { text: "Data security and compliance concerns", weight: "high" },
                "Migration complexity and potential downtime",
                "Vendor dependency risks"
              ]}
              recommendation="Proceed with phased migration approach"
              rationale="Cost savings and operational benefits justify the move, while phased approach mitigates risks."
              confidence="high"
              onApprove={() => handleApprove('Tech Decision')}
            />

            <DecisionBlock 
              decision="Should we expand our product line to include premium offerings?"
              pros={[
                "Higher profit margins on premium products",
                { text: "Addresses high-value customer segment", weight: "high" },
                "Strengthens brand positioning"
              ]}
              cons={[
                { text: "Requires significant R&D investment", weight: "high" },
                "May cannibalize existing product sales",
                "Increased manufacturing complexity"
              ]}
              recommendation="Launch pilot program with limited product range"
              rationale="Market research indicates demand, but pilot approach allows validation before full commitment."
              confidence="medium"
              onApprove={() => handleApprove('Product Decision')}
            />
          </div>

          <OptionComparison 
            title="Investment Strategy Comparison"
            options={[
              {
                id: 'growth',
                name: 'Growth Strategy',
                description: 'Focus on high-growth companies',
                scores: { returns: 8.5, risk: 7.2, liquidity: 9.1, fees: 6.8 },
                totalScore: 7.9,
                recommendation: true
              },
              {
                id: 'value',
                name: 'Value Strategy', 
                description: 'Focus on undervalued companies',
                scores: { returns: 7.1, risk: 5.4, liquidity: 8.7, fees: 8.2 },
                totalScore: 7.4
              },
              {
                id: 'balanced',
                name: 'Balanced Strategy',
                description: 'Mix of growth and value',
                scores: { returns: 7.8, risk: 6.1, liquidity: 8.9, fees: 7.5 },
                totalScore: 7.6
              }
            ]}
            criteria={[
              { id: 'returns', name: 'Expected Returns', weight: 0.3, format: 'score' },
              { id: 'risk', name: 'Risk Level', weight: 0.25, format: 'score' },
              { id: 'liquidity', name: 'Liquidity', weight: 0.25, format: 'score' },
              { id: 'fees', name: 'Cost Efficiency', weight: 0.2, format: 'score' }
            ]}
            showWeights={true}
            onApprove={() => handleApprove('OptionComparison')}
          />

          <Grid columns={2}>
            <ScenarioBlock 
              title="Market Correction Scenario"
              condition="Market declines 15% over 3 months"
              outcome="Portfolio expected to decline 11-13% with defensive positioning providing downside protection"
              probability={25}
              impact="medium"
              onApprove={() => handleApprove('ScenarioBlock')}
            />

            <Checklist 
              title="Quarterly Review Checklist"
              items={[
                { id: '1', text: 'Performance attribution analysis', completed: true, required: true },
                { id: '2', text: 'Risk metrics review', completed: true, required: true },
                { id: '3', text: 'Rebalancing requirements', completed: false, required: true },
                { id: '4', text: 'Tax loss harvesting opportunities', completed: false, required: false },
                { id: '5', text: 'Client communication preparation', completed: false, required: true }
              ]}
              onApprove={() => handleApprove('Checklist')}
            />
          </Grid>

          <SummaryConclusion 
            keyFindings={[
              "Portfolio performance exceeds benchmark by 2.3% YTD",
              "Technology allocation slightly overweight at 23.2% vs 20% target",
              "Risk metrics remain within acceptable ranges",
              "ESG scores improved across all major holdings"
            ]}
            conclusion="Overall portfolio performance remains strong with good risk-adjusted returns. Minor rebalancing recommended to maintain target allocation weights."
            nextSteps={[
              "Execute rebalancing trades within 5 business days",
              "Monitor technology sector volatility",
              "Prepare monthly client reporting",
              "Schedule quarterly strategy review"
            ]}
            confidence="high"
            onApprove={() => handleApprove('SummaryConclusion')}
          />

        </Section>

        {/* Tier 5 - Metadata, Context, and Queries */}
        <Section title="Tier 5 - Metadata, Context, and Queries" onApprove={() => handleApprove('Tier 5')}>
          
          <QueryRestatement 
            originalQuery="Show me the portfolio performance analysis for Q3 2024"
            interpretation="Comprehensive analysis of portfolio returns, risk metrics, and attribution for the third quarter of 2024"
            scope="All holdings, benchmark comparison, risk-adjusted metrics"
            onApprove={() => handleApprove('QueryRestatement')}
          />

          <Grid columns={2}>
            <AssumptionList 
              assumptions={[
                "Historical correlations remain stable over analysis period",
                "No significant regulatory changes affecting portfolio holdings",
                "Market liquidity conditions remain normal",
                "Currency hedging costs estimated at 0.15% annually"
              ]}
              onApprove={() => handleApprove('AssumptionList')}
            />

            <LimitationsNote 
              limitations={[
                "Analysis based on daily price data, intraday volatility not captured",
                "Small-cap holdings may have stale pricing issues",
                "Performance attribution subject to estimation errors",
                "ESG scores rely on third-party data providers"
              ]}
              onApprove={() => handleApprove('LimitationsNote')}
            />
          </Grid>

          <MethodologyBlock 
            methodology="Portfolio analysis conducted using modern portfolio theory principles with risk attribution using factor models. Performance measured against custom benchmark weighted 60% S&P 500, 30% international developed markets, 10% emerging markets."
            dataSource="Bloomberg Terminal, FactSet, Morningstar Direct"
            timeframe="Daily data from Jan 1, 2024 to Nov 15, 2024"
            approach="Quantitative analysis with qualitative overlay"
            onApprove={() => handleApprove('MethodologyBlock')}
          />

          <div className="space-y-6">
            <h4 className="text-lg font-medium text-gray-900">SectionedInsightCard - Versatile Use Cases</h4>
            
            <Grid columns={2}>
              <SectionedInsightCard 
                title="Q3 Financial Performance Review"
                description="Comprehensive quarterly analysis across key business metrics"
                sections={[
                  {
                    title: "Revenue Growth",
                    content: [
                      "Total revenue: $2.4M (+18% YoY)",
                      "Recurring revenue: 78% of total",
                      "New customer acquisition: +24%"
                    ],
                    type: "highlight"
                  },
                  {
                    title: "Cost Management",
                    content: [
                      "Operating expenses: $1.8M (-5% vs target)",
                      "Cost per acquisition: $127 (-15%)",
                      "Efficiency ratio improved to 1.33"
                    ],
                    type: "info"
                  },
                  {
                    title: "Risk Factors",
                    content: [
                      "Customer concentration: Top 5 = 42%",
                      "Regulatory compliance pending",
                      "Market volatility exposure"
                    ],
                    type: "warning"
                  }
                ]}
                onApprove={() => handleApprove('Financial Analysis')}
              />
              
              <SectionedInsightCard 
                title="Project Status Dashboard"
                description="Current status of active development initiatives"
                sections={[
                  {
                    title: "Completed",
                    content: [
                      "User authentication system",
                      "Payment processing integration",
                      "Mobile responsive design",
                      "API documentation"
                    ],
                    type: "info"
                  },
                  {
                    title: "In Progress",
                    content: [
                      "Advanced analytics dashboard",
                      "Third-party integrations (60%)",
                      "Performance optimization"
                    ],
                    type: "default"
                  },
                  {
                    title: "Blocked/Delayed",
                    content: [
                      "Database migration (resource conflict)",
                      "iOS app store approval pending"
                    ],
                    type: "warning"
                  }
                ]}
                onApprove={() => handleApprove('Project Status')}
              />
            </Grid>

            <Grid columns={2}>
              <SectionedInsightCard 
                title="Customer Feedback Analysis"
                description="Analysis of customer satisfaction survey results (n=1,247)"
                sections={[
                  {
                    title: "Top Strengths",
                    content: [
                      "Product reliability: 9.2/10 rating",
                      "Customer support: 8.8/10 rating",
                      "Ease of use: 8.6/10 rating"
                    ],
                    type: "highlight"
                  },
                  {
                    title: "Improvement Areas",
                    content: [
                      "Loading speed: 6.4/10 rating",
                      "Feature discovery: 6.8/10 rating",
                      "Mobile experience: 7.1/10 rating"
                    ],
                    type: "warning"
                  },
                  {
                    title: "Action Items",
                    content: [
                      "Optimize core performance metrics",
                      "Redesign onboarding flow",
                      "Enhance mobile UI/UX"
                    ],
                    type: "info"
                  }
                ]}
                onApprove={() => handleApprove('Customer Analysis')}
              />
              
              <SectionedInsightCard 
                title="Market Research Summary"
                description="Key findings from Q4 2024 market research initiative"
                sections={[
                  {
                    title: "Market Trends",
                    content: [
                      "Cloud adoption accelerating (+67% YoY)",
                      "AI integration demand increasing",
                      "Sustainability focus driving decisions"
                    ],
                    type: "highlight"
                  },
                  {
                    title: "Competitive Landscape",
                    content: [
                      "New entrants: 3 significant players",
                      "Price competition intensifying",
                      "Feature differentiation narrowing"
                    ],
                    type: "default"
                  },
                  {
                    title: "Opportunities",
                    content: [
                      "Enterprise market underserved",
                      "Integration partnerships available",
                      "Geographic expansion viable"
                    ],
                    type: "info"
                  }
                ]}
                onApprove={() => handleApprove('Market Research')}
              />
            </Grid>
          </div>

          <div className="space-y-6">
            <h4 className="text-lg font-medium text-gray-900">MultiMetricComparisonCard - Versatile Use Cases</h4>
            
            <MultiMetricComparisonCard 
              title="Stock Investment Analysis"
              entities={[
                { id: 'aapl', name: 'AAPL', subtitle: 'Apple Inc.', featured: true, badge: 'Popular' },
                { id: 'msft', name: 'MSFT', subtitle: 'Microsoft Corp.' },
                { id: 'googl', name: 'GOOGL', subtitle: 'Alphabet Inc.' }
              ]}
              metrics={[
                { id: 'price', name: 'Current Price', format: 'currency', higherIsBetter: false },
                { id: 'pe_ratio', name: 'P/E Ratio', format: 'number', higherIsBetter: false, description: 'Price to earnings ratio' },
                { id: 'dividend_yield', name: 'Dividend Yield', format: 'percentage', higherIsBetter: true },
                { id: 'market_cap', name: 'Market Cap', format: 'currency', higherIsBetter: true, unit: 'B' },
                { id: 'rating', name: 'Analyst Rating', format: 'rating', higherIsBetter: true }
              ]}
              data={{
                aapl: { price: 189.50, pe_ratio: 28.4, dividend_yield: 0.5, market_cap: 2980, rating: 8.2 },
                msft: { price: 378.90, pe_ratio: 24.1, dividend_yield: 0.8, market_cap: 2810, rating: 8.7 },
                googl: { price: 142.80, pe_ratio: 21.3, dividend_yield: 0.0, market_cap: 1780, rating: 7.9 }
              }}
              highlightBest={true}
              onApprove={() => handleApprove('Stock Comparison')}
            />

            <MultiMetricComparisonCard 
              title="Cloud Provider Comparison"
              entities={[
                { id: 'aws', name: 'AWS', subtitle: 'Amazon Web Services' },
                { id: 'azure', name: 'Azure', subtitle: 'Microsoft Azure', featured: true, badge: 'Recommended' },
                { id: 'gcp', name: 'GCP', subtitle: 'Google Cloud Platform' }
              ]}
              metrics={[
                { id: 'cost_month', name: 'Monthly Cost', format: 'currency', higherIsBetter: false },
                { id: 'uptime', name: 'Uptime SLA', format: 'percentage', higherIsBetter: true },
                { id: 'support_24_7', name: '24/7 Support', format: 'boolean', higherIsBetter: true },
                { id: 'regions', name: 'Global Regions', format: 'number', higherIsBetter: true },
                { id: 'satisfaction', name: 'Customer Rating', format: 'rating', higherIsBetter: true }
              ]}
              data={{
                aws: { cost_month: 2450, uptime: 99.99, support_24_7: true, regions: 26, satisfaction: 8.4 },
                azure: { cost_month: 2280, uptime: 99.95, support_24_7: true, regions: 24, satisfaction: 8.1 },
                gcp: { cost_month: 2150, uptime: 99.90, support_24_7: false, regions: 20, satisfaction: 7.8 }
              }}
              highlightBest={true}
              onApprove={() => handleApprove('Cloud Provider Comparison')}
            />

            <MultiMetricComparisonCard 
              title="Investment Strategy Performance"
              entities={[
                { id: 'growth', name: 'Growth', subtitle: 'High Growth Stocks' },
                { id: 'value', name: 'Value', subtitle: 'Undervalued Stocks', featured: true, badge: 'Conservative' },
                { id: 'dividend', name: 'Dividend', subtitle: 'Income Focused' }
              ]}
              metrics={[
                { id: 'ytd_return', name: 'YTD Return', format: 'percentage', higherIsBetter: true },
                { id: 'volatility', name: 'Volatility', format: 'percentage', higherIsBetter: false, description: 'Standard deviation' },
                { id: 'sharpe_ratio', name: 'Sharpe Ratio', format: 'number', higherIsBetter: true },
                { id: 'max_drawdown', name: 'Max Drawdown', format: 'percentage', higherIsBetter: false },
                { id: 'expense_ratio', name: 'Expense Ratio', format: 'percentage', higherIsBetter: false }
              ]}
              data={{
                growth: { ytd_return: 18.7, volatility: 22.4, sharpe_ratio: 1.12, max_drawdown: -15.8, expense_ratio: 0.75 },
                value: { ytd_return: 12.3, volatility: 16.8, sharpe_ratio: 1.24, max_drawdown: -12.1, expense_ratio: 0.45 },
                dividend: { ytd_return: 9.8, volatility: 14.2, sharpe_ratio: 0.98, max_drawdown: -9.4, expense_ratio: 0.55 }
              }}
              highlightBest={true}
              onApprove={() => handleApprove('Strategy Performance Comparison')}
            />

            <MultiMetricComparisonCard 
              title="Vendor Selection Matrix"
              entities={[
                { id: 'vendor_a', name: 'Vendor A', subtitle: 'Enterprise Solution' },
                { id: 'vendor_b', name: 'Vendor B', subtitle: 'Mid-Market Focus', featured: true, badge: 'Best Value' },
                { id: 'vendor_c', name: 'Vendor C', subtitle: 'Startup Friendly' }
              ]}
              metrics={[
                { id: 'setup_cost', name: 'Setup Cost', format: 'currency', higherIsBetter: false },
                { id: 'monthly_fee', name: 'Monthly Fee', format: 'currency', higherIsBetter: false },
                { id: 'implementation_time', name: 'Implementation', format: 'number', unit: 'days', higherIsBetter: false },
                { id: 'features_score', name: 'Feature Score', format: 'rating', higherIsBetter: true },
                { id: 'scalability', name: 'Scalability', format: 'rating', higherIsBetter: true }
              ]}
              data={{
                vendor_a: { setup_cost: 25000, monthly_fee: 1200, implementation_time: 45, features_score: 9.1, scalability: 9.5 },
                vendor_b: { setup_cost: 8500, monthly_fee: 850, implementation_time: 30, features_score: 8.4, scalability: 8.2 },
                vendor_c: { setup_cost: 2500, monthly_fee: 450, implementation_time: 15, features_score: 7.1, scalability: 6.8 }
              }}
              highlightBest={true}
              onApprove={() => handleApprove('Vendor Selection')}
            />
          </div>

        </Section>

        {/* Tier 6 - Advanced Analytics Components */}
        <Section title="Tier 6 - Advanced Analytics Components" onApprove={() => handleApprove('Tier 6')}>
          
          <TimeProgressIndicator 
            title="Recovery Timeline Analysis"
            stages={[
              { id: 'decline', label: 'Market Decline', duration: 0, type: 'start', description: '10% drop from peak' },
              { id: 'bottom', label: 'Market Bottom', duration: 1.5, type: 'event', description: 'Lowest point reached' },
              { id: 'recovery', label: '5% Recovery', duration: 2.3, type: 'end', description: 'Target recovery achieved' }
            ]}
            unit="days"
            variant="detailed"
            onApprove={() => handleApprove('TimeProgressIndicator')}
          />

          <div className="space-y-6">
            <h4 className="text-lg font-medium text-gray-900">ComparisonCard - Versatile Use Cases</h4>
            
            <Grid columns={2}>
              <ComparisonCard 
                value={2.3}
                comparisonValue={6.4}
                label="Recovery Speed Analysis"
                comparisonLabel="Market Average"
                format="days"
                onApprove={() => handleApprove('Speed Comparison')}
              />
              
              <ComparisonCard 
                value={95.8}
                comparisonValue={87.2}
                label="Customer Satisfaction"
                comparisonLabel="Industry Benchmark"
                format="percentage"
                onApprove={() => handleApprove('Satisfaction Comparison')}
              />
            </Grid>

            <Grid columns={2}>
              <ComparisonCard 
                value={847000}
                comparisonValue={652000}
                label="Q4 Revenue Performance"
                comparisonLabel="Q3 Revenue"
                format="currency"
                onApprove={() => handleApprove('Revenue Comparison')}
              />
              
              <ComparisonCard 
                value={2.84}
                comparisonValue={3.12}
                label="Response Time Optimization"
                comparisonLabel="Previous Version"
                format="number"
                onApprove={() => handleApprove('Performance Comparison')}
              />
            </Grid>
          </div>

          <Grid columns={2}>
            <VelocityIndicator 
              velocity={87.5}
              maxVelocity={100}
              label="Recovery Velocity"
              unit="% faster"
              comparison={{ value: 45.2, label: "Sector Average" }}
              direction="higher-is-better"
              onApprove={() => handleApprove('VelocityIndicator')}
            />

            <EventImpactBlock 
            event={{
              title: "NVDA Q3 Earnings Miss",
              date: "July 15, 2024",
              description: "Semiconductor sector selloff triggered by AI revenue guidance concerns and geopolitical tensions.",
              type: "negative",
              category: "Earnings"
            }}
            beforeValue={485.50}
            afterValue={437.25}
            recoveryValue={462.80}
            metric="Stock Price"
            format="currency"
            timeToRecovery="2.3 days"
            variant="detailed"
            onApprove={() => handleApprove('EventImpactBlock')}
          />
          </Grid>

          <PeriodComparisonTable 
            title="Quarterly Recovery Analysis"
            metrics={[
              { id: 'recovery_time', name: 'Avg Recovery Time', format: 'number', unit: 'days' },
              { id: 'success_rate', name: 'Recovery Success Rate', format: 'percentage' },
              { id: 'volatility', name: 'Recovery Volatility', format: 'percentage' }
            ]}
            periods={[
              { id: 'q1_2024', name: 'Q1 2024', shortName: 'Q1', startDate: '2024-01-01', endDate: '2024-03-31' },
              { id: 'q2_2024', name: 'Q2 2024', shortName: 'Q2', startDate: '2024-04-01', endDate: '2024-06-30' },
              { id: 'q3_2024', name: 'Q3 2024', shortName: 'Q3', startDate: '2024-07-01', endDate: '2024-09-30' },
              { id: 'q4_2024', name: 'Q4 2024', shortName: 'Q4', startDate: '2024-10-01', endDate: '2024-12-31' }
            ]}
            data={{
              recovery_time: { q1_2024: 8.2, q2_2024: 6.7, q3_2024: 4.1, q4_2024: 5.3 },
              success_rate: { q1_2024: 72.5, q2_2024: 68.9, q3_2024: 84.2, q4_2024: 76.8 },
              volatility: { q1_2024: 15.4, q2_2024: 18.7, q3_2024: 12.3, q4_2024: 14.9 }
            }}
            showChange={true}
            highlightBest={true}
            variant="detailed"
            onApprove={() => handleApprove('PeriodComparisonTable')}
          />

          <SignificanceIndicator 
            pValue={0.0023}
            confidenceLevel={0.95}
            effectSize={0.74}
            testType="Two-sample t-test"
            sampleSize={1247}
            hypothesis="Technology stocks have significantly faster recovery times than financial sector stocks"
            confidenceInterval={{ lower: 0.31, upper: 1.18 }}
            variant="detailed"
            onApprove={() => handleApprove('SignificanceIndicator')}
          />

          <TimeSeriesBreakdown 
            title="Hourly Performance Breakdown"
            data={[
              { time: '09:30', value: -2.1, volume: 1250000 },
              { time: '10:30', value: 0.8, volume: 980000 },
              { time: '11:30', value: 1.4, volume: 750000 },
              { time: '12:30', value: 0.3, volume: 620000 },
              { time: '13:30', value: 2.1, volume: 890000 },
              { time: '14:30', value: 3.2, volume: 1100000 },
              { time: '15:30', value: 1.8, volume: 1450000 }
            ]}
            timeFormat="12h"
            valueFormat="percentage"
            variant="detailed"
            onApprove={() => handleApprove('TimeSeriesBreakdown')}
          />

          <Grid columns={2}>
            <ConfirmationIndicator 
              value={82.5}
              label="Signal Confirmation Level"
              description="Probability of signal reliability based on multiple indicators"
              variant="detailed"
              onApprove={() => handleApprove('ConfirmationIndicator')}
            />

            <SignalStrengthGauge 
              strength={74.3}
              label="Market Signal Strength"
              description="Overall market signal quality and reliability"
              variant="detailed"
              onApprove={() => handleApprove('SignalStrengthGauge')}
            />
          </Grid>

          <StatWithConfidence 
            value={18.7}
            confidenceLevel={0.95}
            confidenceInterval={{ lower: 15.2, upper: 22.1 }}
            sampleSize={1247}
            label="Expected Annual Return"
            description="Portfolio expected return with statistical confidence intervals"
            format="percentage"
            variant="detailed"
            onApprove={() => handleApprove('StatWithConfidence')}
          />

        </Section>

        {/* Component Summary */}
        <Divider label="Component Library Summary" />

        <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Complete Component Library
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-3xl font-bold text-blue-600">10</div>
              <div className="text-sm text-blue-800">Core Insights</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-3xl font-bold text-green-600">6</div>
              <div className="text-sm text-green-800">Layout</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-3xl font-bold text-purple-600">8</div>
              <div className="text-sm text-purple-800">Visualization</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-3xl font-bold text-orange-600">6</div>
              <div className="text-sm text-orange-800">Decision Support</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-3xl font-bold text-gray-600">6</div>
              <div className="text-sm text-gray-800">Metadata</div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <div className="text-3xl font-bold text-red-600">10</div>
              <div className="text-sm text-red-800">Advanced Analytics</div>
            </div>
          </div>
          <p className="text-gray-600">
            46 professional components ready for financial analysis applications
          </p>
        </div>

      </div>
    </div>
  );
}