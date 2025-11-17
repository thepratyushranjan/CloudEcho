from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator

from .config import (
    CHAT_SCRIPT,
    MCP_STATUS_SCRIPT,
    REPO_ROOT,
    resolve_node_executable,
    resolve_node_timeout,
)


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

    stdout_str = stdout.decode('utf-8', errors='ignore')
    stderr_str = stderr.decode('utf-8', errors='ignore')

    print("--- Node.js stdout ---")
    print(stdout_str)
    print("--- End Node.js stdout ---")

    if stderr_str:
        print("--- Node.js stderr ---")
        print(stderr_str)
        print("--- End Node.js stderr ---")

    if proc.returncode != 0:
        raise NodeBridgeError(
            f"Node helper exited with {proc.returncode}: {stderr_str}"
        )

    try:
        # The Node.js script may output MCP log messages to stdout before the JSON
        # Find the JSON response by looking for the last line that starts with '{'
        lines = stdout_str.strip().split('\n')

        # Find the JSON response (should be the last line starting with '{')
        json_line = None
        for line in reversed(lines):
            if line.strip().startswith('{'):
                json_line = line.strip()
                break

        if json_line is None:
            raise NodeBridgeError(
                f"No JSON response found in Node helper output: {stdout_str}"
            )

        return json.loads(json_line)
    except json.JSONDecodeError as exc:
        raise NodeBridgeError(
            f"Invalid JSON returned from Node helper: {exc}"
        ) from exc


async def run_chat_helper(payload: dict[str, Any], *, timeout: float | None = None) -> Any:
    return await _invoke_node(CHAT_SCRIPT, payload, timeout=timeout)


async def stream_chat_helper(
    payload: dict[str, Any], *, timeout: float | None = None
) -> AsyncGenerator[bytes, None]:
    if not CHAT_SCRIPT.exists():
        raise NodeBridgeError(f"Node helper not found: {CHAT_SCRIPT}")

    node_executable = resolve_node_executable()

    proc = await asyncio.create_subprocess_exec(
        node_executable,
        str(CHAT_SCRIPT),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(REPO_ROOT),
    )

    input_bytes = json.dumps(payload).encode("utf-8")
    assert proc.stdin is not None
    assert proc.stdout is not None
    assert proc.stderr is not None
    proc.stdin.write(input_bytes)
    await proc.stdin.drain()
    proc.stdin.close()

    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout if timeout else None

    async def read_chunk(size: int = 4096) -> bytes:
        if deadline is None:
            return await proc.stdout.read(size)
        remaining = deadline - loop.time()
        if remaining <= 0:
            raise asyncio.TimeoutError
        return await asyncio.wait_for(proc.stdout.read(size), remaining)

    async def generator():
        try:
            while True:
                chunk = await read_chunk()
                if not chunk:
                    break
                yield chunk

            if deadline is None:
                await proc.wait()
            else:
                remaining = deadline - loop.time()
                if remaining <= 0:
                    raise asyncio.TimeoutError
                await asyncio.wait_for(proc.wait(), remaining)

            if proc.returncode != 0:
                stderr_data = await proc.stderr.read()
                raise NodeBridgeError(
                    f"Node helper exited with {proc.returncode}: {stderr_data.decode('utf-8', errors='ignore')}"
                )
        except asyncio.TimeoutError as exc:
            proc.kill()
            await proc.wait()
            raise NodeBridgeError(
                f"Node helper timed out after {timeout} seconds"
            ) from exc
        finally:
            if proc.returncode is None:
                proc.kill()
                await proc.wait()

    return generator()


async def run_mcp_status_helper(payload: dict[str, Any], *, timeout: float | None = None) -> Any:
    effective_timeout = timeout if timeout is not None else resolve_node_timeout()
    return await _invoke_node(MCP_STATUS_SCRIPT, payload, timeout=effective_timeout)


__all__ = [
    "NodeBridgeError",
    "run_chat_helper",
    "stream_chat_helper",
    "run_mcp_status_helper",
]
