import { loadAllMCPTools } from "../lib/mcp.js";
import {
  looksDbRelated,
  isGreetingOrGeneral,
  buildToolSet,
  isFollowUp,
  loadDomainInstruction,
} from "../lib/agent.js";
import {
  formatResponse,
  extractBetween,
  requiresTools,
} from "../utils/chatUtils.js";
import {
  processWithTools,
  processWithoutTools,
} from "../handlers/chatHandlers.js";

const PRO_MODEL = "gemini-2.5-pro";
const FLASH_MODEL = "gemini-2.5-flash";

export async function runChatWorkflow({ query, history, context }) {
  let closeAll = async () => {};

  try {
    const { tools: allTools, closeAll: disposer } = await loadAllMCPTools();
    closeAll = typeof disposer === "function" ? disposer : async () => {};

    // Regex to check if the query already contains a UUID
    const uuidRegex = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/i;
    const queryHasId = uuidRegex.test(query);

    const isFollowUpQuery = isFollowUp(query);

    let augmentedQuery = query;
    // If the query is generic (no ID), not a greeting or a follow-up, and context exists, append the relevant ID.
    if (
      !queryHasId && context && !isGreetingOrGeneral(query) && !isFollowUpQuery
    ) {
      if (context.cloud_account_id) {
        augmentedQuery = `${query} for cloud account ID \`${context.cloud_account_id}\``;
      } else if (context.organization_id) {
        augmentedQuery = `${query} for organization ID \`${context.organization_id}\``;
      }
    } else if (context) {
      // If query already has an ID, just prepend the context for the model's awareness.
      const contextString = Object.entries(context)
        .filter(([, value]) => value)
        .map(([key, value]) => `${key}: ${value}`)
        .join(", ");
      if (contextString) {
        augmentedQuery = `(Context: ${contextString}) ${query}`;
      }
    }

    const safeTools = buildToolSet(allTools, augmentedQuery);
    const domain = loadDomainInstruction();
    const needsTools = requiresTools(augmentedQuery, safeTools) || looksDbRelated(augmentedQuery);

    const handlerUsesTools =
      needsTools && Object.keys(safeTools).length > 0;

    const workflowResult = handlerUsesTools
      ? await processWithTools(augmentedQuery, history, safeTools, domain)
      : await processWithoutTools(augmentedQuery, history, domain);

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
        modelUsed: handlerUsesTools ? PRO_MODEL : FLASH_MODEL,
      },
      meta: {
        contentText,
        reasoningText,
        plannedTools: plannedToolNames,
        toolsExecuted,
        rawResult: result,
        modelUsed: handlerUsesTools ? PRO_MODEL : FLASH_MODEL,
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
