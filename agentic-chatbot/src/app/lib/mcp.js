import fs from 'node:fs/promises';
import path from 'node:path';
import { experimental_createMCPClient } from 'ai';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js';

// Allow MariaDB tool
const ALLOWED_TOOLS = new Set([
  'connect',
  'list-collections',
  'list-databases',
  'find',
  'count',
  'aggregate',
  'explain',
  'execute_sql' // MariaDB MCP tool
]);

export async function loadAllMCPTools() {
  const configPath = path.join(process.cwd(), 'mcp-config.json');
  const raw = await fs.readFile(configPath, 'utf8');
  const config = JSON.parse(raw);

  const clients = [];
  const toolsMap = {};

  for (const [provider, entry] of Object.entries(config || {})) {
    let transport = null;

    if (entry?.command) {
      transport = new StdioClientTransport({
        command: entry.command,
        args: Array.isArray(entry.args) ? entry.args : [],
        env: { ...process.env, ...(entry.env || {}) }
      });
    } else if (entry?.url) {
      transport = new SSEClientTransport(new URL(entry.url), {});
    } else {
      continue;
    }

    const client = await experimental_createMCPClient({ transport });
    clients.push(client);

    const tools = await client.tools();
    const entries =
      Array.isArray(tools)
        ? tools
            .filter(t => t && typeof t.name === 'string' && ALLOWED_TOOLS.has(t.name))
            .map(t => [t.name, t])
        : Object.entries(tools || {}).filter(([name]) => ALLOWED_TOOLS.has(name));

    for (const [name, def] of entries) {
      toolsMap[`${provider}.${name}`] = def;
    }
  }

  const closeAll = async () => {
    await Promise.allSettled(clients.map(c => c?.close?.()));
  };

  return { tools: toolsMap, closeAll };
}

// --- MCP Ping/Pong utilities (per MCP basic utilities spec) -----------------

// In-memory circular buffer for recent ping results (per process)
const MAX_RECENT_PINGS = 10;
const recentPings = [];

function addRecentPing(entry) {
  recentPings.push(entry);
  while (recentPings.length > MAX_RECENT_PINGS) recentPings.shift();
}

export function getRecentPings() {
  // return newest-first copy
  return [...recentPings].reverse();
}

export async function pingAllMCPProviders() {
  const configPath = path.join(process.cwd(), 'mcp-config.json');
  const raw = await fs.readFile(configPath, 'utf8');
  const config = JSON.parse(raw);

  const results = [];
  const clients = [];

  try {
    for (const [provider, entry] of Object.entries(config || {})) {
      let transport = null;
      if (entry?.command) {
        transport = new StdioClientTransport({
          command: entry.command,
          args: Array.isArray(entry.args) ? entry.args : [],
          env: { ...process.env, ...(entry.env || {}) },
        });
      } else if (entry?.url) {
        transport = new SSEClientTransport(new URL(entry.url), {});
      } else {
        continue;
      }

      const client = await experimental_createMCPClient({ transport });
      clients.push(client);

      const startedAt = Date.now();
      let ok = false;
      let pong = null;
      let error = null;
      try {
        // Prefer real ping if available on client
        const maybePing = client?.ping || client?.utilities?.ping;
        if (typeof maybePing === 'function') {
          pong = await maybePing();
          ok = true;
        } else {
          // Fallback: list tools as a lightweight health check
          await client.tools();
          pong = { message: 'pong (tools())' };
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