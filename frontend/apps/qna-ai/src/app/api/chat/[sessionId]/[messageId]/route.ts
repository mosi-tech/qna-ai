import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ sessionId: string; messageId: string }> }
) {
  try {
    const { sessionId, messageId } = await params;

    // Forward request to backend API with proper REST structure  
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8010';
    const response = await fetch(`${backendUrl}/api/sessions/${sessionId}/messages/${messageId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      console.error('Backend API error:', response.statusText);
      return NextResponse.json(
        { error: 'Failed to fetch message from backend' },
        { status: response.status }
      );
    }

    const messageData = await response.json();
    return NextResponse.json(messageData);

  } catch (error) {
    console.error('Error fetching message:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}