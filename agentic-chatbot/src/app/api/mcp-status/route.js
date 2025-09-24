
import { NextResponse } from 'next/server';
import { pingAllMCPProviders} from '@/app/lib/mcp';

export const runtime = 'nodejs';

export async function GET() {
  try {
    const pingResults = await pingAllMCPProviders();
    const connected = Array.isArray(pingResults) && pingResults.some(r => r.ok);
    return NextResponse.json({
      ok: connected,
      connected,
      result: connected ? 'ping' : 'pong',
      totalProviders: pingResults.length,
    });
  } catch (e) {
    return NextResponse.json({ ok: false, error: e.message }, { status: 500 });
  }
}
