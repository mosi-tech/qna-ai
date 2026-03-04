'use client';

import { useState } from 'react';
import { RiCheckLine, RiLoaderLine, RiExternalLinkLine } from '@remixicon/react';
import type { Entitlements } from '../entitlements';
import type { StripePlan } from '../stripe';

const STATUS_BADGE: Record<string, { label: string; className: string }> = {
    active: { label: 'Active', className: 'bg-green-100 text-green-700' },
    trialing: { label: 'Trial', className: 'bg-indigo-100 text-indigo-700' },
    past_due: { label: 'Past due', className: 'bg-red-100 text-red-700' },
    cancelled: { label: 'Cancelled', className: 'bg-gray-100 text-gray-500' },
    paused: { label: 'Paused', className: 'bg-amber-100 text-amber-700' },
    none: { label: 'Free', className: 'bg-gray-100 text-gray-500' },
};

interface BillingClientProps {
    entitlements: Entitlements;
    plans: StripePlan[];
}

export function BillingClient({ entitlements, plans }: BillingClientProps) {
    const [billing, setBilling] = useState<'monthly' | 'annual'>('monthly');
    const [loadingPriceId, setLoadingPriceId] = useState<string | null>(null);
    const [portalLoading, setPortalLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const badge =
        STATUS_BADGE[entitlements.subscriptionStatus] ?? STATUS_BADGE.none;
    const isPaid = entitlements.planKey !== 'free';

    async function handleUpgrade(priceId: string) {
        setError(null);
        setLoadingPriceId(priceId);
        try {
            const res = await fetch('/api/billing/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ priceId, billing }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error ?? 'Checkout failed');
            window.location.href = data.url;
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Something went wrong');
            setLoadingPriceId(null);
        }
    }

    async function handlePortal() {
        setError(null);
        setPortalLoading(true);
        try {
            const res = await fetch('/api/billing/portal', { method: 'POST' });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error ?? 'Portal unavailable');
            window.location.href = data.url;
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Something went wrong');
            setPortalLoading(false);
        }
    }

    return (
        <div className="space-y-6">
            {/* Current plan summary */}
            <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                <div className="flex items-start justify-between gap-4">
                    <div>
                        <h2 className="text-lg font-semibold text-gray-900">Current plan</h2>
                        <div className="mt-1 flex items-center gap-2">
                            <span className="text-2xl font-bold text-gray-900 capitalize">
                                {entitlements.planName}
                            </span>
                            <span
                                className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${badge.className}`}
                            >
                                {badge.label}
                            </span>
                        </div>
                        {entitlements.periodEnd && (
                            <p className="mt-1 text-sm text-gray-500">
                                {entitlements.cancelAtPeriodEnd ? 'Cancels on' : 'Renews on'}{' '}
                                {entitlements.periodEnd.toLocaleDateString('en-US', {
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric',
                                })}
                            </p>
                        )}
                    </div>

                    {isPaid && (
                        <button
                            onClick={handlePortal}
                            disabled={portalLoading}
                            className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-60"
                        >
                            {portalLoading ? (
                                <RiLoaderLine className="h-4 w-4 animate-spin" />
                            ) : (
                                <RiExternalLinkLine className="h-4 w-4" />
                            )}
                            Manage billing
                        </button>
                    )}
                </div>

                {/* Quota summary */}
                <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
                    {(
                        [
                            ['AI builds', entitlements.quotas['ai_builds']],
                            ['Saved dashboards', entitlements.quotas['saved_dashboards']],
                            ['Exports', entitlements.quotas['exports']],
                        ] as [string, number | null][]
                    ).map(([label, limit]) => (
                        <div key={label} className="rounded-xl bg-gray-50 px-4 py-3">
                            <p className="text-xs font-medium text-gray-500">{label}</p>
                            <p className="mt-0.5 text-sm font-semibold text-gray-900">
                                {limit === null
                                    ? 'Unlimited'
                                    : limit === 0
                                        ? 'Not included'
                                        : `${limit} / mo`}
                            </p>
                        </div>
                    ))}
                </div>
            </section>

            {error && (
                <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </div>
            )}

            {/* Plan grid */}
            <section>
                <div className="mb-4 flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-gray-900">Plans</h2>
                    {/* Billing toggle */}
                    <div className="flex rounded-lg border border-gray-200 bg-gray-50 p-1 text-sm">
                        {(['monthly', 'annual'] as const).map((b) => (
                            <button
                                key={b}
                                onClick={() => setBilling(b)}
                                className={`rounded-md px-3 py-1.5 font-medium capitalize transition-colors ${billing === b
                                    ? 'bg-white text-gray-900 shadow-sm'
                                    : 'text-gray-500 hover:text-gray-700'
                                    }`}
                            >
                                {b === 'annual' ? 'Annual (–17%)' : 'Monthly'}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-3">
                    {plans.map((plan) => {
                        const isCurrent = entitlements.planKey === plan.planKey;
                        const priceEntry = plan.prices.find(
                            (p) => p.interval === (billing === 'annual' ? 'year' : 'month'),
                        );
                        const priceId = priceEntry?.priceId ?? null;
                        const price = priceEntry?.amount ?? null;
                        const isLoading = loadingPriceId === priceId;

                        return (
                            <div
                                key={plan.planKey}
                                className={`relative flex flex-col rounded-2xl border p-6 shadow-sm transition-shadow hover:shadow-md ${isCurrent
                                    ? 'border-indigo-500 bg-indigo-50'
                                    : plan.planKey === 'pro'
                                        ? 'border-indigo-300 bg-white'
                                        : 'border-gray-200 bg-white'
                                    }`}
                            >
                                {plan.planKey === 'pro' && !isCurrent && (
                                    <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-indigo-600 px-3 py-0.5 text-xs font-semibold text-white">
                                        Most popular
                                    </span>
                                )}

                                <div className="mb-4">
                                    <h3 className="text-base font-semibold text-gray-900">
                                        {plan.name}
                                    </h3>
                                    <p className="mt-0.5 text-xs text-gray-500">{plan.description}</p>
                                </div>

                                <div className="mb-4">
                                    {price === null ? (
                                        <p className="text-3xl font-bold text-gray-900">Free</p>
                                    ) : (
                                        <p className="text-3xl font-bold text-gray-900">
                                            ${(price / 100).toFixed(0)}
                                            <span className="text-sm font-normal text-gray-500">
                                                {billing === 'annual' ? '/yr' : '/mo'}
                                            </span>
                                        </p>
                                    )}
                                </div>

                                <ul className="mb-6 flex-1 space-y-2">
                                    {plan.features.map((f) => (
                                        <li key={f} className="flex items-start gap-2 text-sm text-gray-700">
                                            <RiCheckLine className="mt-0.5 h-4 w-4 flex-shrink-0 text-indigo-600" />
                                            {f}
                                        </li>
                                    ))}
                                </ul>

                                {isCurrent ? (
                                    <div className="rounded-lg border border-indigo-300 px-4 py-2.5 text-center text-sm font-medium text-indigo-700">
                                        Current plan
                                    </div>
                                ) : plan.planKey === 'free' ? (
                                    <div className="rounded-lg border border-gray-200 px-4 py-2.5 text-center text-sm text-gray-400">
                                        Downgrade via portal
                                    </div>
                                ) : (
                                    <button
                                        onClick={() => priceId && handleUpgrade(priceId)}
                                        disabled={!priceId || isLoading}
                                        className="flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
                                    >
                                        {isLoading && (
                                            <RiLoaderLine className="h-4 w-4 animate-spin" />
                                        )}
                                        {isLoading ? 'Redirecting…' : 'Upgrade'}
                                    </button>
                                )}
                            </div>
                        );
                    })}
                </div>
            </section>
        </div>
    );
}
