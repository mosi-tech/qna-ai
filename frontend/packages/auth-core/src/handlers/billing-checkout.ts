import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { requireUser } from '../supabase';
import { stripe, getOrCreateStripeCustomer } from '../stripe';
import { subscriptions } from '../db/schema';
import { eq } from 'drizzle-orm';
import type { DbInstance } from '../db/index';

const CheckoutSchema = z.object({
    priceId: z.string().min(1),
    billing: z.enum(['monthly', 'annual']).default('monthly'),
});

interface BillingCheckoutDeps {
    db: DbInstance;
    appUrl: string;
}

export function createBillingCheckoutHandler(deps: BillingCheckoutDeps) {
    return async function POST(req: NextRequest): Promise<NextResponse> {
        const { db, appUrl } = deps;
        const { user } = await requireUser(req);

        if (!user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        const body = await req.json().catch(() => null);
        if (!body) {
            return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
        }

        const parsed = CheckoutSchema.safeParse(body);
        if (!parsed.success) {
            return NextResponse.json(
                { error: parsed.error.flatten().fieldErrors },
                { status: 400 },
            );
        }

        const { priceId } = parsed.data;

        // Look up existing customer ID if they have a subscription
        const existing = await db
            .select()
            .from(subscriptions)
            .where(eq(subscriptions.user_id, user.id))
            .limit(1);
        const existingSub = existing[0] ?? null;

        const stripeCustomerId = await getOrCreateStripeCustomer(
            user.id,
            user.email!,
            existingSub?.stripe_customer_id,
        );

        // Update subscription row with the customer ID if it was just created
        if (existingSub && !existingSub.stripe_customer_id) {
            await db
                .update(subscriptions)
                .set({ stripe_customer_id: stripeCustomerId, updated_at: new Date() })
                .where(eq(subscriptions.id, existingSub.id));
        }

        const session = await stripe.checkout.sessions.create({
            customer: stripeCustomerId,
            mode: 'subscription',
            payment_method_types: ['card'],
            line_items: [{ price: priceId, quantity: 1 }],
            subscription_data: {
                metadata: { userId: user.id },
            },
            success_url: `${appUrl}/billing?session_id={CHECKOUT_SESSION_ID}&success=1`,
            cancel_url: `${appUrl}/billing?cancelled=1`,
            metadata: { userId: user.id },
        });

        if (!session.url) {
            return NextResponse.json(
                { error: 'Failed to create checkout session' },
                { status: 500 },
            );
        }

        return NextResponse.json({ url: session.url });
    };
}

// Default: create db + deps from environment variables
export async function POST(req: NextRequest): Promise<NextResponse> {
    const { createDb } = await import('../db/index');
    const schema = await import('../db/schema');
    const db = createDb(process.env.DATABASE_URL!, schema);
    return createBillingCheckoutHandler({
        db,
        appUrl: process.env.NEXT_PUBLIC_APP_URL!,
    })(req);
}
