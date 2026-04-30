import { NextRequest, NextResponse } from 'next/server';

/**
 * Catch-all proxy route.
 *
 * Any /api/* request that doesn't match a specific route file is forwarded
 * to the backend. The backend URL lives in the server-side BACKEND_URL env
 * var — it is never exposed to the browser.
 *
 * Specific route files in app/api/ take precedence over this catch-all.
 */
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

async function proxy(
  request: NextRequest,
  path: string[]
): Promise<NextResponse> {
  const joinedPath = path.join('/');
  const searchParams = request.nextUrl.searchParams.toString();
  const backendUrl = `${BACKEND_URL}/api/${joinedPath}${searchParams ? `?${searchParams}` : ''}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  const authHeader = request.headers.get('authorization');
  if (authHeader) {
    headers['Authorization'] = authHeader;
  }

  let body: string | undefined;
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    body = await request.text();
  }

  try {
    const response = await fetch(backendUrl, {
      method: request.method,
      headers,
      body,
    });

    const responseText = await response.text();
    return new NextResponse(responseText, {
      status: response.status,
      headers: {
        'Content-Type':
          response.headers.get('content-type') || 'application/json',
      },
    });
  } catch (error) {
    console.error(
      `[proxy] Error forwarding ${request.method} /api/${joinedPath}:`,
      error
    );
    return NextResponse.json({ error: 'Backend unavailable' }, { status: 503 });
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, (await params).path);
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, (await params).path);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, (await params).path);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, (await params).path);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, (await params).path);
}
