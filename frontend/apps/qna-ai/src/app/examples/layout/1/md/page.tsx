'use client';

import Layout1 from '@/components/insights/layout/Layout1';
import SummaryConclusion from '@/components/insights/SummaryConclusion';
import StatGroup from '@/components/insights/StatGroup';
import Section from '@/components/insights/Section';
import ComparisonTable from '@/components/insights/ComparisonTable';
import BulletList from '@/components/insights/BulletList';
import ActionList from '@/components/insights/ActionList';

export default function Layout1MarkdownDemo() {
  return (
    <Layout1
      title={
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Q4 2024 Portfolio Performance Analysis</h1>
          <p className="text-gray-600 mt-1">Executive Summary • Risk Assessment • Strategic Recommendations</p>
        </div>
      }
      
      topLeft={
        <SummaryConclusion
          title="Executive Summary"
          keyFindings={[
            "Portfolio delivered +18.4% returns in Q4 2024, outperforming S&P 500 by +4.2%",
            "Technology sector allocation generated exceptional alpha driven by AI infrastructure",
            "Strong risk-adjusted performance with Sharpe ratio improvement to 1.34"
          ]}
          conclusion="Our diversified equity portfolio demonstrated exceptional performance in Q4 2024, with strategic technology overweight position delivering significant outperformance. The portfolio maintains strong risk metrics while positioning defensively for 2025."
          nextSteps={[
            "Reduce energy exposure by 3% to optimize sector allocation",
            "Increase healthcare allocation for defensive positioning",
            "Maintain current technology overweight given momentum"
          ]}
          confidence="high"
        />
      }
      
      topRight={
        <StatGroup
          title="Key Performance Metrics"
          stats={[
            { label: "Portfolio Value", value: "$3.2M", format: "currency" },
            { label: "YTD Return", value: "+18.4%", changeType: "positive", format: "percentage" },
            { label: "Alpha vs S&P 500", value: "+4.2%", changeType: "positive", format: "percentage" },
            { label: "Sharpe Ratio", value: "1.34", format: "number" },
            { label: "Max Drawdown", value: "-8.2%", changeType: "negative", format: "percentage" },
            { label: "Volatility", value: "15.8%", format: "percentage" }
          ]}
          columns={2}
        />
      }
      
      middleLeft={
        <BulletList
          title="Q4 Highlights"
          items={[
            "Tech Sector Leadership: NVIDIA (+45%), Microsoft (+28%), Apple (+22%)",
            "Strong Risk-Adjusted Returns: Sharpe ratio improved from 1.18 to 1.34",
            "Beat All Benchmarks: Outperformed S&P 500, Russell 2000, and NASDAQ",
            "Energy Underperformance: Oil & Gas down -12% on demand concerns"
          ]}
          variant="detailed"
        />
      }
      
      middleCenter={
        <ComparisonTable
          title="Sector Performance Analysis"
          entities={[
            { id: "tech", name: "Technology", subtitle: "28.5% allocation" },
            { id: "health", name: "Healthcare", subtitle: "18.2% allocation" },
            { id: "finance", name: "Financials", subtitle: "16.8% allocation" },
            { id: "energy", name: "Energy", subtitle: "8.1% allocation" }
          ]}
          metrics={[
            { id: "q4_return", name: "Q4 Return", format: "percentage" },
            { id: "ytd_return", name: "YTD Return", format: "percentage" },
            { id: "vs_benchmark", name: "vs Benchmark", format: "percentage" }
          ]}
          data={{
            "tech": { "q4_return": "+32.1%", "ytd_return": "+42.3%", "vs_benchmark": "+8.7%" },
            "health": { "q4_return": "+12.4%", "ytd_return": "+18.9%", "vs_benchmark": "+2.1%" },
            "finance": { "q4_return": "+18.7%", "ytd_return": "+24.2%", "vs_benchmark": "+3.4%" },
            "energy": { "q4_return": "-4.2%", "ytd_return": "+8.3%", "vs_benchmark": "-6.8%" }
          }}
        />
      }
      
      middleRight={
        <Section title="Market Insights">
          <div className="space-y-4 text-sm">
            <div className="p-3 bg-blue-50 rounded border border-blue-200">
              <div className="font-medium text-blue-800 mb-1">🔥 AI Infrastructure Boom</div>
              <div className="text-blue-700">Semiconductor demand surge drove 45% NVIDIA gains. Trend expected to continue through H1 2025.</div>
            </div>
            
            <div className="p-3 bg-green-50 rounded border border-green-200">
              <div className="font-medium text-green-800 mb-1">📊 Earnings Beat Rate: 78%</div>
              <div className="text-green-700">Portfolio companies exceeded expectations, with average EPS beat of 8.2%.</div>
            </div>
            
            <div className="p-3 bg-purple-50 rounded border border-purple-200">
              <div className="font-medium text-purple-800 mb-1">🌊 Market Regime Shift</div>
              <div className="text-purple-700">Growth stocks outperforming value by widest margin since 2021.</div>
            </div>
            
            <div className="p-3 bg-yellow-50 rounded border border-yellow-200">
              <div className="font-medium text-yellow-800 mb-1">⚠️ Risk Signals</div>
              <div className="text-yellow-700 text-xs">VIX: 18.4 • Bond yields: 4.3% • Dollar strength</div>
            </div>
          </div>
        </Section>
      }
      
      bottom={
        <ActionList
          title="Strategic Actions & Timeline"
          actions={[
            {
              id: "rebalance-energy",
              title: "Rebalance Energy Exposure",
              description: "Reduce from 8.1% to 5.0% allocation (-$99K)",
              priority: "high",
              timeline: "immediate",
              impact: "medium",
              category: "Portfolio Allocation"
            },
            {
              id: "increase-healthcare",
              title: "Increase Healthcare Allocation",
              description: "Target 21% allocation (+$89K additional investment)",
              priority: "high",
              timeline: "immediate",
              impact: "high",
              category: "Portfolio Allocation"
            },
            {
              id: "tax-loss-harvest",
              title: "Harvest Tax Losses",
              description: "Realize $45K losses to offset gains",
              priority: "medium",
              timeline: "immediate",
              impact: "medium",
              category: "Tax Optimization"
            },
            {
              id: "international-exposure",
              title: "Add International Exposure",
              description: "Increase developed markets to 15%",
              priority: "medium",
              timeline: "short-term",
              impact: "high",
              category: "Diversification"
            },
            {
              id: "monitor-fed",
              title: "Monitor Fed Policy",
              description: "Track March FOMC impact on growth stocks",
              priority: "high",
              timeline: "short-term",
              impact: "high",
              category: "Risk Management"
            }
          ]}
          showPriority={true}
        />
      }
    />
  );
}