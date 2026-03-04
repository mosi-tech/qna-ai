// Elegant Financial Components - Built with visx for investment professionals
// Clean, borderless design inspired by Robinhood/TradingView aesthetics

// Core Portfolio Components
export { RobinhoodStylePortfolio, ElegantPortfolioMetrics } from './RobinhoodStylePortfolio';
export { ElegantHoldingsTable, ElegantHoldingsSummary } from './ElegantHoldingsTable';
export { ElegantAllocation } from './ElegantAllocation';

// Individual Metric Components  
export { ElegantMaxDrawdown } from './ElegantMaxDrawdown';
export { ElegantSharpeRatio } from './ElegantSharpeRatio';
export { ElegantAnnualizedReturns } from './ElegantAnnualizedReturns';
export { ElegantCumulativeReturns } from './ElegantCumulativeReturns';
export { ElegantAssetAllocationPie } from './ElegantAssetAllocationPie';
export { ElegantVolatility } from './ElegantVolatility';

// Advanced Analysis Components
export { ElegantRiskDashboard } from './ElegantRiskDashboard';
export { ElegantAttribution } from './ElegantAttribution';

// Component Types (for TypeScript users)
export type { 
  // Core types
  DataPoint,
  AllocationItem,
  Holding,
  RiskMetrics,
  AttributionFactor,
  
  // Component Props
  RobinhoodStylePortfolioProps,
  ElegantAllocationProps,
  ElegantRiskDashboardProps,
  ElegantAttributionProps
} from './types';

/**
 * Elegant Financial Components Library
 * 
 * Key Features:
 * - Investment-grade UI with Robinhood/TradingView aesthetics
 * - Built with visx for optimal performance and customization
 * - Comprehensive risk analytics and portfolio insights
 * - TypeScript support with full type safety
 * - Responsive design for all devices
 * - Professional color schemes with semantic meaning
 * 
 * Usage:
 * import { ElegantSharpeRatio, ElegantMaxDrawdown } from '@/components/financial/elegant';
 * 
 * Design Principles:
 * - Typography-first approach with large, readable numbers
 * - Borderless layouts with generous white space
 * - Semantic color coding (green for gains, red for losses)
 * - Smooth gradients and professional depth
 * - Investment professional insights built-in
 */