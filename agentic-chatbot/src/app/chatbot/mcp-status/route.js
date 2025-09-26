import { NextResponse } from 'next/server';
import { pingAllMCPProviders} from '@/app/lib/mcp';

export const runtime = 'nodejs';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': 'http://localhost:5173',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export async function OPTIONS() {
  return new Response(null, { headers: CORS_HEADERS });
}

export async function GET() {
  try {
    const pingResults = await pingAllMCPProviders();
    const connected = Array.isArray(pingResults) && pingResults.some(r => r.ok);
    return NextResponse.json({
      ok: connected,
      connected,
      result: connected ? 'ping' : 'pong',
      totalProviders: pingResults.length,
    }, { headers: CORS_HEADERS });
  } catch (e) {
    return NextResponse.json({ ok: false, error: e.message }, { status: 500, headers: CORS_HEADERS });
  }
}