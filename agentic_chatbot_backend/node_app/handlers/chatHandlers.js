import { streamText } from "ai";
import {
  looksDbRelated,
  planTools,
  filterTools,
  ensureMeaningfulResponse,
} from "../lib/agent.js";
import { BUDGETS, CONFIG } from "../utils/config.js";
import {
  SYSTEM_PROMPTS,
  withTimeout,
  buildProviderOptions,
  sanitizeHistory,
  buildConversation,
  getModel,
  hasToolCalls,
  isMinimalResponse,
} from "../utils/chatUtils.js";

export async function generateResponse(modelType, messages, tools, budget, signal) {
  const model = getModel(modelType);

  const { textStream, toolCalls, toolResults } = streamText({
    model,
    messages,
    tools,
    maxToolRoundtrips: CONFIG.MAX_TOOL_ROUNDS,
    abortSignal: signal,
    experimental_providerOptions: buildProviderOptions(budget),
  });

  let text = "";
  for await (const chunk of textStream) {
    text += chunk;
  }

  return {
    text,
    toolCalls: await toolCalls,
    toolResults: await toolResults,
  };
}

export async function retryWithForce(
  baseSystemPrompt,
  history,
  query,
  execTools,
  signal
) {
  const forcedMessages = buildConversation(
    SYSTEM_PROMPTS.forced(baseSystemPrompt),
    history,
    query
  );

  return generateResponse(
    "pro",
    forcedMessages,
    execTools,
    BUDGETS.RETRY,
    signal
  );
}

export async function interpretResults(query, toolResults) {
  const interpretMessages = [
    {
      role: "system",
      content: SYSTEM_PROMPTS.interpret(toolResults),
    },
    {
      role: "user",
      content: `Please explain what you found from the ${query}`,
    },
  ];

  const { textStream } = streamText({
    model: getModel("gemini-2.5-flash"),
    messages: interpretMessages,
    tools: {},
    experimental_providerOptions: buildProviderOptions(BUDGETS.INTERPRET),
  });

  let interpreted = "";
  for await (const chunk of textStream) {
    interpreted += chunk;
  }

  return interpreted;
}

export async function processWithTools(query, history, safeTools, domain) {
  const proModel = getModel("pro");

  const plannedToolNames = await planTools(
    proModel,
    [...sanitizeHistory(history), { role: "user", content: query }],
    safeTools,
    buildProviderOptions(BUDGETS.PLAN)
  );

  const execTools = filterTools(safeTools, plannedToolNames);
  const executeBudget = looksDbRelated(query) ? 128 : BUDGETS.EXECUTE;
  const systemPrompt = SYSTEM_PROMPTS.base(domain, execTools, false);

  const runGen = withTimeout(
    (signal) =>
      generateResponse(
        "pro",
        buildConversation(systemPrompt, history, query),
        execTools,
        executeBudget,
        signal
      ),
    CONFIG.TIMEOUT_MS
  );

  let result = await runGen.run();
  let toolsExecuted = hasToolCalls(result);

  if (
    looksDbRelated(query) &&
    !toolsExecuted &&
    Object.keys(execTools).length > 0
  ) {
    const retryGen = withTimeout(
      (signal) =>
        retryWithForce(systemPrompt, history, query, execTools, signal),
      CONFIG.TIMEOUT_MS
    );
    result = await retryGen.run();
    toolsExecuted = hasToolCalls(result);
  }

  let finalText = (result?.text || "").trim();

  if (isMinimalResponse(finalText) && result.toolResults?.length > 0) {
    const interpreted = await interpretResults(query, result.toolResults);
    finalText = (interpreted || finalText).trim();
  }

  finalText = ensureMeaningfulResponse(finalText, result.toolResults);

  return { result, finalText, toolsExecuted, plannedToolNames };
}

export async function processWithoutTools(query, history, domain) {
  const systemPrompt = SYSTEM_PROMPTS.base(domain, {}, false);

  const runGen = withTimeout(
    (signal) =>
      generateResponse(
        "gemini-2.5-flash",
        buildConversation(systemPrompt, history, query),
        {},
        BUDGETS.EXECUTE,
        signal
      ),
    CONFIG.TIMEOUT_MS
  );

  const result = await runGen.run();
  const finalText = (result?.text || "").trim();

  return { result, finalText, toolsExecuted: false, plannedToolNames: [] };
}
