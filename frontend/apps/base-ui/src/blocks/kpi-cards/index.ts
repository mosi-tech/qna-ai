// Type definitions and component exports needed by examples
import React from 'react';

export interface MetricItem {
    id?: string;
    name: string;
    value?: number | string;
    stat?: number | string;
    change?: string | number;
    changeType?: 'positive' | 'negative' | 'neutral';
    secondaryValue?: string | number;
    previousStat?: string | number;
    href?: string;
    [key: string]: any;
}

/**
 * Common formatting props used across KPI cards for finance/trading use cases
 * Provides consistent control over number display, currency, and abbreviation
 */
export interface CommonFormattingProps {
    /**
     * Number of decimal places to display (default: 2)
     * Examples: 2 for prices, 1 for percentages, 0 for large integers
     */
    decimals?: number;

    /**
     * Currency code (USD, EUR, GBP, etc.) or symbol for currency formatting
     * When provided, values are formatted as currency instead of plain numbers
     * Examples: 'USD', 'EUR', 'GBP'
     */
    currency?: string;

    /**
     * Whether to abbreviate large numbers (1000000 -> 1M, 1000 -> 1K, etc.)
     * Useful for showing portfolio values, market caps, volumes at a glance
     */
    abbreviate?: boolean;
}

export const MetricGridWithTrendBlock: React.FC<any> = () => null;
export type MetricGridItem = any;
export type MetricGridWithTrendVariant = 'inline_change_badge' | 'right_aligned_change' | 'with_navigation_link' | 'period_comparison_colored' | 'arrow_icon_variant' | 'period_comparison_badge' | 'colored_left_accent';

// Export finance formatting utilities
export * from '../../lib/financeFormatters';

// Component exports (one per block file)
export * from './kpi-card-01';
export * from './kpi-card-02';
export * from './kpi-card-03';
export * from './kpi-card-04';
export * from './kpi-card-05';
export * from './kpi-card-06';
export * from './kpi-card-07';
export * from './kpi-card-08';
export * from './kpi-card-09';
export * from './kpi-card-10';
export * from './kpi-card-11';
export * from './kpi-card-12';
export * from './kpi-card-13';
export * from './kpi-card-14';
export * from './kpi-card-15';
export * from './kpi-card-16';
export * from './kpi-card-17';
export * from './kpi-card-18';
export * from './kpi-card-19';
export * from './kpi-card-20';
export * from './kpi-card-21';
export type { DetailItem as KpiCard22DetailItem, TokenMetric, KpiCard22Props } from './kpi-card-22';
export { KpiCard22 } from './kpi-card-22';
export * from './kpi-card-23';
export * from './kpi-card-24';
export type { DetailItem as KpiCard25DetailItem, MetricCard, KpiCard25Props } from './kpi-card-25';
export { KpiCard25 } from './kpi-card-25';
export type { DetailLabel, MetricItem as KpiCard26MetricItem, KpiCard26Props } from './kpi-card-26';
export { KpiCard26 } from './kpi-card-26';
export * from './kpi-card-27';
export type { Metric as KpiCard28Metric, IssueItem, KpiCard28Props } from './kpi-card-28';
export { KpiCard28 } from './kpi-card-28';
export * from './kpi-card-29';

// Example exports
export * from './examples';
