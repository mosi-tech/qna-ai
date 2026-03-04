'use client';

import React, { useMemo } from 'react';
import { Group } from '@visx/group';
import { LinePath, AreaClosed } from '@visx/shape';
import { curveCardinal } from '@visx/curve';
import { LinearGradient } from '@visx/gradient';
import { scaleTime, scaleLinear } from '@visx/scale';
import { AxisBottom, AxisLeft } from '@visx/axis';

interface VolatilityDataPoint {
  date: Date;
  volatility: number;
  regime?: 'low' | 'normal' | 'high' | 'crisis';
}

interface ElegantVolatilityProps {
  volatility: number;
  regime?: string;
  percentile?: number;
  benchmark?: number;
  historicalData?: VolatilityDataPoint[];
  period?: string;
  title?: string;
  subtitle?: string;
}

export function ElegantVolatility({
  volatility,
  regime = 'normal',
  percentile = 50,
  benchmark,
  historicalData = [],
  period = "12M",
  title = "Volatility Analysis",
  subtitle = "Risk measurement and regime assessment"
}: ElegantVolatilityProps) {
  // Volatility assessment
  const getVolatilityAssessment = () => {
    if (volatility <= 8) return { 
      level: 'Very Low', 
      color: 'emerald', 
      score: 90,
      description: 'Conservative, low-risk profile'
    };
    if (volatility <= 15) return { 
      level: 'Low', 
      color: 'blue', 
      score: 75,
      description: 'Moderate risk, suitable for balanced portfolios'
    };
    if (volatility <= 25) return { 
      level: 'Moderate', 
      color: 'yellow', 
      score: 55,
      description: 'Elevated risk requiring active monitoring'
    };
    if (volatility <= 35) return { 
      level: 'High', 
      color: 'orange', 
      score: 35,
      description: 'High risk demanding careful management'
    };
    return { 
      level: 'Extreme', 
      color: 'red', 
      score: 15,
      description: 'Extreme risk requiring immediate attention'
    };
  };

  const assessment = getVolatilityAssessment();

  // Regime analysis
  const getRegimeInfo = () => {
    switch (regime.toLowerCase()) {
      case 'low':
        return { color: 'emerald', label: 'Low Volatility', description: 'Calm market conditions' };
      case 'normal':
        return { color: 'blue', label: 'Normal Volatility', description: 'Typical market conditions' };
      case 'high':
        return { color: 'orange', label: 'High Volatility', description: 'Stressed market conditions' };
      case 'crisis':
        return { color: 'red', label: 'Crisis Volatility', description: 'Extreme market stress' };
      default:
        return { color: 'gray', label: 'Unknown', description: 'Regime not classified' };
    }
  };

  const regimeInfo = getRegimeInfo();

  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-light text-gray-900 mb-1">{title}</h2>
        <p className="text-sm text-gray-500">{subtitle} • {period}</p>
      </div>

      {/* Main Volatility Display */}
      <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 border border-gray-200 shadow-sm mb-6">
        <div className="flex items-center justify-between mb-8">
          {/* Primary Volatility Display */}
          <div className="flex items-baseline space-x-4">
            <div className={`text-6xl font-bold text-${assessment.color}-600`}>
              {volatility.toFixed(1)}%
            </div>
            <div>
              <div className={`text-xl font-semibold text-${assessment.color}-700`}>
                {assessment.level}
              </div>
              <div className="text-sm text-gray-600">Annualized</div>
            </div>
          </div>

          {/* Risk Score Gauge */}
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
                  {assessment.score}
                </span>
              </div>
            </div>
            <div className="text-xs text-gray-600">Stability Score</div>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <MetricCard
            label="Market Regime"
            value={regimeInfo.label}
            sublabel={regimeInfo.description}
            color={regimeInfo.color}
          />
          
          <MetricCard
            label="Percentile Rank"
            value={`${percentile.toFixed(0)}th`}
            sublabel="Historical ranking"
            color={percentile <= 25 ? 'emerald' : percentile <= 75 ? 'blue' : 'red'}
          />
          
          {benchmark && (
            <MetricCard
              label="vs Benchmark"
              value={`${(volatility - benchmark) >= 0 ? '+' : ''}${(volatility - benchmark).toFixed(1)}%`}
              sublabel={`Benchmark: ${benchmark.toFixed(1)}%`}
              color={volatility < benchmark ? 'emerald' : 'red'}
            />
          )}
          
          <MetricCard
            label="Risk Category"
            value={getRiskCategory(volatility)}
            sublabel="Investment suitability"
            color={assessment.color}
          />
        </div>

        <div className={`p-4 rounded-xl ${
          assessment.color === 'emerald' ? 'bg-emerald-50 border border-emerald-200' :
          assessment.color === 'blue' ? 'bg-blue-50 border border-blue-200' :
          assessment.color === 'yellow' ? 'bg-yellow-50 border border-yellow-200' :
          assessment.color === 'orange' ? 'bg-orange-50 border border-orange-200' :
          'bg-red-50 border border-red-200'
        }`}>
          <p className={`text-sm font-medium text-${assessment.color}-800`}>
            {assessment.description}
          </p>
        </div>
      </div>

      {/* Historical Volatility Chart */}
      {historicalData.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-6">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900">Historical Volatility</h3>
            <p className="text-sm text-gray-500 mt-1">
              Volatility evolution with regime identification
            </p>
          </div>
          <div className="p-6">
            <VolatilityChart data={historicalData} currentLevel={volatility} />
          </div>
        </div>
      )}

      {/* Volatility Implications */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk Management */}
        <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl border border-blue-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Management</h3>
          <div className="space-y-3 text-sm text-gray-700">
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <strong>Position Sizing:</strong> {getPositionSizingAdvice(volatility)}
              </div>
            </div>
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <strong>Stop Loss:</strong> {getStopLossAdvice(volatility)}
              </div>
            </div>
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <strong>Monitoring:</strong> {getMonitoringAdvice(volatility)}
              </div>
            </div>
          </div>
        </div>

        {/* Portfolio Implications */}
        <div className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl border border-purple-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Implications</h3>
          <div className="space-y-3 text-sm text-gray-700">
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
              <div>
                <strong>Allocation:</strong> {getAllocationAdvice(volatility)}
              </div>
            </div>
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
              <div>
                <strong>Diversification:</strong> {getDiversificationAdvice(volatility)}
              </div>
            </div>
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
              <div>
                <strong>Rebalancing:</strong> {getRebalancingAdvice(volatility)}
              </div>
            </div>
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
  color: string;
}

function MetricCard({ label, value, sublabel, color }: MetricCardProps) {
  return (
    <div className="text-center">
      <div className={`text-2xl font-bold mb-1 text-${color}-600`}>
        {value}
      </div>
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className="text-xs text-gray-500">{sublabel}</div>
    </div>
  );
}

// Volatility Chart Component
interface VolatilityChartProps {
  data: VolatilityDataPoint[];
  currentLevel: number;
}

function VolatilityChart({ data, currentLevel }: VolatilityChartProps) {
  const width = 700;
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
    domain: [0, Math.max(...data.map(d => d.volatility), currentLevel) * 1.1],
    nice: true
  });

  // Get regime colors
  const getRegimeColor = (regime: string) => {
    switch (regime) {
      case 'low': return '#10B981';
      case 'normal': return '#3B82F6';
      case 'high': return '#F59E0B';
      case 'crisis': return '#EF4444';
      default: return '#6B7280';
    }
  };

  return (
    <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
      <defs>
        <LinearGradient 
          id="volatility-area" 
          from="#8B5CF6" 
          to="#8B5CF6" 
          fromOpacity={0.3} 
          toOpacity={0} 
        />
      </defs>
      
      <Group left={margin.left} top={margin.top}>
        {/* Regime background areas */}
        {data.map((d, i) => {
          if (i === 0 || !d.regime) return null;
          const prevD = data[i - 1];
          return (
            <rect
              key={i}
              x={xScale(prevD.date)}
              y={0}
              width={xScale(d.date) - xScale(prevD.date)}
              height={chartHeight}
              fill={getRegimeColor(d.regime)}
              fillOpacity={0.1}
            />
          );
        })}

        {/* Current level line */}
        <line
          x1={0}
          x2={chartWidth}
          y1={yScale(currentLevel)}
          y2={yScale(currentLevel)}
          stroke="#8B5CF6"
          strokeWidth={2}
          strokeDasharray="5,5"
        />

        {/* Volatility area */}
        <AreaClosed
          data={data}
          x={d => xScale(d.date)}
          y={d => yScale(d.volatility)}
          yScale={yScale}
          fill="url(#volatility-area)"
          curve={curveCardinal}
        />

        {/* Volatility line */}
        <LinePath
          data={data}
          x={d => xScale(d.date)}
          y={d => yScale(d.volatility)}
          stroke="#8B5CF6"
          strokeWidth={2}
          curve={curveCardinal}
        />

        {/* Axes */}
        <AxisBottom
          top={chartHeight}
          scale={xScale}
          numTicks={5}
          stroke="transparent"
          tickStroke="#E5E7EB"
          tickLabelProps={() => ({
            fill: '#6B7280',
            fontSize: 12,
            textAnchor: 'middle'
          })}
        />
        
        <AxisLeft
          scale={yScale}
          numTicks={5}
          stroke="transparent"
          tickStroke="#E5E7EB"
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

// Utility Functions
function getRiskCategory(volatility: number): string {
  if (volatility <= 8) return 'Conservative';
  if (volatility <= 15) return 'Moderate';
  if (volatility <= 25) return 'Aggressive';
  return 'Speculative';
}

function getPositionSizingAdvice(volatility: number): string {
  if (volatility <= 15) {
    return "Standard position sizing appropriate. Consider 2-5% risk per trade.";
  } else if (volatility <= 25) {
    return "Reduce position sizes by 25-50%. Consider 1-3% risk per trade.";
  } else {
    return "Significantly reduce positions. Limit risk to 0.5-1% per trade.";
  }
}

function getStopLossAdvice(volatility: number): string {
  const stopDistance = volatility * 1.5;
  return `Consider stop losses at ${stopDistance.toFixed(1)}% distance based on current volatility.`;
}

function getMonitoringAdvice(volatility: number): string {
  if (volatility <= 15) {
    return "Weekly monitoring sufficient for this volatility level.";
  } else if (volatility <= 25) {
    return "Daily monitoring recommended due to elevated volatility.";
  } else {
    return "Intraday monitoring required. Consider real-time alerts.";
  }
}

function getAllocationAdvice(volatility: number): string {
  if (volatility <= 15) {
    return "Suitable for core portfolio allocation. Consider 10-20% weight.";
  } else if (volatility <= 25) {
    return "Appropriate for satellite positions. Limit to 5-10% allocation.";
  } else {
    return "Use only for tactical trades. Limit exposure to 1-5%.";
  }
}

function getDiversificationAdvice(volatility: number): string {
  if (volatility <= 15) {
    return "Standard diversification principles apply.";
  } else {
    return "Increased diversification critical. Consider uncorrelated assets.";
  }
}

function getRebalancingAdvice(volatility: number): string {
  if (volatility <= 15) {
    return "Quarterly rebalancing frequency appropriate.";
  } else if (volatility <= 25) {
    return "Monthly rebalancing may be beneficial.";
  } else {
    return "Consider dynamic rebalancing based on volatility triggers.";
  }
}