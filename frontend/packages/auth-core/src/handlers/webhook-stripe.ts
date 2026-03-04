import { NextRequest, NextResponse } from 'next/server';
import { stripe, resolvePlanKeyFromPrice } from '../stripe';
import {
    triggerSubscriptionActivated,
    triggerPaymentFailed,
    triggerSubscriptionCancelled,
} from '../novu';
import { subscriptions } from '../db/schema';
import { eq } from 'drizzle-orm';
import type { DbInstance } from '../db/index';
import type Stripe from 'stripe';

interface WebhookStripeDeps {
    db: DbInstance;
    stripeWebhookSecret: string;
}

async function handleCheckoutCompleted(
    session: Stripe.Checkout.Session,
    db: DbInstance,
): Promise<void> {
    const userId = session.metadata?.userId;
    if (!userId) return;

    const stripeSubscriptionId =
        typeof session.subscription === 'string'
            ? session.subscription
            : session.subscription?.id ?? null;

    if (!stripeSubscriptionId) return;

    const stripeSubscription =
        await stripe.subscriptions.retrieve(stripeSubscriptionId);
    const priceId = stripeSubscription.items.data[0]?.price?.id ?? null;
    const { planKey, planName } = await resolvePlanKeyFromPrice(priceId);

    const stripeCustomerId =
        typeof session.customer === 'string'
            ? session.customer
            : session.customer?.id ?? null;

    const periodStart = stripeSubscription.current_period_start
        ? new Date(stripeSubscription.current_period_start * 1000)
        : null;
    const periodEnd = stripeSubscription.current_period_end
        ? new Date(stripeSubscription.current_period_end * 1000)
        : null;

    // Check if row exists
    const existing = await db
        .select()
        .from(subscriptions)
        .where(eq(subscriptions.user_id, userId))
        .limit(1);

    if (existing[0]) {
        await db
            .update(subscriptions)
            .set({
                plan_key: planKey,
                status: 'active',
                stripe_subscription_id: stripeSubscriptionId,
                stripe_customer_id: stripeCustomerId,
                period_start: periodStart,
                period_end: periodEnd,
                cancel_at_period_end: false,
                updated_at: new Date(),
            })
            .where(eq(subscriptions.user_id, userId));
    } else {
        await db.insert(subscriptions).values({
            user_id: userId,
            plan_key: planKey,
            status: 'active',
            stripe_subscription_id: stripeSubscriptionId,
            stripe_customer_id: stripeCustomerId,
            period_start: periodStart,
            period_end: periodEnd,
            cancel_at_period_end: false,
            created_at: new Date(),
            updated_at: new Date(),
        });
    }

    // Trigger Novu notification
    const customerEmail =
        typeof session.customer_details?.email === 'string'
            ? session.customer_details.email
            : undefined;
    if (customerEmail) {
        try {
            await triggerSubscriptionActivated(userId, customerEmail, planName);
        } catch (err) {
            console.error('[webhook] triggerSubscriptionActivated error:', err);
        }
    }
}

async function handleInvoicePaid(
    invoice: Stripe.Invoice,
    db: DbInstance,
): Promise<void> {
    const stripeSubscriptionId =
        typeof invoice.subscription === 'string'
            ? invoice.subscription
            : invoice.subscription?.id ?? null;
    if (!stripeSubscriptionId) return;

    const stripeSubscription =
        await stripe.subscriptions.retrieve(stripeSubscriptionId);
    const periodStart = stripeSubscription.current_period_start
        ? new Date(stripeSubscription.current_period_start * 1000)
        : null;
    const periodEnd = stripeSubscription.current_period_end
        ? new Date(stripeSubscription.current_period_end * 1000)
        : null;

    await db
        .update(subscriptions)
        .set({
            status: 'active',
            period_start: periodStart,
            period_end: periodEnd,
            updated_at: new Date(),
        })
        .where(eq(subscriptions.stripe_subscription_id, stripeSubscriptionId));
}

async function handleInvoicePaymentFailed(
    invoice: Stripe.Invoice,
    db: DbInstance,
): Promise<void> {
    const stripeSubscriptionId =
        typeof invoice.subscription === 'string'
            ? invoice.subscription
            : invoice.subscription?.id ?? null;
    if (!stripeSubscriptionId) return;

    const rows = await db
        .select()
        .from(subscriptions)
        .where(eq(subscriptions.stripe_subscription_id, stripeSubscriptionId))
        .limit(1);
    const sub = rows[0] ?? null;

    await db
        .update(subscriptions)
        .set({ status: 'past_due', updated_at: new Date() })
        .where(eq(subscriptions.stripe_subscription_id, stripeSubscriptionId));

    if (sub) {
        const customerEmail =
            typeof invoice.customer_email === 'string'
                ? invoice.customer_email
                : undefined;
        if (customerEmail) {
            try {
                await triggerPaymentFailed(sub.user_id, customerEmail);
            } catch (err) {
                console.error('[webhook] triggerPaymentFailed error:', err);
            }
        }
    }
}

async function handleSubscriptionUpdated(
    subscription: Stripe.Subscription,
    db: DbInstance,
): Promise<void> {
    const priceId = subscription.items.data[0]?.price?.id ?? null;
    const { planKey, planName } = await resolvePlanKeyFromPrice(priceId);

    const periodStart = subscription.current_period_start
        ? new Date(subscription.current_period_start * 1000)
        : null;
    const periodEnd = subscription.current_period_end
        ? new Date(subscription.current_period_end * 1000)
        : null;

    await db
        .update(subscriptions)
        .set({
            plan_key: planKey,
            status: subscription.status as string,
            period_start: periodStart,
            period_end: periodEnd,
            cancel_at_period_end: subscription.cancel_at_period_end,
            updated_at: new Date(),
        })
        .where(eq(subscriptions.stripe_subscription_id, subscription.id));
}

async function handleSubscriptionDeleted(
    subscription: Stripe.Subscription,
    db: DbInstance,
): Promise<void> {
    const rows = await db
        .select()
        .from(subscriptions)
        .where(eq(subscriptions.stripe_subscription_id, subscription.id))
        .limit(1);
    const sub = rows[0] ?? null;

    await db
        .update(subscriptions)
        .set({ status: 'cancelled', updated_at: new Date() })
        .where(eq(subscriptions.stripe_subscription_id, subscription.id));

    if (sub) {
        // Try to get customer email
        let customerEmail: string | undefined;
        try {
            const customerId =
                typeof subscription.customer === 'string'
                    ? subscription.customer
                    : subscription.customer?.id;
            if (customerId) {
                const customer = await stripe.customers.retrieve(customerId);
                if (!customer.deleted && customer.email) {
                    customerEmail = customer.email;
                }
            }
        } catch {
            // ignore
        }

        if (customerEmail) {
            try {
                await triggerSubscriptionCancelled(
                    sub.user_id,
                    customerEmail,
                    sub.plan_key.charAt(0).toUpperCase() + sub.plan_key.slice(1),
                );
            } catch (err) {
                console.error('[webhook] triggerSubscriptionCancelled error:', err);
            }
        }
    }
}

export function createWebhookStripeHandler(deps: WebhookStripeDeps) {
    return async function POST(req: NextRequest): Promise<NextResponse> {
        const { db, stripeWebhookSecret } = deps;

        const rawBody = await req.text();
        const sig = req.headers.get('stripe-signature');

        if (!sig) {
            return NextResponse.json(
                { error: 'Missing stripe-signature header' },
                { status: 400 },
            );
        }

        let event: Stripe.Event;
        try {
            event = stripe.webhooks.constructEvent(rawBody, sig, stripeWebhookSecret);
        } catch (err) {
            console.error('[webhook] Signature verification failed:', err);
            return NextResponse.json(
                { error: 'Webhook signature verification failed' },
                { status: 400 },
            );
        }

        try {
            switch (event.type) {
                case 'checkout.session.completed':
                    await handleCheckoutCompleted(
                        event.data.object as Stripe.Checkout.Session,
                        db,
                    );
                    break;
                case 'invoice.paid':
                    await handleInvoicePaid(event.data.object as Stripe.Invoice, db);
                    break;
                case 'invoice.payment_failed':
                    await handleInvoicePaymentFailed(
                        event.data.object as Stripe.Invoice,
                        db,
                    );
                    break;
                case 'customer.subscription.updated':
                    await handleSubscriptionUpdated(
                        event.data.object as Stripe.Subscription,
                        db,
                    );
                    break;
                case 'customer.subscription.deleted':
                    await handleSubscriptionDeleted(
                        event.data.object as Stripe.Subscription,
                        db,
                    );
                    break;
                default:
                    // Unhandled event — return 200 to acknowledge receipt
                    break;
            }
        } catch (err) {
            console.error('[webhook] Error handling event:', event.type, err);
            return NextResponse.json(
                { error: 'Internal server error' },
                { status: 500 },
            );
        }

        return NextResponse.json({ received: true });
    };
}

export async function POST(req: NextRequest): Promise<NextResponse> {
    const { createDb } = await import('../db/index');
    const schema = await import('../db/schema');
    const db = createDb(process.env.DATABASE_URL!, schema);
    return createWebhookStripeHandler({
        db,
        stripeWebhookSecret: process.env.STRIPE_WEBHOOK_SECRET!,
    })(req);
}
