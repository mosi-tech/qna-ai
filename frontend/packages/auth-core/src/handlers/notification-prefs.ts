import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { requireUser } from '../supabase';
import { notification_prefs } from '../db/schema';
import { eq, and } from 'drizzle-orm';
import type { DbInstance } from '../db/index';

// ─── Canonical event definitions ─────────────────────────────────────────────

export const NOTIFICATION_EVENTS = [
    { id: 'payment-failed', label: 'Payment failed', channels: ['email', 'in_app'] },
    { id: 'subscription-activated', label: 'Subscription activated', channels: ['email'] },
    { id: 'subscription-cancelled', label: 'Subscription cancelled', channels: ['email'] },
    { id: 'usage-80pct', label: 'Usage at 80%', channels: ['email', 'in_app'] },
    { id: 'usage-exceeded', label: 'Quota exceeded', channels: ['in_app'] },
    { id: 'trial-ending', label: 'Trial ending (3 days)', channels: ['email'] },
    { id: 'welcome', label: 'Welcome', channels: ['email'] },
] as const;

export type EventId = (typeof NOTIFICATION_EVENTS)[number]['id'];
export type Channel = 'email' | 'in_app';

export interface PrefEntry {
    eventType: EventId;
    channel: Channel;
    enabled: boolean;
}

// ─── Shared schema ────────────────────────────────────────────────────────────

const UpdateSchema = z.object({
    eventType: z.string().min(1),
    channel: z.enum(['email', 'in_app']),
    enabled: z.boolean(),
});

// ─── Handler factories ────────────────────────────────────────────────────────

interface NotificationPrefsDeps {
    db: DbInstance;
}

export function createNotificationPrefsHandler(deps: NotificationPrefsDeps) {
    async function GET(req: NextRequest): Promise<NextResponse> {
        const { db } = deps;
        const { user } = await requireUser(req);

        if (!user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        const rows = await db
            .select()
            .from(notification_prefs)
            .where(eq(notification_prefs.user_id, user.id));

        const rowMap = new Map(
            rows.map((r) => [`${r.event_type}::${r.channel}`, r.enabled]),
        );

        const prefs: PrefEntry[] = NOTIFICATION_EVENTS.flatMap(
            ({ id: eventType, channels }) =>
                channels.map((channel) => ({
                    eventType,
                    channel: channel as Channel,
                    enabled: rowMap.get(`${eventType}::${channel}`) ?? true,
                })),
        );

        return NextResponse.json({ prefs });
    }

    async function PUT(req: NextRequest): Promise<NextResponse> {
        const { db } = deps;
        const { user } = await requireUser(req);

        if (!user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        const body = await req.json().catch(() => null);
        if (!body) {
            return NextResponse.json(
                { error: 'Invalid JSON body' },
                { status: 400 },
            );
        }

        const parsed = UpdateSchema.safeParse(body);
        if (!parsed.success) {
            return NextResponse.json(
                { error: parsed.error.flatten().fieldErrors },
                { status: 400 },
            );
        }

        const { eventType, channel, enabled } = parsed.data;

        const existing = await db
            .select()
            .from(notification_prefs)
            .where(
                and(
                    eq(notification_prefs.user_id, user.id),
                    eq(notification_prefs.channel, channel),
                    eq(notification_prefs.event_type, eventType),
                ),
            )
            .limit(1);

        if (existing[0]) {
            await db
                .update(notification_prefs)
                .set({ enabled })
                .where(eq(notification_prefs.id, existing[0].id));
        } else {
            await db.insert(notification_prefs).values({
                user_id: user.id,
                channel,
                event_type: eventType,
                enabled,
            });
        }

        return NextResponse.json({ ok: true, eventType, channel, enabled });
    }

    return { GET, PUT };
}

// ─── Default exports ──────────────────────────────────────────────────────────

async function getHandler() {
    const { createDb } = await import('../db/index');
    const schema = await import('../db/schema');
    const db = createDb(process.env.DATABASE_URL!, schema);
    return createNotificationPrefsHandler({ db });
}

export async function GET(req: NextRequest): Promise<NextResponse> {
    const handler = await getHandler();
    return handler.GET(req);
}

export async function PUT(req: NextRequest): Promise<NextResponse> {
    const handler = await getHandler();
    return handler.PUT(req);
}
