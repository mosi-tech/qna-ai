'use client';

import React from 'react';
import { Group } from '@visx/group';
import { Bar } from '@visx/shape';
import { scaleBand, scaleLinear } from '@visx/scale';
import { AxisBottom, AxisLeft } from '@visx/axis';
import { LinearGradient } from '@visx/gradient';

interface SharpeComparison {
  name: string;
  value: number;
}

interface ElegantSharpeRatioProps {
  value: number;
  benchmark?: number;
  historicalRange?: {
    min: number;
    max: number;
    avg: number;
  };
  riskFreeRate?: number;
  period?: string;
  portfolioLabel?: string;
  benchmarkLabel?: string;
  peerComparison?: SharpeComparison[];
  title?: string;
}

export function ElegantSharpeRatio({
  value,
  benchmark,
  historicalRange,
  riskFreeRate = 2.0,
  period = "3Y",
  portfolioLabel = "Portfolio",
  benchmarkLabel = "Benchmark",
  peerComparison = [],
  title = "Sharpe Ratio Analysis"
}: ElegantSharpeRatioProps) {
  // Quality assessment
  const getQualityAssessment = () => {
    if (value >= 2.0) return { level: 'Exceptional', color: 'emerald', score: 95, description: 'Outstanding risk-adjusted returns' };
    if (value >= 1.5) return { level: 'Excellent', color: 'emerald', score: 85, description: 'Strong risk-adjusted performance' };
    if (value >= 1.0) return { level: 'Good', color: 'blue', score: 70, description: 'Solid risk-adjusted returns' };
    if (value >= 0.5) return { level: 'Fair', color: 'yellow', score: 50, description: 'Moderate risk efficiency' };
    return { level: 'Poor', color: 'red', score: 30, description: 'Below average risk-adjusted returns' };
  };

  const quality = getQualityAssessment();
  const excessReturn = (value * Math.sqrt(252) * 15) + riskFreeRate; // Approximate annualized return

  // Create comparison data
  const comparisonData = [
    { name: portfolioLabel, value, isPortfolio: true },
    ...(benchmark ? [{ name: benchmarkLabel, value: benchmark, isPortfolio: false }] : []),
    ...peerComparison.map(p => ({ ...p, isPortfolio: false }))
  ].sort((a, b) => b.value - a.value);

  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-light text-gray-900 mb-1">{title}</h2>
        <p className="text-sm text-gray-500">Risk-adjusted return measurement ({period})</p>
      </div>

      {/* Main Display */}
      <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 border border-gray-200 shadow-sm mb-6">
        <div className="flex items-center justify-between mb-8">
          {/* Primary Metric */}
          <div className="flex items-baseline space-x-4">
            <div className={`text-6xl font-bold text-${quality.color}-600`}>
              {value.toFixed(2)}
            </div>
            <div>
              <div className={`text-xl font-semibold text-${quality.color}-700`}>
                {quality.level}
              </div>
              <div className="text-sm text-gray-600">Sharpe Ratio</div>
            </div>
          </div>

          {/* Quality Indicator */}
          <div className="text-center">
            <div className="relative w-24 h-24 mb-3">
              <svg className="transform -rotate-90" width="96" height="96">
                <circle
                  cx="48"
                  cy="48"
                  r="40"
                  stroke="#E5E7EB"
                  strokeWidth="8"
                  fill="none"
                />
                <circle
                  cx="48"
                  cy="48"
                  r="40"
                  stroke={`var(--${quality.color}-500)`}
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${(quality.score / 100) * 251} 251`}
                  strokeLinecap="round"
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={`text-xl font-bold text-${quality.color}-600`}>
                  {quality.score}
                </span>
              </div>
            </div>
            <div className="text-xs text-gray-600">Quality Score</div>
          </div>
        </div>

        {/* Key Insights */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <InsightCard
            label="Implied Return"
            value={`${excessReturn.toFixed(1)}%`}
            sublabel="Annualized"
            positive={excessReturn > riskFreeRate + 3}
          />
          
          <InsightCard
            label="Risk Premium"
            value={`${(excessReturn - riskFreeRate).toFixed(1)}%`}
            sublabel="Above risk-free"
            positive={(excessReturn - riskFreeRate) > 3}
          />
          
          {benchmark && (
            <InsightCard
              label="vs Benchmark"
              value={`${((value - benchmark) * 100).toFixed(0)}bps`}
              sublabel={value > benchmark ? "Outperforming" : "Underperforming"}
              positive={value > benchmark}
            />
          )}
          
          {historicalRange && (
            <InsightCard
              label="Percentile"
              value={`${calculatePercentile(value, historicalRange).toFixed(0)}th`}
              sublabel="Historical rank"
              positive={value > historicalRange.avg}
            />
          )}
        </div>

        <div className={`p-4 rounded-xl ${
          quality.color === 'emerald' ? 'bg-emerald-50 border border-emerald-200' :
          quality.color === 'blue' ? 'bg-blue-50 border border-blue-200' :
          quality.color === 'yellow' ? 'bg-yellow-50 border border-yellow-200' :
          'bg-red-50 border border-red-200'
        }`}>
          <p className={`text-sm font-medium text-${quality.color}-800`}>
            {quality.description}
          </p>
        </div>
      </div>

      {/* Comparison Chart */}
      {comparisonData.length > 1 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-6">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900">Comparative Analysis</h3>
            <p className="text-sm text-gray-500 mt-1">
              Sharpe ratio comparison across investments
            </p>
          </div>
          <div className="p-6">
            <ComparisonChart data={comparisonData} />
          </div>
        </div>
      )}

      {/* Historical Context */}
      {historicalRange && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-6">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900">Historical Context</h3>
            <p className="text-sm text-gray-500 mt-1">
              Performance relative to historical range
            </p>
          </div>
          <div className="p-6">
            <HistoricalRange current={value} range={historicalRange} />
          </div>
        </div>
      )}

      {/* Investment Implications */}
      <div className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border border-blue-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Implications</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Risk Efficiency</h4>
            <p className="text-sm text-gray-700">
              {getRiskEfficiencyInsight(value)}
            </p>
          </div>
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Portfolio Allocation</h4>
            <p className="text-sm text-gray-700">
              {getAllocationInsight(value, benchmark)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Insight Card Component
interface InsightCardProps {
  label: string;
  value: string;
  sublabel: string;
  positive: boolean;
}

function InsightCard({ label, value, sublabel, positive }: InsightCardProps) {
  return (
    <div className="text-center">
      <div className={`text-2xl font-bold mb-1 ${
        positive ? 'text-emerald-600' : 'text-gray-900'
      }`}>
        {value}
      </div>
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className={`text-xs font-medium ${
        positive ? 'text-emerald-600' : 'text-gray-500'
      }`}>
        {sublabel}
      </div>
    </div>
  );
}

// Comparison Chart Component
function ComparisonChart({ data }: { data: Array<{ name: string; value: number; isPortfolio: boolean }> }) {
  const width = 600;
  const height = 300;
  const margin = { top: 20, right: 30, bottom: 60, left: 100 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const yScale = scaleBand({
    range: [chartHeight, 0],
    domain: data.map(d => d.name),
    padding: 0.3
  });

  const maxValue = Math.max(...data.map(d => d.value));
  const xScale = scaleLinear({
    range: [0, chartWidth],
    domain: [0, maxValue * 1.2],
    nice: true
  });

  return (
    <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
      <defs>
        <LinearGradient id="portfolio-bar" from="#10B981" to="#059669" />
        <LinearGradient id="benchmark-bar" from="#6B7280" to="#4B5563" />
      </defs>
      
      <Group left={margin.left} top={margin.top}>
        {data.map((d, i) => (
          <Group key={d.name}>
            <Bar
              x={0}
              y={yScale(d.name) || 0}
              width={xScale(d.value)}
              height={yScale.bandwidth()}
              fill={d.isPortfolio ? "url(#portfolio-bar)" : "url(#benchmark-bar)"}
              rx={4}
            />
            <text
              x={xScale(d.value) + 8}
              y={(yScale(d.name) || 0) + yScale.bandwidth() / 2}
              dy="0.33em"
              fontSize={12}
              fontWeight="600"
              fill={d.value >= 1.0 ? "#059669" : d.value >= 0.5 ? "#D97706" : "#DC2626"}
            >
              {d.value.toFixed(2)}
            </text>
          </Group>
        ))}

        <AxisLeft
          scale={yScale}
          stroke="transparent"
          tickStroke="transparent"
          tickLabelProps={() => ({
            fill: '#374151',
            fontSize: 14,
            fontWeight: '500',
            textAnchor: 'end'
          })}
        />

        <AxisBottom
          top={chartHeight}
          scale={xScale}
          stroke="#E5E7EB"
          tickStroke="#E5E7EB"
          numTicks={5}
          tickLabelProps={() => ({
            fill: '#6B7280',
            fontSize: 12,
            textAnchor: 'middle'
          })}
        />
      </Group>
    </svg>
  );
}

// Historical Range Component
function HistoricalRange({ 
  current, 
  range 
}: { 
  current: number; 
  range: { min: number; max: number; avg: number } 
}) {
  const position = ((current - range.min) / (range.max - range.min)) * 100;
  const avgPosition = ((range.avg - range.min) / (range.max - range.min)) * 100;

  return (
    <div className="space-y-4">
      <div className="flex justify-between text-sm text-gray-600">
        <span>Min: {range.min.toFixed(2)}</span>
        <span>Avg: {range.avg.toFixed(2)}</span>
        <span>Max: {range.max.toFixed(2)}</span>
      </div>
      
      <div className="relative h-8 bg-gray-200 rounded-full">
        {/* Range bar */}
        <div className="absolute inset-0 bg-gradient-to-r from-red-300 via-yellow-300 to-emerald-300 rounded-full"></div>
        
        {/* Average marker */}
        <div 
          className="absolute top-0 bottom-0 w-1 bg-blue-600 rounded-full"
          style={{ left: `${avgPosition}%` }}
        />
        
        {/* Current position */}
        <div 
          className="absolute top-0 bottom-0 w-3 bg-gray-900 rounded-full shadow-lg"
          style={{ left: `${Math.max(0, Math.min(100, position))}%` }}
        />
      </div>
      
      <div className="text-center">
        <span className="text-lg font-semibold text-gray-900">
          Current: {current.toFixed(2)}
        </span>
        <span className="text-sm text-gray-500 ml-2">
          ({calculatePercentile(current, range).toFixed(0)}th percentile)
        </span>
      </div>
    </div>
  );
}

// Utility Functions
function calculatePercentile(
  value: number, 
  range: { min: number; max: number; avg: number }
): number {
  return ((value - range.min) / (range.max - range.min)) * 100;
}

function getRiskEfficiencyInsight(sharpe: number): string {
  if (sharpe >= 1.5) {
    return "Excellent risk efficiency. Each unit of risk is being well-compensated with returns, indicating optimal portfolio construction.";
  } else if (sharpe >= 1.0) {
    return "Good risk-adjusted performance. The portfolio demonstrates reasonable efficiency in converting risk into returns.";
  } else if (sharpe >= 0.5) {
    return "Moderate risk efficiency. Consider reviewing portfolio construction to improve return per unit of risk taken.";
  } else {
    return "Below-average risk efficiency. Significant opportunity exists to improve risk-adjusted returns through better portfolio optimization.";
  }
}

function getAllocationInsight(sharpe: number, benchmark?: number): string {
  if (!benchmark) {
    return sharpe >= 1.0 
      ? "Strong risk-adjusted performance supports current allocation strategy."
      : "Consider reducing position size or improving diversification to enhance risk efficiency.";
  }
  
  if (sharpe > benchmark) {
    return `Outperforming benchmark by ${((sharpe - benchmark) * 100).toFixed(0)} basis points. Consider increasing allocation to this strategy.`;
  } else {
    return `Underperforming benchmark. Evaluate whether allocation should be reduced or strategy improved.`;
  }
}