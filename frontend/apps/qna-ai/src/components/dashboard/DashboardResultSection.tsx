'use client';

/**
 * Phase 8 — DashboardResultSection
 *
 * Renders a live dashboard instead of the legacy single-result view when a
 * chat message carries a `dashboard_id` in its `data` field.
 *
 * Lifecycle:
 *  1. Mount: build initial BlockState array from `initialPlan.blocks`.
 *            Blocks whose status is "cached" or "complete" start as "loaded";
 *            everything else starts as "loading".
 *  2. SSE:   `useBlockUpdates` listens for `block_update` events and flips
 *            individual blocks from "loading" → "loaded" as results arrive.
 *  3. Render: `DashboardCanvas` (from @ui-gen/base-ui) paints blocks
 *             progressively.
 *
 * SessionId is obtained from the nearest `SessionContext` rather than being
 * threaded through ChatMessage → ChatInterface → DashboardResultSection — this
 * keeps the ChatMessage prop surface unchanged.
 */

import React, { useState, useCallback } from 'react';
import { DashboardCanvas } from '@ui-gen/base-ui';
import type { BlockState, DashboardSpec } from '@ui-gen/base-ui';
import { useSession } from '@/lib/context/SessionContext';
import { useBlockUpdates } from '@/lib/hooks/useBlockUpdates';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Shape of a block entry as returned by POST /api/dashboard/create. */
interface InitialBlock {
    block_id: string;
    status: string;       // "cached" | "complete" | "pending" | "running" | "failed"
    result_data?: Record<string, unknown>;
    [key: string]: unknown;
}

/** Superset of DashboardSpec — adds the per-block persistence fields. */
type InitialPlan = DashboardSpec & {
    dashboard_id: string;
    blocks: InitialBlock[];
};

interface DashboardResultSectionProps {
    dashboardId: string;
    initialPlan: InitialPlan;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function DashboardResultSection({
    dashboardId,
    initialPlan,
}: DashboardResultSectionProps) {
    const { session_id } = useSession();

    const [blockStates, setBlockStates] = useState<BlockState[]>(() =>
        initialPlan.blocks.map((b) => ({
            spec: b as BlockState['spec'],
            loadState: (b.status === 'cached' || b.status === 'complete') ? 'loaded' : 'loading',
            data: b.result_data ?? undefined,
        })),
    );

    const handleBlockUpdate = useCallback(
        (blockId: string, resultData: Record<string, unknown>) => {
            setBlockStates((prev) =>
                prev.map((bs) =>
                    (bs.spec as InitialBlock).block_id === blockId
                        ? { ...bs, loadState: 'loaded' as const, data: resultData }
                        : bs,
                ),
            );
        },
        [],
    );

    useBlockUpdates(session_id ?? '', dashboardId, handleBlockUpdate);

    return (
        <DashboardCanvas
            spec={initialPlan}
            blockStates={blockStates}
            specLoading={false}
        />
    );
}
