from __future__ import annotations

import asyncio
import json
from typing import Any

from .config import CHAT_SCRIPT, MCP_STATUS_SCRIPT, REPO_ROOT, resolve_node_executable


class NodeBridgeError(RuntimeError):
    """Raised when a Node helper script fails or returns invalid data."""


async def _invoke_node(
    script_path,
    payload: dict[str, Any],
    *,
    timeout: float | None = None,
) -> Any:
    if not script_path.exists():
        raise NodeBridgeError(f"Node helper not found: {script_path}")

    node_executable = resolve_node_executable()

    proc = await asyncio.create_subprocess_exec(
        node_executable,
        str(script_path),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(REPO_ROOT),
    )

    input_bytes = json.dumps(payload).encode("utf-8")

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=input_bytes), timeout=timeout
        )
    except asyncio.TimeoutError as exc:
        proc.kill()
        await proc.wait()
        raise NodeBridgeError(
            f"Node helper timed out after {timeout} seconds"
        ) from exc

    if proc.returncode != 0:
        raise NodeBridgeError(
            f"Node helper exited with {proc.returncode}: {stderr.decode('utf-8', errors='ignore')}"
        )

    try:
        return json.loads(stdout.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise NodeBridgeError(
            f"Invalid JSON returned from Node helper: {exc}"
        ) from exc


async def run_chat_helper(payload: dict[str, Any], *, timeout: float | None = None) -> Any:
    return await _invoke_node(CHAT_SCRIPT, payload, timeout=timeout)


async def run_mcp_status_helper(payload: dict[str, Any], *, timeout: float | None = None) -> Any:
    return await _invoke_node(MCP_STATUS_SCRIPT, payload, timeout=timeout)


__all__ = [
    "NodeBridgeError",
    "run_chat_helper",
    "run_mcp_status_helper",
]
