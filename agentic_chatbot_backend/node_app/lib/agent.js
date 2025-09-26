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

export function ensureMeaningfulResponse(text, toolResults) {
  const minimalResponses = [
    "done",
    "done.",
    "completed",
    "finished",
    "ok",
    "okay",
  ];
  const isMinimal = minimalResponses.includes(text.toLowerCase().trim());

  if (toolResults && toolResults.length > 0) {
    let sawAnyData = false;
    let sawExplicitZero = false;
    for (const result of toolResults) {
      const contents = Array.isArray(result?.content)
        ? result.content
        : [result?.content].filter(Boolean);
      for (const c of contents) {
        if (c?.type === "text" && typeof c.text === "string") {
          const t = c.text.trim();
          if (!t) continue;
          if (
            t === "[]" ||
            /^\s*\{\s*\}\s*$/.test(t) ||
            /\bno results?\b/i.test(t) ||
            /\bnot found\b/i.test(t)
          ) {
            sawExplicitZero = true;
            continue;
          }
          try {
            const parsed = JSON.parse(t);
            if (Array.isArray(parsed) && parsed.length === 0) {
              sawExplicitZero = true;
            } else if (
              parsed &&
              typeof parsed === "object" &&
              Object.keys(parsed).length === 0
            ) {
              sawExplicitZero = true;
            } else {
              sawAnyData = true;
            }
          } catch {
            if (t.length > 0) sawAnyData = true;
          }
        }
      }
    }
    if (!sawAnyData && sawExplicitZero) {
      return "I couldn't find any matching records for your request. Please verify the ID or provide more context (e.g., account ID, organization ID, or resource details).";
    }
  }

  if (isMinimal && toolResults && toolResults.length > 0) {
    let fallback = "I've completed the operation. ";

    for (const result of toolResults) {
      if (result?.content) {
        const content = Array.isArray(result.content)
          ? result.content
          : [result.content];
        const textContent = content
          .filter((c) => c?.type === "text" && c?.text)
          .map((c) => c.text);

        if (textContent.length > 0) {
          if (textContent[0].includes("id") || textContent[0].includes("account")) {
            try {
              const parsed = JSON.parse(textContent[0]);
              if (Array.isArray(parsed) && parsed.length > 0) {
                fallback = `I found ${parsed.length} result${parsed.length !== 1 ? "s" : ""}:\n\n`;
                parsed.forEach((row, i) => {
                  fallback += `**Result ${i + 1}:**\n`;
                  for (const [key, value] of Object.entries(row)) {
                    fallback += `- ${key}: ${value}\n`;
                  }
                  fallback += "\n";
                });
              } else if (typeof parsed === "object") {
                fallback = "Here's the result:\n\n";
                for (const [key, value] of Object.entries(parsed)) {
                  fallback += `- ${key}: ${value}\n`;
                }
              }
            } catch {
              fallback += textContent.join("\n\n");
            }
          } else if (textContent.length) {
            fallback += textContent.join("\n\n");
          }
        }
      }
    }
    return fallback.trim();
  }

  return text;
}
