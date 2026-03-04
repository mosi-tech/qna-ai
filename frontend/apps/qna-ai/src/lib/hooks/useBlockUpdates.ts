import { useEffect } from 'react';

/**
 * Phase 8 — useBlockUpdates
 *
 * Subscribes to the existing SSE stream (relayed via the `sse_event` window
 * CustomEvent published by `useProgressStream`) and calls `onBlockUpdate`
 * whenever a `block_update` event arrives for the given `dashboardId`.
 *
 * This hook attaches to the window event bus instead of opening its own
 * EventSource, so there is zero extra network overhead.
 *
 * @param sessionId  The chat session ID (used as a dependency guard only).
 * @param dashboardId  The dashboard whose blocks we are tracking.
 * @param onBlockUpdate  Stable callback (wrap in useCallback) to avoid
 *                       unbounded re-registration.
 */
export function useBlockUpdates(
    sessionId: string,
    dashboardId: string,
    onBlockUpdate: (blockId: string, resultData: Record<string, unknown>) => void,
): void {
    useEffect(() => {
        const handler = (event: CustomEvent) => {
            const data = event.detail;
            if (
                data?.type === 'block_update' &&
                data?.dashboard_id === dashboardId &&
                data?.status === 'complete'
            ) {
                onBlockUpdate(data.block_id as string, data.result_data as Record<string, unknown>);
            }
        };

        window.addEventListener('sse_event', handler as EventListener);
        return () => window.removeEventListener('sse_event', handler as EventListener);
    }, [sessionId, dashboardId, onBlockUpdate]);
}
