/**
 * finBlocks Library - Financial UI Components
 *
 * A comprehensive collection of 110 financial UI blocks for retail investor dashboards.
 * Organized into 11 categories for easy discovery and use.
 */

'use client';

// Export all categories
export * from './components/portfolio';
export * from './components/stock_research';
export * from './components/etf_analysis';
export * from './components/risk_management';
export * from './components/performance';
export * from './components/income';
export * from './components/sector';
export * from './components/technical';
export * from './components/fundamental';
export * from './components/tax';
export * from './components/monitoring';

// Export registry and utilities
export {
  FINBLOCKS,
  getFinBlock,
  getFinBlocksByCategory,
  getAllFinBlocks,
  getFinBlocksByFinancialConcept,
  type FinBlockMetadata,
} from './finBlockRegistry';
