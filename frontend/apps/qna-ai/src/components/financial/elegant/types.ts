// Shared TypeScript interfaces for elegant financial components

export interface DataPoint {
  date: Date;
  value: number;
  benchmark?: number;
}

export interface AllocationItem {
  name: string;
  value: number;
  color?: string;
  target?: number;
  drift?: number;
  risk?: 'low' | 'medium' | 'high';
  expectedReturn?: number;
  sharpeRatio?: number;
  yield?: number;
  category?: string;
}

export interface Holding {
  symbol: string;
  name: string;
  shares: number;
  value: number;
  weight: number;
  dayChange: number;
  sector: string;
  pe?: number;
  yield?: number;
}

export interface RiskMetrics {
  sharpe: number;
  sortino: number;
  beta: number;
  volatility: number;
  maxDrawdown: number;
  var95: number;
  var99?: number;
  expectedShortfall?: number;
  calmar?: number;
  treynor?: number;
}

export interface AttributionFactor {
  name: string;
  selection: number;
  allocation: number;
  interaction: number;
  total: number;
  description?: string;
  category?: 'sector' | 'factor' | 'style' | 'geography';
}

export interface VolatilityDataPoint {
  date: Date;
  volatility: number;
  regime?: 'low' | 'normal' | 'high' | 'crisis';
}

export interface DrawdownDataPoint {
  date: Date;
  drawdown: number;
  underwater: boolean;
}

// Component Props Interfaces
export interface RobinhoodStylePortfolioProps {
  data: DataPoint[];
  currentValue: number;
  dayChange: number;
  dayChangePercent: number;
  title?: string;
  showBenchmark?: boolean;
  height?: number;
}

export interface ElegantAllocationProps {
  allocations: AllocationItem[];
  title?: string;
  showTargets?: boolean;
  showRiskMetrics?: boolean;
  size?: number;
  innerRadius?: number;
}

export interface ElegantRiskDashboardProps {
  metrics: RiskMetrics;
  volatilityData: VolatilityDataPoint[];
  drawdownData: DrawdownDataPoint[];
  benchmarkMetrics?: Partial<RiskMetrics>;
  title?: string;
  timeframe?: string;
  height?: number;
}

export interface ElegantAttributionProps {
  factors: AttributionFactor[];
  totalAlpha: number;
  benchmarkReturn: number;
  portfolioReturn: number;
  title?: string;
  timeframe?: string;
  height?: number;
}