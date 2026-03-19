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

import React, { useState, useCallback, useEffect } from 'react';
import ChatPanel, { type ChatMessage } from './ChatPanel';
import DashboardCanvas, { type BlockState } from './DashboardCanvas';
import { buildDashboardSpec, runHeadlessPipeline, headlessResultToSpec, type DashboardSpec, type HeadlessResult } from '@/services/dashboardAI';
import { fetchMockData } from '@/services/mockDataService';

type BlockLoadState = 'idle' | 'loading' | 'loaded' | 'error' | 'cached';

function uid() {
    return Math.random().toString(36).slice(2, 9);
}

export default function BuilderApp() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [spec, setSpec] = useState<DashboardSpec | null>(null);
    const [blockStates, setBlockStates] = useState<BlockState[]>([]);
    const [specLoading, setSpecLoading] = useState(false);
    const [specError, setSpecError] = useState<string | undefined>();
    const [mockMode, setMockMode] = useState(true);
    const [skipReuse, setSkipReuse] = useState(true);

    const handleSend = useCallback(async (text: string) => {
        const assistantId = uid();
        setMessages((prev) => [
            ...prev,
            { id: uid(), role: 'user', content: text },
            { id: assistantId, role: 'assistant', content: 'Running headless pipeline...', loading: true },
        ]);

        setSpec(null);
        setBlockStates([]);
        setSpecError(undefined);
        setSpecLoading(true);

        let headlessResult: HeadlessResult;
        try {
            headlessResult = await runHeadlessPipeline(text, { useNoCode: true, mock: mockMode, skipReuse });
        } catch (err: any) {
            const msg = err?.message ?? 'Unknown error from headless pipeline';
            setMessages((prev) =>
                prev.map((m) => m.id === assistantId ? { ...m, loading: false, error: msg } : m),
            );
            setSpecLoading(false);
            setSpecError(msg);
            return;
        }

        const dashSpec = headlessResultToSpec(headlessResult);
        const blockList = dashSpec.blocks.map((b) => `• ${b.title} (${b.blockId})`).join('\n');
        const statusBadge = headlessResult.status === 'cached' ? ' (cached)' : '';
        const summary = `Generated in ${headlessResult.elapsed_s.toFixed(1)}s${statusBadge}`;

        // Debug: Log data structures
        console.log('[BuilderApp] Result received:', {
            status: headlessResult.status,
            ui_blocks_count: headlessResult.ui_blocks?.length || 0,
            blocks_data_count: headlessResult.blocks_data?.length || 0,
            blocks_data_sample: headlessResult.blocks_data?.[0] ? {
                block_id: headlessResult.blocks_data[0].block_id,
                has_data: headlessResult.blocks_data[0].data !== undefined,
                data_keys: headlessResult.blocks_data[0].data ? Object.keys(headlessResult.blocks_data[0].data) : [],
            } : null,
        });

        // Build steps summary for display
        let stepsContent = '';
        if (headlessResult.steps && headlessResult.steps.length > 0) {
            const stepsList = headlessResult.steps.map((step, idx) => {
                const icon = step.success ? '✅' : '❌';
                return `${icon} ${idx + 1}. ${step.step.replace(/_/g, ' ')} (${step.duration.toFixed(2)}s)`;
            }).join('\n');
            stepsContent = `\n\n**Pipeline Steps:**\n${stepsList}`;
        }

        setMessages((prev) =>
            prev.map((m) =>
                m.id === assistantId
                    ? {
                        ...m,
                        loading: false,
                        content: `Here's your **${dashSpec.title}** dashboard with ${dashSpec.blocks.length} components:\n\n${blockList}\n\n${summary}${stepsContent}`,
                    }
                    : m,
            ),
        );

        // Create block states based on headless result status
        const uiBlocks = headlessResult.ui_blocks || [];
        const blocksData = headlessResult.blocks_data || [];

        console.log('[BuilderApp] Matching blocks to data:');
        console.log('  dashSpec.blocks:', dashSpec.blocks.map(b => b.blockId));
        console.log('  blocksData:', blocksData.map(b => b.block_id));

        const initial: BlockState[] = dashSpec.blocks.map((blockSpec, idx) => {
            // Find matching data by blockId
            const backendBlock = blocksData.find(b => b.block_id === blockSpec.blockId);
            if (!backendBlock) {
                console.warn(`[BuilderApp] No data found for block ${blockSpec.blockId}`);
            } else {
                console.log(`[BuilderApp] ✓ Matched ${blockSpec.blockId} with data`);
            }

            // Also check if there's a matching UI block
            const uiBlock = uiBlocks.find(b => b.blockId === blockSpec.blockId);

            let loadState: BlockLoadState = headlessResult.status === 'cached' ? 'loaded' : 'loading';
            let data: Record<string, unknown> | undefined;
            let error: string | undefined;

            if (backendBlock) {
                if (backendBlock.status === 'complete' && backendBlock.has_result) {
                    loadState = 'loaded';
                    // Use actual data from backend
                    data = backendBlock.data as Record<string, unknown>;
                } else if (backendBlock.status === 'failed') {
                    loadState = 'error';
                    error = backendBlock.error || 'Analysis failed';
                }
            } else if (uiBlock) {
                // No data but UI block exists - keep as loading or mark as failed
                loadState = 'loading';
                error = undefined;
            } else {
                // No matching block
                loadState = 'error';
                error = 'Block not found';
            }

            return { spec: blockSpec, loadState, data, error };
        });

        setSpec(dashSpec);
        setBlockStates(initial);
        setSpecLoading(false);
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
                    <label className="flex items-center gap-1.5 cursor-pointer group">
                        <input
                            type="checkbox"
                            checked={mockMode}
                            onChange={(e) => setMockMode(e.target.checked)}
                            className="sr-only peer"
                        />
                        <div className="relative w-8 h-4 bg-slate-200 dark:bg-slate-700 rounded-full peer peer-checked:bg-amber-500 transition-colors">
                            <div className={`absolute top-0.5 left-0.5 w-3 h-3 bg-white rounded-full transition-transform ${mockMode ? 'translate-x-4' : ''}`} />
                        </div>
                        <span className="text-xs font-medium text-slate-600 dark:text-slate-400 group-hover:text-slate-800 dark:group-hover:text-slate-200">
                            Mock
                        </span>
                    </label>
                    <label className="flex items-center gap-1.5 cursor-pointer group">
                        <input
                            type="checkbox"
                            checked={skipReuse}
                            onChange={(e) => setSkipReuse(e.target.checked)}
                            className="sr-only peer"
                        />
                        <div className="relative w-8 h-4 bg-slate-200 dark:bg-slate-700 rounded-full peer peer-checked:bg-orange-500 transition-colors">
                            <div className={`absolute top-0.5 left-0.5 w-3 h-3 bg-white rounded-full transition-transform ${skipReuse ? 'translate-x-4' : ''}`} />
                        </div>
                        <span className="text-xs font-medium text-slate-600 dark:text-slate-400 group-hover:text-slate-800 dark:group-hover:text-slate-200">
                            Skip Cache
                        </span>
                    </label>
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
