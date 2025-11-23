'use client';

import React from 'react';
import { Group } from '@visx/group';
import { LinePath, AreaClosed } from '@visx/shape';
import { curveCardinal } from '@visx/curve';
import { LinearGradient } from '@visx/gradient';
import { scaleTime, scaleLinear } from '@visx/scale';
import { AxisBottom } from '@visx/axis';

interface DrawdownPoint {
  date: Date;
  drawdown: number;
}

interface ElegantMaxDrawdownProps {
  value: number;
  benchmark?: number;
  currentDrawdown?: number;
  date?: string;
  recoveryDate?: string;
  duration?: number;
  drawdownHistory?: DrawdownPoint[];
  title?: string;
  subtitle?: string;
}

export function ElegantMaxDrawdown({
  value,
  benchmark,
  currentDrawdown = 0,
  date,
  recoveryDate,
  duration,
  drawdownHistory = [],
  title = "Maximum Drawdown",
  subtitle = "Worst peak-to-trough decline"
}: ElegantMaxDrawdownProps) {
  // Risk assessment based on max drawdown
  const getRiskLevel = () => {
    const absValue = Math.abs(value);
    if (absValue <= 5) return { level: 'Low', color: 'emerald', score: 95 };
    if (absValue <= 10) return { level: 'Moderate', color: 'yellow', score: 75 };
    if (absValue <= 20) return { level: 'High', color: 'orange', score: 50 };
    return { level: 'Extreme', color: 'red', score: 25 };
  };

  const riskAssessment = getRiskLevel();
  const isRecovered = currentDrawdown === 0;

  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-light text-gray-900 mb-1">{title}</h2>
        <p className="text-sm text-gray-500">{subtitle}</p>
      </div>

      {/* Main Metric Display */}
      <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 border border-gray-200 shadow-sm mb-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-baseline space-x-4">
            <div className={`text-5xl font-bold text-${riskAssessment.color}-600`}>
              {value.toFixed(1)}%
            </div>
            <div>
              <div className={`text-lg font-semibold text-${riskAssessment.color}-700`}>
                {riskAssessment.level} Risk
              </div>
              <div className="text-sm text-gray-600">Drawdown Level</div>
            </div>
          </div>

          {/* Risk Score Gauge */}
          <div className="text-center">
            <div className="relative w-20 h-20 mb-2">
              <svg className="transform -rotate-90" width="80" height="80">
                <circle
                  cx="40"
                  cy="40"
                  r="32"
                  stroke="#E5E7EB"
                  strokeWidth="8"
                  fill="none"
                />
                <circle
                  cx="40"
                  cy="40"
                  r="32"
                  stroke={`var(--${riskAssessment.color}-500)`}
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${(riskAssessment.score / 100) * 201} 201`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={`text-lg font-bold text-${riskAssessment.color}-600`}>
                  {riskAssessment.score}
                </span>
              </div>
            </div>
            <div className="text-xs text-gray-600">Risk Score</div>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            label="Current Drawdown"
            value={`${currentDrawdown.toFixed(1)}%`}
            status={isRecovered ? 'Recovered' : 'Underwater'}
            positive={isRecovered}
          />
          
          {benchmark && (
            <MetricCard
              label="vs Benchmark"
              value={`${benchmark.toFixed(1)}%`}
              status={Math.abs(value) < Math.abs(benchmark) ? 'Better' : 'Worse'}
              positive={Math.abs(value) < Math.abs(benchmark)}
            />
          )}
          
          {duration && (
            <MetricCard
              label="Recovery Time"
              value={`${duration} days`}
              status={duration <= 90 ? 'Fast' : duration <= 180 ? 'Normal' : 'Slow'}
              positive={duration <= 90}
            />
          )}
          
          <MetricCard
            label="Severity"
            value={`${Math.abs(value).toFixed(1)}%`}
            status={riskAssessment.level}
            positive={riskAssessment.level === 'Low'}
          />
        </div>
      </div>

      {/* Timeline Information */}
      {(date || recoveryDate) && (
        <div className="bg-blue-50 rounded-xl p-6 border border-blue-200 mb-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">Drawdown Timeline</h3>
          <div className="space-y-3">
            {date && (
              <div className="flex items-center justify-between">
                <span className="text-blue-700 font-medium">Peak Date:</span>
                <span className="text-blue-900">{new Date(date).toLocaleDateString()}</span>
              </div>
            )}
            {recoveryDate && (
              <div className="flex items-center justify-between">
                <span className="text-blue-700 font-medium">Recovery Date:</span>
                <span className="text-blue-900">{new Date(recoveryDate).toLocaleDateString()}</span>
              </div>
            )}
            {duration && (
              <div className="flex items-center justify-between">
                <span className="text-blue-700 font-medium">Duration:</span>
                <span className="text-blue-900">{duration} days ({Math.round(duration / 30)} months)</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Historical Drawdown Chart */}
      {drawdownHistory.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900">Drawdown History</h3>
            <p className="text-sm text-gray-500 mt-1">
              Historical underwater periods and recovery patterns
            </p>
          </div>
          <div className="p-6">
            <DrawdownChart data={drawdownHistory} maxDrawdown={value} />
          </div>
        </div>
      )}

      {/* Investment Insights */}
      <div className="mt-6 p-6 bg-gradient-to-r from-gray-50 to-slate-50 rounded-2xl border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Risk Assessment</h4>
            <p className="text-sm text-gray-700">
              {getRiskInsight(Math.abs(value))}
            </p>
          </div>
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Recovery Analysis</h4>
            <p className="text-sm text-gray-700">
              {getRecoveryInsight(duration, isRecovered)}
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
  status: string;
  positive: boolean;
}

function MetricCard({ label, value, status, positive }: MetricCardProps) {
  return (
    <div className="text-center">
      <div className="text-lg font-semibold text-gray-900 mb-1">{value}</div>
      <div className="text-sm text-gray-600 mb-2">{label}</div>
      <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
        positive 
          ? 'bg-emerald-100 text-emerald-800' 
          : 'bg-red-100 text-red-800'
      }`}>
        {status}
      </div>
    </div>
  );
}

// Drawdown Chart Component
interface DrawdownChartProps {
  data: DrawdownPoint[];
  maxDrawdown: number;
}

function DrawdownChart({ data, maxDrawdown }: DrawdownChartProps) {
  const width = 800;
  const height = 300;
  const margin = { top: 20, right: 30, bottom: 40, left: 60 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  if (data.length === 0) return null;

  const xScale = scaleTime({
    range: [0, chartWidth],
    domain: [
      Math.min(...data.map(d => d.date)),
      Math.max(...data.map(d => d.date))
    ]
  });

  const yScale = scaleLinear({
    range: [chartHeight, 0],
    domain: [Math.min(maxDrawdown * 1.2, Math.min(...data.map(d => d.drawdown))), 0],
    nice: true
  });

  return (
    <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
      <defs>
        <LinearGradient 
          id="drawdown-fill" 
          from="#EF4444" 
          to="#EF4444" 
          fromOpacity={0.3} 
          toOpacity={0} 
        />
      </defs>
      
      <Group left={margin.left} top={margin.top}>
        {/* Zero line */}
        <line
          x1={0}
          x2={chartWidth}
          y1={yScale(0)}
          y2={yScale(0)}
          stroke="#9CA3AF"
          strokeWidth={1}
          strokeDasharray="3,3"
        />

        {/* Drawdown area */}
        <AreaClosed
          data={data}
          x={d => xScale(d.date)}
          y={d => yScale(d.drawdown)}
          yScale={yScale}
          fill="url(#drawdown-fill)"
          curve={curveCardinal}
        />

        {/* Drawdown line */}
        <LinePath
          data={data}
          x={d => xScale(d.date)}
          y={d => yScale(d.drawdown)}
          stroke="#EF4444"
          strokeWidth={2}
          curve={curveCardinal}
        />

        {/* X-Axis */}
        <AxisBottom
          top={chartHeight}
          scale={xScale}
          numTicks={5}
          stroke="transparent"
          tickStroke="#E5E7EB"
          tickLabelProps={() => ({
            fill: '#9CA3AF',
            fontSize: 12,
            textAnchor: 'middle'
          })}
        />
      </Group>
    </svg>
  );
}

// Utility functions for insights
function getRiskInsight(drawdown: number): string {
  if (drawdown <= 5) {
    return "Excellent downside protection. This low drawdown indicates strong risk management and portfolio resilience.";
  } else if (drawdown <= 10) {
    return "Good risk control with moderate drawdowns. Acceptable for most balanced investment strategies.";
  } else if (drawdown <= 20) {
    return "Elevated drawdown levels require careful monitoring. Consider risk management improvements.";
  } else {
    return "High drawdown indicates significant volatility. Review risk tolerance and portfolio construction.";
  }
}

function getRecoveryInsight(duration?: number, isRecovered?: boolean): string {
  if (!duration && isRecovered) {
    return "Portfolio has fully recovered from previous drawdowns, showing good resilience.";
  } else if (!duration) {
    return "Currently in drawdown period. Monitor for recovery signals and support levels.";
  } else if (duration <= 90) {
    return "Fast recovery demonstrates strong portfolio momentum and effective risk management.";
  } else if (duration <= 180) {
    return "Normal recovery timeframe. Consistent with typical market cycle patterns.";
  } else {
    return "Extended recovery period suggests need for portfolio review and possible rebalancing.";
  }
}