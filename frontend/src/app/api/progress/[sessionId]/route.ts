import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';

const activeConnections = new Map<
  string,
  Array<WritableStreamDefaultWriter<Uint8Array>>
>();

export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  const { sessionId } = await Promise.resolve(params);

  console.log(`[Progress Route] Starting SSE proxy for session: ${sessionId}`);

  // ENABLED CODE:
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const progressUrl = `${backendUrl}/api/progress/${sessionId}`;

  console.log(`[Progress Route] Proxying to backend: ${progressUrl}`);

  try {
    // Fetch the backend SSE stream
    const backendResponse = await fetch(progressUrl, {
      method: 'GET',
      headers: {
        'Accept': 'text/event-stream',
      },
    });

    if (!backendResponse.ok) {
      console.error(`[Progress Route] Backend returned ${backendResponse.status}`);
      return NextResponse.json(
        { error: 'Failed to connect to backend progress stream' },
        { status: backendResponse.status }
      );
    }

    // Create a readable stream from the backend response
    const reader = backendResponse.body?.getReader();
    if (!reader) {
      console.error('[Progress Route] No response body from backend');
      return NextResponse.json(
        { error: 'No stream available' },
        { status: 500 }
      );
    }

    const stream = new ReadableStream({
      async start(controller) {
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) {
              console.log(`[Progress Route] Backend stream closed for session ${sessionId}`);
              controller.close();
              break;
            }
            controller.enqueue(value);
          }
        } catch (error) {
          console.error('[Progress Route] Error reading from backend:', error);
          controller.error(error);
        }
      },
      cancel() {
        reader.cancel();
      },
    });

    return new NextResponse(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'X-Accel-Buffering': 'no',
      },
    });
  } catch (error) {
    console.error('[Progress Route] Error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to progress stream' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  const { sessionId } = await Promise.resolve(params);
  const body = await request.json();

  const connections = activeConnections.get(sessionId);
  if (connections && connections.length > 0) {
    const encoder = new TextEncoder();
    const message = `data: ${JSON.stringify(body)}\n\n`;

    for (const conn of connections) {
      try {
        (conn as any).write(message);
      } catch (e) {
        console.error('Error sending to client:', e);
      }
    }
  }

  return NextResponse.json({ success: true });
}
