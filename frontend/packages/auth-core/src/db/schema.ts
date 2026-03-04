import {
    pgTable,
    uuid,
    text,
    timestamp,
    boolean,
    jsonb,
    integer,
    unique,
    index,
} from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

// ─── profiles ──────────────────────────────────────────────────────────────────
// Extends supabase.auth.users — id FK is enforced at the DB level via migration.
export const profiles = pgTable('profiles', {
    id: uuid('id').primaryKey(), // FK → auth.users.id CASCADE DELETE
    display_name: text('display_name'),
    avatar_url: text('avatar_url'),
    timezone: text('timezone').default('UTC').notNull(),
    deleted_at: timestamp('deleted_at', { withTimezone: true }),
    created_at: timestamp('created_at', { withTimezone: true })
        .default(sql`now()`)
        .notNull(),
    updated_at: timestamp('updated_at', { withTimezone: true })
        .default(sql`now()`)
        .notNull(),
});

// ─── subscriptions ─────────────────────────────────────────────────────────────
// Stripe is the source of truth for plan definitions.
// We cache the relevant Stripe IDs here + a denormalised plan_key for fast
// quota lookups without hitting the Stripe API.
export const subscriptions = pgTable('subscriptions', {
    id: uuid('id')
        .primaryKey()
        .default(sql`gen_random_uuid()`),
    user_id: uuid('user_id').notNull(), // FK → auth.users.id CASCADE DELETE
    // ── Stripe references ─────────────────────────────────────────────────────
    stripe_customer_id: text('stripe_customer_id'),
    stripe_subscription_id: text('stripe_subscription_id').unique(),
    stripe_product_id: text('stripe_product_id'), // Stripe product driving this sub
    stripe_price_id: text('stripe_price_id'),     // active Stripe price (monthly or annual)
    // ── Denormalised plan key ─────────────────────────────────────────────────
    // Matches a key in PLAN_QUOTAS: 'free' | 'pro' | 'team'
    plan_key: text('plan_key').notNull().default('free'),
    // ── Lifecycle ─────────────────────────────────────────────────────────────
    status: text('status').notNull().default('active'),
    // 'active' | 'trialing' | 'past_due' | 'cancelled' | 'paused'
    period_start: timestamp('period_start', { withTimezone: true }),
    period_end: timestamp('period_end', { withTimezone: true }),
    trial_end: timestamp('trial_end', { withTimezone: true }),
    cancel_at_period_end: boolean('cancel_at_period_end').default(false).notNull(),
    created_at: timestamp('created_at', { withTimezone: true })
        .default(sql`now()`)
        .notNull(),
    updated_at: timestamp('updated_at', { withTimezone: true })
        .default(sql`now()`)
        .notNull(),
});

// ─── subscription_overrides ────────────────────────────────────────────────────
// Per-user quota overrides for enterprise / custom deals.
// Takes precedence over PLAN_QUOTAS[plan_key][event_type] when set.
// null limit_override = unlimited for this user regardless of plan.
export const subscription_overrides = pgTable(
    'subscription_overrides',
    {
        id: uuid('id')
            .primaryKey()
            .default(sql`gen_random_uuid()`),
        user_id: uuid('user_id').notNull(), // FK → auth.users.id CASCADE DELETE
        event_type: text('event_type').notNull(), // e.g. 'ai_builds'
        limit_override: integer('limit_override'), // null = unlimited
        created_at: timestamp('created_at', { withTimezone: true })
            .default(sql`now()`)
            .notNull(),
        updated_at: timestamp('updated_at', { withTimezone: true })
            .default(sql`now()`)
            .notNull(),
    },
    (table) => ({
        uniq_user_event: unique('uniq_override_user_event').on(
            table.user_id,
            table.event_type,
        ),
    }),
);

// ─── usage_events ──────────────────────────────────────────────────────────────
export const usage_events = pgTable(
    'usage_events',
    {
        id: uuid('id')
            .primaryKey()
            .default(sql`gen_random_uuid()`),
        user_id: uuid('user_id').notNull(), // FK → auth.users.id CASCADE DELETE
        app_id: text('app_id').notNull(), // e.g. 'ai-builder'
        event_type: text('event_type').notNull(), // e.g. 'ai_builds'
        quantity: integer('quantity').default(1).notNull(),
        metadata: jsonb('metadata'),
        recorded_at: timestamp('recorded_at', { withTimezone: true })
            .default(sql`now()`)
            .notNull(),
    },
    (table) => ({
        usage_lookup_idx: index('usage_lookup_idx').on(
            table.user_id,
            table.app_id,
            table.event_type,
            table.recorded_at,
        ),
    }),
);

// ─── notification_prefs ────────────────────────────────────────────────────────
export const notification_prefs = pgTable(
    'notification_prefs',
    {
        id: uuid('id')
            .primaryKey()
            .default(sql`gen_random_uuid()`),
        user_id: uuid('user_id').notNull(), // FK → auth.users.id CASCADE DELETE
        channel: text('channel').notNull(), // 'email' | 'in_app'
        event_type: text('event_type').notNull(), // matches Novu event IDs
        enabled: boolean('enabled').default(true).notNull(),
    },
    (table) => ({
        unique_user_channel_event: unique('uniq_user_channel_event').on(
            table.user_id,
            table.channel,
            table.event_type,
        ),
    }),
);

// ─── Types ─────────────────────────────────────────────────────────────────────
export type Profile = typeof profiles.$inferSelect;
export type NewProfile = typeof profiles.$inferInsert;

export type Subscription = typeof subscriptions.$inferSelect;
export type NewSubscription = typeof subscriptions.$inferInsert;

export type SubscriptionOverride = typeof subscription_overrides.$inferSelect;
export type NewSubscriptionOverride = typeof subscription_overrides.$inferInsert;

export type UsageEvent = typeof usage_events.$inferSelect;
export type NewUsageEvent = typeof usage_events.$inferInsert;

export type NotificationPref = typeof notification_prefs.$inferSelect;
export type NewNotificationPref = typeof notification_prefs.$inferInsert;
