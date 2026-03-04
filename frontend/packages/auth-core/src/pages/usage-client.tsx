'use client';

import type { MetricItem } from '@ui-gen/base-ui';
import { KpiCard01 } from '@ui-gen/base-ui';

function ProgressBar({ percent, exceeded }: { percent: number; exceeded: boolean }) {
    const clamped = Math.min(percent, 100);
    const color = exceeded
        ? 'bg-red-500'
        : clamped >= 80
            ? 'bg-amber-400'
            : 'bg-indigo-500';

    return (
        <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
            <div
                className={`h-full rounded-full transition-all ${color}`}
                style={{ width: `${clamped}%` }}
            />
        </div>
    );
}

interface QuotaEntry {
    used: number;
    limit: number | null;
    exceeded: boolean;
    percentUsed: number | null;
}

export interface UsageClientProps {
    kpiMetrics: MetricItem[];
    quotaRows: Array<{ key: string; label: string } & QuotaEntry>;
    anyExceeded: boolean;
    planKey: string;
    planName: string;
}

export function UsageClient({
    kpiMetrics,
    quotaRows,
    anyExceeded,
    planKey,
    planName,
}: UsageClientProps) {
    return (
        <div className="animate-fadeIn space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Usage</h1>
                <p className="mt-1 text-sm text-gray-500">
                    Track your current billing-cycle consumption against your plan quotas
                </p>
            </div>

            {/* Plan summary KPIs */}
            <KpiCard01 metrics={kpiMetrics} cols={3} />

            {/* Quota meters */}
            <div>
                <h2 className="mb-4 text-base font-semibold text-gray-800">Quota breakdown</h2>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {quotaRows.map(({ key, label, used, limit, exceeded, percentUsed }) => {
                        const isUnlimited = limit === null;
                        const displayPct = percentUsed !== null ? Math.round(percentUsed) : null;
                        return (
                            <div key={key} className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
                                <div className="mb-3 flex items-start justify-between gap-3">
                                    <h3 className="text-sm font-medium text-gray-700">{label}</h3>
                                    {isUnlimited ? (
                                        <span className="shrink-0 rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-600">
                                            Unlimited
                                        </span>
                                    ) : exceeded ? (
                                        <span className="shrink-0 rounded-full bg-red-50 px-2 py-0.5 text-xs font-medium text-red-600">
                                            Quota exceeded
                                        </span>
                                    ) : displayPct !== null && displayPct >= 80 ? (
                                        <span className="shrink-0 rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-600">
                                            {displayPct}% used
                                        </span>
                                    ) : null}
                                </div>

                                <div className="mb-2 flex items-baseline gap-1">
                                    <span className="text-2xl font-bold tabular-nums text-gray-900">
                                        {used.toLocaleString()}
                                    </span>
                                    {!isUnlimited && (
                                        <span className="text-sm text-gray-400">
                                            / {limit!.toLocaleString()}
                                        </span>
                                    )}
                                </div>

                                {!isUnlimited && limit! > 0 ? (
                                    <ProgressBar percent={percentUsed ?? 0} exceeded={exceeded} />
                                ) : isUnlimited ? (
                                    <div className="h-2 w-full rounded-full bg-indigo-50" />
                                ) : (
                                    <div className="h-2 w-full rounded-full bg-gray-100" />
                                )}

                                {!isUnlimited && limit! > 0 && (
                                    <p className="mt-1.5 text-xs text-gray-400">
                                        {Math.max(0, limit! - used).toLocaleString()} remaining this cycle
                                    </p>
                                )}
                                {!isUnlimited && limit === 0 && (
                                    <p className="mt-1.5 text-xs text-gray-400">
                                        Not available on your current plan
                                    </p>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {anyExceeded && planKey !== 'team' && (
                <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4">
                    <p className="text-sm font-medium text-red-700">
                        You&apos;ve exceeded one or more quotas on your{' '}
                        <span className="font-semibold capitalize">{planName}</span> plan.{' '}
                        <a href="/billing" className="underline hover:text-red-900">
                            Upgrade your plan
                        </a>{' '}
                        to continue working without interruption.
                    </p>
                </div>
            )}
        </div>
    );
}
