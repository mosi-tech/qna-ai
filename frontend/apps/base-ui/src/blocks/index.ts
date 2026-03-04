/**
 * Canonical Finance-Semantic Blocks
 * 
 * This module exports reusable example components, component stubs, and types
 * that answer specific financial questions. Each example demonstrates
 * a canonical presentation pattern for financial data.
 */

// Export all blocks and examples from each category
export * from './bar-charts';
export * from './bar-lists';
export * from './donut-charts';
export * from './kpi-cards';
export * from './line-charts';
export * from './spark-charts';
export * from './status-monitoring';
export * from './tables';
// Phase 2 — new chart categories
export * from './treemaps';
export * from './heatmaps';
// Phase 1 — shared dashboard types + canvas
export * from './types';
export { default as DashboardCanvas } from './DashboardCanvas';
export { default as BlockShell } from './BlockShell';
export type { BlockShellProps } from './BlockShell';
