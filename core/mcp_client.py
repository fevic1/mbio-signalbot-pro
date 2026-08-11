"""Standard MCP client runtime.

Provider-agnostic client for Streamable HTTP (preferred) and legacy SSE.
Authentication is expressed as HTTP headers; no provider-specific OAuth flow is
embedded here. OAuth-capable providers can supply an access token through the
same standard Authorization header once the user completes authorization.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Tuple

from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

from core.mcp_registry import MCPServerConfig


class MCPClientError(RuntimeError):
    """Raised for MCP transport, authentication, or protocol failures."""


def _headers(config: MCPServerConfig) -> Dict[str, str]:
    headers = dict(config.headers or {})
    auth_type = (config.auth_type or "none").lower()

    if auth_type in {"bearer", "oauth", "oauth2", "access_token"}:
        token = config.auth_token or config.api_key
        if token:
            headers.setdefault("Authorization", f"Bearer {token}")
    elif auth_type == "api_key" and config.api_key:
        headers.setdefault(config.auth_header or "X-API-Key", config.api_key)

    return headers


def _transport(config: MCPServerConfig) -> str:
    value = (config.transport or "auto").lower().replace("-", "_")
    aliases = {
        "http": "streamable_http",
        "http_stream": "streamable_http",
        "streamablehttp": "streamable_http",
        "streamable_http": "streamable_http",
        "sse": "sse",
    }
    if value in aliases:
        return aliases[value]
    if value != "auto":
        raise MCPClientError(f"Unsupported MCP transport: {config.transport}")
    return "streamable_http"


@asynccontextmanager
async def open_session(config: MCPServerConfig) -> AsyncIterator[ClientSession]:
    """Open an initialized MCP session using the configured transport."""
    if not config.endpoint:
        raise MCPClientError("MCP endpoint is required")

    headers = _headers(config)
    transport = _transport(config)

    try:
        if transport == "sse":
            async with sse_client(config.endpoint, headers=headers) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    yield session
        else:
            async with streamable_http_client(config.endpoint, headers=headers) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    yield session
    except Exception as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        if status == 401 or "401" in str(exc):
            raise MCPClientError("MCP authentication required or credentials rejected") from exc
        if status == 403 or "403" in str(exc):
            raise MCPClientError("MCP credentials are not authorized") from exc
        raise MCPClientError(str(exc)) from exc


async def detect_transport(config: MCPServerConfig) -> Tuple[str, str | None]:
    """Probe transports without invoking tools.

    Streamable HTTP is always attempted first because it is the current
    standard. A 401/403 still proves the endpoint speaks the selected
    transport, so authentication can be completed separately.
    """
    if (config.transport or "auto").lower() not in {"", "auto"}:
        return _transport(config), None

    stream_config = MCPServerConfig(**{**config.__dict__, "transport": "streamable_http"})
    try:
        async with open_session(stream_config):
            return "streamable_http", None
    except MCPClientError as exc:
        message = str(exc)
        if "authentication required" in message or "not authorized" in message:
            return "streamable_http", "authentication_required"

    sse_config = MCPServerConfig(**{**config.__dict__, "transport": "sse"})
    try:
        async with open_session(sse_config):
            return "sse", None
    except MCPClientError as exc:
        message = str(exc)
        if "authentication required" in message or "not authorized" in message:
            return "sse", "authentication_required"
        raise MCPClientError(f"Unable to connect using Streamable HTTP or SSE: {message}") from exc


async def list_tools(config: MCPServerConfig) -> List[Dict[str, Any]]:
    async with open_session(config) as session:
        response = await session.list_tools()
        return [tool.model_dump(mode="json") for tool in response.tools]


async def call_tool(config: MCPServerConfig, name: str, arguments: Dict[str, Any] | None = None) -> Dict[str, Any]:
    async with open_session(config) as session:
        result = await session.call_tool(name, arguments or {})
        return result.model_dump(mode="json")


async def health(config: MCPServerConfig) -> Dict[str, Any]:
    try:
        async with open_session(config) as session:
            await session.send_ping()
            capabilities = session.get_server_capabilities()
            return {
                "status": "healthy",
                "transport": _transport(config),
                "protocol_version": getattr(session, "protocol_version", None),
                "capabilities": capabilities.model_dump(mode="json") if capabilities else {},
            }
    except MCPClientError as exc:
        message = str(exc)
        if "authentication required" in message or "not authorized" in message:
            return {"status": "auth_required", "transport": _transport(config), "error": message}
        return {"status": "unhealthy", "transport": _transport(config), "error": message}
