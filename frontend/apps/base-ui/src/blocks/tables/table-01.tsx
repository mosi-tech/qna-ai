'use client';

import React from 'react';
import { cx } from '../../lib/utils';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeaderCell,
    TableRow,
} from '../../tremor/components/Table';

// ─── Generic column definition ────────────────────────────────────────────────

export interface TableColumn<T> {
    /** Data key to read from the row object */
    key: keyof T & string;
    /** Column header label */
    label: string;
    /** Horizontal alignment (default: 'left') */
    align?: 'left' | 'right' | 'center';
    /** Optional custom cell renderer — receives the cell value and full row */
    render?: (value: T[keyof T & string], row: T) => React.ReactNode;
}

export interface Table01Props<T extends Record<string, unknown>> {
    data?: T[];
    columns?: TableColumn<T>[];
    /** Derive a stable React key from a row; defaults to row index */
    getRowKey?: (row: T, index: number) => string;
    className?: string;
}

// ─── Status badge helper (re-usable across domains) ──────────────────────────

export type StatusVariants = Record<string, string>;

/**
 * Default status colour map — extend or override for your domain.
 * Keys are lowercased for case-insensitive matching.
 */
export const defaultStatusVariants: StatusVariants = {
    // generic operational
    live: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-200',
    active: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-200',
    inactive: 'bg-gray-100 text-gray-700 dark:bg-gray-900 dark:text-gray-200',
    downtime: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200',
    // finance / trading
    executed: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-200',
    filled: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-200',
    settled: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200',
    pending: 'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-200',
    open: 'bg-sky-100 text-sky-700 dark:bg-sky-900 dark:text-sky-200',
    closed: 'bg-gray-100 text-gray-700 dark:bg-gray-900 dark:text-gray-200',
    cancelled: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200',
    rejected: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200',
    expired: 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-200',
    // risk
    low: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-200',
    medium: 'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-200',
    high: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200',
};

/** Renders a status value as a coloured badge. Pass custom `variants` to override colours. */
export const statusBadge = (
    value: string,
    variants: StatusVariants = defaultStatusVariants,
): React.ReactNode => {
    const cls =
        variants[value.toLowerCase()] ??
        'bg-gray-100 text-gray-700 dark:bg-gray-900 dark:text-gray-200';
    return (
        <span className={`inline-block rounded-full px-2 py-1 text-xs font-medium ${cls}`}>
            {value}
        </span>
    );
};

// ─── Component ────────────────────────────────────────────────────────────────

const alignClass = (align?: 'left' | 'right' | 'center'): string => {
    if (align === 'right') return 'text-right';
    if (align === 'center') return 'text-center';
    return 'text-left';
};

/**
 * Table01: Generic data table with configurable columns and optional cell renderers.
 * Accepts any row shape — suitable for workspace monitoring, portfolio holdings,
 * trade blotters, order books, risk summaries, and more.
 *
 * @example
 * // Finance usage
 * <Table01
 *   data={positions}
 *   columns={[
 *     { key: 'ticker', label: 'Ticker' },
 *     { key: 'status', label: 'Status', render: (v) => statusBadge(String(v)) },
 *     { key: 'pnl', label: 'P&L', align: 'right' },
 *   ]}
 *   getRowKey={(row) => row.ticker}
 * />
 */
export function Table01<T extends Record<string, unknown>>({
    data = [],
    columns = [],
    getRowKey = (_row, index) => String(index),
    className = '',
}: Table01Props<T>) {
    return (
        <div className={cx('obfuscate', className)}>
            <Table>
                <TableHead>
                    <TableRow>
                        {columns.map((col) => (
                            <TableHeaderCell key={col.key} className={alignClass(col.align)}>
                                {col.label}
                            </TableHeaderCell>
                        ))}
                    </TableRow>
                </TableHead>
                <TableBody>
                    {data.map((row, index) => (
                        <TableRow key={getRowKey(row, index)}>
                            {columns.map((col, colIndex) => (
                                <TableCell
                                    key={col.key}
                                    className={[
                                        colIndex === 0 ? 'font-medium' : '',
                                        alignClass(col.align),
                                    ]
                                        .filter(Boolean)
                                        .join(' ')}
                                >
                                    {col.render
                                        ? col.render(row[col.key], row)
                                        : String(row[col.key] ?? '')}
                                </TableCell>
                            ))}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}
