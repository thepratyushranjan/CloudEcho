import { loadAllMCPTools } from "@/app/lib/mcp.js";
import {
  looksDbRelated,
  buildToolSet,
  loadDomainInstruction,
} from "@/app/lib/agent.js";
import {
  formatResponse,
  extractBetween,
  requiresTools,
} from "@/app/utils/chatUtils.js";
import {
  processWithTools,
  processWithoutTools,
} from "@/app/handlers/chatHandlers.js";

const PRO_MODEL = "gemini-2.5-pro";
const FLASH_MODEL = "gemini-2.5-flash";

export async function runChatWorkflow({ query, history }) {
  let closeAll = async () => {};

  try {
    const { tools: allTools, closeAll: disposer } = await loadAllMCPTools();
    closeAll = typeof disposer === "function" ? disposer : async () => {};

    const safeTools = buildToolSet(allTools, query);
    const domain = loadDomainInstruction();
    const needsTools = requiresTools(query, safeTools) || looksDbRelated(query);

    const handlerUsesTools =
      needsTools && Object.keys(safeTools).length > 0;

    const workflowResult = handlerUsesTools
      ? await processWithTools(query, history, safeTools, domain)
      : await processWithoutTools(query, history, domain);

    const { result, finalText, toolsExecuted, plannedToolNames } =
      workflowResult;

    const formattedText = formatResponse(finalText, toolsExecuted);
    const reasoningText = extractBetween(
      formattedText,
      "<EXPLANATION>",
      "</EXPLANATION>"
    );
    const contentText =
      extractBetween(formattedText, "<CONTENT>", "</CONTENT>") || formattedText;

    return {
      response: {
        result: contentText,
        reasoning: reasoningText || null,
        plannedTools: plannedToolNames || [],
        toolCalls: result?.toolCalls || [],
        toolResults: result?.toolResults || [],
        toolsExecuted: Boolean(toolsExecuted),
        modelUsed: handlerUsesTools ? PRO_MODEL : FLASH_MODEL,
      },
      meta: {
        formattedText,
        contentText,
        reasoningText,
        plannedToolNames: plannedToolNames || [],
        rawResult: result,
        toolsExecuted: Boolean(toolsExecuted),
      },
    };
  } finally {
    try {
      await closeAll();
    } catch (err) {
      console.warn("Failed to dispose MCP clients", err);
    }
  }
}

export default runChatWorkflow;
