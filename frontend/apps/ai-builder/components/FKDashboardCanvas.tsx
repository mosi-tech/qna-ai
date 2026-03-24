'use client';

/**
 * FKDashboardCanvas.tsx
 *
 * Layout engine for finkit dashboards. Mirrors the row-based layout logic
 * of base-ui's DashboardCanvas but uses FKBlockShell (finkit renderers)
 * instead of the Tremor-based BlockShell.
 */

import React from 'react';
import type { DashboardSpec, BlockState, RowWidth } from '@ui-gen/base-ui';
import FKBlockShell from './FKBlockShell';

// ─── Width → Tailwind col-span ────────────────────────────────────────────────

function widthToColSpan(width: RowWidth): string {
    const map: Record<RowWidth, string> = {
        full: 'col-span-12',
        '3/4': 'col-span-9',
        '2/3': 'col-span-8',
        '1/2': 'col-span-6',
        '1/3': 'col-span-4',
        '1/4': 'col-span-3',
    };
    return map[width] ?? 'col-span-12';
}

// ─── State UI ─────────────────────────────────────────────────────────────────

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
                        <div key={i} className="h-40 bg-slate-100 dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700" />
                    ))}
                </div>
            </div>
        </div>
    );
}

function SpecErrorState({ error }: { error: string }) {
    return (
        <div className="flex items-center justify-center h-full p-8">
            <div className="rounded-2xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950 p-6 max-w-md text-center">
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
                <span>Loading {total - done} block{total - done !== 1 ? 's' : ''}…</span>
                <span>{pct}%</span>
            </div>
            <div className="h-1 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 rounded-full transition-all duration-500" style={{ width: `${pct}%` }} />
            </div>
        </div>
    );
}

// ─── FKDashboardCanvas ────────────────────────────────────────────────────────

interface FKDashboardCanvasProps {
    spec: DashboardSpec | null;
    blockStates: BlockState[];
    specLoading: boolean;
    specError?: string;
}

export default function FKDashboardCanvas({ spec, blockStates, specLoading, specError }: FKDashboardCanvasProps) {
    if (specLoading) return <SpecLoadingState />;
    if (specError)   return <SpecErrorState error={specError} />;
    if (!spec)       return <EmptyCanvas />;

    const hasRows = spec.rows && spec.rows.length > 0;

    return (
        <div className="p-6 overflow-y-auto h-full">
            {/* Dashboard header */}
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{spec.title}</h1>
                {spec.subtitle && (
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{spec.subtitle}</p>
                )}
                <div className="flex items-center gap-2 mt-3">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950 border border-indigo-200 dark:border-indigo-800 text-xs font-medium text-indigo-700 dark:text-indigo-300">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                        {spec.blocks.length} components
                    </span>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-violet-50 dark:bg-violet-950 border border-violet-200 dark:border-violet-800 text-xs font-medium text-violet-700 dark:text-violet-300">
                        FINKIT
                    </span>
                </div>
            </div>

            <LoadProgress states={blockStates} />

            {hasRows ? (
                // Row-based layout (new UI Planner output)
                <div className="space-y-5 max-w-6xl">
                    {spec.rows!.map((row, rowIdx) => (
                        <div key={rowIdx} className="grid grid-cols-12 gap-5">
                            {row.columns.map((col) => {
                                const blockState = blockStates.find((bs) => bs.spec.blockId === col.blockId);
                                if (!blockState) return null;
                                return (
                                    <div key={col.blockId} className={widthToColSpan(col.width)}>
                                        <FKBlockShell
                                            spec={blockState.spec}
                                            loadState={blockState.loadState}
                                            data={blockState.data}
                                            error={blockState.error}
                                            index={blockStates.indexOf(blockState)}
                                        />
                                    </div>
                                );
                            })}
                        </div>
                    ))}
                </div>
            ) : (
                // Fallback: single-column
                <div className="space-y-5 max-w-6xl">
                    {blockStates.map((bs, i) => (
                        <FKBlockShell
                            key={bs.spec.blockId + i}
                            spec={bs.spec}
                            loadState={bs.loadState}
                            data={bs.data}
                            error={bs.error}
                            index={i}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
