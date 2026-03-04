import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';

export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  const { sessionId } = await Promise.resolve(params);

  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const progressUrl = `${backendUrl}/api/progress/${sessionId}`;

  console.log(`[Progress Route] Proxying SSE to backend: ${progressUrl}`);

  // Wire browser disconnect → backend connection abort.
  // Without this the Python uvicorn worker slot leaks open until the
  // next heartbeat cycle even after the browser tab closes.
  const controller = new AbortController();
  request.signal.addEventListener('abort', () => {
    console.log(`[Progress Route] Browser disconnected for session ${sessionId} — aborting backend fetch`);
    controller.abort();
  });

  try {
    const backendResponse = await fetch(progressUrl, {
      method: 'GET',
      headers: { 'Accept': 'text/event-stream' },
      signal: controller.signal,
    });

    if (!backendResponse.ok) {
      console.error(`[Progress Route] Backend returned ${backendResponse.status}`);
      return NextResponse.json(
        { error: 'Failed to connect to backend progress stream' },
        { status: backendResponse.status }
      );
    }

    const reader = backendResponse.body?.getReader();
    if (!reader) {
      console.error('[Progress Route] No response body from backend');
      return NextResponse.json({ error: 'No stream available' }, { status: 500 });
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
          if ((error as any)?.name !== 'AbortError') {
            console.error('[Progress Route] Error reading from backend:', error);
          }
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
        'X-Accel-Buffering': 'no',
      },
    });
  } catch (error) {
    if ((error as any)?.name === 'AbortError') {
      // Client disconnected before backend responded — not an error
      return new NextResponse(null, { status: 499 });
    }
    console.error('[Progress Route] Error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to progress stream' },
      { status: 500 }
    );
  }
}
