import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { getAuthUser, updateUser } from '../auth/server';
import { profiles } from '../db/schema';
import { eq } from 'drizzle-orm';
import type { DbInstance } from '../db/index';

const UpdateProfileSchema = z.object({
    display_name: z.string().min(1).max(100),
    avatar_url: z.string().url().optional().nullable(),
    timezone: z.string().min(1).max(64),
});

interface ProfileUpdateDeps {
    db: DbInstance;
}

export function createProfileUpdateHandler(deps: ProfileUpdateDeps) {
    return async function PUT(req: NextRequest): Promise<NextResponse> {
        const { db } = deps;

        const user = await getAuthUser();
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

        const parsed = UpdateProfileSchema.safeParse(body);
        if (!parsed.success) {
            return NextResponse.json(
                { error: parsed.error.flatten().fieldErrors },
                { status: 400 },
            );
        }

        const { display_name, avatar_url, timezone } = parsed.data;

        await db
            .insert(profiles)
            .values({
                id: user.id,
                display_name,
                avatar_url: avatar_url ?? null,
                timezone,
                updated_at: new Date(),
            })
            .onConflictDoUpdate({
                target: profiles.id,
                set: {
                    display_name,
                    avatar_url: avatar_url ?? null,
                    timezone,
                    updated_at: new Date(),
                },
            });

        // Sync display_name to auth provider metadata
        await updateUser({ displayName: display_name });

        return NextResponse.json({ ok: true });
    };
}

// The original auth-hub route used POST — we export PUT as specified by auth-core plan
export async function PUT(req: NextRequest): Promise<NextResponse> {
    const { createDb } = await import('../db/index');
    const schema = await import('../db/schema');
    const db = createDb(process.env.DATABASE_URL!, schema);
    return createProfileUpdateHandler({ db })(req);
}
