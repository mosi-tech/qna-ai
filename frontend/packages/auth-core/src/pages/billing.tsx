// ─── Server Component (default export) ───────────────────────────────────────
import { redirect } from 'next/navigation';
import { getAuthUser } from '../auth/server';
import { createDb } from '../db/index';
import * as schema from '../db/schema';
import { getEntitlements } from '../entitlements';
import { getStripePlans } from '../stripe';
import { BillingClient } from './billing-client';

export const metadata = { title: 'Billing' };

export default async function BillingPage({
    searchParams,
}: {
    searchParams: Promise<Record<string, string>>;
}) {
    const user = await getAuthUser();
    if (!user) redirect('/login');

    const db = createDb(process.env.DATABASE_URL!, schema);

    const [entitlements, plans] = await Promise.all([
        getEntitlements(user.id, db),
        getStripePlans(),
    ]);

    const params = await searchParams;
    const successMessage = params.success
        ? 'Your subscription has been activated!'
        : params.cancelled
            ? 'Checkout was cancelled — no charge was made.'
            : null;

    return (
        <div className="animate-fadeIn space-y-8">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Billing</h1>
                <p className="mt-1 text-sm text-gray-500">
                    Manage your subscription and billing information
                </p>
            </div>

            {successMessage && (
                <div
                    className={`rounded-lg px-4 py-3 text-sm ${params.success
                        ? 'bg-green-50 text-green-700'
                        : 'bg-amber-50 text-amber-700'
                        }`}
                >
                    {successMessage}
                </div>
            )}

            <BillingClient entitlements={entitlements} plans={plans} />
        </div>
    );
}