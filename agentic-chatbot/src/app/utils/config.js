// --- Configuration ---
export const CONFIG = {
    TIMEOUT_MS: Number(process.env.CHATBOT_RESPONSE_TIMEOUT_MS) || 30000,
    MODEL_PRO: process.env.GOOGLE_GEMINI_MODEL,
    MODEL_FLASH: process.env.GOOGLE_GEMINI_FLASH_MODEL,
    CHUNK_SIZE: 30,
    STREAM_DELAY: 10,
    MAX_TOOL_ROUNDS: 3,
  };

export const BUDGETS = {
    PLAN: getEnvInt("THINKING_BUDGET_PLAN"),
    EXECUTE: getEnvInt("THINKING_BUDGET_EXECUTE"),
    RETRY: getEnvInt("THINKING_BUDGET_RETRY"),
    INTERPRET: getEnvInt("THINKING_BUDGET_INTERPRET"),
  };

// --- Utilities ---
function getEnvInt(name, fallback) {
    const raw = process.env[name];
    if (!raw) return fallback;
    const n = Number(raw);
    return Number.isFinite(n) ? n : fallback;
  }