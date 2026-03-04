/**
 * app/api/ollama/route.ts
 *
 * Server-side proxy to Ollama API.
 * The API key stays server-only (OLLAMA_API_KEY — no NEXT_PUBLIC_ prefix),
 * never exposed to the browser.
 *
 * POST /api/ollama
 * Body: same JSON shape you'd send to Ollama's /api/chat
 *
 * Usage is recorded to auth-hub on every successful response.
 * The userId is injected by middleware via the x-user-id header.
 */

import { NextRequest, NextResponse } from 'next/server';
import { recordUsageEvent } from '@ui-gen/auth-core/entitlements';
import { db } from '../../../lib/db';

const OLLAMA_URL = 'https://ollama.com/api/chat';

export async function POST(req: NextRequest) {
    const apiKey = process.env.OLLAMA_API_KEY;

    if (!apiKey) {
        // Signal to the client to use the local fallback
        return NextResponse.json({ error: 'NO_API_KEY' }, { status: 503 });
    }

    // userId injected by middleware — present when user is authenticated
    const userId = req.headers.get('x-user-id');

    let body: unknown;
    try {
        body = await req.json();
    } catch {
        return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
    }

    try {
        const upstream = await fetch(OLLAMA_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${apiKey}`,
            },
            body: JSON.stringify(body),
        });

        const data = await upstream.json();

        if (!upstream.ok) {
            return NextResponse.json(data, { status: upstream.status });
        }

        // Record usage after successful AI build (fire-and-forget, never throws)
        if (userId) {
            void recordUsageEvent(userId, 'ai-builder', 'ai_builds', 1, db, {
                model: (body as Record<string, unknown>)?.model,
            });
        }

        return NextResponse.json(data);
    } catch (err: any) {
        console.error('[/api/ollama] Upstream fetch failed:', err?.message);
        return NextResponse.json(
            { error: 'Upstream request failed', detail: err?.message },
            { status: 502 },
        );
    }
}
