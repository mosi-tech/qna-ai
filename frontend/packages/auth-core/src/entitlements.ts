import type { DbInstance } from './db/index';
import { subscriptions, subscription_overrides, usage_events } from './db/schema';
import { eq, and, inArray, gte, sum, desc } from 'drizzle-orm';
import { getStripeFeatures, type StripeFeatures } from './stripe';

// ─── Quota constants ───────────────────────────────────────────────────────────
// These are application-level limits, not billing concepts.
// Stripe Entitlements handles feature flags; these handle non-billable quotas.
// null = unlimited.

export const PLAN_QUOTAS = {
    free: { ai_builds: 10, saved_dashboards: 3, exports: 0 },
    pro: { ai_builds: 100, saved_dashboards: null, exports: null },
    team: { ai_builds: 500, saved_dashboards: null, exports: null },
} as const;

export type PlanKey = keyof typeof PLAN_QUOTAS;
export type QuotaKey = keyof (typeof PLAN_QUOTAS)['free'];

/** Convenience re-export of feature keys driven by Stripe Entitlements. */
export type FeatureKey = keyof StripeFeatures;

export interface Entitlements {
    planKey: PlanKey;
    planName: string;
    subscriptionStatus: string;
    stripeCustomerId: string | null;
    /** From PLAN_QUOTAS — overridden per-user by subscription_overrides */
    quotas: Record<string, number | null>;
    /** From Stripe Entitlements API — keyed by can_export, custom_branding, etc. */
    features: StripeFeatures;
    periodEnd: Date | null;
    cancelAtPeriodEnd: boolean;
}

const ACTIVE_STATUSES = ['active', 'trialing'];

function isValidPlanKey(id: string): id is PlanKey {
    return id in PLAN_QUOTAS;
}

/**
 * Returns entitlements for a user based on their active subscription.
 * - Quotas: PLAN_QUOTAS[plan_key], overridden by subscription_overrides rows.
 * - Features: Stripe Entitlements API (active entitlements for the customer).
 * Falls back to free plan if no active subscription.
 */
export async function getEntitlements(
    userId: string,
    db: DbInstance,
): Promise<Entitlements> {
    // Load subscription + user overrides in parallel
    const [subscriptionRows, overrides] = await Promise.all([
        db
            .select()
            .from(subscriptions)
            .where(and(
                eq(subscriptions.user_id, userId),
                inArray(subscriptions.status, ACTIVE_STATUSES),
            ))
            .orderBy(desc(subscriptions.created_at))
            .limit(1),
        db
            .select({
                event_type: subscription_overrides.event_type,
                limit_override: subscription_overrides.limit_override,
            })
            .from(subscription_overrides)
            .where(eq(subscription_overrides.user_id, userId)),
    ]);
    const subscription = subscriptionRows[0] ?? null;

    const planKey: PlanKey = subscription && isValidPlanKey(subscription.plan_key)
        ? subscription.plan_key
        : 'free';

    const planName = planKey.charAt(0).toUpperCase() + planKey.slice(1);
    const status = subscription?.status ?? 'none';

    // Build quotas from const, then apply per-user overrides
    const baseQuotas = PLAN_QUOTAS[planKey] as Record<string, number | null>;
    const quotas: Record<string, number | null> = { ...baseQuotas };
    for (const ov of overrides) {
        // limit_override === null means unlimited for this user
        quotas[ov.event_type] = ov.limit_override ?? null;
    }

    // Features come from Stripe Entitlements
    const features = await getStripeFeatures(subscription?.stripe_customer_id);

    return {
        planKey,
        planName,
        subscriptionStatus: status,
        stripeCustomerId: subscription?.stripe_customer_id ?? null,
        quotas,
        features,
        periodEnd: subscription?.period_end ?? null,
        cancelAtPeriodEnd: subscription?.cancel_at_period_end ?? false,
    };
}

// ─── Usage types ───────────────────────────────────────────────────────────────

/** Shape returned per event type from getUsageSummary / checkQuota */
export interface UsageQuotaEntry {
    used: number;
    limit: number | null; // null = unlimited
    exceeded: boolean;
    percentUsed: number | null; // null when unlimited
}

export type UsageSummary = Record<string, UsageQuotaEntry>;

/**
 * Returns the start of the current billing period for a user.
 * Uses the subscription's period_start if available,
 * otherwise first day of the current calendar month.
 */
async function getCurrentPeriodStart(userId: string, db: DbInstance): Promise<Date> {
    const rows = await db
        .select({ period_start: subscriptions.period_start })
        .from(subscriptions)
        .where(and(
            eq(subscriptions.user_id, userId),
            inArray(subscriptions.status, ['active', 'trialing']),
        ))
        .limit(1);
    const sub = rows[0] ?? null;

    if (sub?.period_start) return sub.period_start;

    const now = new Date();
    return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 1));
}

/**
 * Returns current-period usage totals for every event type recorded,
 * mapped against the user's effective quota (plan + overrides).
 *
 * @param appId - optional filter by consuming app (e.g. 'ai-builder')
 */
export async function getUsageSummary(
    userId: string,
    db: DbInstance,
    appId?: string,
): Promise<UsageSummary> {
    const [entitlements, periodStart] = await Promise.all([
        getEntitlements(userId, db),
        getCurrentPeriodStart(userId, db),
    ]);

    const conditions = [
        eq(usage_events.user_id, userId),
        gte(usage_events.recorded_at, periodStart),
        ...(appId ? [eq(usage_events.app_id, appId)] : []),
    ];

    const rows = await db
        .select({
            event_type: usage_events.event_type,
            total: sum(usage_events.quantity).mapWith(Number),
        })
        .from(usage_events)
        .where(and(...conditions))
        .groupBy(usage_events.event_type);

    const usageMap = new Map(rows.map((r) => [r.event_type, r.total ?? 0]));

    const allKeys = new Set<string>([
        ...Object.keys(entitlements.quotas),
        ...usageMap.keys(),
    ]);

    const summary: UsageSummary = {};

    for (const key of allKeys) {
        const used = usageMap.get(key) ?? 0;
        const limit = key in entitlements.quotas ? (entitlements.quotas[key] ?? null) : null;
        const exceeded = limit !== null && used > limit;
        const percentUsed = limit !== null && limit > 0 ? (used / limit) * 100 : null;
        summary[key] = { used, limit, exceeded, percentUsed };
    }

    return summary;
}

/**
 * Check quota for a single event type.
 * Useful as a quick gate before allowing an action.
 */
export async function checkQuota(
    userId: string,
    eventType: string,
    db: DbInstance,
): Promise<UsageQuotaEntry> {
    const summary = await getUsageSummary(userId, db);
    return summary[eventType] ?? { used: 0, limit: null, exceeded: false, percentUsed: null };
}

/**
 * Records a usage event and returns whether the 80% and exceeded thresholds
 * were crossed for the first time in this call.
 *
 * Returns { crossed80, exceeded } flags so callers can fire Novu notifications.
 */
export async function recordUsageEvent(
    userId: string,
    appId: string,
    eventType: string,
    quantity: number = 1,
    db: DbInstance,
    metadata?: Record<string, unknown>,
): Promise<{ crossed80: boolean; exceeded: boolean; entry: UsageQuotaEntry }> {
    const before = await checkQuota(userId, eventType, db);

    await db.insert(usage_events).values({
        user_id: userId,
        app_id: appId,
        event_type: eventType,
        quantity,
        metadata: metadata ?? null,
        recorded_at: new Date(),
    });

    const after = await checkQuota(userId, eventType, db);

    const pctBefore = before.percentUsed ?? 0;
    const pctAfter = after.percentUsed ?? 0;

    const crossed80 = pctBefore < 80 && pctAfter >= 80;
    const exceeded = !before.exceeded && after.exceeded;

    return { crossed80, exceeded, entry: after };
}
