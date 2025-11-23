'use client';

import React from 'react';
import { Group } from '@visx/group';
import { Bar } from '@visx/shape';
import { scaleBand, scaleLinear } from '@visx/scale';
import { AxisBottom, AxisLeft } from '@visx/axis';
import { LinearGradient } from '@visx/gradient';

interface PeriodReturn {
  period: string;
  portfolio: number;
  benchmark?: number;
  target?: number;
}

interface ElegantAnnualizedReturnsProps {
  returns: number;
  benchmark?: number;
  target?: number;
  period?: string;
  portfolioLabel?: string;
  benchmarkLabel?: string;
  periodBreakdown?: PeriodReturn[];
  volatility?: number;
  title?: string;
  subtitle?: string;
}

export function ElegantAnnualizedReturns({
  returns,
  benchmark,
  target,
  period = "3Y",
  portfolioLabel = "Portfolio",
  benchmarkLabel = "Benchmark", 
  periodBreakdown = [],
  volatility,
  title = "Annualized Returns",
  subtitle = "Risk-adjusted performance analysis"
}: ElegantAnnualizedReturnsProps) {
  // Performance assessment
  const getPerformanceAssessment = () => {
    let score = 50; // Base score
    
    // Absolute return scoring
    if (returns >= 15) score += 30;
    else if (returns >= 10) score += 20;
    else if (returns >= 7) score += 10;
    else if (returns >= 5) score += 5;
    else if (returns >= 0) score += 0;
    else score -= 20;
    
    // Benchmark relative scoring
    if (benchmark) {
      const outperformance = returns - benchmark;
      if (outperformance >= 3) score += 20;
      else if (outperformance >= 1) score += 10;
      else if (outperformance >= 0) score += 5;
      else score -= 10;
    }
    
    // Target achievement scoring
    if (target) {
      const achievement = (returns / target) * 100;
      if (achievement >= 110) score += 15;
      else if (achievement >= 100) score += 10;
      else if (achievement >= 90) score += 5;
      else score -= 10;
    }
    
    score = Math.min(100, Math.max(0, score));
    
    if (score >= 85) return { level: 'Exceptional', color: 'emerald', score };
    if (score >= 70) return { level: 'Strong', color: 'blue', score };
    if (score >= 55) return { level: 'Adequate', color: 'yellow', score };
    return { level: 'Below Target', color: 'red', score };
  };

  const assessment = getPerformanceAssessment();
  const targetAchievement = target ? (returns / target) * 100 : null;

  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-light text-gray-900 mb-1">{title}</h2>
        <p className="text-sm text-gray-500">{subtitle} • {period}</p>
      </div>

      {/* Main Performance Display */}
      <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 border border-gray-200 shadow-sm mb-6">
        <div className="flex items-center justify-between mb-8">
          {/* Primary Return Display */}
          <div className="flex items-baseline space-x-4">
            <div className={`text-6xl font-bold text-${assessment.color}-600`}>
              {returns >= 0 ? '+' : ''}{returns.toFixed(1)}%
            </div>
            <div>
              <div className={`text-xl font-semibold text-${assessment.color}-700`}>
                {assessment.level}
              </div>
              <div className="text-sm text-gray-600">Annualized</div>
            </div>
          </div>

          {/* Performance Score */}
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
                  stroke={`var(--${assessment.color}-500)`}
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${(assessment.score / 100) * 251} 251`}
                  strokeLinecap="round"
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={`text-xl font-bold text-${assessment.color}-600`}>
                  {assessment.score.toFixed(0)}
                </span>
              </div>
            </div>
            <div className="text-xs text-gray-600">Performance Score</div>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          {benchmark && (
            <MetricCard
              label="vs Benchmark"
              value={`${(returns - benchmark) >= 0 ? '+' : ''}${(returns - benchmark).toFixed(1)}%`}
              sublabel={`${benchmarkLabel}: ${benchmark.toFixed(1)}%`}
              positive={returns > benchmark}
            />
          )}
          
          {target && (
            <MetricCard
              label="Target Achievement"
              value={`${targetAchievement?.toFixed(0)}%`}
              sublabel={`Target: ${target.toFixed(1)}%`}
              positive={(targetAchievement || 0) >= 100}
            />
          )}
          
          {volatility && (
            <MetricCard
              label="Return/Risk"
              value={`${(returns / volatility).toFixed(2)}`}
              sublabel={`Vol: ${volatility.toFixed(1)}%`}
              positive={(returns / volatility) > 0.5}
            />
          )}
          
          <MetricCard
            label="Compound Growth"
            value={`${(Math.pow(1 + returns/100, parseInt(period.replace(/\D/g, ''))) * 1000 - 1000).toFixed(0)}`}
            sublabel={`per $1,000 invested`}
            positive={returns > 5}
          />
        </div>

        {/* Progress Bar for Target */}
        {target && (
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Progress to Target</span>
              <span className={`text-sm font-semibold ${
                (targetAchievement || 0) >= 100 ? 'text-emerald-600' : 'text-gray-600'
              }`}>
                {targetAchievement?.toFixed(1)}%
              </span>
            </div>
            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-1000 ${
                  (targetAchievement || 0) >= 100 ? 'bg-emerald-500' : 
                  (targetAchievement || 0) >= 80 ? 'bg-blue-500' : 'bg-yellow-500'
                }`}
                style={{ width: `${Math.min(100, targetAchievement || 0)}%` }}
              />
            </div>
          </div>
        )}

        <div className={`p-4 rounded-xl ${
          assessment.color === 'emerald' ? 'bg-emerald-50 border border-emerald-200' :
          assessment.color === 'blue' ? 'bg-blue-50 border border-blue-200' :
          assessment.color === 'yellow' ? 'bg-yellow-50 border border-yellow-200' :
          'bg-red-50 border border-red-200'
        }`}>
          <p className={`text-sm font-medium text-${assessment.color}-800`}>
            {getPerformanceInsight(returns, benchmark, target)}
          </p>
        </div>
      </div>

      {/* Period Breakdown Chart */}
      {periodBreakdown.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-6">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900">Period Breakdown</h3>
            <p className="text-sm text-gray-500 mt-1">
              Performance across different time horizons
            </p>
          </div>
          <div className="p-6">
            <PeriodBreakdownChart data={periodBreakdown} />
          </div>
        </div>
      )}

      {/* Risk-Return Analysis */}
      {volatility && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-6">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900">Risk-Return Profile</h3>
            <p className="text-sm text-gray-500 mt-1">
              Efficiency of returns relative to risk taken
            </p>
          </div>
          <div className="p-6">
            <RiskReturnProfile returns={returns} volatility={volatility} benchmark={benchmark} />
          </div>
        </div>
      )}

      {/* Investment Context */}
      <div className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border border-blue-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Context</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Performance Analysis</h4>
            <p className="text-sm text-gray-700">
              {getDetailedPerformanceAnalysis(returns, period)}
            </p>
          </div>
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Strategic Implications</h4>
            <p className="text-sm text-gray-700">
              {getStrategicImplications(returns, benchmark, target)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Metric Card Component
interface MetricCardProps {
  label: string;
  value: string;
  sublabel: string;
  positive: boolean;
}

function MetricCard({ label, value, sublabel, positive }: MetricCardProps) {
  return (
    <div className="text-center">
      <div className={`text-2xl font-bold mb-1 ${
        positive ? 'text-emerald-600' : 'text-red-600'
      }`}>
        {value}
      </div>
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className="text-xs text-gray-500">{sublabel}</div>
    </div>
  );
}

// Period Breakdown Chart
function PeriodBreakdownChart({ data }: { data: PeriodReturn[] }) {
  const width = 600;
  const height = 300;
  const margin = { top: 20, right: 30, bottom: 60, left: 60 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const xScale = scaleBand({
    range: [0, chartWidth],
    domain: data.map(d => d.period),
    padding: 0.3
  });

  const allValues = data.flatMap(d => [d.portfolio, d.benchmark || 0]).filter(v => v !== 0);
  const maxValue = Math.max(...allValues);
  const minValue = Math.min(...allValues);
  const yScale = scaleLinear({
    range: [chartHeight, 0],
    domain: [Math.min(0, minValue * 1.1), maxValue * 1.1],
    nice: true
  });

  return (
    <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
      <defs>
        <LinearGradient id="portfolio-gradient" from="#10B981" to="#059669" />
        <LinearGradient id="benchmark-gradient" from="#6B7280" to="#4B5563" />
      </defs>
      
      <Group left={margin.left} top={margin.top}>
        {/* Zero line */}
        <line
          x1={0}
          x2={chartWidth}
          y1={yScale(0)}
          y2={yScale(0)}
          stroke="#E5E7EB"
          strokeWidth={1}
        />

        {data.map((d, i) => {
          const barWidth = xScale.bandwidth() / 2;
          const x = xScale(d.period) || 0;
          
          return (
            <Group key={d.period}>
              {/* Portfolio bar */}
              <Bar
                x={x}
                y={d.portfolio >= 0 ? yScale(d.portfolio) : yScale(0)}
                width={barWidth}
                height={Math.abs(yScale(d.portfolio) - yScale(0))}
                fill="url(#portfolio-gradient)"
                rx={2}
              />
              
              {/* Benchmark bar */}
              {d.benchmark !== undefined && (
                <Bar
                  x={x + barWidth}
                  y={d.benchmark >= 0 ? yScale(d.benchmark) : yScale(0)}
                  width={barWidth}
                  height={Math.abs(yScale(d.benchmark) - yScale(0))}
                  fill="url(#benchmark-gradient)"
                  rx={2}
                />
              )}
              
              {/* Value labels */}
              <text
                x={x + barWidth / 2}
                y={yScale(d.portfolio) - (d.portfolio >= 0 ? 5 : -15)}
                fontSize={10}
                fontWeight="600"
                fill="#059669"
                textAnchor="middle"
              >
                {d.portfolio.toFixed(1)}%
              </text>
            </Group>
          );
        })}

        <AxisBottom
          top={chartHeight}
          scale={xScale}
          stroke="#E5E7EB"
          tickStroke="#E5E7EB"
          tickLabelProps={() => ({
            fill: '#6B7280',
            fontSize: 12,
            textAnchor: 'middle'
          })}
        />

        <AxisLeft
          scale={yScale}
          stroke="#E5E7EB"
          tickStroke="#E5E7EB"
          numTicks={6}
          tickLabelProps={() => ({
            fill: '#6B7280',
            fontSize: 12,
            textAnchor: 'end'
          })}
          tickFormat={(value) => `${value}%`}
        />
      </Group>
    </svg>
  );
}

// Risk-Return Profile Component
function RiskReturnProfile({ 
  returns, 
  volatility, 
  benchmark 
}: { 
  returns: number; 
  volatility: number; 
  benchmark?: number; 
}) {
  const efficiency = returns / volatility;
  const benchmarkEfficiency = benchmark ? benchmark / volatility : undefined;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-6 text-center">
        <div>
          <div className="text-2xl font-bold text-blue-600">{returns.toFixed(1)}%</div>
          <div className="text-sm text-gray-600">Return</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-purple-600">{volatility.toFixed(1)}%</div>
          <div className="text-sm text-gray-600">Volatility</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-emerald-600">{efficiency.toFixed(2)}</div>
          <div className="text-sm text-gray-600">Return/Risk</div>
        </div>
      </div>
      
      <div className="p-4 bg-gray-50 rounded-xl">
        <h4 className="font-medium text-gray-800 mb-2">Efficiency Analysis</h4>
        <p className="text-sm text-gray-700">
          {efficiency >= 1.0 
            ? "Excellent return per unit of risk. Strong risk-adjusted performance."
            : efficiency >= 0.5
            ? "Reasonable return per unit of risk. Consider opportunities for optimization."
            : "Below average return per unit of risk. Review risk management strategy."
          }
          {benchmarkEfficiency && (
            ` Portfolio efficiency is ${efficiency > benchmarkEfficiency ? 'superior' : 'inferior'} to benchmark (${benchmarkEfficiency.toFixed(2)}).`
          )}
        </p>
      </div>
    </div>
  );
}

// Utility Functions
function getPerformanceInsight(returns: number, benchmark?: number, target?: number): string {
  if (returns >= 15) {
    return "Exceptional performance with strong absolute returns. Continue monitoring for sustainability.";
  } else if (returns >= 10) {
    return "Strong performance exceeding most investor expectations. Maintain current strategy.";
  } else if (returns >= 7) {
    return "Solid performance meeting reasonable return expectations for the risk level.";
  } else if (returns >= 5) {
    return "Moderate performance. Consider optimization opportunities to enhance returns.";
  } else if (returns >= 0) {
    return "Positive but below-target performance. Review strategy for improvement opportunities.";
  } else {
    return "Negative performance requires immediate attention and potential strategy revision.";
  }
}

function getDetailedPerformanceAnalysis(returns: number, period: string): string {
  const periodYears = parseInt(period.replace(/\D/g, '')) || 1;
  const compoundValue = Math.pow(1 + returns/100, periodYears) * 10000;
  
  return `Over the ${period} period, a $10,000 investment would have grown to $${compoundValue.toFixed(0)}, representing ${((compoundValue - 10000) / 100).toFixed(0)}% total growth. This ${returns >= 10 ? 'strong' : returns >= 5 ? 'moderate' : 'weak'} performance ${returns >= 7 ? 'exceeds' : 'falls below'} typical equity market expectations.`;
}

function getStrategicImplications(returns: number, benchmark?: number, target?: number): string {
  if (benchmark && target) {
    const vsTarget = returns >= target;
    const vsBenchmark = returns >= benchmark;
    
    if (vsTarget && vsBenchmark) {
      return "Strong performance justifies increased allocation consideration. Monitor for consistency.";
    } else if (vsTarget) {
      return "Meeting targets but lagging benchmark suggests need for strategy refinement.";
    } else if (vsBenchmark) {
      return "Outperforming market but missing targets indicates need for realistic goal setting.";
    } else {
      return "Underperformance on both metrics requires comprehensive strategy review.";
    }
  }
  
  return returns >= 7 
    ? "Strong returns support maintaining or increasing strategic allocation."
    : "Moderate returns suggest careful evaluation of risk-return trade-offs.";
}