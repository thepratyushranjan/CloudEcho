import { pingAllMCPProviders } from "../lib/mcp.js";


export async function getMCPStatus() {
  const pingResults = await pingAllMCPProviders();
  const connected = Array.isArray(pingResults) && pingResults.some((r) => r.ok);

  return {
    connected,
    result: connected ? "ping" : "pong",
    totalProviders: Array.isArray(pingResults) ? pingResults.length : 0,
  };
}

export default getMCPStatus;
