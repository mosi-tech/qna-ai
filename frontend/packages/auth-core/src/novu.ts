import { Novu } from '@novu/api';
import crypto from 'crypto';

// ─── Singleton Novu instance ──────────────────────────────────────────────────

let _novu: Novu | null = null;

function getNovu(): Novu | null {
    if (!process.env.NOVU_API_KEY) return null;
    if (!_novu) {
        _novu = new Novu({ secretKey: process.env.NOVU_API_KEY });
    }
    return _novu;
}

// ─── Subscriber shape ─────────────────────────────────────────────────────────

interface Subscriber {
    subscriberId: string;
    email?: string;
    firstName?: string;
    lastName?: string;
}

type ToParam = string | Subscriber;

// ─── Core trigger helper ──────────────────────────────────────────────────────

/**
 * Fires a Novu workflow event. No-ops gracefully if NOVU_API_KEY is not set.
 * All errors are swallowed so notification failures never break app logic.
 */
async function trigger(
    workflowId: string,
    to: ToParam,
    payload: Record<string, unknown> = {},
): Promise<void> {
    const novu = getNovu();
    if (!novu) return;

    try {
        await novu.trigger({ workflowId, to, payload });
    } catch (err) {
        console.error(`[novu] failed to trigger "${workflowId}":`, err);
    }
}

// ─── HMAC subscriber hash (for Novu inbox security) ──────────────────────────

/**
 * Generates the HMAC-SHA256 subscriber hash required by @novu/react to verify
 * that the subscriberId has not been tampered with on the client.
 *
 * Set NOVU_SECRET_HASH_KEY in .env.local to the value from Novu dashboard
 * → Settings → In-App → Security Mode.
 */
export function generateSubscriberHash(subscriberId: string): string | null {
    const secret = process.env.NOVU_SECRET_HASH_KEY;
    if (!secret) return null;
    return crypto.createHmac('sha256', secret).update(subscriberId).digest('hex');
}

// ─── Typed trigger functions ──────────────────────────────────────────────────

export async function triggerWelcome(
    userId: string,
    email: string,
    name: string,
): Promise<void> {
    await trigger('welcome', { subscriberId: userId, email }, { name, email });
}

export async function triggerEmailVerify(
    userId: string,
    email: string,
): Promise<void> {
    await trigger('email-verify', { subscriberId: userId, email }, { email });
}

export async function triggerPaymentFailed(
    userId: string,
    email: string,
): Promise<void> {
    await trigger('payment-failed', { subscriberId: userId, email }, { email });
}

export async function triggerSubscriptionActivated(
    userId: string,
    email: string,
    planName: string,
): Promise<void> {
    await trigger(
        'subscription-activated',
        { subscriberId: userId, email },
        { email, planName },
    );
}

export async function triggerSubscriptionCancelled(
    userId: string,
    email: string,
    planName: string,
): Promise<void> {
    await trigger(
        'subscription-cancelled',
        { subscriberId: userId, email },
        { email, planName },
    );
}

export async function triggerUsage80Pct(
    userId: string,
    email: string,
    eventType: string,
    used: number,
    limit: number,
): Promise<void> {
    await trigger(
        'usage-80pct',
        { subscriberId: userId, email },
        { email, eventType, used, limit, percentUsed: Math.round((used / limit) * 100) },
    );
}

export async function triggerUsageExceeded(
    userId: string,
    eventType: string,
): Promise<void> {
    await trigger('usage-exceeded', userId, { eventType });
}

export async function triggerTrialEnding(
    userId: string,
    email: string,
    trialEnd: Date,
): Promise<void> {
    await trigger(
        'trial-ending',
        { subscriberId: userId, email },
        { email, trialEnd: trialEnd.toISOString(), daysRemaining: 3 },
    );
}
