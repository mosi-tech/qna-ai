import { NextRequest, NextResponse } from 'next/server';
import { requireUser } from '../supabase';
import { generateSubscriberHash } from '../novu';

/**
 * GET /api/notifications/hash
 *
 * Returns the HMAC-SHA256 subscriber hash for the authenticated user.
 * Used by the NovuBell client component to initialise @novu/react in secure mode.
 *
 * Response: { subscriberHash: string | null }
 * (null when NOVU_SECRET_HASH_KEY is not configured)
 */
export async function GET(req: NextRequest): Promise<NextResponse> {
    const { user } = await requireUser(req);

    if (!user) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const subscriberHash = generateSubscriberHash(user.id);
    return NextResponse.json({ subscriberHash });
}
