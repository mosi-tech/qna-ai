import Stripe from 'stripe';

// Singleton Stripe instance
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
    apiVersion: '2025-02-24.acacia',
    typescript: true,
});

// ─── Dynamic plan resolution ───────────────────────────────────────────────────
// Plans are defined entirely in Stripe (Products + Prices).
// No local PLANS array, no hardcoded price IDs in env vars.
//
// Required Stripe product metadata:
//   plan_key:   'free' | 'pro' | 'team'   ← matches PLAN_QUOTAS keys in entitlements.ts
//   sort_order: '0' | '1' | '2'            ← display order on pricing page (default 99)
//
// Use Stripe's built-in product.marketing_features[] for bullet points in the UI.
// Use Stripe Entitlements to gate features per customer.

export interface StripePlan {
    productId: string;
    planKey: string;
    name: string;
    description: string;
    features: string[];       // from product.marketing_features[].name
    prices: StripePlanPrice[];
    sortOrder: number;
}

export interface StripePlanPrice {
    priceId: string;
    amount: number;           // unit_amount in cents
    currency: string;
    interval: 'month' | 'year';
}

/**
 * Fetches all active Stripe products that carry a `plan_key` metadata field,
 * along with their active recurring prices.
 *
 * Always includes a synthetic Free tier if no Stripe product has plan_key='free'.
 * Server-side only.
 */
export async function getStripePlans(): Promise<StripePlan[]> {
    const [productsPage, pricesPage] = await Promise.all([
        stripe.products.list({ active: true, limit: 100 }),
        stripe.prices.list({ active: true, limit: 100, type: 'recurring' }),
    ]);

    // Index prices by product ID
    const pricesByProduct: Record<string, StripePlanPrice[]> = {};
    for (const price of pricesPage.data) {
        const productId =
            typeof price.product === 'string' ? price.product : price.product.id;
        if (!pricesByProduct[productId]) pricesByProduct[productId] = [];
        pricesByProduct[productId].push({
            priceId: price.id,
            amount: price.unit_amount ?? 0,
            currency: price.currency,
            interval: price.recurring!.interval as 'month' | 'year',
        });
    }

    const plans: StripePlan[] = [];
    for (const product of productsPage.data) {
        const planKey = product.metadata?.plan_key;
        if (!planKey) continue; // skip products not managed by auth-hub

        plans.push({
            productId: product.id,
            planKey,
            name: product.name,
            description: product.description ?? '',
            features: (product.marketing_features ?? [])
                .map((f) => f.name ?? '')
                .filter(Boolean),
            prices: pricesByProduct[product.id] ?? [],
            sortOrder: parseInt(product.metadata?.sort_order ?? '99', 10),
        });
    }

    // Prepend a synthetic Free tier if Stripe has no product for it
    if (!plans.some((p) => p.planKey === 'free')) {
        plans.unshift({
            productId: '',
            planKey: 'free',
            name: 'Free',
            description: 'Get started with the basics',
            features: ['10 AI builds / month', '3 saved dashboards', 'Community support'],
            prices: [],
            sortOrder: 0,
        });
    }

    return plans.sort((a, b) => a.sortOrder - b.sortOrder);
}

/**
 * Resolves plan_key and plan name from a Stripe price ID by expanding its
 * product and reading product.metadata.plan_key.
 *
 * Never throws — returns { planKey: 'free', ... } on any error.
 * Server-side only.
 */
export async function resolvePlanKeyFromPrice(
    priceId: string | null | undefined,
): Promise<{ planKey: string; planName: string; productId: string | null }> {
    if (!priceId) return { planKey: 'free', planName: 'Free', productId: null };

    try {
        const price = await stripe.prices.retrieve(priceId, {
            expand: ['product'],
        });
        const product = price.product as Stripe.Product;
        if (product.deleted) return { planKey: 'free', planName: 'Free', productId: null };

        const planKey = product.metadata?.plan_key ?? 'free';
        return { planKey, planName: product.name, productId: product.id };
    } catch {
        return { planKey: 'free', planName: 'Free', productId: null };
    }
}

/**
 * Gets or creates a Stripe customer for a user.
 */
export async function getOrCreateStripeCustomer(
    userId: string,
    email: string,
    existingCustomerId?: string | null,
): Promise<string> {
    if (existingCustomerId) return existingCustomerId;

    const customer = await stripe.customers.create({
        email,
        metadata: { userId },
    });

    return customer.id;
}

// ─── Stripe Entitlements ───────────────────────────────────────────────────────
// Feature flag lookup keys stored in Stripe Entitlements.
// These must match the `lookup_key` values on your Stripe Entitlement Features.
export const STRIPE_FEATURE_KEYS = [
    'can_export',
    'custom_branding',
    'priority_support',
    'seat_billing',
] as const;

export type StripeFeatureKey = (typeof STRIPE_FEATURE_KEYS)[number];

export type StripeFeatures = Record<StripeFeatureKey, boolean>;

/**
 * Returns the Stripe Entitlement feature flags for a customer.
 * Falls back to all-false if no customer ID or the API call fails.
 *
 * Uses server-side Stripe SDK — call only from server components / route handlers.
 */
export async function getStripeFeatures(
    stripeCustomerId: string | null | undefined,
): Promise<StripeFeatures> {
    const defaults = Object.fromEntries(
        STRIPE_FEATURE_KEYS.map((k) => [k, false]),
    ) as StripeFeatures;

    if (!stripeCustomerId) return defaults;

    try {
        const entitlements = await stripe.entitlements.activeEntitlements.list({
            customer: stripeCustomerId,
        });

        const activeKeys = new Set(
            entitlements.data.map((e) => e.lookup_key),
        );

        return Object.fromEntries(
            STRIPE_FEATURE_KEYS.map((k) => [k, activeKeys.has(k)]),
        ) as StripeFeatures;
    } catch (err) {
        console.error('[stripe] getStripeFeatures error:', err);
        return defaults;
    }
}
