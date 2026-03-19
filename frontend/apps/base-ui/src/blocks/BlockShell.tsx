'use client';

/**
 * BlockShell.tsx — @ui-gen/base-ui
 *
 * Wrapper that renders the correct base-ui block component from a BlockSpec.
 * Shows a skeleton while loading, handles errors gracefully, and handles the
 * 'cached' fast-paint state added in Phase 8.
 *
 * Moved from apps/ai-builder/components/BlockShell.tsx in Phase 1.
 */

import React from 'react';
import { KpiCard01 } from './kpi-cards';
import { LineChart01 } from './line-charts';
import { BarChart01, BarChart05 } from './bar-charts';
import { BarList01 } from './bar-lists';
import { DonutChart01 } from './donut-charts';
import { SparkChart01 } from './spark-charts';
import { Table01 } from './tables';
import { Tracker01 } from './status-monitoring';
import type { BlockSpec, BlockLoadState } from './types';

// ─── Skeleton ─────────────────────────────────────────────────────────────────

function Skeleton({ lines = 3 }: { lines?: number }) {
    return (
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm animate-pulse">
            <div className="h-3 w-1/3 bg-slate-200 dark:bg-slate-700 rounded mb-4" />
            {Array.from({ length: lines }).map((_, i) => (
                <div
                    key={i}
                    className="h-3 bg-slate-200 dark:bg-slate-700 rounded mb-2"
                    style={{ width: `${85 - i * 12}%` }}
                />
            ))}
            <div className="mt-4 h-24 bg-slate-100 dark:bg-slate-700/50 rounded-lg" />
        </div>
    );
}

// ─── Block renderers ──────────────────────────────────────────────────────────

type Renderer = (data: Record<string, unknown>, spec: BlockSpec) => React.ReactNode;

function renderKpiCard(data: Record<string, unknown>, _spec: BlockSpec): React.ReactNode {
    const metrics = (data.metrics as any[]) ?? [];
    const cols = (data.cols as number) ?? Math.min(metrics.length, 4);
    return <KpiCard01 metrics={metrics} cols={cols} />;
}

function renderLineChart01(data: Record<string, unknown>, spec: BlockSpec): React.ReactNode {
    const chartData = (data.data as any[]) ?? [];
    const categories = (data.categories as string[]) ?? ['Value'];
    const summary = (data.summary as any[]) ?? categories.map((c: string) => ({ name: c, value: 0 }));
    return <LineChart01 title={spec.title} data={chartData} categories={categories} summary={summary} indexField="date" />;
}

function renderBarChart01(data: Record<string, unknown>, spec: BlockSpec): React.ReactNode {
    const chartData = (data.data as any[]) ?? [];
    const categories = (data.categories as string[]) ?? ['Value'];
    return (
        <BarChart01
            title={spec.title}
            description={spec.dataContract.description}
            data={chartData}
            indexField="date"
            defaultCategories={[categories[0] ?? 'Value']}
            comparisonCategories={categories}
        />
    );
}

function renderBarChart05(data: Record<string, unknown>, spec: BlockSpec): React.ReactNode {
    const chartData = (data.data as any[]) ?? [];
    const categories = (data.categories as string[]) ?? ['Value'];
    if (chartData.length > 0 && 'name' in chartData[0] && !('date' in chartData[0])) {
        return (
            <BarChart01
                title={spec.title}
                description={spec.dataContract.description}
                data={chartData}
                indexField="name"
                defaultCategories={['value']}
                comparisonCategories={['value']}
            />
        );
    }
    const summary = [{
        name: categories[0] ?? 'Overview',
        data: chartData,
        details: categories.map((c: string) => ({
            name: c,
            value: chartData.reduce((sum: number, row: any) => sum + (Number(row[c]) || 0), 0),
        })),
    }];
    return <BarChart05 title={spec.title} summary={summary} categories={categories} indexField="date" />;
}

function renderBarList01(data: Record<string, unknown>, spec: BlockSpec): React.ReactNode {
    const listData = (data.data as any[]) ?? [];
    return <BarList01 title={spec.title} subtitle="Value" data={listData} />;
}

function renderDonutChart01(data: Record<string, unknown>, spec: BlockSpec): React.ReactNode {
    const donutData = (data.data as any[]) ?? [];
    return <DonutChart01 title={spec.title} data={donutData} />;
}

function renderSparkChart01(data: Record<string, unknown>, spec: BlockSpec): React.ReactNode {
    const sparkData = (data.data as any[]) ?? [];
    const items = (data.items as any[]) ?? [];
    return <SparkChart01 title={spec.title} data={sparkData} items={items} dataIndex="date" />;
}

function renderTable01(data: Record<string, unknown>, _spec: BlockSpec): React.ReactNode {
    const rows = (data.rows as Record<string, unknown>[]) ?? [];
    const columnNames = (data.columns as string[]) ?? [];

    // Convert column names to TableColumn objects
    const columns = columnNames.map(name => ({
        key: name,
        label: name,
        align: (name.toLowerCase().includes('p&l') || name.toLowerCase().includes('value') || name.toLowerCase().includes('%') || name.toLowerCase().includes('cost') || name.toLowerCase().includes('price')) ? 'right' as const : 'left' as const,
    }));

    return <Table01 data={rows} columns={columns} />;
}

function renderTracker01(data: Record<string, unknown>, spec: BlockSpec): React.ReactNode {
    const raw = (data.data as Array<{ status: string }>) ?? [];
    const statusMap: Record<string, string> = { ok: 'Operational', warning: 'Degraded', error: 'Downtime' };
    const trackerData = raw.map((item, i) => ({ tooltip: `Day ${i + 1}`, status: statusMap[item.status] ?? 'Operational' }));
    const okCount = raw.filter((d) => d.status === 'ok').length;
    const uptime = raw.length ? `${((okCount / raw.length) * 100).toFixed(1)}%` : '100%';
    const latestStatus = trackerData.length ? trackerData[trackerData.length - 1].status : 'Operational';
    return <Tracker01 data={trackerData} serviceName={spec.title} displayName={spec.title} uptime={uptime} status={latestStatus} />;
}

// ─── Registry ─────────────────────────────────────────────────────────────────

const BLOCK_REGISTRY: Record<string, Renderer> = {
    'kpi-card-01': renderKpiCard, 'kpi-card-02': renderKpiCard, 'kpi-card-03': renderKpiCard,
    'kpi-card-04': renderKpiCard, 'kpi-card-05': renderKpiCard, 'kpi-card-06': renderKpiCard, 'kpi-card-07': renderKpiCard,
    'kpi-card-08': renderKpiCard, 'kpi-card-09': renderKpiCard, 'kpi-card-10': renderKpiCard, 'kpi-card-11': renderKpiCard,
    'kpi-card-12': renderKpiCard, 'kpi-card-13': renderKpiCard, 'kpi-card-14': renderKpiCard, 'kpi-card-15': renderKpiCard,
    'kpi-card-16': renderKpiCard, 'kpi-card-17': renderKpiCard, 'kpi-card-18': renderKpiCard, 'kpi-card-19': renderKpiCard,
    'kpi-card-20': renderKpiCard, 'kpi-card-21': renderKpiCard, 'kpi-card-22': renderKpiCard, 'kpi-card-23': renderKpiCard,
    'kpi-card-24': renderKpiCard, 'kpi-card-25': renderKpiCard, 'kpi-card-26': renderKpiCard, 'kpi-card-27': renderKpiCard,
    'kpi-card-28': renderKpiCard, 'kpi-card-29': renderKpiCard,
    'line-chart-01': renderLineChart01, 'line-chart-02': renderLineChart01,
    'line-chart-03': renderLineChart01, 'line-chart-04': renderLineChart01, 'line-chart-05': renderLineChart01,
    'line-chart-06': renderLineChart01, 'line-chart-07': renderLineChart01, 'line-chart-08': renderLineChart01, 'line-chart-09': renderLineChart01,
    'bar-chart-01': renderBarChart01, 'bar-chart-02': renderBarChart01, 'bar-chart-03': renderBarChart01,
    'bar-chart-04': renderBarChart01, 'bar-chart-05': renderBarChart05, 'bar-chart-06': renderBarChart01,
    'bar-chart-07': renderBarChart01, 'bar-chart-08': renderBarChart01, 'bar-chart-09': renderBarChart01,
    'bar-chart-10': renderBarChart01, 'bar-chart-11': renderBarChart01, 'bar-chart-12': renderBarChart01,
    'bar-list-01': renderBarList01, 'bar-list-02': renderBarList01, 'bar-list-03': renderBarList01,
    'bar-list-04': renderBarList01, 'bar-list-05': renderBarList01, 'bar-list-06': renderBarList01, 'bar-list-07': renderBarList01,
    'donut-chart-01': renderDonutChart01, 'donut-chart-02': renderDonutChart01, 'donut-chart-03': renderDonutChart01,
    'donut-chart-04': renderDonutChart01, 'donut-chart-05': renderDonutChart01, 'donut-chart-06': renderDonutChart01, 'donut-chart-07': renderDonutChart01,
    'spark-chart-01': renderSparkChart01, 'spark-chart-02': renderSparkChart01, 'spark-chart-03': renderSparkChart01,
    'spark-chart-04': renderSparkChart01, 'spark-chart-05': renderSparkChart01, 'spark-chart-06': renderSparkChart01,
    'table-01': renderTable01, 'table-action-01': renderTable01,
    'tracker-01': renderTracker01, 'tracker-02': renderTracker01, 'tracker-03': renderTracker01, 'tracker-04': renderTracker01,
};

// ─── BlockShell ───────────────────────────────────────────────────────────────

export interface BlockShellProps {
    spec: BlockSpec;
    loadState: BlockLoadState;
    data?: Record<string, unknown>;
    error?: string;
    index?: number;
}

export default function BlockShell({ spec, loadState, data, error, index = 0 }: BlockShellProps) {
    const delay = `${index * 60}ms`;

    if (loadState === 'idle') return null;

    if (loadState === 'loading') {
        return (
            <div style={{ animationDelay: delay }} className="animate-fadeIn">
                <Skeleton lines={3} />
            </div>
        );
    }

    if (loadState === 'error' || error) {
        return (
            <div className="rounded-xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950 p-5">
                <p className="text-sm font-medium text-red-700 dark:text-red-300 mb-1">{spec.title}</p>
                <p className="text-xs text-red-500 dark:text-red-400">{error ?? 'Failed to load data'}</p>
            </div>
        );
    }

    if ((loadState === 'loaded' || loadState === 'cached') && data) {
        const renderer = BLOCK_REGISTRY[spec.blockId];
        if (!renderer) {
            return (
                <div className="rounded-xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950 p-5">
                    <p className="text-sm text-amber-700 dark:text-amber-300">
                        Unknown block: <code>{spec.blockId}</code>
                    </p>
                </div>
            );
        }
        return (
            <div key={spec.blockId} style={{ animationDelay: delay }} className="animate-fadeIn">
                {renderer(data, spec)}
            </div>
        );
    }

    return null;
}
