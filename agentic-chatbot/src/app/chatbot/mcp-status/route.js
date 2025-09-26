import { NextResponse } from 'next/server';
import { pingAllMCPProviders } from '@/app/lib/mcp';

export const runtime = 'nodejs';

// CORS configuration - Allow all origins
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Accept, Origin',
  'Access-Control-Allow-Credentials': 'true',
  'Access-Control-Max-Age': '86400', // Cache preflight for 24 hours
};

// OPTIONS Request for CORS preflight
export async function OPTIONS() {
  return new Response(null, { headers: CORS_HEADERS });
}

// GET Request - Ping all MCP providers
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
    return NextResponse.json(
      { ok: false, error: e.message }, 
      { status: 500, headers: CORS_HEADERS }
    );
  }
}