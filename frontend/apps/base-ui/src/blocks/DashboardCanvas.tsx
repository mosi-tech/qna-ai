'use client';

/**
 * DashboardCanvas.tsx — @ui-gen/base-ui
 *
 * Receives a DashboardSpec + per-block load states and renders the dashboard
 * progressively as each block's data resolves.
 *
 * Moved from apps/ai-builder/components/DashboardCanvas.tsx in Phase 1.
 */

import React from 'react';
import type { DashboardSpec, BlockState } from './types';
import BlockShell from './BlockShell';

interface DashboardCanvasProps {
    spec: DashboardSpec | null;
    blockStates: BlockState[];
    specLoading: boolean;
    specError?: string;
}

function EmptyCanvas() {
    return (
        <div className="flex flex-col items-center justify-center h-full text-center gap-4 px-8">
            <div className="text-6xl opacity-20 select-none">◫</div>
            <div>
                <p className="text-slate-400 dark:text-slate-500 text-base font-medium">Dashboard canvas</p>
                <p className="text-slate-400 dark:text-slate-600 text-sm mt-1">
                    Ask a question in the chat to generate your dashboard
                </p>
            </div>
        </div>
    );
}

function SpecLoadingState() {
    return (
        <div className="p-8">
            <div className="animate-pulse space-y-4">
                <div className="h-7 w-64 bg-slate-200 dark:bg-slate-700 rounded-lg" />
                <div className="h-4 w-96 bg-slate-200 dark:bg-slate-700 rounded" />
                <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="h-40 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700" />
                    ))}
                </div>
            </div>
        </div>
    );
}

function SpecErrorState({ error }: { error: string }) {
    return (
        <div className="flex items-center justify-center h-full p-8">
            <div className="rounded-xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950 p-6 max-w-md text-center">
                <div className="text-2xl mb-3">⚠</div>
                <p className="text-sm font-medium text-red-700 dark:text-red-300 mb-1">Failed to build dashboard</p>
                <p className="text-xs text-red-500 dark:text-red-400">{error}</p>
            </div>
        </div>
    );
}

function LoadProgress({ states }: { states: BlockState[] }) {
    const total = states.length;
    const done = states.filter((s) => s.loadState === 'loaded' || s.loadState === 'cached' || s.loadState === 'error').length;
    if (total === 0 || done === total) return null;
    const pct = Math.round((done / total) * 100);
    return (
        <div className="mb-6">
            <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1.5">
                <span>Loading data for {total - done} block{total - done !== 1 ? 's' : ''}…</span>
                <span>{pct}%</span>
            </div>
            <div className="h-1 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full transition-all duration-500" style={{ width: `${pct}%` }} />
            </div>
        </div>
    );
}

export default function DashboardCanvas({ spec, blockStates, specLoading, specError }: DashboardCanvasProps) {
    if (specLoading) return <SpecLoadingState />;
    if (specError) return <SpecErrorState error={specError} />;
    if (!spec) return <EmptyCanvas />;

    const isGrid = spec.layout === 'grid';

    return (
        <div className="p-6 overflow-y-auto h-full">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{spec.title}</h1>
                {spec.subtitle && <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{spec.subtitle}</p>}
                <div className="flex items-center gap-2 mt-3">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 text-xs font-medium text-blue-700 dark:text-blue-300">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                        {spec.blocks.length} components
                    </span>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-violet-50 dark:bg-violet-950 border border-violet-200 dark:border-violet-800 text-xs font-medium text-violet-700 dark:text-violet-300">
                        AI-generated
                    </span>
                </div>
            </div>

            <LoadProgress states={blockStates} />

            {isGrid ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    {blockStates.map((bs, i) => {
                        const isFullWidth =
                            bs.spec.category === 'kpi-cards' ||
                            bs.spec.category === 'spark-charts' ||
                            bs.spec.category === 'tables' ||
                            bs.spec.category === 'status-monitoring';
                        return (
                            <div key={bs.spec.blockId + i} className={isFullWidth ? 'md:col-span-2' : ''}>
                                <p className="text-xs font-medium text-slate-400 dark:text-slate-600 uppercase tracking-wide mb-2">
                                    {bs.spec.category} · {bs.spec.blockId}
                                </p>
                                <BlockShell spec={bs.spec} loadState={bs.loadState} data={bs.data} error={bs.error} index={i} />
                            </div>
                        );
                    })}
                </div>
            ) : (
                <div className="space-y-6">
                    {blockStates.map((bs, i) => (
                        <div key={bs.spec.blockId + i}>
                            <p className="text-xs font-medium text-slate-400 dark:text-slate-600 uppercase tracking-wide mb-2">
                                {bs.spec.category} · {bs.spec.blockId}
                            </p>
                            <BlockShell spec={bs.spec} loadState={bs.loadState} data={bs.data} error={bs.error} index={i} />
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
