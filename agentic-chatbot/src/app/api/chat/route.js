import { NextResponse } from "next/server";
import { loadAllMCPTools } from "@/app/lib/mcp.js";
import { looksDbRelated, buildToolSet, loadDomainInstruction } from "@/app/lib/agent.js";
import {
  validateRequest,
  formatResponse,
  extractBetween,
  createStreamResponse,
  requiresTools
} from "../../utils/chatUtils.js";
import {
  processWithTools,
  processWithoutTools
} from "../../handlers/chatHandlers.js";

export const runtime = "nodejs";

// POST Request :- chat

export async function POST(req) {
  let resources = null;

  try {
    const url = new URL(req.url);
    const streamMode = url.searchParams.get("stream") === "1";
    const body = await req.json();
    const { query, history } = validateRequest(body);

    const { tools: allTools, closeAll } = await loadAllMCPTools();
    resources = { closeAll };

    const safeTools = buildToolSet(allTools, query);
    const domain = loadDomainInstruction();
    const needsTools = requiresTools(query, safeTools) || looksDbRelated(query);

    // Process request based on tool requirements
    const { result, finalText, toolsExecuted, plannedToolNames } =
      needsTools && Object.keys(safeTools).length > 0
        ? await processWithTools(query, history, safeTools, domain)
        : await processWithoutTools(query, history, domain);

    const formattedText = formatResponse(finalText, toolsExecuted);
    const reasoningText = extractBetween(
      formattedText,
      "<EXPLANATION>",
      "</EXPLANATION>"
    );
    const contentText =
      extractBetween(formattedText, "<CONTENT>", "</CONTENT>") || formattedText;

    if (streamMode) {
      return await createStreamResponse(
        contentText,
        reasoningText,
        plannedToolNames,
        result,
        toolsExecuted
      );
    }

    return NextResponse.json({
      result: contentText,
      reasoning: reasoningText,
      plannedTools: plannedToolNames,
      toolCalls: result?.toolCalls || [],
      toolResults: result?.toolResults || [],
      toolsExecuted,
      modelUsed: needsTools ? "gemini-2.5-pro" : "gemini-2.5-flash",
    });
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
  } finally {
    if (resources?.closeAll) {
      try {
        await resources.closeAll();
      } catch {}
    }
  }
}
