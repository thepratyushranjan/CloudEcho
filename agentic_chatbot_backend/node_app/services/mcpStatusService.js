import { pingAllMCPProviders } from "../lib/mcp.js";

function mapProviders(pingResults) {
  if (!Array.isArray(pingResults)) return {};
  return Object.fromEntries(
    pingResults
      .filter((entry) => entry && typeof entry.provider === "string")
      .map((entry) => [entry.provider, []])
  );
}

export async function getMCPStatus() {
  const pingResults = await pingAllMCPProviders();
  const connected = Array.isArray(pingResults) && pingResults.some((r) => r.ok);

  return {
    ok: connected,
    connected,
    result: connected ? "ping" : "pong",
    totalProviders: Array.isArray(pingResults) ? pingResults.length : 0,
    totalTools: 0,
    providers: mapProviders(pingResults),
  };
}

export default getMCPStatus;
