// ─── Server Component (default export) ───────────────────────────────────────
import { createClient } from '@supabase/supabase-js';
import { createDb } from '../db/index';
import * as schema from '../db/schema';
import { usage_events, subscriptions, profiles } from '../db/schema';
import { inArray, sum, gte } from 'drizzle-orm';
import { PLAN_QUOTAS, type PlanKey } from '../entitlements';
import { AdminUsageTable } from './usage-table';

export const metadata = { title: 'Usage Inspector — Admin' };
export const dynamic = 'force-dynamic';

export default async function AdminUsagePage() {
    const now = new Date();
    const periodStart = new Date(now.getFullYear(), now.getMonth(), 1);

    const db = createDb(process.env.DATABASE_URL!, schema);

    const rawUsage = await db
        .select({
            user_id: usage_events.user_id,
            app_id: usage_events.app_id,
            event_type: usage_events.event_type,
            total: sum(usage_events.quantity).mapWith(Number),
        })
        .from(usage_events)
        .where(gte(usage_events.recorded_at, periodStart))
        .groupBy(usage_events.user_id, usage_events.app_id, usage_events.event_type);

    if (rawUsage.length === 0) {
        return (
            <div className="space-y-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Usage Inspector</h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Cross-user consumption data for the current billing period
                    </p>
                </div>
                <div className="rounded-xl border border-gray-200 bg-white p-12 text-center shadow-sm">
                    <p className="text-sm text-gray-400">No usage events recorded this period.</p>
                </div>
            </div>
        );
    }

    const userIds = Array.from(new Set(rawUsage.map((r) => r.user_id)));

    const [profileRows, subscriptionRows] = await Promise.all([
        db.select().from(profiles).where(inArray(profiles.id, userIds)),
        db
            .select({
                user_id: subscriptions.user_id,
                plan_name: subscriptions.plan_key,
            })
            .from(subscriptions)
            .where(inArray(subscriptions.user_id, userIds)),
    ]);

    const profileMap = new Map(profileRows.map((p) => [p.id, p]));
    const subMap = new Map(subscriptionRows.map((s) => [s.user_id, s]));

    const adminClient = createClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.SUPABASE_SERVICE_ROLE_KEY!,
        { auth: { autoRefreshToken: false, persistSession: false } },
    );

    const emailMap = new Map<string, string>();
    const { data: adminData } = await adminClient.auth.admin.listUsers({
        page: 1,
        perPage: 1000,
    });
    if (adminData) {
        for (const u of adminData.users) {
            if (u.email) emailMap.set(u.id, u.email);
        }
    }

    const rows = rawUsage.map((r) => {
        const profile = profileMap.get(r.user_id);
        const planName = (subMap.get(r.user_id)?.plan_name ?? 'free') as PlanKey;
        const validPlan: PlanKey = planName in PLAN_QUOTAS ? planName : 'free';
        const quotas = PLAN_QUOTAS[validPlan] as Record<string, number | null>;
        const limit = quotas[r.event_type] ?? null;
        const total = r.total ?? 0;
        const percentUsed =
            limit !== null && limit > 0
                ? (total / limit) * 100
                : limit === 0
                    ? 100
                    : null;

        return {
            userId: r.user_id,
            email: emailMap.get(r.user_id) ?? '(unknown)',
            displayName: profile?.display_name ?? null,
            appId: r.app_id,
            eventType: r.event_type,
            total,
            planName: validPlan,
            limit,
            percentUsed,
        };
    });

    const totalEvents = rows.reduce((acc, r) => acc + r.total, 0);
    const exceedingQuota = rows.filter((r) => (r.percentUsed ?? 0) >= 100).length;
    const nearQuota = rows.filter(
        (r) => (r.percentUsed ?? 0) >= 80 && (r.percentUsed ?? 0) < 100,
    ).length;

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Usage Inspector</h1>
                <p className="mt-1 text-sm text-gray-500">
                    Cross-user consumption for{' '}
                    {periodStart.toLocaleString(undefined, { month: 'long', year: 'numeric' })}
                </p>
            </div>

            {/* KPI row */}
            <div className="grid grid-cols-3 gap-4">
                {[
                    {
                        label: 'Total Events (period)',
                        value: totalEvents.toLocaleString(),
                        color: 'text-gray-900',
                    },
                    {
                        label: 'Near Quota (≥80%)',
                        value: nearQuota.toLocaleString(),
                        color: 'text-amber-600',
                    },
                    {
                        label: 'Exceeded Quota',
                        value: exceedingQuota.toLocaleString(),
                        color: 'text-red-600',
                    },
                ].map((kpi) => (
                    <div
                        key={kpi.label}
                        className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
                    >
                        <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                            {kpi.label}
                        </p>
                        <p className={`mt-2 text-3xl font-bold tabular-nums ${kpi.color}`}>
                            {kpi.value}
                        </p>
                    </div>
                ))}
            </div>

            <AdminUsageTable rows={rows} />
        </div>
    );
}