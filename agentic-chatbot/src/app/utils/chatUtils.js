import { AGENT_POLICY, FORMAT_DIRECTIVE } from "@/app/prompt/constant_prompt";
import { CONFIG } from "@/app/utils/config";
import { google } from "@ai-sdk/google";

export const SYSTEM_PROMPTS = {
  base: (domain, availableTools, toolsWereExecuted) => {
    const followUpInstruction = toolsWereExecuted
      ? "\n\nIMPORTANT: Since database tools were executed in this response, include 1-3 relevant follow-up questions based on the NEW data retrieved."
      : "\n\nIMPORTANT: No database tools were executed in this response. Do NOT include any follow-up questions.";

    return `${AGENT_POLICY}
${domain ? domain + "\n" : ""}
Available tools: ${Object.keys(availableTools).join(", ") || "None"}

REMEMBER: You MUST interpret ALL tool results into natural, readable language. Never just say "Done."

${FORMAT_DIRECTIVE}${followUpInstruction}`;
  },

  forced: (basePrompt) => `${basePrompt}
CRITICAL: This query is database-related. You MUST:
1. Call at least one MCP tool
2. Interpret ALL results into natural language
3. NEVER just say "Done"`,

  interpret: (
    toolResults
  ) => `You just executed tools but provided a minimal response. 
You MUST now interpret the tool results into natural language.
${FORMAT_DIRECTIVE}

Tool results to interpret: ${JSON.stringify(toolResults)}

Provide a detailed, natural language explanation of what was found.
Include 1-3 follow-up questions since tools were executed.`,
};

export function withTimeout(promiseFactory, ms) {
  const ac = new AbortController();
  const timeout = setTimeout(() => ac.abort(), ms);

  return {
    run: async () => {
      try {
        return await promiseFactory(ac.signal);
      } finally {
        clearTimeout(timeout);
      }
    },
  };
}

export const buildProviderOptions = (budget) => ({
  google: {
    generationConfig: {
      thinkingConfig: { thinkingBudget: budget },
    },
  },
});

export const sanitizeHistory = (msgs = []) =>
  msgs
    .filter((m) => m && (m.role === "user" || m.role === "assistant"))
    .map((m) => ({ role: m.role, content: String(m.content ?? "") }));

export const buildConversation = (systemText, history, userQuery) => [
  { role: "system", content: systemText },
  ...sanitizeHistory(history),
  { role: "user", content: userQuery },
];

export const extractBetween = (text, startTag, endTag) => {
  const start = text.indexOf(startTag);
  const end = text.indexOf(endTag);
  return start !== -1 && end !== -1 && end > start
    ? text.slice(start + startTag.length, end).trim()
    : null;
};

export const isMinimalResponse = (text) => {
  const cleaned = text.toLowerCase().trim();
  return cleaned === "done" || cleaned === "done." || text.length < 20;
};

export const hasToolCalls = (result) =>
  result.toolCalls && result.toolCalls.length > 0;

export const requiresTools = (query, availableTools) => {
  if (Object.keys(availableTools).length === 0) return false;

  return (
    /\b(find|search|list|show|get|retrieve|query|count|aggregate|stats|analyze)\b/i.test(
      query
    )
  );
};

export const getModel = (modelType) =>
  google(modelType === "pro" ? CONFIG.MODEL_PRO : CONFIG.MODEL_FLASH);

export function validateRequest(body) {
  const query = typeof body?.query === "string" ? body.query.trim() : "";
  const history = Array.isArray(body?.messages) ? body.messages : [];

  if (!query) {
    throw new Error('Invalid "query" provided');
  }

  if (!process.env.GOOGLE_GENERATIVE_AI_API_KEY) {
    throw new Error("GOOGLE_GENERATIVE_AI_API_KEY not set");
  }

  return { query, history };
}

export function formatResponse(finalText, toolsExecuted) {
  if (toolsExecuted && finalText.indexOf("<CONTENT>") === -1) {
    return `<EXPLANATION>
Processing your request.
</EXPLANATION>

<CONTENT>
${finalText}
</CONTENT>`;
  }
  return finalText;
}

export async function createStreamResponse(
  contentText,
  reasoningText,
  plannedTools,
  result,
  toolsExecuted
) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      try {
        // Detect and split follow-up questions from main content
        const FOLLOWUP_MARKER = "**What would you like to explore next?**";
        let mainText = contentText;
        let followupText = "";
        const idx = contentText.indexOf(FOLLOWUP_MARKER);
        if (idx !== -1) {
          mainText = contentText.slice(0, idx).trimEnd();
          followupText = contentText.slice(idx).trimStart();
        }

        // Stream main content in chunks
        for (let i = 0; i < mainText.length; i += CONFIG.CHUNK_SIZE) {
          const part = mainText.slice(i, i + CONFIG.CHUNK_SIZE);
          const line = JSON.stringify({ type: "content", delta: part }) + "\n";
          controller.enqueue(encoder.encode(line));
          await new Promise((r) => setTimeout(r, CONFIG.STREAM_DELAY));
        }

        // Stream follow-up questions (if present) with a different type
        if (followupText) {
          for (let i = 0; i < followupText.length; i += CONFIG.CHUNK_SIZE) {
            const part = followupText.slice(i, i + CONFIG.CHUNK_SIZE);
            const line =
              JSON.stringify({ type: "followupquestion", delta: part }) + "\n";
            controller.enqueue(encoder.encode(line));
            await new Promise((r) => setTimeout(r, CONFIG.STREAM_DELAY));
          }
        }

        // Stream metadata
        const metadata = [
          { type: "reasoning", content: reasoningText || null },
          {
            type: "meta",
            plannedTools,
            toolCalls: result.toolCalls || [],
            toolsExecuted,
          },
          { type: "done" },
        ];

        metadata.forEach((data) => {
          controller.enqueue(encoder.encode(JSON.stringify(data) + "\n"));
        });

        controller.close();
      } catch (e) {
        controller.enqueue(
          encoder.encode(
            JSON.stringify({
              type: "error",
              error: e?.message || "stream error",
            }) + "\n"
          )
        );
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "application/x-ndjson; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
