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

/**
 * Fixes single-quote issue in MongoDB pipelines
 */
function fixMongoDBPipeline(pipeline) {
  if (!Array.isArray(pipeline)) {
    return pipeline;
  }

  try {
    const pipelineStr = JSON.stringify(pipeline);
    
    // Check if fix is needed
    if (!pipelineStr.includes("'$") && !pipelineStr.includes("'_")) {
      return pipeline; // No fix needed
    }
    
    // Fix single quotes around keys
    const fixedStr = pipelineStr
      .replace(/"'(\$[^']+)'"\s*:/g, '"$1":')
      .replace(/"'(_[^']+)'"\s*:/g, '"$1":')
      .replace(/"'([a-zA-Z][^']+)'"\s*:/g, '"$1":');
    
    return JSON.parse(fixedStr);
  } catch (err) {
    return pipeline;
  }
}

/**
 * Wraps tools to fix MongoDB pipeline issues before execution
 */
function wrapToolsWithFixer(tools) {
  const wrapped = {};
  
  for (const [name, tool] of Object.entries(tools)) {
    if (name === 'mongo-http.aggregate') {
      wrapped[name] = {
        description: tool.description,
        parameters: tool.parameters,
        execute: async (params) => {
          
          if (params.pipeline) {
            // If pipeline is a string, parse it first
            let pipeline = params.pipeline;
            if (typeof pipeline === 'string') {
              try {
                pipeline = JSON.parse(pipeline);
              } catch (err) {
                console.error("Failed to parse pipeline:", err.message);
              }
            }
            
            // Fix single-quote issues
            const fixedPipeline = fixMongoDBPipeline(pipeline);
            params = { ...params, pipeline: fixedPipeline };
          }

          // Call the original tool
          const result = await tool.execute(params);
          return result;
        }
      };
    } else {
      wrapped[name] = tool;
    }
  }
  
  return wrapped;
}

export async function generateResponse(modelType, messages, tools, budget, signal) {
  const model = getModel(modelType);
  
  // Wrap tools to fix MongoDB pipeline issues
  const wrappedTools = wrapToolsWithFixer(tools);
  
  const { textStream, toolCalls, toolResults } = streamText({
    model,
    messages,
    tools: wrappedTools,
    maxToolRoundtrips: CONFIG.MAX_TOOL_ROUNDS,
    abortSignal: signal,
    experimental_providerOptions: buildProviderOptions(budget),
  });

  let text = "";
  for await (const chunk of textStream) {
    text += chunk;
  }

  const resolvedToolCalls = await toolCalls;
  const resolvedToolResults = await toolResults;

  return {
    text,
    toolCalls: resolvedToolCalls,
    toolResults: resolvedToolResults,
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
  // console.log("Tool Calls:", result.toolCalls);
  console.log("Tool Results:", result.toolResults);
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
