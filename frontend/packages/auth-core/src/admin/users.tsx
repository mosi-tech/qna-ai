// ─── Server Component (default export) ───────────────────────────────────────
import { createClient } from '@supabase/supabase-js';
import { createDb } from '../db/index';
import * as schema from '../db/schema';
import { profiles, subscriptions } from '../db/schema';
import { inArray } from 'drizzle-orm';
import { UsersTable } from './users-table';

export const metadata = { title: 'Users — Admin' };
export const dynamic = 'force-dynamic';

export default async function AdminUsersPage() {
    const adminClient = createClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.SUPABASE_SERVICE_ROLE_KEY!,
        { auth: { autoRefreshToken: false, persistSession: false } },
    );

    const { data: authData, error } = await adminClient.auth.admin.listUsers({
        page: 1,
        perPage: 1000,
    });

    if (error) {
        return (
            <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
                Failed to load users: {error.message}
            </div>
        );
    }

    const db = createDb(process.env.DATABASE_URL!, schema);
    const userIds = authData.users.map((u) => u.id);

    type ProfileRow = typeof profiles.$inferSelect;
    type SubRow = { user_id: string; status: string; plan_name: string };

    let profileRows: ProfileRow[] = [];
    let subscriptionRows: SubRow[] = [];

    if (userIds.length > 0) {
        const ids = userIds as [string, ...string[]];
        [profileRows, subscriptionRows] = await Promise.all([
            db.select().from(profiles).where(inArray(profiles.id, ids)),
            db
                .select({
                    user_id: subscriptions.user_id,
                    status: subscriptions.status,
                    plan_name: subscriptions.plan_key,
                })
                .from(subscriptions)
                .where(inArray(subscriptions.user_id, ids)),
        ]);
    }

    const profileMap = new Map<string, ProfileRow>(profileRows.map((p) => [p.id, p]));
    const subMap = new Map<string, SubRow>(subscriptionRows.map((s) => [s.user_id, s]));

    const users = authData.users.map((u) => {
        const profile = profileMap.get(u.id);
        const sub = subMap.get(u.id);
        return {
            id: u.id,
            email: u.email ?? '(no email)',
            displayName: profile?.display_name ?? null,
            createdAt: u.created_at,
            planName: sub?.plan_name ?? 'free',
            subscriptionStatus: sub?.status ?? 'none',
            isAdmin: u.user_metadata?.role === 'admin',
            deletedAt: profile?.deleted_at ? profile.deleted_at.toISOString() : null,
        };
    });

    const totalUsers = users.length;
    const activeSubscribers = users.filter((u) =>
        ['active', 'trialing'].includes(u.subscriptionStatus),
    ).length;
    const proUsers = users.filter((u) => u.planName === 'pro').length;
    const teamUsers = users.filter((u) => u.planName === 'team').length;

    const kpis = [
        { title: 'Total Users', metric: totalUsers.toLocaleString(), delta: '' },
        {
            title: 'Active Subscribers',
            metric: activeSubscribers.toLocaleString(),
            delta: `${Math.round((activeSubscribers / Math.max(totalUsers, 1)) * 100)}%`,
        },
        { title: 'Pro Plan', metric: proUsers.toLocaleString(), delta: '' },
        { title: 'Team Plan', metric: teamUsers.toLocaleString(), delta: '' },
    ];

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Users</h1>
                <p className="mt-1 text-sm text-gray-500">
                    All registered users, their plans, and subscription status
                </p>
            </div>

            {/* KPI summary row */}
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                {kpis.map((kpi) => (
                    <div
                        key={kpi.title}
                        className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
                    >
                        <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                            {kpi.title}
                        </p>
                        <p className="mt-2 text-3xl font-bold tabular-nums text-gray-900">
                            {kpi.metric}
                        </p>
                        {kpi.delta && (
                            <p className="mt-1 text-xs font-medium text-indigo-600">{kpi.delta}</p>
                        )}
                    </div>
                ))}
            </div>

            <UsersTable users={users} />
        </div>
    );
}