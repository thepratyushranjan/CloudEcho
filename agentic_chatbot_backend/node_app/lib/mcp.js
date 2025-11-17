import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { experimental_createMCPClient } from "@ai-sdk/mcp";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { fixMongoDBPipeline } from "./toolWrapper.js";

const CURRENT_DIR = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_CONFIG = path.resolve(CURRENT_DIR, "../../mcp-config.json");

function ensureHttpUrl(value) {
  if (typeof value !== "string") return value;
  const trimmed = value.trim();
  if (!trimmed) return trimmed;
  if (/^[a-zA-Z][a-zA-Z\d+.-]*:/.test(trimmed)) {
    return trimmed;
  }
  if (trimmed.startsWith("//")) {
    return `http:${trimmed}`;
  }
  return `http://${trimmed}`;
}

function getConfigPath() {
  const override = process.env.MCP_CONFIG_PATH;
  return override ? path.resolve(override) : DEFAULT_CONFIG;
}

function resolveEnvVars(value) {
  if (typeof value === "string") {
    return value.replace(/\$\{([^}]+)\}/g, (_, name) => {
      const envValue = process.env[name];
      if (envValue === undefined) {
        throw new Error(`Environment variable ${name} is not defined`);
      }
      return envValue;
    });
  }

  if (Array.isArray(value)) {
    return value.map((item) => resolveEnvVars(item));
  }

  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, val]) => [key, resolveEnvVars(val)])
    );
  }

  return value;
}

function createTransport(provider, entry) {
  if (entry.command) {
    return new StdioClientTransport({
      command: entry.command,
      args: Array.isArray(entry.args) ? entry.args : [],
      env: { ...process.env, ...(entry.env || {}) },
    });
  }

  const transportType = entry.transport || entry.type;
  if (transportType === "sse" || transportType === "http") {
    if (!entry.url) {
      throw new Error(
        `Missing "url" for ${transportType.toUpperCase()} transport on provider "${provider}"`
      );
    }

    let url;
    try {
      url = new URL(ensureHttpUrl(entry.url));
    } catch (err) {
      throw new Error(
        `Invalid URL "${entry.url}" for ${transportType.toUpperCase()} transport on provider "${provider}": ${err.message}`
      );
    }

    const headers =
      entry.headers && typeof entry.headers === "object"
        ? Object.fromEntries(
            Object.entries(entry.headers).map(([key, value]) => [key, String(value)])
          )
        : undefined;

    if (transportType === "sse") {
      return new SSEClientTransport(url, { headers });
    }

    const httpOptions = {};
    if (headers) httpOptions.headers = headers;
    if (entry.sessionId) httpOptions.sessionId = String(entry.sessionId);

    return new StreamableHTTPClientTransport(url, httpOptions);
  }

  throw new Error(
    `Unsupported MCP transport for provider "${provider}". Include a "command" or set "transport" to "sse" or "http"`
  );
}

async function loadConfig() {
  const configPath = getConfigPath();
  const raw = await fs.readFile(configPath, "utf8");
  return JSON.parse(raw);
}

export async function loadAllMCPTools() {
  const config = await loadConfig();

  const clients = [];
  const toolsMap = {};

  for (const [provider, entry] of Object.entries(config || {})) {
    if (!entry) continue;

    try {
      const normalized = resolveEnvVars(entry);
      const transportKind = (normalized.transport || normalized.type || "stdio").toUpperCase();
      const targetDesc = normalized.url
        ? normalized.url
        : normalized.command || "unknown";
      const transport = createTransport(provider, normalized);
      const client = await experimental_createMCPClient({ transport });

      try {
        const tools = await client.tools();
        for (const [name, def] of Object.entries(tools || {})) {
          const fullName = `${provider}.${name}`;

          if (fullName === 'mongo-http.aggregate') {
            toolsMap[fullName] = {
              ...def,
              execute: async (params) => {
                if (params.pipeline) {
                  const fixedPipeline = fixMongoDBPipeline(params.pipeline);
                  params = { ...params, pipeline: fixedPipeline };
                }
                return def.execute(params);
              }
            };
          } else {
            toolsMap[fullName] = def;
          }
        }
        clients.push(client);
      } catch (err) {
        if (typeof client.close === "function") {
          try {
            await client.close();
          } catch {}
        }
        throw err;
      }
    } catch (err) {
      console.error(
        `Failed to initialize MCP provider "${provider}": ${err.message}`
      );
    }
  }

  const closeAll = async () => {
    await Promise.allSettled(clients.map((c) => c?.close?.()));
  };

  return { tools: toolsMap, closeAll };
}

const MAX_RECENT_PINGS = 10;
const recentPings = [];

function addRecentPing(entry) {
  recentPings.push(entry);
  while (recentPings.length > MAX_RECENT_PINGS) recentPings.shift();
}

export function getRecentPings() {
  return [...recentPings].reverse();
}

export async function pingAllMCPProviders() {
  const config = await loadConfig();

  const results = [];
  const clients = [];

  try {
    for (const [provider, entry] of Object.entries(config || {})) {
      if (!entry) continue;

      let client = null;
      let connectionError = null;

      try {
        const normalized = resolveEnvVars(entry);
        const transport = createTransport(provider, normalized);
        client = await experimental_createMCPClient({ transport });
        clients.push(client);
      } catch (err) {
        connectionError = err;
      }

      if (!client) {
        const failure = {
          provider,
          ok: false,
          pong: null,
          latencyMs: null,
          error: connectionError?.message || String(connectionError || "Unable to initialise MCP client"),
          ts: new Date().toISOString(),
        };
        results.push(failure);
        addRecentPing(failure);
        continue;
      }

      const startedAt = Date.now();
      let ok = false;
      let pong = null;
      let error = null;

      try {
        const maybePing = client?.ping || client?.utilities?.ping;
        if (typeof maybePing === "function") {
          pong = await maybePing();
          ok = true;
        } else {
          await client.tools();
          pong = { message: "pong (tools())" };
          ok = true;
        }
      } catch (e) {
        ok = false;
        error = e?.message || String(e);
      }

      const finishedAt = Date.now();
      const latencyMs = finishedAt - startedAt;

      const entryResult = {
        provider,
        ok,
        pong,
        latencyMs,
        error: ok ? null : error,
        ts: new Date().toISOString(),
      };
      results.push(entryResult);
      addRecentPing(entryResult);
    }
  } finally {
    await Promise.allSettled(clients.map((c) => c?.close?.()));
  }

  return results;
}
