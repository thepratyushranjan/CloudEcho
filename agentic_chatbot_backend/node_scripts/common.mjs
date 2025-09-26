export async function readJsonFromStdin(defaultValue = {}) {
  const chunks = [];
  for await (const chunk of process.stdin) {
    chunks.push(Buffer.from(chunk));
  }
  if (chunks.length === 0) return defaultValue;
  const raw = Buffer.concat(chunks).toString("utf8");
  if (!raw) return defaultValue;
  try {
    return JSON.parse(raw);
  } catch (err) {
    throw new Error(`Failed to parse stdin JSON: ${err.message}`);
  }
}

export function writeJsonToStdout(payload) {
  process.stdout.write(JSON.stringify(payload));
}

export function writeErrorAndExit(err) {
  process.stderr.write(String(err?.message || err));
  process.exitCode = 1;
}
