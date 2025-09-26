import { NextResponse } from "next/server";
import { runChatWorkflow } from "@/server/chatService.js";
import {
  validateRequest,
  createStreamResponse,
} from "../../utils/chatUtils.js";

export const runtime = "nodejs";

export async function POST(req) {
  try {
    const url = new URL(req.url);
    const streamMode = url.searchParams.get("stream") === "1";
    const body = await req.json();
    const { query, history } = validateRequest(body);

    const chat = await runChatWorkflow({ query, history });

    if (streamMode) {
      const {
        contentText,
        reasoningText,
        plannedToolNames,
        rawResult,
        toolsExecuted,
      } = chat.meta;
      return await createStreamResponse(
        contentText,
        reasoningText,
        plannedToolNames,
        rawResult,
        toolsExecuted
      );
    }

    return NextResponse.json(chat.response);
  } catch (err) {
    const isAbort = err?.name === "AbortError";
    return NextResponse.json(
      {
        error: isAbort
          ? "Timed out waiting for model/tools"
          : err?.message || "Internal Error",
      },
      { status: 500 }
    );
  }
}
