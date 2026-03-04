import { NextRequest, NextResponse } from 'next/server';
import { requireUser } from '../supabase';
import { getEntitlements, getUsageSummary } from '../entitlements';
import type { DbInstance } from '../db/index';

interface SessionValidateDeps {
    db: DbInstance;
}

export function createSessionValidateHandler(deps: SessionValidateDeps) {
    return async function GET(req: NextRequest): Promise<NextResponse> {
        const { db } = deps;
        const { user } = await requireUser(req);

        if (!user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        const [entitlements, usageThisCycle] = await Promise.all([
            getEntitlements(user.id, db),
            getUsageSummary(user.id, db),
        ]);

        return NextResponse.json({
            userId: user.id,
            email: user.email,
            plan: {
                id: entitlements.planKey,
                name: entitlements.planName,
                status: entitlements.subscriptionStatus,
                periodEnd: entitlements.periodEnd,
                cancelAtPeriodEnd: entitlements.cancelAtPeriodEnd,
            },
            entitlements: {
                quotas: entitlements.quotas,
                features: entitlements.features,
            },
            usageThisCycle,
        });
    };
}

export async function GET(req: NextRequest): Promise<NextResponse> {
    const { createDb } = await import('../db/index');
    const schema = await import('../db/schema');
    const db = createDb(process.env.DATABASE_URL!, schema);
    return createSessionValidateHandler({ db })(req);
}
