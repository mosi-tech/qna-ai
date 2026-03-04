import { stripe, getStripePlans, type StripePlan } from '../stripe';
import { createDb } from '../db/index';
import * as schema from '../db/schema';
import { subscriptions } from '../db/schema';
import { inArray, count } from 'drizzle-orm';

export const metadata = { title: 'Revenue — Admin' };
export const dynamic = 'force-dynamic';

interface InvoiceRow {
    id: string;
    customerEmail: string;
    amount: number;
    currency: string;
    status: string;
    period: string;
    planName: string;
}

function formatCurrency(cents: number, currency = 'usd') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency.toUpperCase(),
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(cents / 100);
}

function formatDate(ts: number) {
    return new Date(ts * 1000).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });
}

const INVOICE_STATUS_COLORS: Record<string, string> = {
    paid: 'bg-green-50 text-green-700',
    open: 'bg-amber-50 text-amber-700',
    void: 'bg-gray-50 text-gray-500',
    uncollectible: 'bg-red-50 text-red-600',
};

export default async function AdminRevenuePage() {
    const db = createDb(process.env.DATABASE_URL!, schema);

    const [planCounts, stripeData, stripePlansResult] = await Promise.allSettled([
        db
            .select({ plan_name: subscriptions.plan_key, count: count() })
            .from(subscriptions)
            .where(inArray(subscriptions.status, ['active', 'trialing']))
            .groupBy(subscriptions.plan_key),
        stripe.invoices.list({ limit: 50, status: 'paid' }),
        getStripePlans(),
    ]);

    const stripePlans: StripePlan[] =
        stripePlansResult.status === 'fulfilled' ? stripePlansResult.value : [];

    const priceToplanName: Record<string, string> = {};
    for (const plan of stripePlans) {
        for (const p of plan.prices) {
            priceToplanName[p.priceId] = plan.name;
        }
    }

    const planCountMap: Record<string, number> = {};
    if (planCounts.status === 'fulfilled') {
        for (const row of planCounts.value) {
            planCountMap[row.plan_name] = Number(row.count);
        }
    }

    let mrr = 0;
    for (const plan of stripePlans) {
        const monthlyPrice = plan.prices.find((p) => p.interval === 'month')?.amount ?? 0;
        if (!monthlyPrice) continue;
        mrr += (planCountMap[plan.planKey] ?? 0) * monthlyPrice;
    }

    const invoices: InvoiceRow[] = [];
    let stripeRevenue30d = 0;
    if (stripeData.status === 'fulfilled') {
        const now = Date.now() / 1000;
        const thirtyDaysAgo = now - 30 * 24 * 60 * 60;
        for (const inv of stripeData.value.data) {
            const customerEmail =
                typeof inv.customer_email === 'string' ? inv.customer_email : '(unknown)';
            const lineItem = inv.lines?.data?.[0];
            const priceId = lineItem?.price?.id ?? '';
            invoices.push({
                id: inv.id,
                customerEmail,
                amount: inv.amount_paid,
                currency: inv.currency,
                status: inv.status ?? 'unknown',
                period: inv.created ? formatDate(inv.created) : '—',
                planName: priceToplanName[priceId] ?? 'Unknown',
            });
            if (inv.created && inv.created >= thirtyDaysAgo) {
                stripeRevenue30d += inv.amount_paid;
            }
        }
    }

    const activeSubscribers = Object.values(planCountMap).reduce((a, b) => a + b, 0);

    const kpis = [
        {
            label: 'Estimated MRR',
            value: formatCurrency(mrr),
            sub: 'Based on active plan counts',
        },
        {
            label: 'Revenue (30d)',
            value: formatCurrency(stripeRevenue30d),
            sub: 'From Stripe paid invoices',
        },
        {
            label: 'Active Subscribers',
            value: activeSubscribers.toLocaleString(),
            sub: 'Active + trialing',
        },
        {
            label: 'Avg. Revenue / User',
            value: activeSubscribers > 0 ? formatCurrency(mrr / activeSubscribers) : '$0',
            sub: 'MRR ÷ subscribers',
        },
    ];

    const planBreakdown = stripePlans
        .filter((p) => p.planKey !== 'free')
        .map((p) => {
            const monthlyPrice =
                p.prices.find((pr) => pr.interval === 'month')?.amount ?? 0;
            return {
                id: p.planKey,
                name: p.name,
                count: planCountMap[p.planKey] ?? 0,
                monthlyRevenue: (planCountMap[p.planKey] ?? 0) * monthlyPrice,
            };
        });

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Revenue</h1>
                <p className="mt-1 text-sm text-gray-500">
                    MRR estimates, plan breakdown, and recent Stripe invoices
                </p>
            </div>

            {/* KPI row */}
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                {kpis.map((kpi) => (
                    <div
                        key={kpi.label}
                        className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
                    >
                        <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                            {kpi.label}
                        </p>
                        <p className="mt-2 text-3xl font-bold tabular-nums text-gray-900">
                            {kpi.value}
                        </p>
                        <p className="mt-1 text-xs text-gray-400">{kpi.sub}</p>
                    </div>
                ))}
            </div>

            {/* Plan breakdown */}
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                <h2 className="mb-4 text-base font-semibold text-gray-900">Plan Breakdown</h2>
                <div className="space-y-4">
                    {planBreakdown.map((plan) => {
                        const mrrShare = mrr > 0 ? (plan.monthlyRevenue / mrr) * 100 : 0;
                        return (
                            <div key={plan.id}>
                                <div className="mb-1.5 flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <span
                                            className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${plan.id === 'pro'
                                                    ? 'bg-indigo-50 text-indigo-700'
                                                    : 'bg-purple-50 text-purple-700'
                                                }`}
                                        >
                                            {plan.name}
                                        </span>
                                        <span className="text-sm text-gray-600">
                                            {plan.count.toLocaleString()} subscriber
                                            {plan.count !== 1 ? 's' : ''}
                                        </span>
                                    </div>
                                    <span className="text-sm font-semibold tabular-nums text-gray-900">
                                        {formatCurrency(plan.monthlyRevenue)}
                                        <span className="ml-1 text-xs font-normal text-gray-400">/mo</span>
                                    </span>
                                </div>
                                <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
                                    <div
                                        className={`h-full rounded-full ${plan.id === 'pro' ? 'bg-indigo-500' : 'bg-purple-500'
                                            }`}
                                        style={{ width: `${mrrShare}%` }}
                                    />
                                </div>
                            </div>
                        );
                    })}
                    {planBreakdown.every((p) => p.count === 0) && (
                        <p className="py-4 text-center text-sm text-gray-400">
                            No paid subscribers yet.
                        </p>
                    )}
                </div>
            </div>

            {/* Recent invoices */}
            <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
                <div className="border-b border-gray-100 px-6 py-4">
                    <h2 className="text-base font-semibold text-gray-900">Recent Paid Invoices</h2>
                    <p className="mt-0.5 text-xs text-gray-400">Last 50 paid invoices from Stripe</p>
                </div>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-50">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    Customer
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    Plan
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    Amount
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    Status
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                                    Date
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                            {invoices.length === 0 ? (
                                <tr>
                                    <td
                                        colSpan={5}
                                        className="py-10 text-center text-sm text-gray-400"
                                    >
                                        {stripeData.status === 'rejected'
                                            ? 'Failed to load invoices from Stripe — check STRIPE_SECRET_KEY.'
                                            : 'No paid invoices found.'}
                                    </td>
                                </tr>
                            ) : (
                                invoices.map((inv) => (
                                    <tr
                                        key={inv.id}
                                        className="transition-colors hover:bg-gray-50"
                                    >
                                        <td className="px-4 py-3 text-sm text-gray-700">
                                            {inv.customerEmail}
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="text-xs text-gray-500">
                                                {inv.planName}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-sm font-semibold tabular-nums text-gray-900">
                                            {formatCurrency(inv.amount, inv.currency)}
                                        </td>
                                        <td className="px-4 py-3">
                                            <span
                                                className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${INVOICE_STATUS_COLORS[inv.status] ?? 'bg-gray-100 text-gray-600'}`}
                                            >
                                                {inv.status.charAt(0).toUpperCase() +
                                                    inv.status.slice(1)}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-xs text-gray-500">
                                            {inv.period}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
