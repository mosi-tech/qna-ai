import { NextRequest, NextResponse } from 'next/server';
import { requireUser } from '../supabase';
import { getUsageSummary } from '../entitlements';
import type { DbInstance } from '../db/index';

interface UsageSummaryDeps {
    db: DbInstance;
}

export function createUsageSummaryHandler(deps: UsageSummaryDeps) {
    return async function GET(req: NextRequest): Promise<NextResponse> {
        const { db } = deps;
        const { user } = await requireUser(req);

        if (!user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        const { searchParams } = new URL(req.url);
        const appId = searchParams.get('appId') ?? undefined;

        const summary = await getUsageSummary(user.id, db, appId);
        return NextResponse.json(summary);
    };
}

export async function GET(req: NextRequest): Promise<NextResponse> {
    const { createDb } = await import('../db/index');
    const schema = await import('../db/schema');
    const db = createDb(process.env.DATABASE_URL!, schema);
    return createUsageSummaryHandler({ db })(req);
}
