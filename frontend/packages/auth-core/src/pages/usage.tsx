// ─── Server Component (default export) ───────────────────────────────────────
import { redirect } from 'next/navigation';
import { getAuthUser } from '../auth/server';
import { createDb } from '../db/index';
import * as schema from '../db/schema';
import { getEntitlements, getUsageSummary, PLAN_QUOTAS } from '../entitlements';
import { UsageClient } from './usage-client';
import type { UsageClientProps } from './usage-client';

export const metadata = { title: 'Usage' };

const QUOTA_LABELS: Record<string, string> = {
    ai_builds: 'AI Builds',
    saved_dashboards: 'Saved Dashboards',
    exports: 'Exports',
};

export default async function UsagePage() {
    const user = await getAuthUser();
    if (!user) redirect('/login');

    const db = createDb(process.env.DATABASE_URL!, schema);

    const [entitlements, summary] = await Promise.all([
        getEntitlements(user.id, db),
        getUsageSummary(user.id, db),
    ]);

    const totalUsed = Object.values(summary).reduce((acc, e) => acc + e.used, 0);
    const anyExceeded = Object.values(summary).some((e) => e.exceeded);

    const kpiMetrics: UsageClientProps['kpiMetrics'] = [
        {
            name: 'Current Plan',
            stat: entitlements.planName,
            change:
                entitlements.subscriptionStatus !== 'none'
                    ? entitlements.subscriptionStatus
                    : undefined,
            changeType:
                entitlements.subscriptionStatus === 'active' ||
                    entitlements.subscriptionStatus === 'trialing'
                    ? 'positive'
                    : entitlements.subscriptionStatus === 'past_due'
                        ? 'negative'
                        : 'neutral',
        },
        {
            name: 'Total Events This Cycle',
            stat: totalUsed,
            change: anyExceeded ? 'Quota exceeded' : undefined,
            changeType: anyExceeded ? 'negative' : 'neutral',
        },
        {
            name: 'Billing Period End',
            stat: entitlements.periodEnd
                ? new Intl.DateTimeFormat('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                }).format(entitlements.periodEnd)
                : 'N/A',
        },
    ];

    const planQuotaKeys = Object.keys(
        PLAN_QUOTAS[entitlements.planKey as keyof typeof PLAN_QUOTAS] ?? PLAN_QUOTAS.free,
    );
    const allKeys = Array.from(new Set([...planQuotaKeys, ...Object.keys(summary)]));

    const quotaRows = allKeys.map((key) => {
        const entry = summary[key] ?? {
            used: 0,
            limit: entitlements.quotas[key as keyof typeof entitlements.quotas] ?? null,
            exceeded: false,
            percentUsed: null,
        };
        return {
            key,
            label: QUOTA_LABELS[key] ?? key.replace(/_/g, ' '),
            ...entry,
        };
    });

    return (
        <UsageClient
            kpiMetrics={kpiMetrics}
            quotaRows={quotaRows}
            anyExceeded={anyExceeded}
            planKey={entitlements.planKey}
            planName={entitlements.planName}
        />
    );
}
