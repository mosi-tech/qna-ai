'use client';

import React, { useMemo } from 'react';
import { Group } from '@visx/group';
import { LinePath, AreaClosed, Bar } from '@visx/shape';
import { curveCardinal } from '@visx/curve';
import { LinearGradient } from '@visx/gradient';
import { scaleTime, scaleLinear, scaleBand } from '@visx/scale';
import { AxisBottom, AxisLeft } from '@visx/axis';
import { PatternLines } from '@visx/pattern';

interface RiskMetrics {
  sharpe: number;
  sortino: number;
  beta: number;
  volatility: number;
  maxDrawdown: number;
  var95: number;
  var99: number;
  expectedShortfall: number;
  calmar: number;
  treynor: number;
}

interface VolatilityDataPoint {
  date: Date;
  volatility: number;
  regime: 'low' | 'normal' | 'high' | 'crisis';
}

interface DrawdownDataPoint {
  date: Date;
  drawdown: number;
  underwater: boolean;
}

interface ElegantRiskDashboardProps {
  metrics: RiskMetrics;
  volatilityData: VolatilityDataPoint[];
  drawdownData: DrawdownDataPoint[];
  benchmarkMetrics?: Partial<RiskMetrics>;
  title?: string;
  height?: number;
}

export function ElegantRiskDashboard({
  metrics,
  volatilityData,
  drawdownData,
  benchmarkMetrics,
  title = "Risk Analytics",
  height = 400
}: ElegantRiskDashboardProps) {
  return (
    <div className="w-full space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-light text-gray-900 mb-2">{title}</h1>
        <p className="text-gray-500">
          Comprehensive risk assessment with market context
        </p>
      </div>

      {/* Risk Score Overview */}
      <RiskScoreOverview metrics={metrics} benchmarkMetrics={benchmarkMetrics} />

      {/* Key Risk Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <RiskMetricCard
          label="Sharpe Ratio"
          value={metrics.sharpe}
          benchmark={benchmarkMetrics?.sharpe}
          format="decimal"
          description="Risk-adjusted return"
          quality={getRiskQuality('sharpe', metrics.sharpe)}
        />
        <RiskMetricCard
          label="Max Drawdown"
          value={metrics.maxDrawdown}
          benchmark={benchmarkMetrics?.maxDrawdown}
          format="percentage"
          description="Worst peak-to-trough decline"
          quality={getRiskQuality('drawdown', metrics.maxDrawdown)}
          negative
        />
        <RiskMetricCard
          label="Volatility"
          value={metrics.volatility}
          benchmark={benchmarkMetrics?.volatility}
          format="percentage"
          description="Annualized standard deviation"
          quality={getRiskQuality('volatility', metrics.volatility)}
        />
        <RiskMetricCard
          label="VaR (95%)"
          value={metrics.var95}
          benchmark={benchmarkMetrics?.var95}
          format="percentage"
          description="1-day value at risk"
          quality={getRiskQuality('var', metrics.var95)}
          negative
        />
      </div>

      {/* Volatility Regime Chart */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">Volatility Regimes</h3>
          <p className="text-sm text-gray-500 mt-1">
            Historical volatility with market regime identification
          </p>
        </div>
        <div className="p-6">
          <VolatilityChart data={volatilityData} height={height * 0.7} />
        </div>
      </div>

      {/* Drawdown Analysis */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">Drawdown Analysis</h3>
          <p className="text-sm text-gray-500 mt-1">
            Underwater periods and recovery patterns
          </p>
        </div>
        <div className="p-6">
          <DrawdownChart data={drawdownData} height={height * 0.7} />
        </div>
      </div>

      {/* Advanced Risk Metrics */}
      <AdvancedRiskMetrics metrics={metrics} benchmarkMetrics={benchmarkMetrics} />
    </div>
  );
}

// Risk score overview component
function RiskScoreOverview({ 
  metrics, 
  benchmarkMetrics 
}: { 
  metrics: RiskMetrics; 
  benchmarkMetrics?: Partial<RiskMetrics> 
}) {
  // Calculate composite risk score (0-100, higher is better risk-adjusted performance)
  const riskScore = useMemo(() => {
    const sharpeWeight = 0.4;
    const drawdownWeight = 0.3;
    const volatilityWeight = 0.3;
    
    const sharpeScore = Math.min(metrics.sharpe * 25, 100); // Normalize Sharpe ratio
    const drawdownScore = Math.max(0, 100 + metrics.maxDrawdown * 2); // Less negative is better
    const volatilityScore = Math.max(0, 100 - metrics.volatility * 2); // Lower volatility is better
    
    return sharpeScore * sharpeWeight + drawdownScore * drawdownWeight + volatilityScore * volatilityWeight;
  }, [metrics]);

  const scoreColor = riskScore >= 80 ? 'emerald' : riskScore >= 60 ? 'blue' : riskScore >= 40 ? 'yellow' : 'red';
  const scoreLabel = riskScore >= 80 ? 'Excellent' : riskScore >= 60 ? 'Good' : riskScore >= 40 ? 'Fair' : 'Poor';

  return (
    <div className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-2xl p-8 border border-slate-200">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div className="mb-6 md:mb-0">
          <div className="flex items-baseline space-x-4">
            <div className={`text-5xl font-bold text-${scoreColor}-600`}>
              {riskScore.toFixed(0)}
            </div>
            <div>
              <div className={`text-lg font-semibold text-${scoreColor}-700`}>
                {scoreLabel}
              </div>
              <div className="text-sm text-gray-600">Risk Score</div>
            </div>
          </div>
          <p className="text-gray-600 mt-3 max-w-md">
            Composite risk assessment based on risk-adjusted returns, 
            maximum drawdown, and volatility characteristics.
          </p>
        </div>

        {/* Risk Score Breakdown */}
        <div className="grid grid-cols-3 gap-6">
          <ScoreComponent
            label="Return Quality"
            score={Math.min(metrics.sharpe * 25, 100)}
            color="blue"
          />
          <ScoreComponent
            label="Downside Protection"
            score={Math.max(0, 100 + metrics.maxDrawdown * 2)}
            color="emerald"
          />
          <ScoreComponent
            label="Stability"
            score={Math.max(0, 100 - metrics.volatility * 2)}
            color="purple"
          />
        </div>
      </div>
    </div>
  );
}

// Score component
function ScoreComponent({ 
  label, 
  score, 
  color 
}: { 
  label: string; 
  score: number; 
  color: string; 
}) {
  return (
    <div className="text-center">
      <div className={`text-2xl font-bold text-${color}-600`}>
        {score.toFixed(0)}
      </div>
      <div className="text-xs text-gray-600 mt-1">{label}</div>
      <div className="w-16 h-1 bg-gray-200 rounded-full mx-auto mt-2">
        <div 
          className={`h-1 bg-${color}-500 rounded-full transition-all duration-500`}
          style={{ width: `${Math.min(score, 100)}%` }}
        />
      </div>
    </div>
  );
}

// Risk metric card
interface RiskMetricCardProps {
  label: string;
  value: number;
  benchmark?: number;
  format: 'percentage' | 'decimal' | 'currency';
  description: string;
  quality: 'excellent' | 'good' | 'fair' | 'poor';
  negative?: boolean;
}

function RiskMetricCard({
  label,
  value,
  benchmark,
  format,
  description,
  quality,
  negative = false
}: RiskMetricCardProps) {
  const formatValue = (val: number) => {
    switch (format) {
      case 'percentage':
        return `${val.toFixed(1)}%`;
      case 'decimal':
        return val.toFixed(2);
      case 'currency':
        return `$${val.toLocaleString()}`;
      default:
        return val.toString();
    }
  };

  const qualityConfig = {
    excellent: { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700' },
    good: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700' },
    fair: { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-700' },
    poor: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700' }
  };

  const config = qualityConfig[quality];

  return (
    <div className={`${config.bg} ${config.border} border rounded-xl p-6 hover:shadow-md transition-shadow`}>
      <div className="flex items-center justify-between mb-4">
        <h4 className="font-semibold text-gray-900">{label}</h4>
        <QualityIndicator quality={quality} />
      </div>
      
      <div className="space-y-3">
        <div className={`text-3xl font-bold ${config.text}`}>
          {negative && value > 0 ? '' : negative ? '' : ''}
          {formatValue(value)}
        </div>
        
        {benchmark && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">vs benchmark:</span>
            <span className={`text-sm font-medium ${
              (negative ? value < benchmark : value > benchmark) 
                ? 'text-emerald-600' 
                : 'text-red-600'
            }`}>
              {formatValue(benchmark)}
            </span>
          </div>
        )}
        
        <p className="text-xs text-gray-600">{description}</p>
      </div>
    </div>
  );
}

// Quality indicator
function QualityIndicator({ quality }: { quality: string }) {
  const config = {
    excellent: { color: 'bg-emerald-500', dots: 4 },
    good: { color: 'bg-blue-500', dots: 3 },
    fair: { color: 'bg-yellow-500', dots: 2 },
    poor: { color: 'bg-red-500', dots: 1 }
  };

  const { color, dots } = config[quality as keyof typeof config];

  return (
    <div className="flex space-x-1">
      {Array.from({ length: 4 }).map((_, i) => (
        <div
          key={i}
          className={`w-2 h-2 rounded-full ${
            i < dots ? color : 'bg-gray-200'
          }`}
        />
      ))}
    </div>
  );
}

// Volatility chart component
function VolatilityChart({ data, height }: { data: VolatilityDataPoint[]; height: number }) {
  const width = 800;
  const margin = { top: 20, right: 30, bottom: 40, left: 60 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const xScale = scaleTime({
    range: [0, chartWidth],
    domain: [Math.min(...data.map(d => d.date)), Math.max(...data.map(d => d.date))]
  });

  const yScale = scaleLinear({
    range: [chartHeight, 0],
    domain: [0, Math.max(...data.map(d => d.volatility)) * 1.1],
    nice: true
  });

  // Color coding for regimes
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
        <LinearGradient id="volatility-gradient" from="#3B82F6" to="#3B82F6" fromOpacity={0.3} toOpacity={0} />
      </defs>
      
      <Group left={margin.left} top={margin.top}>
        {/* Background regime areas */}
        {data.map((d, i) => {
          if (i === 0) return null;
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

        {/* Volatility area */}
        <AreaClosed
          data={data}
          x={d => xScale(d.date)}
          y={d => yScale(d.volatility)}
          yScale={yScale}
          fill="url(#volatility-gradient)"
          curve={curveCardinal}
        />

        {/* Volatility line */}
        <LinePath
          data={data}
          x={d => xScale(d.date)}
          y={d => yScale(d.volatility)}
          stroke="#3B82F6"
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
            fill: '#9CA3AF',
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
            fill: '#9CA3AF',
            fontSize: 12,
            textAnchor: 'end'
          })}
          tickFormat={(value) => `${value}%`}
        />
      </Group>
    </svg>
  );
}

// Drawdown chart component
function DrawdownChart({ data, height }: { data: DrawdownDataPoint[]; height: number }) {
  const width = 800;
  const margin = { top: 20, right: 30, bottom: 40, left: 60 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const xScale = scaleTime({
    range: [0, chartWidth],
    domain: [Math.min(...data.map(d => d.date)), Math.max(...data.map(d => d.date))]
  });

  const yScale = scaleLinear({
    range: [chartHeight, 0],
    domain: [Math.min(...data.map(d => d.drawdown)) * 1.1, 0],
    nice: true
  });

  return (
    <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
      <defs>
        <LinearGradient id="drawdown-gradient" from="#EF4444" to="#EF4444" fromOpacity={0.3} toOpacity={0} />
        <PatternLines id="underwater" height={4} width={4} stroke="#EF4444" strokeWidth={1} />
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

        {/* Underwater areas */}
        <AreaClosed
          data={data}
          x={d => xScale(d.date)}
          y={d => yScale(d.drawdown)}
          yScale={yScale}
          fill="url(#drawdown-gradient)"
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

        {/* Axes */}
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
        
        <AxisLeft
          scale={yScale}
          numTicks={5}
          stroke="transparent"
          tickStroke="#E5E7EB"
          tickLabelProps={() => ({
            fill: '#9CA3AF',
            fontSize: 12,
            textAnchor: 'end'
          })}
          tickFormat={(value) => `${value}%`}
        />
      </Group>
    </svg>
  );
}

// Advanced risk metrics component
function AdvancedRiskMetrics({ 
  metrics, 
  benchmarkMetrics 
}: { 
  metrics: RiskMetrics; 
  benchmarkMetrics?: Partial<RiskMetrics> 
}) {
  const advancedMetrics = [
    { label: 'Sortino Ratio', value: metrics.sortino, description: 'Downside risk-adjusted return', benchmark: benchmarkMetrics?.sortino },
    { label: 'Calmar Ratio', value: metrics.calmar, description: 'Return vs max drawdown', benchmark: benchmarkMetrics?.calmar },
    { label: 'Treynor Ratio', value: metrics.treynor, description: 'Systematic risk-adjusted return', benchmark: benchmarkMetrics?.treynor },
    { label: 'Expected Shortfall', value: metrics.expectedShortfall, description: 'Average loss beyond VaR', negative: true }
  ];

  return (
    <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-2xl p-8 border border-gray-200">
      <h3 className="text-xl font-semibold text-gray-900 mb-6">Advanced Risk Metrics</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {advancedMetrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-center">
              <div className={`text-2xl font-bold mb-2 ${
                metric.negative ? 'text-red-600' : 'text-blue-600'
              }`}>
                {metric.negative && metric.value > 0 ? '' : ''}
                {metric.value.toFixed(2)}
                {metric.negative ? '%' : ''}
              </div>
              <div className="font-semibold text-gray-900 mb-1">{metric.label}</div>
              <div className="text-xs text-gray-600">{metric.description}</div>
              
              {metric.benchmark && (
                <div className="mt-2 pt-2 border-t border-gray-100">
                  <div className="text-xs text-gray-600">
                    Benchmark: <span className="font-medium">{metric.benchmark.toFixed(2)}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Utility function to determine risk quality
function getRiskQuality(metricType: string, value: number): 'excellent' | 'good' | 'fair' | 'poor' {
  switch (metricType) {
    case 'sharpe':
      return value >= 1.5 ? 'excellent' : value >= 1.0 ? 'good' : value >= 0.5 ? 'fair' : 'poor';
    case 'drawdown':
      return value >= -5 ? 'excellent' : value >= -10 ? 'good' : value >= -20 ? 'fair' : 'poor';
    case 'volatility':
      return value <= 10 ? 'excellent' : value <= 15 ? 'good' : value <= 25 ? 'fair' : 'poor';
    case 'var':
      return value >= -1 ? 'excellent' : value >= -2 ? 'good' : value >= -3 ? 'fair' : 'poor';
    default:
      return 'fair';
  }
}