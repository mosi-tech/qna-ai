'use client';

import React, { useState } from 'react';
import { cx } from '../../lib/utils';
import { Card } from '../../tremor/components/Card';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface HeatmapPeriod {
    label: string;
    matrix: number[][];
    description?: string;
}

export interface Heatmap01Props {
    /** Asset/factor names — array length N drives an N×N grid */
    labels: string[];
    /** N×N correlation matrix — values in [-1, 1]. Ignored when `periods` is provided. */
    matrix?: number[][];
    /** Optional multi-period matrices with selector buttons (e.g. 1M / 3M / 6M / 1Y) */
    periods?: HeatmapPeriod[];
    title?: string;
    description?: string;
    /** Display numeric value inside each cell. Default: true */
    showValues?: boolean;
    /** Decimal places shown in cells. Default: 2 */
    decimals?: number;
    /** Render full matrix, upper triangle only, or lower triangle only. Default: 'full' */
    triangle?: 'full' | 'upper' | 'lower';
    /** Dim cells with |r| below this threshold (e.g. 0.2 for low-significance mask). */
    maskBelow?: number;
    className?: string;
}

// ─── 5-stop diverging color scale  red-700 → red-300 → slate-50 → blue-300 → blue-700 ─────

const SCALE = [
    { stop: -1.0, r: 185, g: 28, b: 28 }, // red-700
    { stop: -0.4, r: 252, g: 165, b: 165 }, // red-300
    { stop: 0.0, r: 248, g: 250, b: 252 }, // slate-50
    { stop: 0.4, r: 147, g: 197, b: 253 }, // blue-300
    { stop: 1.0, r: 29, g: 78, b: 216 }, // blue-700
];

function corrToRgb(v: number): string {
    const c = Math.max(-1, Math.min(1, v));
    for (let i = 1; i < SCALE.length; i++) {
        const lo = SCALE[i - 1];
        const hi = SCALE[i];
        if (c <= hi.stop) {
            const t = (c - lo.stop) / (hi.stop - lo.stop);
            return `rgb(${Math.round(lo.r + (hi.r - lo.r) * t)},${Math.round(lo.g + (hi.g - lo.g) * t)},${Math.round(lo.b + (hi.b - lo.b) * t)})`;
        }
    }
    const last = SCALE[SCALE.length - 1];
    return `rgb(${last.r},${last.g},${last.b})`;
}

function textColorForBg(v: number): string {
    return Math.abs(v) >= 0.48 ? 'rgb(255,255,255)' : 'rgb(15,23,42)'; // white vs slate-900
}

// ─── Component ────────────────────────────────────────────────────────────────

export function Heatmap01({
    labels,
    matrix: matrixProp,
    periods,
    title,
    description,
    showValues = true,
    decimals = 2,
    triangle = 'full',
    maskBelow,
    className,
}: Heatmap01Props) {
    const [activePeriod, setActivePeriod] = useState(0);
    const [hoverCell, setHoverCell] = useState<{ i: number; j: number; x: number; y: number } | null>(null);

    const activeMatrix = periods ? periods[activePeriod].matrix : (matrixProp ?? []);
    const activeDesc = periods ? (periods[activePeriod].description ?? description) : description;
    const n = labels.length;

    const isVisible = (i: number, j: number) => {
        if (triangle === 'upper') return j >= i;
        if (triangle === 'lower') return i >= j;
        return true;
    };

    const cellValue = (i: number, j: number) => i === j ? 1 : (activeMatrix[i]?.[j] ?? 0);

    // Adaptive cell size
    const CELL = n > 10 ? 34 : n > 7 ? 44 : 52;

    return (
        <Card className={cx('overflow-auto', className)}>
            {/* ── Header ── */}
            <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
                <div>
                    {title && (
                        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-50">{title}</h3>
                    )}
                    {activeDesc && (
                        <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{activeDesc}</p>
                    )}
                </div>
                {periods && periods.length > 1 && (
                    <div className="flex shrink-0 gap-1">
                        {periods.map((p, idx) => (
                            <button
                                key={p.label}
                                onClick={() => setActivePeriod(idx)}
                                className={cx(
                                    'rounded px-2.5 py-1 text-xs font-medium transition-colors',
                                    idx === activePeriod
                                        ? 'bg-blue-600 text-white shadow-sm'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700',
                                )}
                            >
                                {p.label}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* ── Grid ── */}
            <div
                className="inline-grid gap-[2px]"
                style={{ gridTemplateColumns: `4.5rem repeat(${n}, ${CELL}px)` }}
            >
                {/* Corner */}
                <div />

                {/* Column headers */}
                {labels.map((label, j) => (
                    <div
                        key={label}
                        className={cx(
                            'flex items-end justify-center pb-1 transition-opacity duration-100',
                            hoverCell && hoverCell.j !== j ? 'opacity-35' : 'opacity-100',
                        )}
                        style={{ height: CELL }}
                    >
                        <span
                            className="inline-block text-[11px] font-semibold tracking-tight text-gray-700 dark:text-gray-300"
                            style={{
                                writingMode: 'vertical-rl',
                                transform: 'rotate(180deg)',
                                whiteSpace: 'nowrap',
                                maxHeight: 88,
                            }}
                        >
                            {label}
                        </span>
                    </div>
                ))}

                {/* Rows */}
                {labels.map((rowLabel, i) => (
                    <React.Fragment key={rowLabel}>
                        {/* Row label */}
                        <div
                            className={cx(
                                'flex items-center justify-end pr-2 text-[11px] font-semibold tracking-tight text-gray-700 dark:text-gray-300 transition-opacity duration-100',
                                hoverCell && hoverCell.i !== i ? 'opacity-35' : 'opacity-100',
                            )}
                        >
                            {rowLabel}
                        </div>

                        {/* Cells */}
                        {labels.map((_, j) => {
                            const v = cellValue(i, j);
                            const visible = isVisible(i, j);
                            const isDiag = i === j;
                            const isMasked = !isDiag && maskBelow !== undefined && Math.abs(v) < maskBelow;
                            const isHovered = hoverCell?.i === i && hoverCell?.j === j;
                            const isInLine = hoverCell !== null && (hoverCell.i === i || hoverCell.j === j);

                            if (!visible) return <div key={j} style={{ width: CELL, height: CELL }} />;

                            return (
                                <div
                                    key={j}
                                    onMouseEnter={(e) => setHoverCell({ i, j, x: e.clientX, y: e.clientY })}
                                    onMouseMove={(e) => setHoverCell((prev) => prev ? { ...prev, x: e.clientX, y: e.clientY } : null)}
                                    onMouseLeave={() => setHoverCell(null)}
                                    className={cx(
                                        'relative flex items-center justify-center rounded transition-all duration-100 cursor-default select-none',
                                        isHovered && 'z-10 scale-[1.18] ring-2 ring-gray-900 ring-offset-1 dark:ring-white shadow-md',
                                        !isHovered && isInLine && 'ring-1 ring-gray-400 dark:ring-gray-500',
                                        !isInLine && hoverCell !== null && 'opacity-40',
                                        isMasked && 'opacity-25',
                                    )}
                                    style={{
                                        width: CELL,
                                        height: CELL,
                                        backgroundColor: isDiag ? 'rgb(30,41,59)' : corrToRgb(v),
                                    }}
                                >
                                    {showValues && (
                                        <span
                                            className="text-[10px] font-semibold leading-none"
                                            style={{ color: isDiag ? 'rgb(148,163,184)' : textColorForBg(v) }}
                                        >
                                            {isDiag ? '—' : (isMasked ? '' : v.toFixed(decimals))}
                                        </span>
                                    )}
                                </div>
                            );
                        })}
                    </React.Fragment>
                ))}
            </div>

            {/* ── Gradient legend bar ── */}
            <div className="mt-5 flex items-center gap-3">
                <span className="shrink-0 text-[11px] font-medium tabular-nums text-gray-500 dark:text-gray-400">
                    −1.0
                </span>
                <div
                    className="h-2.5 grow rounded-full"
                    style={{
                        background: `linear-gradient(to right, ${corrToRgb(-1)}, ${corrToRgb(-0.5)}, ${corrToRgb(0)}, ${corrToRgb(0.5)}, ${corrToRgb(1)})`,
                    }}
                />
                <span className="shrink-0 text-[11px] font-medium tabular-nums text-gray-500 dark:text-gray-400">
                    +1.0
                </span>
            </div>
            <div className="mt-1.5 flex justify-between px-8 text-[10px] text-gray-400 dark:text-gray-500">
                <span>Strong negative</span>
                <span>Uncorrelated</span>
                <span>Strong positive</span>
            </div>

            {/* ── Floating tooltip ── */}
            {hoverCell !== null && hoverCell.i !== hoverCell.j && (() => {
                const { i, j, x, y } = hoverCell;
                const v = cellValue(i, j);
                const accentColor = corrToRgb(Math.sign(v) * Math.min(Math.abs(v) + 0.3, 1));
                const strength = Math.abs(v) >= 0.7 ? 'strong' : Math.abs(v) >= 0.4 ? 'moderate' : 'weak';
                const direction = v < 0 ? 'negative' : 'positive';
                const isMasked = maskBelow !== undefined && Math.abs(v) < maskBelow;
                return (
                    <div
                        className="pointer-events-none fixed z-50 min-w-[160px] rounded-lg border border-gray-200 bg-white px-3 py-2.5 shadow-xl dark:border-gray-700 dark:bg-gray-900"
                        style={{ left: x + 14, top: y - 64 }}
                    >
                        <div className="mb-1.5 flex items-center gap-1.5">
                            <span
                                className="inline-block h-2.5 w-2.5 rounded-sm flex-shrink-0"
                                style={{ backgroundColor: corrToRgb(v) }}
                            />
                            <span className="text-[11px] font-semibold text-gray-800 dark:text-gray-200">
                                {labels[i]}
                            </span>
                            <span className="text-[11px] text-gray-400">×</span>
                            <span className="text-[11px] font-semibold text-gray-800 dark:text-gray-200">
                                {labels[j]}
                            </span>
                        </div>
                        <div className="flex items-baseline gap-2">
                            <span
                                className="text-base font-bold tabular-nums leading-none"
                                style={{ color: accentColor }}
                            >
                                {v.toFixed(decimals)}
                            </span>
                            <span className="text-[10px] text-gray-500 dark:text-gray-400">
                                {strength} {direction}
                            </span>
                        </div>
                        {isMasked && (
                            <div className="mt-1 text-[10px] text-amber-500">below significance threshold</div>
                        )}
                    </div>
                );
            })()}
        </Card>
    );
}
