'use client';

import { useState, useMemo } from 'react';
import { RiSearchLine, RiFilterLine } from '@remixicon/react';

interface UsageRow {
    userId: string;
    email: string;
    displayName: string | null;
    appId: string;
    eventType: string;
    total: number;
    planName: string;
    limit: number | null;
    percentUsed: number | null;
}

const EVENT_LABELS: Record<string, string> = {
    ai_builds: 'AI Builds',
    saved_dashboards: 'Saved Dashboards',
    exports: 'Exports',
};

function UsageBar({ percent, limit }: { percent: number | null; limit: number | null }) {
    if (limit === null) {
        return <span className="text-xs font-medium text-indigo-500">Unlimited</span>;
    }
    const clamped = Math.min(percent ?? 0, 100);
    const color =
        clamped >= 100
            ? 'bg-red-500'
            : clamped >= 80
                ? 'bg-amber-400'
                : 'bg-indigo-500';
    return (
        <div className="flex items-center gap-2">
            <div className="h-1.5 w-24 shrink-0 overflow-hidden rounded-full bg-gray-100">
                <div
                    className={`h-full rounded-full transition-all ${color}`}
                    style={{ width: `${clamped}%` }}
                />
            </div>
            <span className="tabular-nums text-xs text-gray-500">
                {Math.round(percent ?? 0)}%
            </span>
        </div>
    );
}

export function AdminUsageTable({ rows }: { rows: UsageRow[] }) {
    const [search, setSearch] = useState('');
    const [appFilter, setAppFilter] = useState('all');
    const [eventFilter, setEventFilter] = useState('all');
    const [sortKey, setSortKey] = useState<'total' | 'percent'>('total');

    const apps = useMemo(
        () => ['all', ...Array.from(new Set(rows.map((r) => r.appId)))],
        [rows],
    );
    const events = useMemo(
        () => ['all', ...Array.from(new Set(rows.map((r) => r.eventType)))],
        [rows],
    );

    const filtered = useMemo(() => {
        const q = search.toLowerCase().trim();
        return rows
            .filter((r) => {
                if (appFilter !== 'all' && r.appId !== appFilter) return false;
                if (eventFilter !== 'all' && r.eventType !== eventFilter) return false;
                if (q) {
                    if (
                        !r.email.toLowerCase().includes(q) &&
                        !(r.displayName ?? '').toLowerCase().includes(q) &&
                        !r.userId.toLowerCase().includes(q)
                    ) {
                        return false;
                    }
                }
                return true;
            })
            .sort((a, b) => {
                if (sortKey === 'percent') {
                    return (b.percentUsed ?? Infinity) - (a.percentUsed ?? Infinity);
                }
                return b.total - a.total;
            });
    }, [rows, search, appFilter, eventFilter, sortKey]);

    return (
        <div className="space-y-4">
            {/* Filters */}
            <div className="flex flex-wrap items-center gap-3">
                <div className="relative min-w-[200px] max-w-sm flex-1">
                    <RiSearchLine className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search by email, name, or ID…"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full rounded-lg border border-gray-200 bg-white py-2 pl-9 pr-4 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                    />
                </div>

                <div className="flex items-center gap-2">
                    <RiFilterLine className="h-4 w-4 text-gray-400" />
                    <select
                        value={appFilter}
                        onChange={(e) => setAppFilter(e.target.value)}
                        className="rounded-lg border border-gray-200 bg-white py-2 pl-3 pr-8 text-sm text-gray-700 focus:outline-none"
                    >
                        {apps.map((a) => (
                            <option key={a} value={a}>
                                {a === 'all' ? 'All Apps' : a}
                            </option>
                        ))}
                    </select>

                    <select
                        value={eventFilter}
                        onChange={(e) => setEventFilter(e.target.value)}
                        className="rounded-lg border border-gray-200 bg-white py-2 pl-3 pr-8 text-sm text-gray-700 focus:outline-none"
                    >
                        {events.map((e) => (
                            <option key={e} value={e}>
                                {e === 'all' ? 'All Events' : EVENT_LABELS[e] ?? e}
                            </option>
                        ))}
                    </select>

                    <select
                        value={sortKey}
                        onChange={(e) =>
                            setSortKey(e.target.value as 'total' | 'percent')
                        }
                        className="rounded-lg border border-gray-200 bg-white py-2 pl-3 pr-8 text-sm text-gray-700 focus:outline-none"
                    >
                        <option value="total">Sort: Highest Usage</option>
                        <option value="percent">Sort: Quota % Used</option>
                    </select>
                </div>

                <span className="ml-auto text-xs text-gray-400">
                    {filtered.length.toLocaleString()} row{filtered.length !== 1 ? 's' : ''}
                </span>
            </div>

            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-100">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    User
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    App
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    Event
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    Plan
                                </th>
                                <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    Usage
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    Quota
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                            {filtered.length === 0 ? (
                                <tr>
                                    <td
                                        colSpan={6}
                                        className="py-12 text-center text-sm text-gray-400"
                                    >
                                        No usage data matches your filters.
                                    </td>
                                </tr>
                            ) : (
                                filtered.map((row, i) => (
                                    <tr
                                        key={`${row.userId}-${row.appId}-${row.eventType}-${i}`}
                                        className={`transition-colors hover:bg-gray-50 ${(row.percentUsed ?? 0) >= 100 ? 'bg-red-50/30' : ''
                                            }`}
                                    >
                                        <td className="px-4 py-3">
                                            <p className="max-w-[160px] truncate text-sm font-medium text-gray-900">
                                                {row.displayName ?? (
                                                    <span className="italic text-gray-400">
                                                        No name
                                                    </span>
                                                )}
                                            </p>
                                            <p className="max-w-[160px] truncate text-xs text-gray-400">
                                                {row.email}
                                            </p>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
                                                {row.appId}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-xs text-gray-600">
                                            {EVENT_LABELS[row.eventType] ?? row.eventType}
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="text-xs capitalize text-gray-500">
                                                {row.planName}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-right">
                                            <span className="text-sm font-semibold tabular-nums text-gray-900">
                                                {row.total.toLocaleString()}
                                            </span>
                                            {row.limit !== null && (
                                                <span className="ml-1 text-xs text-gray-400">
                                                    / {row.limit.toLocaleString()}
                                                </span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3">
                                            <UsageBar
                                                percent={row.percentUsed}
                                                limit={row.limit}
                                            />
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
