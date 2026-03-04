'use client';

/**
 * BuilderApp.tsx
 *
 * Full-screen AI Dashboard Builder. Split-panel layout:
 *   LEFT  (~36%): Chat interface
 *   RIGHT (~64%): Dashboard canvas — blocks materialise progressively
 *
 * Flow:
 *  1. User submits prompt → buildDashboardSpec() via /api/ollama
 *  2. Spec returned → each block enters 'loading' state
 *  3. Each block calls fetchMockData() with staggered latency (~300–1200ms)
 *  4. As each resolves the block hydrates — "cards popping in" effect
 */

import React, { useState, useCallback } from 'react';
import ChatPanel, { type ChatMessage } from './ChatPanel';
import DashboardCanvas, { type BlockState } from './DashboardCanvas';
import { buildDashboardSpec, type DashboardSpec } from '@/services/dashboardAI';
import { fetchMockData } from '@/services/mockDataService';

function uid() {
    return Math.random().toString(36).slice(2, 9);
}

export default function BuilderApp() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [spec, setSpec] = useState<DashboardSpec | null>(null);
    const [blockStates, setBlockStates] = useState<BlockState[]>([]);
    const [specLoading, setSpecLoading] = useState(false);
    const [specError, setSpecError] = useState<string | undefined>();

    const handleSend = useCallback(async (text: string) => {
        const assistantId = uid();
        setMessages((prev) => [
            ...prev,
            { id: uid(), role: 'user', content: text },
            { id: assistantId, role: 'assistant', content: '', loading: true },
        ]);

        setSpec(null);
        setBlockStates([]);
        setSpecError(undefined);
        setSpecLoading(true);

        let dashSpec: DashboardSpec;
        try {
            dashSpec = await buildDashboardSpec(text);
        } catch (err: any) {
            const msg = err?.message ?? 'Unknown error from AI service';
            setMessages((prev) =>
                prev.map((m) => m.id === assistantId ? { ...m, loading: false, error: msg } : m),
            );
            setSpecLoading(false);
            setSpecError(msg);
            return;
        }

        const blockList = dashSpec.blocks.map((b) => `• ${b.title} (${b.blockId})`).join('\n');
        setMessages((prev) =>
            prev.map((m) =>
                m.id === assistantId
                    ? {
                        ...m,
                        loading: false,
                        content: `Here's your **${dashSpec.title}** dashboard with ${dashSpec.blocks.length} components:\n\n${blockList}\n\nFetching live data for each block…`,
                    }
                    : m,
            ),
        );

        const initial: BlockState[] = dashSpec.blocks.map((b) => ({ spec: b, loadState: 'loading' }));
        setSpec(dashSpec);
        setBlockStates(initial);
        setSpecLoading(false);

        dashSpec.blocks.forEach((block, idx) => {
            fetchMockData(block)
                .then((data) => {
                    setBlockStates((prev) =>
                        prev.map((bs, i) => i === idx ? { ...bs, loadState: 'loaded', data } : bs),
                    );
                })
                .catch((err: any) => {
                    setBlockStates((prev) =>
                        prev.map((bs, i) =>
                            i === idx ? { ...bs, loadState: 'error', error: err?.message ?? 'Data fetch failed' } : bs,
                        ),
                    );
                });
        });
    }, []);

    const isLoading = specLoading || blockStates.some((bs) => bs.loadState === 'loading');

    return (
        <div className="flex flex-col flex-1 min-h-0 overflow-hidden bg-slate-50 dark:bg-slate-950">
            {/* Header */}
            <header className="flex-shrink-0 h-12 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center px-4 gap-3">
                <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-violet-500 to-blue-600 flex items-center justify-center text-white text-xs font-bold">
                    ✦
                </div>
                <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">AI Dashboard Builder</span>
                <div className="ml-auto flex items-center gap-3">
                    {isLoading && (
                        <span className="flex items-center gap-1.5 text-xs text-blue-500 dark:text-blue-400">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                            Working…
                        </span>
                    )}
                    <span className="text-xs text-slate-400 dark:text-slate-600 hidden sm:block">
                        Powered by glm-4.7:cloud · base-ui blocks
                    </span>
                </div>
            </header>

            {/* Split panel */}
            <div className="flex flex-1 min-h-0 overflow-hidden">
                {/* Left: Chat */}
                <div
                    className="flex-shrink-0 border-r border-slate-200 dark:border-slate-700 overflow-hidden flex flex-col"
                    style={{ width: '36%', minWidth: 320 }}
                >
                    <ChatPanel messages={messages} onSend={handleSend} isLoading={specLoading} />
                </div>

                {/* Right: Dashboard canvas */}
                <div className="flex-1 overflow-y-auto bg-slate-50 dark:bg-slate-950">
                    <DashboardCanvas
                        spec={spec}
                        blockStates={blockStates}
                        specLoading={specLoading}
                        specError={specError}
                    />
                </div>
            </div>
        </div>
    );
}
