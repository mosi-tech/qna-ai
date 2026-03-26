/**
 * /api/headless/stream
 *
 * SSE variant of /api/headless/run.
 * Runs the same Python orchestrator but streams the result back block-by-block:
 *
 *   data: {"event":"spec",  "title":"...", "rows":[...], "blocks":[...], "elapsed_s":0}
 *   data: {"event":"block", "blockId":"FKMetricGrid", "data":{...}}
 *   data: {"event":"block", "blockId":"FKLineChart",  "data":{...}}
 *   ...
 *   data: {"event":"done",  "elapsed_s":2.3, "steps":[...]}
 *   data: {"event":"error", "message":"..."}   ← only on failure
 */

import { NextRequest } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

export const runtime = 'nodejs';
export const maxDuration = 600;

const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));
const enc   = new TextEncoder();
const sse   = (obj: object) => enc.encode(`data: ${JSON.stringify(obj)}\n\n`);

export async function POST(request: NextRequest) {
    const body                                          = await request.json();
    const { question, mock = true, mockV2 = false, skipReuse = true, mcpLive = false, mcpScript = false, pipeline = false, blockDelay = 300 } = body;

    if (!question) {
        return new Response('question required', { status: 400 });
    }

    // ── Resolve paths ────────────────────────────────────────────────────────
    const scriptPath = path.join(process.cwd(), '..', '..', '..', 'backend', 'headless', 'agents', 'orchestrator.py');
    const backendDir = path.resolve(path.join(process.cwd(), '..', '..', '..', 'backend'));

    const envVars: Record<string, string> = {};
    const envPath = path.join(backendDir, 'apiServer', '.env');
    if (fs.existsSync(envPath)) {
        fs.readFileSync(envPath, 'utf-8').split('\n').forEach(line => {
            const m = line.match(/^([^#][^=]+)=(.*)/);
            if (m) envVars[m[1].trim()] = m[2].trim().replace(/^["']|["']$/g, '');
        });
    }

    // ── Build orchestrator args ───────────────────────────────────────────────
    const args = [scriptPath, '--question', question, '--skip-enhancement'];
    if (mock)       args.push('--mock');
    if (mockV2)     args.push('--mock-v2');
    if (skipReuse)  args.push('--skip-reuse');
    if (mcpLive)    args.push('--mcp-live');
    if (mcpScript)  args.push('--mcp-script');
    if (pipeline)   args.push('--pipeline');

    // ── SSE stream ────────────────────────────────────────────────────────────
    const stream = new ReadableStream({
        start(controller) {
            let stdout = '';
            let stderr = '';

            const python = spawn('python3', args, {
                env: {
                    ...process.env,
                    ...envVars,
                    PYTHONPATH: backendDir,
                    UI_PLANNER_LLM_MODEL: 'gpt-oss:20b',
                    // HTTP Toolkit proxy — captures all LLM traffic
                    HTTP_PROXY:  'http://localhost:8000',
                    HTTPS_PROXY: 'http://localhost:8000',
                    REQUESTS_CA_BUNDLE: `${process.env.HOME}/.httptoolkit-ca.pem`,
                    SSL_CERT_FILE:      `${process.env.HOME}/.httptoolkit-ca.pem`,
                },
                cwd: backendDir,
            });

            python.stdout.on('data', (d: Buffer) => { stdout += d.toString(); });
            python.stderr.on('data', (d: Buffer) => { stderr += d.toString(); });

            python.on('close', async (code: number | null) => {
                if (code !== 0) {
                    controller.enqueue(sse({ event: 'error', message: stderr.split('\n').filter(Boolean).slice(-3).join(' | ') }));
                    controller.close();
                    return;
                }

                try {
                    const lines     = stdout.trim().split('\n');
                    const jsonStart = lines.findIndex(l => l.trim().startsWith('{'));
                    if (jsonStart === -1) throw new Error('No JSON in orchestrator output');
                    const result    = JSON.parse(lines.slice(jsonStart).join('\n'));

                    // 1. Emit spec — all layout/block metadata, no data yet
                    controller.enqueue(sse({
                        event:    'spec',
                        title:    result.title,
                        rows:     result.rows     || [],
                        blocks:   result.blocks   || [],
                        steps:    result.steps    || [],
                        elapsed_s: result.total_time,
                    }));

                    // 2. Emit each block's data with a configurable delay
                    const blocksData: Array<{ blockId: string; data: any }> = result.blocks_data || [];
                    for (const block of blocksData) {
                        await sleep(blockDelay);
                        controller.enqueue(sse({
                            event:   'block',
                            blockId: block.blockId,
                            data:    block.data ?? null,
                        }));
                    }

                    // 3. Done
                    controller.enqueue(sse({ event: 'done', elapsed_s: result.total_time }));
                    controller.close();
                } catch (e) {
                    controller.enqueue(sse({ event: 'error', message: String(e) }));
                    controller.close();
                }
            });
        },
    });

    return new Response(stream, {
        headers: {
            'Content-Type':  'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection':    'keep-alive',
        },
    });
}
