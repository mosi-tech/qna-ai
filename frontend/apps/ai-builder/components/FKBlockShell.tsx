'use client';

/**
 * FKBlockShell.tsx
 *
 * Renders finkit-ui blocks from a BlockSpec + data payload.
 * Replaces the base-ui Tremor-based BlockShell for all blocks
 * emitted by the updated UI Planner (blockIds = FKLineChart, etc.).
 */

import React from 'react';
// @ts-expect-error — finkit is a JSX/ESM package, no TS declarations yet
import {
    FKMetricGrid,
    FKLineChart,
    FKAreaChart,
    FKBandChart,
    FKAnnotatedChart,
    FKBarChart,
    FKWaterfall,
    FKHistogram,
    FKPartChart,
    FKHeatGrid,
    FKScatterChart,
    FKBulletChart,
    FKRangeChart,
    FKCandleChart,
    FKMultiPanel,
    FKProjectionChart,
    FKRadarChart,
    FKSankeyChart,
    FKTable,
    FKRankedList,
    FKTimeline,
} from '@finkit/ui';

import type { BlockSpec, BlockLoadState } from '@ui-gen/base-ui';

// ─── Skeleton ─────────────────────────────────────────────────────────────────

function Skeleton() {
    return (
        <div className="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-5 animate-pulse" style={{ minHeight: 160 }}>
            <div className="h-3 w-1/3 bg-slate-200 dark:bg-slate-700 rounded mb-4" />
            <div className="h-3 w-2/3 bg-slate-100 dark:bg-slate-800 rounded mb-2" />
            <div className="h-3 w-1/2 bg-slate-100 dark:bg-slate-800 rounded mb-2" />
            <div className="mt-5 h-20 bg-slate-100 dark:bg-slate-800 rounded-xl" />
        </div>
    );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

type D = Record<string, unknown>;

function arr<T = unknown>(v: unknown): T[] {
    return Array.isArray(v) ? (v as T[]) : [];
}

// ─── Renderers ────────────────────────────────────────────────────────────────

function renderMetricGrid(data: D, spec: BlockSpec) {
    const cards = arr(data.cards);
    return <FKMetricGrid cards={cards} title={spec.title} subtitle={spec.subtitle} />;
}

function renderLineChart(data: D, spec: BlockSpec) {
    return (
        <FKLineChart
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data)}
            series={arr(data.series)}
            xKey={(data.xKey as string) ?? 'date'}
            yFormat={data.yFormat as any}
            rangeSelector={data.rangeSelector ?? true}
            referenceLines={arr(data.referenceLines)}
            stats={arr(data.stats).length ? arr(data.stats) : undefined}
            {...(data.props as object ?? {})}
        />
    );
}

function renderAreaChart(data: D, spec: BlockSpec) {
    return (
        <FKAreaChart
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data)}
            series={arr(data.series)}
            xKey={(data.xKey as string) ?? 'date'}
            fillMode={(data.fillMode as string) ?? 'above'}
            rangeSelector={data.rangeSelector ?? true}
            {...(data.props as object ?? {})}
        />
    );
}

function renderBandChart(data: D, spec: BlockSpec) {
    return (
        <FKBandChart
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data)}
            series={arr(data.series)}
            xKey={(data.xKey as string) ?? 'date'}
            {...(data.props as object ?? {})}
        />
    );
}

function renderAnnotatedChart(data: D, spec: BlockSpec) {
    return (
        <FKAnnotatedChart
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data)}
            series={arr(data.series)}
            events={arr(data.events)}
            bands={arr(data.bands)}
            callouts={arr(data.callouts)}
            rangeSelector={data.rangeSelector ?? true}
            {...(data.props as object ?? {})}
        />
    );
}

function renderBarChart(data: D, spec: BlockSpec) {
    return (
        <FKBarChart
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data)}
            series={arr(data.series)}
            xKey={(data.xKey as string) ?? 'date'}
            mode={(data.mode as string) ?? 'grouped'}
            referenceLines={arr(data.referenceLines)}
            {...(data.props as object ?? {})}
        />
    );
}

function renderWaterfall(data: D, spec: BlockSpec) {
    return (
        <FKWaterfall
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data)}
            {...(data.props as object ?? {})}
        />
    );
}

function renderHistogram(data: D, spec: BlockSpec) {
    return (
        <FKHistogram
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data) as number[]}
            overlayNormal={data.overlayNormal as boolean}
            referenceLines={arr(data.referenceLines)}
            {...(data.props as object ?? {})}
        />
    );
}

function renderPartChart(data: D, spec: BlockSpec) {
    return (
        <FKPartChart
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data)}
            mode={(data.mode as string) ?? 'donut'}
            valueKey={(data.valueKey as string) ?? 'value'}
            labelKey={(data.labelKey as string) ?? 'label'}
            innerLabel={data.innerLabel as string}
            innerSub={data.innerSub as string}
            {...(data.props as object ?? {})}
        />
    );
}

function renderHeatGrid(data: D, spec: BlockSpec) {
    return (
        <FKHeatGrid
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data)}
            rowKey={(data.rowKey as string) ?? 'row'}
            colKey={(data.colKey as string) ?? 'col'}
            valueKey={(data.valueKey as string) ?? 'value'}
            colorScale={(data.colorScale as string) ?? 'diverging'}
            valueFormat={data.valueFormat as any}
            {...(data.props as object ?? {})}
        />
    );
}

function renderScatterChart(data: D, spec: BlockSpec) {
    return (
        <FKScatterChart
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data)}
            xKey={(data.xKey as string) ?? 'x'}
            yKey={(data.yKey as string) ?? 'y'}
            labelKey={data.labelKey as string}
            sizeKey={data.sizeKey as string}
            trendLine={data.trendLine as boolean}
            {...(data.props as object ?? {})}
        />
    );
}

function renderBulletChart(data: D, spec: BlockSpec) {
    return (
        <FKBulletChart
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data)}
            {...(data.props as object ?? {})}
        />
    );
}

function renderRangeChart(data: D, spec: BlockSpec) {
    return (
        <FKRangeChart
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data)}
            labelKey={(data.labelKey as string) ?? 'label'}
            minKey={(data.minKey as string) ?? 'min'}
            maxKey={(data.maxKey as string) ?? 'max'}
            valueKey={(data.valueKey as string) ?? 'value'}
            {...(data.props as object ?? {})}
        />
    );
}

function renderCandleChart(data: D, spec: BlockSpec) {
    return (
        <FKCandleChart
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data)}
            rangeSelector={data.rangeSelector ?? true}
            {...(data.props as object ?? {})}
        />
    );
}

function renderMultiPanel(data: D, spec: BlockSpec) {
    return (
        <FKMultiPanel
            title={spec.title}
            subtitle={spec.subtitle}
            panels={arr(data.panels)}
            xKey={(data.xKey as string) ?? 'date'}
            {...(data.props as object ?? {})}
        />
    );
}

function renderProjectionChart(data: D, spec: BlockSpec) {
    return (
        <FKProjectionChart
            title={spec.title}
            subtitle={spec.subtitle}
            historical={arr(data.historical)}
            projection={arr(data.projection)}
            scenarios={arr(data.scenarios)}
            splitDate={data.splitDate as string}
            {...(data.props as object ?? {})}
        />
    );
}

function renderRadarChart(data: D, spec: BlockSpec) {
    return (
        <FKRadarChart
            title={spec.title}
            subtitle={spec.subtitle}
            axes={arr(data.axes)}
            series={arr(data.series)}
            {...(data.props as object ?? {})}
        />
    );
}

function renderSankeyChart(data: D, spec: BlockSpec) {
    return (
        <FKSankeyChart
            title={spec.title}
            subtitle={spec.subtitle}
            nodes={arr(data.nodes)}
            flows={arr(data.flows)}
            {...(data.props as object ?? {})}
        />
    );
}

function renderTable(data: D, spec: BlockSpec) {
    const columns = arr(data.columns);
    const rows = arr(data.rows);
    // columns may arrive as string[] (names only) or as {key,label,...}[] — normalise
    const resolvedColumns = columns.map((c: any) =>
        typeof c === 'string' ? { key: c, label: c } : c
    );
    return (
        <FKTable
            title={spec.title}
            subtitle={spec.subtitle}
            columns={resolvedColumns}
            rows={rows}
            {...(data.props as object ?? {})}
        />
    );
}

function renderRankedList(data: D, spec: BlockSpec) {
    return (
        <FKRankedList
            title={spec.title}
            subtitle={spec.subtitle}
            data={arr(data.data)}
            labelKey={(data.labelKey as string) ?? 'label'}
            valueKey={(data.valueKey as string) ?? 'value'}
            {...(data.props as object ?? {})}
        />
    );
}

function renderTimeline(data: D, spec: BlockSpec) {
    return (
        <FKTimeline
            title={spec.title}
            subtitle={spec.subtitle}
            events={arr(data.events)}
            {...(data.props as object ?? {})}
        />
    );
}

// ─── Registry ─────────────────────────────────────────────────────────────────

type Renderer = (data: D, spec: BlockSpec) => React.ReactNode;

const FK_REGISTRY: Record<string, Renderer> = {
    FKMetricGrid:      renderMetricGrid,
    FKLineChart:       renderLineChart,
    FKAreaChart:       renderAreaChart,
    FKBandChart:       renderBandChart,
    FKAnnotatedChart:  renderAnnotatedChart,
    FKBarChart:        renderBarChart,
    FKWaterfall:       renderWaterfall,
    FKHistogram:       renderHistogram,
    FKPartChart:       renderPartChart,
    FKHeatGrid:        renderHeatGrid,
    FKScatterChart:    renderScatterChart,
    FKBulletChart:     renderBulletChart,
    FKRangeChart:      renderRangeChart,
    FKCandleChart:     renderCandleChart,
    FKMultiPanel:      renderMultiPanel,
    FKProjectionChart: renderProjectionChart,
    FKRadarChart:      renderRadarChart,
    FKSankeyChart:     renderSankeyChart,
    FKDataTable:       renderTable,   // alias used in system prompt
    FKTable:           renderTable,
    FKRankedList:      renderRankedList,
    FKTimeline:        renderTimeline,
};

// ─── FKBlockShell ─────────────────────────────────────────────────────────────

export interface FKBlockShellProps {
    spec: BlockSpec;
    loadState: BlockLoadState;
    data?: Record<string, unknown>;
    error?: string;
    index?: number;
}

export default function FKBlockShell({ spec, loadState, data, error, index = 0 }: FKBlockShellProps) {
    const delay = `${index * 60}ms`;

    if (loadState === 'idle') return null;

    if (loadState === 'loading') {
        return (
            <div style={{ animationDelay: delay }} className="animate-fadeIn">
                <Skeleton />
            </div>
        );
    }

    if (loadState === 'error' || error) {
        return (
            <div className="rounded-2xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950 p-5">
                <p className="text-sm font-medium text-red-700 dark:text-red-300 mb-1">{spec.title}</p>
                <p className="text-xs text-red-500 dark:text-red-400">{error ?? 'Failed to load data'}</p>
            </div>
        );
    }

    if ((loadState === 'loaded' || loadState === 'cached') && data) {
        const renderer = FK_REGISTRY[spec.blockId];
        if (!renderer) {
            return (
                <div className="rounded-2xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950 p-5">
                    <p className="text-sm text-amber-700 dark:text-amber-300">
                        Unknown block: <code>{spec.blockId}</code>
                    </p>
                </div>
            );
        }
        return (
            <div style={{ animationDelay: delay }} className="animate-fadeIn">
                {renderer(data, spec)}
            </div>
        );
    }

    return null;
}
