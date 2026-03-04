'use client';

import { useState, useMemo } from 'react';
import {
    RiSearchLine,
    RiFilterLine,
    RiMailLine,
    RiTimeLine,
} from '@remixicon/react';

interface UserRow {
    id: string;
    email: string;
    displayName: string | null;
    createdAt: string;
    planName: string;
    subscriptionStatus: string;
    isAdmin: boolean;
    deletedAt: string | null;
}

const STATUS_COLORS: Record<string, string> = {
    active: 'bg-green-50 text-green-700',
    trialing: 'bg-blue-50 text-blue-700',
    past_due: 'bg-amber-50 text-amber-700',
    cancelled: 'bg-gray-50 text-gray-500',
    paused: 'bg-gray-50 text-gray-500',
    none: 'bg-gray-50 text-gray-400',
};

const PLAN_COLORS: Record<string, string> = {
    free: 'bg-gray-100 text-gray-600',
    pro: 'bg-indigo-50 text-indigo-700',
    team: 'bg-purple-50 text-purple-700',
};

export function UsersTable({ users }: { users: UserRow[] }) {
    const [search, setSearch] = useState('');
    const [planFilter, setPlanFilter] = useState<string>('all');
    const [statusFilter, setStatusFilter] = useState<string>('all');
    const [showDeleted, setShowDeleted] = useState(false);

    const plans = useMemo(
        () => ['all', ...Array.from(new Set(users.map((u) => u.planName)))],
        [users],
    );
    const statuses = useMemo(
        () => ['all', ...Array.from(new Set(users.map((u) => u.subscriptionStatus)))],
        [users],
    );

    const filtered = useMemo(() => {
        const q = search.toLowerCase().trim();
        return users.filter((u) => {
            if (!showDeleted && u.deletedAt) return false;
            if (planFilter !== 'all' && u.planName !== planFilter) return false;
            if (statusFilter !== 'all' && u.subscriptionStatus !== statusFilter) return false;
            if (q) {
                if (
                    !u.email.toLowerCase().includes(q) &&
                    !(u.displayName ?? '').toLowerCase().includes(q) &&
                    !u.id.toLowerCase().includes(q)
                ) {
                    return false;
                }
            }
            return true;
        });
    }, [users, search, planFilter, statusFilter, showDeleted]);

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
                        value={planFilter}
                        onChange={(e) => setPlanFilter(e.target.value)}
                        className="rounded-lg border border-gray-200 bg-white py-2 pl-3 pr-8 text-sm text-gray-700 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                    >
                        {plans.map((p) => (
                            <option key={p} value={p}>
                                {p === 'all' ? 'All Plans' : p.charAt(0).toUpperCase() + p.slice(1)}
                            </option>
                        ))}
                    </select>

                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="rounded-lg border border-gray-200 bg-white py-2 pl-3 pr-8 text-sm text-gray-700 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                    >
                        {statuses.map((s) => (
                            <option key={s} value={s}>
                                {s === 'all'
                                    ? 'All Statuses'
                                    : s.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                            </option>
                        ))}
                    </select>
                </div>

                <label className="flex cursor-pointer select-none items-center gap-2 text-sm text-gray-600">
                    <input
                        type="checkbox"
                        checked={showDeleted}
                        onChange={(e) => setShowDeleted(e.target.checked)}
                        className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    />
                    Show deleted
                </label>

                <span className="ml-auto text-xs text-gray-400">
                    {filtered.length.toLocaleString()} user{filtered.length !== 1 ? 's' : ''}
                </span>
            </div>

            {/* Table */}
            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-100">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    User
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    Plan
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    Status
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    Joined
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    Flags
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                            {filtered.length === 0 ? (
                                <tr>
                                    <td
                                        colSpan={5}
                                        className="py-12 text-center text-sm text-gray-400"
                                    >
                                        No users match your filters.
                                    </td>
                                </tr>
                            ) : (
                                filtered.map((user) => (
                                    <tr
                                        key={user.id}
                                        className={`transition-colors hover:bg-gray-50 ${user.deletedAt ? 'opacity-50' : ''}`}
                                    >
                                        <td className="px-4 py-3">
                                            <div className="flex items-center gap-3">
                                                <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
                                                    {(user.displayName ?? user.email)?.[0]?.toUpperCase() ?? '?'}
                                                </div>
                                                <div className="min-w-0">
                                                    <p className="truncate text-sm font-medium text-gray-900">
                                                        {user.displayName ?? (
                                                            <span className="italic text-gray-400">
                                                                No name
                                                            </span>
                                                        )}
                                                    </p>
                                                    <p className="flex items-center gap-1 truncate text-xs text-gray-500">
                                                        <RiMailLine className="h-3 w-3 flex-shrink-0" />
                                                        {user.email}
                                                    </p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span
                                                className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${PLAN_COLORS[user.planName] ?? 'bg-gray-100 text-gray-600'}`}
                                            >
                                                {user.planName.charAt(0).toUpperCase() + user.planName.slice(1)}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span
                                                className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[user.subscriptionStatus] ?? 'bg-gray-100 text-gray-600'}`}
                                            >
                                                {user.subscriptionStatus === 'none'
                                                    ? 'No sub'
                                                    : user.subscriptionStatus
                                                        .replace('_', ' ')
                                                        .replace(/\b\w/g, (c) => c.toUpperCase())}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="flex items-center gap-1 text-xs text-gray-500">
                                                <RiTimeLine className="h-3.5 w-3.5 flex-shrink-0" />
                                                {new Date(user.createdAt).toLocaleDateString(undefined, {
                                                    year: 'numeric',
                                                    month: 'short',
                                                    day: 'numeric',
                                                })}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex items-center gap-1.5">
                                                {user.isAdmin && (
                                                    <span className="rounded-full bg-red-50 px-2 py-0.5 text-xs font-medium text-red-600">
                                                        Admin
                                                    </span>
                                                )}
                                                {user.deletedAt && (
                                                    <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-500">
                                                        Deleted
                                                    </span>
                                                )}
                                                {!user.isAdmin && !user.deletedAt && (
                                                    <span className="text-xs text-gray-300">—</span>
                                                )}
                                            </div>
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
