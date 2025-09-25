import fs from 'node:fs/promises';
import path from 'node:path';
import { experimental_createMCPClient } from 'ai';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';

function resolveEnvVars(value) {
  if (typeof value === 'string') {
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

  if (value && typeof value === 'object') {
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
  if (transportType === 'sse' || transportType === 'http') {
    if (!entry.url) {
      throw new Error(`Missing "url" for ${transportType.toUpperCase()} transport on provider "${provider}"`);
    }

    let url;
    try {
      url = new URL(entry.url);
    } catch (err) {
      throw new Error(
        `Invalid URL "${entry.url}" for ${transportType.toUpperCase()} transport on provider "${provider}": ${err.message}`
      );
    }

    const headers = entry.headers && typeof entry.headers === 'object'
      ? Object.fromEntries(
          Object.entries(entry.headers).map(([key, value]) => [key, String(value)])
        )
      : undefined;

    if (transportType === 'sse') {
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

/**
 * Loads all MCP providers defined in ./mcp-config.json
 * Returns { tools: Map<string, Tool>, closeAll: () => Promise<void> }
 * Tool names are namespaced as "<provider>.<tool>"
 */
export async function loadAllMCPTools() {
  const configPath = path.join(process.cwd(), 'mcp-config.json');
  const raw = await fs.readFile(configPath, 'utf8');
  const config = JSON.parse(raw);

  const clients = [];
  const toolsMap = {};

  for (const [provider, entry] of Object.entries(config || {})) {
    if (!entry) continue;

    try {
      const normalized = resolveEnvVars(entry);
      const transportKind = (normalized.transport || normalized.type || 'stdio').toUpperCase();
      const targetDesc = normalized.url ? normalized.url : normalized.command || 'unknown';
      console.info(`[MCP] Initializing provider "${provider}" via ${transportKind} -> ${targetDesc}`);
      const transport = createTransport(provider, normalized);
      const client = await experimental_createMCPClient({ transport });

      try {
        const tools = await client.tools();
        for (const [name, def] of Object.entries(tools || {})) {
          toolsMap[`${provider}.${name}`] = def;
        }
        clients.push(client);
      } catch (err) {
        if (typeof client.close === 'function') {
          try {
            await client.close();
          } catch {}
        }
        throw err;
      }
    } catch (err) {
      console.error(`Failed to initialize MCP provider "${provider}": ${err.message}`);
    }
  }

  const closeAll = async () => {
    await Promise.allSettled(clients.map((c) => c?.close?.()));
  };

  return { tools: toolsMap, closeAll };
}