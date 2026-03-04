import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { requireUser } from '../supabase';
import { recordUsageEvent, getUsageSummary } from '../entitlements';
import { triggerUsage80Pct, triggerUsageExceeded } from '../novu';
import type { DbInstance } from '../db/index';

const RecordSchema = z.object({
    userId: z.string().uuid(),
    appId: z.string().min(1),
    eventType: z.string().min(1),
    quantity: z.number().int().positive().default(1),
    metadata: z.record(z.unknown()).optional(),
});

interface UsageRecordDeps {
    db: DbInstance;
    serviceSecret?: string;
    supabaseUrl: string;
    supabaseServiceRoleKey: string;
}

export function createUsageRecordHandler(deps: UsageRecordDeps) {
    return async function POST(req: NextRequest): Promise<NextResponse> {
        const {
            db,
            serviceSecret,
            supabaseUrl,
            supabaseServiceRoleKey,
        } = deps;

        // Dual auth: Supabase session cookie OR SERVICE_SECRET bearer token
        let authUserId: string | null = null;
        let isServiceCall = false;

        const authHeader = req.headers.get('authorization');
        if (
            authHeader &&
            serviceSecret &&
            authHeader === `Bearer ${serviceSecret}`
        ) {
            isServiceCall = true;
        } else {
            // Try Supabase session cookie
            const { user } = await requireUser(req);
            if (user) {
                authUserId = user.id;
            }
        }

        if (!isServiceCall && !authUserId) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        const body = await req.json().catch(() => null);
        if (!body) {
            return NextResponse.json(
                { error: 'Invalid JSON body' },
                { status: 400 },
            );
        }

        const parsed = RecordSchema.safeParse(body);
        if (!parsed.success) {
            return NextResponse.json(
                { error: parsed.error.flatten().fieldErrors },
                { status: 400 },
            );
        }

        const { userId, appId, eventType, quantity, metadata } = parsed.data;

        // Cookie auth users can only record events for themselves
        if (!isServiceCall && authUserId && authUserId !== userId) {
            return NextResponse.json(
                { error: 'Forbidden: cannot record events for another user' },
                { status: 403 },
            );
        }

        const { crossed80, exceeded, entry } = await recordUsageEvent(
            userId,
            appId,
            eventType,
            quantity,
            db,
            metadata,
        );

        // Fire Novu notifications on threshold crossings
        if (crossed80 || exceeded) {
            try {
                const { createClient } = await import('@supabase/supabase-js');
                const adminClient = createClient(supabaseUrl, supabaseServiceRoleKey);
                const {
                    data: { user: targetUser },
                } = await adminClient.auth.admin.getUserById(userId);

                const email = targetUser?.email;
                if (email) {
                    const summary = await getUsageSummary(userId, db, appId);
                    const percentUsed = summary[eventType]?.percentUsed ?? 0;

                    if (exceeded) {
                        await triggerUsageExceeded(userId, eventType);
                    } else if (crossed80) {
                        await triggerUsage80Pct(
                            userId,
                            email,
                            eventType,
                            entry.used,
                            entry.limit ?? 0,
                        );
                    }
                }
            } catch (err) {
                console.error('[usage-record] Novu notification error:', err);
                // non-fatal
            }
        }

        return NextResponse.json({
            recorded: true,
            usage: {
                eventType,
                used: entry.used,
                limit: entry.limit,
                exceeded: entry.exceeded,
                percentUsed: entry.percentUsed,
            },
        });
    };
}

export async function POST(req: NextRequest): Promise<NextResponse> {
    const { createDb } = await import('../db/index');
    const schema = await import('../db/schema');
    const db = createDb(process.env.DATABASE_URL!, schema);
    return createUsageRecordHandler({
        db,
        serviceSecret: process.env.SERVICE_SECRET,
        supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL!,
        supabaseServiceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY!,
    })(req);
}
