import { NextResponse } from "next/server";
import { getMCPStatus } from "@/server/mcpStatusService.js";

export const runtime = "nodejs";

export async function GET() {
  try {
    const status = await getMCPStatus();
    return NextResponse.json(status);
  } catch (e) {
    return NextResponse.json({ ok: false, error: e.message }, { status: 500 });
  }
}
