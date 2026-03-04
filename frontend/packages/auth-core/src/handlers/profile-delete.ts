import { NextRequest, NextResponse } from 'next/server';
import { getAuthUser, deleteUser } from '../auth/server';
import { profiles } from '../db/schema';
import { eq } from 'drizzle-orm';
import type { DbInstance } from '../db/index';

interface ProfileDeleteDeps {
    db: DbInstance;
}

export function createProfileDeleteHandler(deps: ProfileDeleteDeps) {
    return async function DELETE(req: NextRequest): Promise<NextResponse> {
        const { db } = deps;

        const user = await getAuthUser();

        if (!user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        // Soft-delete the profile row
        await db
            .update(profiles)
            .set({ deleted_at: new Date(), updated_at: new Date() })
            .where(eq(profiles.id, user.id));

        const { error: deleteError } = await deleteUser(user.id);

        if (deleteError) {
            console.error('[profile-delete] Failed to delete auth user:', deleteError);
            return NextResponse.json(
                { error: 'Failed to delete account' },
                { status: 500 },
            );
        }

        return NextResponse.json({ ok: true });
    };
}

// The original auth-hub route used POST — we export DELETE as specified by auth-core plan
export async function DELETE(req: NextRequest): Promise<NextResponse> {
    const { createDb } = await import('../db/index');
    const schema = await import('../db/schema');
    const db = createDb(process.env.DATABASE_URL!, schema);
    return createProfileDeleteHandler({ db })(req);
}
