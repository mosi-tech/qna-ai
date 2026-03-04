import { redirect } from 'next/navigation';
import { getAuthUser } from '../auth/server';
import { createDb } from '../db/index';
import * as schema from '../db/schema';
import { profiles } from '../db/schema';
import { eq } from 'drizzle-orm';
import { AccountForm } from './account-form';

export const metadata = { title: 'Account' };

export default async function AccountPage() {
    const user = await getAuthUser();
    if (!user) redirect('/login');

    const db = createDb(process.env.DATABASE_URL!, schema);

    // Fetch or seed the profile row
    let profileRows = await db
        .select()
        .from(profiles)
        .where(eq(profiles.id, user.id))
        .limit(1);

    let profile = profileRows[0] ?? null;

    if (!profile) {
        const inserted = await db
            .insert(profiles)
            .values({
                id: user.id,
                display_name: user.displayName,
                avatar_url: null,
            })
            .returning();
        profile = inserted[0] ?? null;
    }

    return (
        <div className="animate-fadeIn space-y-8">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Account</h1>
                <p className="mt-1 text-sm text-gray-500">
                    Manage your profile and personal settings
                </p>
            </div>
            <AccountForm
                userId={user.id}
                email={user.email ?? ''}
                initialDisplayName={profile?.display_name ?? ''}
                initialAvatarUrl={profile?.avatar_url ?? ''}
                initialTimezone={profile?.timezone ?? 'UTC'}
            />
        </div>
    );
}
