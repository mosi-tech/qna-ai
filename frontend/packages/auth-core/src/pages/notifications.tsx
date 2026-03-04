// ─── Server Component (default export) ───────────────────────────────────────
import { redirect } from 'next/navigation';
import { getAuthUser } from '../auth/server';
import { createDb } from '../db/index';
import * as schema from '../db/schema';
import { notification_prefs } from '../db/schema';
import { eq } from 'drizzle-orm';
import { NOTIFICATION_EVENTS } from '../handlers/notification-prefs';
import type { PrefEntry } from '../handlers/notification-prefs';
import { NotificationPrefsClient } from './notifications-client';

export const metadata = { title: 'Notifications' };

export default async function NotificationsPage() {
    const user = await getAuthUser();
    if (!user) redirect('/login');

    const db = createDb(process.env.DATABASE_URL!, schema);

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
                channel: channel as 'email' | 'in_app',
                enabled: rowMap.get(`${eventType}::${channel}`) ?? true,
            })),
    );

    return (
        <div className="animate-fadeIn space-y-8">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
                <p className="mt-1 text-sm text-gray-500">
                    Choose which notifications you receive and through which channels
                </p>
            </div>

            <NotificationPrefsClient initialPrefs={prefs} events={NOTIFICATION_EVENTS} />
        </div>
    );
}