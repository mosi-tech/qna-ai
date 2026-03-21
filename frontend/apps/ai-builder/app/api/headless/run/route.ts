import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export const runtime = 'nodejs';
export const maxDuration = 600; // 10 minutes max for pipeline execution

interface OrchestratorOutput {
    success: boolean;
    action: 'generated' | 'mcp_direct' | 'mock_generated' | 'mock_reused';
    title?: string;
    blocks?: Array<{
        blockId: string;
        category: string;
        title: string;
        dataContract: any;
        sub_question?: string;
        canonical_params?: any;
    }>;
    blocks_data?: Array<{
        blockId: string;
        data?: any;
    }>;
    layout?: {
        templateId: string;
        slots: Record<string, any>;
    };
    mock_data_file?: string;
    similarity?: number;
    total_time: number;
    steps: Array<{
        step: string;
        success: boolean;
        duration: number;
    }>;
    error?: string;
    timestamp: string;
}

interface HeadlessBlockData {
    block_id: string;
    title: string;
    status: string;
    has_result: boolean;
    data?: any;
    error?: string;
}

interface HeadlessResult {
    question: string;
    cache_key: string;
    status: 'generated' | 'cached' | 'mock_generated' | 'mock_reused' | 'failed';
    analysis_id?: string;
    execution_id?: string;
    elapsed_s: number;
    total_elapsed_s: number;
    blocks: number;
    blocks_data?: Array<{
        block_id: string;
        title: string;
        status: string;
        data?: any;
    }>;
    // Include original blocks array from UI Planner
    ui_blocks?: Array<{
        blockId: string;
        category: string;
        title: string;
        dataContract: any;
        sub_question?: string;
        canonical_params?: any;
    }>;
    // Grid layout from orchestrator
    layout?: {
        templateId: string;
        slots: Record<string, any>;
    };
    plan_title?: string;
    mock_data_file?: string;
    similarity?: number;
    error?: string;
    steps?: Array<{
        step: string;
        success: boolean;
        duration: number;
    }>;
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { question, useNoCode, mock, mockV2, skipReuse } = body;

        if (!question || typeof question !== 'string') {
            return NextResponse.json({ error: 'question is required' }, { status: 400 });
        }

        // Debug logging with timestamp
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] [headless/run] POST received:`, { question: question.substring(0, 80), useNoCode, mock, mockV2, skipReuse });

        // Path to the new orchestrator script
        const scriptPath = path.join(
            process.cwd(),
            '..',
            '..',
            '..',
            'backend',
            'headless',
            'agents',
            'orchestrator.py'
        );

        // Get absolute path to backend directory
        const backendDir = path.resolve(
            path.join(
                process.cwd(),
                '..',
                '..',
                '..',
                'backend'
            )
        );

        // Load environment variables from backend .env file
        const fs = require('fs');
        const envPath = path.join(backendDir, 'apiServer', '.env');
        const envVars: Record<string, string> = {};

        if (fs.existsSync(envPath)) {
            const envContent = fs.readFileSync(envPath, 'utf-8');
            envContent.split('\n').forEach(line => {
                const match = line.match(/^([^#][^=]+)=(.*)$/);
                if (match) {
                    const [, key, value] = match;
                    // Remove quotes from value if present
                    const cleanValue = value.trim().replace(/^["']|["']$/g, '');
                    envVars[key.trim()] = cleanValue;
                }
            });
        }

        // Build command arguments
        const args = [
            scriptPath,
            '--question',
            question
        ];

        if (useNoCode) {
            args.push('--no-code');
        }

        if (mock) {
            args.push('--mock');
        }

        if (mockV2) {
            args.push('--mock-v2');
            console.log(`[${timestamp}] [headless/run] 🔄 Decomposition Mode ENABLED (breaks question into sub-Qs)`);
        }

        if (skipReuse) {
            args.push('--skip-reuse');
            console.log(`[${timestamp}] [headless/run] ⚠️  SKIP CACHE ENABLED`);
        }

        // Use fast settings: skip enhancement and fast model
        args.push('--skip-enhancement');

        console.log(`[${timestamp}] [headless/run] Executing orchestrator with args:`, args.slice(1).join(' '));

        // Spawn Python process
        const python = spawn('python3', args, {
            env: {
                ...process.env,
                ...envVars, // Pass backend .env variables
                PYTHONPATH: backendDir, // Ensure Python can find the backend modules
                // Use fast model for ui_planner
                UI_PLANNER_LLM_MODEL: 'gpt-oss:20b',
            },
            cwd: backendDir, // Set working directory to backend so .env loads correctly
        });

        let stdout = '';
        let stderr = '';

        python.stdout.on('data', (data: Buffer) => {
            stdout += data.toString();
        });

        python.stderr.on('data', (data: Buffer) => {
            stderr += data.toString();
            // Log stderr for debugging but don't include in response
            console.error('[headless run]', data.toString());
        });

        return new Promise<NextResponse>((resolve) => {
            python.on('close', (code: number | null) => {
                const closeTimestamp = new Date().toISOString();
                console.log(`[${closeTimestamp}] [headless/run] Process exited with code:`, code);

                if (code !== 0) {
                    // Extract useful debug info from logs
                    const logLines = stderr.trim().split('\n');
                    const lastLogs = logLines.slice(-10);
                    const errorLogs = logLines.filter(l =>
                        l.includes('Traceback') ||
                        l.includes('ValueError') ||
                        l.includes('ERROR') ||
                        l.includes('❌')
                    );

                    resolve(NextResponse.json(
                        {
                            error: 'Dashboard generation failed',
                            details: {
                                exitCode: code,
                                error: errorLogs[0] || 'Unknown error',
                                lastLogs: lastLogs,
                            },
                        },
                        { status: 500 }
                    ));
                    return;
                }

                try {
                    // Parse the JSON output from stdout
                    const lines = stdout.trim().split('\n');
                    console.log(`[${closeTimestamp}] [headless/run] stdout lines: ${lines.length}, searching for JSON...`);

                    // Find the line that starts with '{' (JSON start)
                    const jsonStartIndex = lines.findIndex(line => line.trim().startsWith('{'));

                    if (jsonStartIndex === -1) {
                        console.error(`[${closeTimestamp}] [headless/run] ❌ No JSON found in output. Last 5 lines:`, lines.slice(-5));
                        throw new Error('No JSON found in output');
                    }

                    console.log(`[${closeTimestamp}] [headless/run] JSON found at line ${jsonStartIndex}, parsing...`);

                    // Collect all lines from the JSON start to the end
                    const jsonLines = lines.slice(jsonStartIndex);
                    const jsonString = jsonLines.join('\n');

                    const orchestratorResult = JSON.parse(jsonString) as OrchestratorOutput;
                    console.log(`[${closeTimestamp}] [headless/run] ✅ Parsed orchestrator result:`, {
                        success: orchestratorResult.success,
                        action: orchestratorResult.action,
                        blocks: orchestratorResult.blocks?.length || 0,
                        blocks_data: orchestratorResult.blocks_data?.length || 0,
                    });

                    // Debug: Show blocks_data structure
                    if (!orchestratorResult.blocks_data || orchestratorResult.blocks_data.length === 0) {
                        console.error(`[${closeTimestamp}] [headless/run] ❌ CRITICAL: blocks_data is empty!`);
                        console.error(`[${closeTimestamp}] [headless/run] orchestratorResult keys:`, Object.keys(orchestratorResult).sort());
                        console.error(`[${closeTimestamp}] [headless/run] Full orchestratorResult:`, orchestratorResult);
                    } else {
                        console.log(`[${closeTimestamp}] [headless/run] blocks_data[0]:`, orchestratorResult.blocks_data[0]);
                    }

                    // Transform orchestrator output to HeadlessResult format
                    const headlessResult: HeadlessResult = {
                        question: question,
                        cache_key: `orchestrator_${Date.now()}_${question.length}`, // Simple cache key
                        status: orchestratorResult.success ? (
                            orchestratorResult.action === 'mock_generated' ? 'mock_generated' :
                            orchestratorResult.action === 'mock_reused' ? 'mock_reused' : 'generated'
                        ) : 'failed',
                        elapsed_s: orchestratorResult.total_time,
                        total_elapsed_s: orchestratorResult.total_time,
                        blocks: orchestratorResult.blocks?.length || 0,
                        ui_blocks: orchestratorResult.blocks || [],
                        blocks_data: orchestratorResult.blocks_data?.map(block => {
                            const hasData = block.data !== null && block.data !== undefined;
                            const transformed = {
                                block_id: block.blockId,
                                title: orchestratorResult.blocks?.find(b => b.blockId === block.blockId)?.title || block.blockId,
                                status: hasData ? 'complete' : 'failed',
                                has_result: hasData,
                                data: block.data,
                                error: hasData ? undefined : 'No data available',
                            };
                            if (!hasData) {
                                console.warn(`[${closeTimestamp}] [headless/run] ⚠️  Block ${block.blockId} has no data`);
                            }
                            return transformed;
                        }) || [],
                        layout: orchestratorResult.layout,
                        plan_title: orchestratorResult.title,
                        mock_data_file: orchestratorResult.mock_data_file,
                        similarity: orchestratorResult.similarity,
                        error: orchestratorResult.error,
                        steps: orchestratorResult.steps || [],
                    };

                    console.log(`[${closeTimestamp}] [headless/run] ✅ Returning HeadlessResult:`, {
                        question: headlessResult.question.substring(0, 60),
                        status: headlessResult.status,
                        blocks: headlessResult.blocks,
                        blocks_data_count: headlessResult.blocks_data?.length || 0,
                        elapsed_s: headlessResult.elapsed_s,
                    });

                    // Log layout details if available
                    if (headlessResult.layout) {
                        console.log(`[${closeTimestamp}] [headless/run] 📐 Grid Layout:`, {
                            template: headlessResult.layout.templateId,
                            slots: Object.keys(headlessResult.layout.slots).length,
                            slotAssignments: Object.entries(headlessResult.layout.slots).reduce((acc: any, [slotId, slotConfig]: [string, any]) => {
                                acc[slotId] = {
                                    blockId: slotConfig.blockId,
                                    title: slotConfig.title,
                                };
                                return acc;
                            }, {}),
                        });
                    }

                    resolve(NextResponse.json(headlessResult));
                } catch (e) {
                    const logLines = stdout.trim().split('\n');
                    const lastLogs = logLines.slice(-20);
                    const errorLogs = logLines.filter(l =>
                        l.includes('ERROR') || l.includes('❌') || l.includes('Failed')
                    );

                    resolve(NextResponse.json(
                        {
                            error: 'Dashboard generation failed',
                            details: {
                                lastLogs: lastLogs,
                                errors: errorLogs,
                                parseError: String(e),
                            },
                        },
                        { status: 500 }
                    ));
                }
            });
        });

    } catch (error: any) {
        return NextResponse.json(
            { error: error?.message || 'Unknown error' },
            { status: 500 }
        );
    }
}