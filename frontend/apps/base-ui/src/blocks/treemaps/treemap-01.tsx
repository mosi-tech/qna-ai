'use client';

import React, { useState } from 'react';
import { Treemap, ResponsiveContainer } from 'recharts';
import { cx } from '../../lib/utils';
import { Card } from '../../tremor/components/Card';

// ─── Types ─────────────────────────────────────────────────────────────────────

export interface TreemapNode {
    name: string;
    /** Weight / AUM / notional — determines cell area */
    value: number;
    /** % daily change — drives fill color when colorMode='change' */
    change?: number;
    /** Optional subtitle shown in tooltip (e.g. sector name for leaf nodes) */
    group?: string;
    children?: TreemapNode[];
}

export interface Treemap01Props {
    data?: TreemapNode[];
    title?: string;
    description?: string;
    /**
     * 'change' — diverging red/green scale driven by `change` field (default)
     * 'value'  — monochrome blue scale driven by `value` field (useful when change is N/A)
     */
    colorMode?: 'change' | 'value';
    /** Max absolute % change at color scale endpoints. Default: 4 */
    changeRange?: number;
    /** Pixel height of the chart area. Default: 380 */
    height?: number;
    valueFormatter?: (v: number) => string;
    changeFormatter?: (v: number) => string;
    /** Label shown in the tooltip for the value row. Default: 'Value' */
    valueLabel?: string;
    /** Label shown in the tooltip for the change row. Default: 'Change' */
    changeLabel?: string;
    className?: string;
}

// ─── 5-stop diverging color scale ──────────────────────────────────────────────
// red-700 → red-300 → slate-300 → emerald-300 → emerald-700

const CHANGE_SCALE = [
    { stop: -1.0, r: 185, g: 28, b: 28 }, // red-700
    { stop: -0.4, r: 252, g: 165, b: 165 }, // red-300
    { stop: 0.0, r: 203, g: 213, b: 225 }, // slate-300
    { stop: 0.4, r: 110, g: 231, b: 183 }, // emerald-300
    { stop: 1.0, r: 4, g: 120, b: 87 }, // emerald-700
];

function changeToRgb(change: number, range: number): string {
    const normalized = Math.max(-1, Math.min(1, change / range));
    for (let i = 1; i < CHANGE_SCALE.length; i++) {
        const lo = CHANGE_SCALE[i - 1];
        const hi = CHANGE_SCALE[i];
        if (normalized <= hi.stop) {
            const t = (normalized - lo.stop) / (hi.stop - lo.stop);
            return `rgb(${Math.round(lo.r + (hi.r - lo.r) * t)},${Math.round(lo.g + (hi.g - lo.g) * t)},${Math.round(lo.b + (hi.b - lo.b) * t)})`;
        }
    }
    return 'rgb(4,120,87)';
}

function valueToRgb(value: number, max: number): string {
    // slate-700 → blue-600
    const t = Math.min(1, value / Math.max(1, max * 0.75));
    const r = Math.round(51 + (37 - 51) * t);
    const g = Math.round(65 + (99 - 65) * t);
    const b = Math.round(85 + (235 - 85) * t);
    return `rgb(${r},${g},${b})`;
}

function textColorForFill(change: number | undefined, range: number, colorMode: 'change' | 'value'): string {
    if (colorMode === 'value') return 'rgb(255,255,255)';
    if (change === undefined) return 'rgb(15,23,42)';
    return Math.abs(change) / range > 0.3 ? 'rgb(255,255,255)' : 'rgb(15,23,42)';
}

// ─── Cell content ──────────────────────────────────────────────────────────────

interface ContentProps {
    x: number;
    y: number;
    width: number;
    height: number;
    depth: number;
    name: string;
    value: number;
    change?: number;
    group?: string;
    colorMode: 'change' | 'value';
    changeRange: number;
    maxValue: number;
    valueFormatter: (v: number) => string;
    changeFormatter: (v: number) => string;
    valueLabel: string;
    changeLabel: string;
    onCellEnter: (node: { name: string; value: number; change?: number; group?: string; valueLabel?: string; changeLabel?: string }, x: number, y: number) => void;
    onCellLeave: () => void;
}

function CustomContent(props: ContentProps) {
    const {
        x, y, width, height, depth,
        name, value, change, group,
        colorMode, changeRange, maxValue,
        valueFormatter, changeFormatter,
        valueLabel, changeLabel,
        onCellEnter, onCellLeave,
    } = props;

    if (depth === 0) return null;

    // depth=1 with no change = hierarchy group node (sector/category wrapper)
    const isHierarchyGroup = depth === 1 && change === undefined;

    if (isHierarchyGroup) {
        // Group cell: slate outline + uppercase label in top-left corner
        return (
            <g>
                <rect
                    x={x + 1}
                    y={y + 1}
                    width={width - 2}
                    height={height - 2}
                    fill="rgba(15,23,42,0.05)"
                    stroke="rgb(71,85,105)"
                    strokeWidth={2}
                    rx={3}
                />
                {width > 50 && height > 22 && (
                    <text
                        x={x + 7}
                        y={y + 14}
                        fontSize={Math.min(11, width / 7)}
                        fontWeight={700}
                        fill="rgb(71,85,105)"
                    >
                        {name.toUpperCase()}
                    </text>
                )}
            </g>
        );
    }

    // Leaf cell
    const fill = colorMode === 'change'
        ? changeToRgb(change ?? 0, changeRange)
        : valueToRgb(value, maxValue);
    const textColor = textColorForFill(change, changeRange, colorMode);

    const tooNarrow = width < 34;
    const tooShort = height < 20;
    const showBothLines = width >= 46 && height >= 44;
    const showOneLine = !tooNarrow && !tooShort;

    const nameFS = Math.max(8, Math.min(13, width / 6, height / 4));
    const valueFS = Math.max(7, Math.min(10, width / 7));
    const shortName = name.length > 7 && width < 64 ? name.slice(0, 6) + '\u2026' : name;

    return (
        <g
            onMouseEnter={(e) => onCellEnter({ name, value, change, group, valueLabel, changeLabel }, e.clientX, e.clientY)}
            onMouseMove={(e) => onCellEnter({ name, value, change, group, valueLabel, changeLabel }, e.clientX, e.clientY)}
            onMouseLeave={onCellLeave}
            style={{ cursor: 'default' }}
        >
            <rect
                x={x + 1}
                y={y + 1}
                width={width - 2}
                height={height - 2}
                fill={fill}
                stroke="rgba(0,0,0,0.12)"
                strokeWidth={1}
                rx={2}
            />
            {showOneLine && (
                <text
                    x={x + width / 2}
                    y={y + height / 2 - (showBothLines ? nameFS * 0.7 : 0)}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize={nameFS}
                    fontWeight={700}
                    fill={textColor}
                    style={{ pointerEvents: 'none', userSelect: 'none' }}
                >
                    {shortName}
                </text>
            )}
            {showBothLines && (
                <text
                    x={x + width / 2}
                    y={y + height / 2 + nameFS * 0.9}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize={valueFS}
                    fontWeight={400}
                    fill={textColor}
                    style={{ opacity: 0.88, pointerEvents: 'none', userSelect: 'none' }}
                >
                    {valueFormatter(value)}
                    {change !== undefined ? `  ${changeFormatter(change)}` : ''}
                </text>
            )}
        </g>
    );
}

// ─── Floating tooltip ─────────────────────────────────────────────────────────

interface HoverState {
    name: string;
    value: number;
    change?: number;
    group?: string;
    valueLabel?: string;
    changeLabel?: string;
    x: number;
    y: number;
}

function FloatingTooltip({
    hover,
    valueFormatter,
    changeFormatter,
}: {
    hover: HoverState;
    valueFormatter: (v: number) => string;
    changeFormatter: (v: number) => string;
}) {
    const { change } = hover;
    const vLabel = hover.valueLabel ?? 'Value';
    const cLabel = hover.changeLabel ?? 'Change';
    const changeColor =
        change === undefined ? 'text-gray-400'
            : change >= 0 ? 'text-emerald-400'
                : 'text-red-400';

    const strength =
        change === undefined ? null
            : Math.abs(change) >= 3 ? (change >= 0 ? 'Strong move' : 'Steep decline')
                : Math.abs(change) >= 1 ? 'Moderate move'
                    : 'Small move';

    return (
        <div
            style={{ position: 'fixed', left: hover.x + 16, top: hover.y - 12, zIndex: 9999, pointerEvents: 'none' }}
            className="min-w-[160px] rounded-lg border border-slate-700 bg-slate-900 px-3 py-2.5 shadow-xl"
        >
            <p className="text-xs font-bold text-white">{hover.name}</p>
            {hover.group && (
                <p className="mt-0.5 text-[10px] uppercase tracking-wide text-slate-400">{hover.group}</p>
            )}
            <div className="mt-2 space-y-1">
                <div className="flex items-center justify-between gap-4">
                    <span className="text-[10px] uppercase tracking-wide text-slate-500">{vLabel}</span>
                    <span className="text-xs font-semibold text-slate-200">{valueFormatter(hover.value)}</span>
                </div>
                {change !== undefined && (
                    <div className="flex items-center justify-between gap-4">
                        <span className="text-[10px] uppercase tracking-wide text-slate-500">{cLabel}</span>
                        <span className={cx('text-xs font-semibold', changeColor)}>
                            {changeFormatter(change)}
                            {strength && <span className="ml-1.5 text-[10px] font-normal text-slate-400">{strength}</span>}
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
}

// ─── Component ────────────────────────────────────────────────────────────────

export function Treemap01({
    data = [],
    title,
    description,
    colorMode = 'change',
    changeRange = 4,
    height = 380,
    valueFormatter = (v) => String(v),
    changeFormatter = (v) => `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`,
    valueLabel = 'Value',
    changeLabel = 'Change',
    className,
}: Treemap01Props) {
    const [hover, setHover] = useState<HoverState | null>(null);

    function flatValues(nodes: TreemapNode[]): number[] {
        return nodes.flatMap((n) => (n.children ? flatValues(n.children) : [n.value]));
    }
    const maxValue = Math.max(...flatValues(data), 1);

    const onCellEnter = (
        node: { name: string; value: number; change?: number; group?: string; valueLabel?: string; changeLabel?: string },
        x: number,
        y: number,
    ) => setHover({ ...node, x, y });
    const onCellLeave = () => setHover(null);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const renderContent = (props: any) => (
        <CustomContent
            {...props}
            colorMode={colorMode}
            changeRange={changeRange}
            maxValue={maxValue}
            valueFormatter={valueFormatter}
            changeFormatter={changeFormatter}
            valueLabel={valueLabel}
            changeLabel={changeLabel}
            onCellEnter={onCellEnter}
            onCellLeave={onCellLeave}
        />
    );

    const gradStops = CHANGE_SCALE.map((s) => `rgb(${s.r},${s.g},${s.b})`).join(', ');

    return (
        <Card className={cx('overflow-hidden', className)}>
            {(title || description) && (
                <div className="mb-4">
                    {title && (
                        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-50">{title}</h3>
                    )}
                    {description && (
                        <p className="mt-0.5 text-sm text-gray-500 dark:text-gray-400">{description}</p>
                    )}
                </div>
            )}

            <ResponsiveContainer width="100%" height={height}>
                <Treemap
                    data={data}
                    dataKey="value"
                    content={renderContent as unknown as React.ReactElement}
                    isAnimationActive={false}
                />
            </ResponsiveContainer>

            {colorMode === 'change' && (
                <div className="mt-4 px-1">
                    <div
                        className="h-2.5 w-full rounded-full"
                        style={{ background: `linear-gradient(to right, ${gradStops})` }}
                    />
                    <div className="mt-1.5 flex justify-between text-[10px] text-gray-500 dark:text-gray-400">
                        <span>&#8722;{changeRange}%</span>
                        <span>Flat</span>
                        <span>+{changeRange}%</span>
                    </div>
                </div>
            )}
            {colorMode === 'value' && (
                <div className="mt-4 px-1">
                    <div
                        className="h-2.5 w-full rounded-full"
                        style={{ background: 'linear-gradient(to right, rgb(51,65,85), rgb(37,99,235))' }}
                    />
                    <div className="mt-1.5 flex justify-between text-[10px] text-gray-500 dark:text-gray-400">
                        <span>Small</span>
                        <span>Large</span>
                    </div>
                </div>
            )}

            {hover && (
                <FloatingTooltip
                    hover={hover}
                    valueFormatter={valueFormatter}
                    changeFormatter={changeFormatter}
                />
            )}
        </Card>
    );
}
