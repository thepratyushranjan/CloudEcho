import { generateText } from "ai";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const CURRENT_DIR = path.dirname(fileURLToPath(import.meta.url));
const PROMPT_DIR = path.resolve(CURRENT_DIR, "../prompt");
const WRITE_NAME_RE = /(insert|update|delete|create[-_ ]?index|drop|write|bulk|merge|out)$/i;

export function looksDbRelated(q = "") {
  return /\b(db|database|collection|collections|find|aggregate|count|index|indexes|schema|stats|log|logs|explain|collstats|storage size|size on disk|perf|performance|mongodb|mariadb|sql|account|account id|organization|org id|orgid|name|user|customer|lookup|search for|get|retrieve)\b/i.test(
    q
  );
}

export function isGreetingOrGeneral(query) {
  const q = query.toLowerCase().trim();

  const greetingPatterns = [
    /^\s*h(i|ey|ello|owdy)\b/,
    /^\s*good (morning|afternoon|evening)/,
    /^\s*how are you/,
    /^\s*what'?s up/,
    /^\s*what (is|are) you/,
    /^\s*what can you do/,
    /^\s*what is cloudtuner/,
  ];

  const isGreeting = greetingPatterns.some(pattern => pattern.test(q));
  return isGreeting || (q.length < 25 && !looksDbRelated(q));
}

export function isFollowUp(query) {
  const q = query.toLowerCase().trim();

  // More comprehensive patterns to detect follow-up questions dynamically.
  const followUpPatterns = [
    // General requests for more information
    /^(what|tell me|show me) more about (that|this|it|them)/,
    /^(can you )?(explain|elaborate on|give me more details about) (that|this|it|them)/,
    /^could you (please )?provide (more|further|a more detailed) (info|information|explanation|details)/,
    /in more detail/,

    // Questions about the previous response
    /^(that's|that is) interesting, can you/,
    /^(and )?what about/,
    /^why is (that|it)/,
    /what does (that|it) mean/,
    /how did you (get|find|determine) that/,
    /what about the (first|second|third|last|other) one/,
    /^(show|format|present) this (data|info|information) (as a|in a) (table|list) (comparison with|comparison between)/,
  ];

  return followUpPatterns.some(pattern => pattern.test(q));
}

let cachedDomainInstruction = null;

function resolvePromptPaths() {
  const files = {
    mongodb: path.join(PROMPT_DIR, "chat-bot.md"),
    mariadb: path.join(PROMPT_DIR, "mariadb-instructions.md"),
  };

  for (const [key, target] of Object.entries(files)) {
    if (!fs.existsSync(target)) {
      files[key] = null;
    }
  }

  return files;
}

export function loadDomainInstruction() {
  if (cachedDomainInstruction !== null) return cachedDomainInstruction;

  const files = resolvePromptPaths();
  let instructions = "";

  try {
    if (files.mongodb) {
      const mongoContent = fs.readFileSync(files.mongodb, "utf8");
      instructions += `MongoDB guidance (from prompt/chat-bot.md):\n${mongoContent}\n\n`;
    }

    if (files.mariadb) {
      const mariaContent = fs.readFileSync(files.mariadb, "utf8");
      instructions += `MariaDB guidance (from prompt/mariadb-instructions.md):\n${mariaContent}\n`;
    }

    cachedDomainInstruction = instructions || "";
  } catch {
    cachedDomainInstruction = "";
  }

  return cachedDomainInstruction;
}

export function buildToolSet(allTools, query) {
  const confirmed = /confirm:\s*(true|yes)/i.test(query || "");
  if (confirmed) return allTools;

  const safe = {};
  for (const [name, def] of Object.entries(allTools || {})) {
    if (!WRITE_NAME_RE.test(name)) safe[name] = def;
  }
  return safe;
}

export function filterTools(all, allowList) {
  if (!allowList?.length) return all;
  const filtered = {};
  for (const k of allowList) if (all[k]) filtered[k] = all[k];
  return Object.keys(filtered).length ? filtered : all;
}

export async function planTools(model, historyMessages, tools, providerOptions) {
  const domain = loadDomainInstruction();

  const systemContent = `You are a strict planner. Decide which MCP tools to use.

Database Selection Rules:
- For cloud account names, account IDs, organization ID, user lookups → prefer mariadb-mcp-server.execute_sql
- For cloud costs, expenses, resources, security checks, Recommendations → use MongoDB tools
- For MongoDB queries → use appropriate mongodb tools (find, aggregate, count, etc.)
- In MongoDB queries, do not fabricate or assume any data under any circumstances.

CRITICAL MongoDB Format:
- When using mongo-http.aggregate, pipeline MUST use MongoDB Extended JSON v2
- Stage operators: "$match", "$group", "$project" (quoted keys)
- Dates: {"$date": "YYYY-MM-DDTHH:mm:ss.sssZ"} NOT ISODate(...)
- Example: [{"$match": {"_last_seen_date": {"$gte": {"$date": "2025-03-01T00:00:00.000Z"}}}}]

IMPORTANT for MariaDB:
- Do NOT assume database or table names. Use only names provided by configuration or prior tool responses
- NEVER hallucinate database, table, or column names o any type of data.
- Validate SQL queries before execution

${domain ? domain + "\n" : ""}

Available tools: ${Object.keys(tools).join(", ")}

Return STRICT JSON only: {"tools":[{"name":"<exact-tool-name>","why":"<short>"}]}`;

  const { text } = await generateText({
    model,
    messages: [{ role: "system", content: systemContent }, ...historyMessages],
    tools: {},
    providerOptions,
  });

  try {
    const plan = JSON.parse(text || "{}");
    const chosen = (plan.tools || [])
      .map((t) => (t && t.name ? String(t.name) : ""))
      .filter((n) => n && tools[n]);

    return [...new Set(chosen)];
  } catch {
    return [];
  }
}

function extractTextContents(result) {
  const contents = Array.isArray(result?.content)
    ? result.content
    : [result?.content].filter(Boolean);
  
  return contents
    .filter((c) => c?.type === "text" && c?.text)
    .map((c) => c.text);
}

function isEmptyResult(text) {
  return (
    text === "[]" ||
    /^\s*\{\s*\}\s*$/.test(text) ||
    /\bno results?\b/i.test(text) ||
    /\bnot found\b/i.test(text)
  );
}

function hasData(text) {
  try {
    const parsed = JSON.parse(text);
    if (Array.isArray(parsed)) return parsed.length > 0;
    if (parsed && typeof parsed === "object") return Object.keys(parsed).length > 0;
    return false;
  } catch {
    return text.length > 0;
  }
}

function formatParsedResults(parsed) {
  if (Array.isArray(parsed) && parsed.length > 0) {
    let output = `I found ${parsed.length} result${parsed.length !== 1 ? "s" : ""}:\n\n`;
    parsed.forEach((row, i) => {
      output += `**Result ${i + 1}:**\n`;
      for (const [key, value] of Object.entries(row)) {
        output += `- ${key}: ${value}\n`;
      }
      output += "\n";
    });
    return output;
  }
  
  if (typeof parsed === "object") {
    let output = "Here's the result:\n\n";
    for (const [key, value] of Object.entries(parsed)) {
      output += `- ${key}: ${value}\n`;
    }
    return output;
  }
  
  return null;
}

export function ensureMeaningfulResponse(text, toolResults) {
  const minimalResponses = ["done", "done.", "completed", "finished", "ok", "okay"];
  const isMinimal = minimalResponses.includes(text.toLowerCase().trim());

  if (!toolResults?.length) return text;

  // Check if we have any actual data
  let sawAnyData = false;
  let sawExplicitZero = false;

  for (const result of toolResults) {
    const textContents = extractTextContents(result);
    
    for (const t of textContents) {
      const trimmed = t.trim();
      if (!trimmed) continue;
      
      if (isEmptyResult(trimmed)) {
        sawExplicitZero = true;
      } else if (hasData(trimmed)) {
        sawAnyData = true;
      }
    }
  }

  if (!sawAnyData && sawExplicitZero) {
    return "I couldn't find any matching records for your request. Please verify the ID or provide more context (e.g., account ID, organization ID, or resource details).";
  }

  if (!isMinimal) return text;

  // Build fallback response for minimal text
  let fallback = "I've completed the operation. ";

  for (const result of toolResults) {
    const textContent = extractTextContents(result);

    if (textContent.length > 0) {
      const firstText = textContent[0];
      
      if (firstText.includes("id") || firstText.includes("account")) {
        try {
          const parsed = JSON.parse(firstText);
          const formatted = formatParsedResults(parsed);
          if (formatted) return formatted.trim();
        } catch {
          fallback += textContent.join("\n\n");
        }
      } else {
        fallback += textContent.join("\n\n");
      }
    }
  }

  return fallback.trim();
}
