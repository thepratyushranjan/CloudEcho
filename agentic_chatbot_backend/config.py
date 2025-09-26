from __future__ import annotations

from os import getenv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR
NODE_SCRIPTS_DIR = BASE_DIR / "node_scripts"

# Individual script entry points.
CHAT_SCRIPT = NODE_SCRIPTS_DIR / "chat.mjs"
MCP_STATUS_SCRIPT = NODE_SCRIPTS_DIR / "mcp-status.mjs"

# Default executable name for Node.js. Override via NODE_EXECUTABLE env if needed.
DEFAULT_NODE_EXECUTABLE = "node"
DEFAULT_STATUS_TIMEOUT_SECONDS = 15.0


def resolve_node_executable() -> str:
    """Return the Node.js executable to use for helper scripts."""
    return getenv("NODE_EXECUTABLE", DEFAULT_NODE_EXECUTABLE)


def resolve_node_timeout() -> float | None:
    raw = getenv("NODE_HELPER_TIMEOUT")
    if raw is None or raw.strip() == "":
        return DEFAULT_STATUS_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_STATUS_TIMEOUT_SECONDS
    return None if value <= 0 else value


__all__ = [
    "BASE_DIR",
    "REPO_ROOT",
    "NODE_SCRIPTS_DIR",
    "CHAT_SCRIPT",
    "MCP_STATUS_SCRIPT",
    "resolve_node_executable",
    "resolve_node_timeout",
]
