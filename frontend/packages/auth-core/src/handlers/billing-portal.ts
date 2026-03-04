import { NextRequest, NextResponse } from 'next/server';
import { requireUser } from '../supabase';
import { stripe } from '../stripe';
import { subscriptions } from '../db/schema';
import { eq } from 'drizzle-orm';
import type { DbInstance } from '../db/index';

interface BillingPortalDeps {
    db: DbInstance;
    appUrl: string;
}

export function createBillingPortalHandler(deps: BillingPortalDeps) {
    return async function POST(req: NextRequest): Promise<NextResponse> {
        const { db, appUrl } = deps;
        const { user } = await requireUser(req);

        if (!user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        const rows = await db
            .select()
            .from(subscriptions)
            .where(eq(subscriptions.user_id, user.id))
            .limit(1);
        const sub = rows[0] ?? null;

        if (!sub?.stripe_customer_id) {
            return NextResponse.json(
                { error: 'No active subscription found' },
                { status: 404 },
            );
        }

        const session = await stripe.billingPortal.sessions.create({
            customer: sub.stripe_customer_id,
            return_url: `${appUrl}/billing`,
        });

        return NextResponse.json({ url: session.url });
    };
}

export async function POST(req: NextRequest): Promise<NextResponse> {
    const { createDb } = await import('../db/index');
    const schema = await import('../db/schema');
    const db = createDb(process.env.DATABASE_URL!, schema);
    return createBillingPortalHandler({
        db,
        appUrl: process.env.NEXT_PUBLIC_APP_URL!,
    })(req);
}
