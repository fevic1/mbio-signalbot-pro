"""Provider-agnostic MCP management and gateway API.

The dashboard talks to this API. The API owns registry state and uses the
standard MCP client runtime for discovery, health checks, and tool execution.
No provider-specific endpoints or authentication flows are embedded here.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException

from core.mcp_client import MCPClientError, call_tool, detect_transport, health, list_tools
from core.mcp_registry import MCPServerConfig, mcp_registry
from routes.dashboard_auth import get_current_user

router = APIRouter(prefix="/api/mcp", tags=["mcp"])


def _public_server(server: MCPServerConfig) -> Dict[str, Any]:
    return {
        "server_id": server.server_id,
        "name": server.name,
        "description": server.description or "",
        "endpoint": server.endpoint,
        "transport": server.transport,
        "auth_type": server.auth_type,
        "rate_limit_per_min": server.rate_limit_per_min,
        "is_active": server.enabled,
        "status": server.last_status,
        "last_heartbeat": server.last_heartbeat.isoformat() if server.last_heartbeat else None,
        "last_error": server.last_error,
    }


def _auth_providers(config: MCPServerConfig) -> list[dict[str, str]]:
    providers: list[dict[str, str]] = [{"type": "none", "label": "No authentication"}]
    auth_type = (config.auth_type or "none").lower()
    if config.api_key or auth_type == "api_key":
        providers.append({"type": "api_key", "label": "API key"})
    if config.auth_token or auth_type in {"bearer", "access_token"}:
        providers.append({"type": "bearer", "label": "Bearer token"})
    if auth_type in {"oauth", "oauth2"}:
        providers.append({"type": "oauth", "label": "OAuth 2.1 access token"})
    return providers


@router.post("/validate")
async def validate_config(config: MCPServerConfig, _: dict = Depends(get_current_user)):
    if not config.server_id.strip():
        return {"valid": False, "error": "server_id is required"}
    if not config.name.strip():
        return {"valid": False, "error": "name is required"}
    if not config.endpoint:
        return {"valid": False, "error": "endpoint is required"}
    if config.rate_limit_per_min < 1:
        return {"valid": False, "error": "rate_limit_per_min must be >= 1"}
    return {"valid": True}


@router.post("/detect-transport")
async def detect(config: MCPServerConfig, _: dict = Depends(get_current_user)):
    try:
        transport, state = await detect_transport(config)
        return {
            "transport": transport,
            "status": state or "detected",
            "auth_required": state == "authentication_required",
        }
    except MCPClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/{server_id}/auth-providers")
async def auth_providers(server_id: str, _: dict = Depends(get_current_user)):
    server = await mcp_registry.get_server(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="MCP server not found")
    return {"providers": _auth_providers(server)}


@router.post("/{server_id}/connect")
async def connect(server_id: str, payload: Dict[str, Any], _: dict = Depends(get_current_user)):
    server = await mcp_registry.get_server(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="MCP server not found")

    if payload.get("transport"):
        server.transport = payload["transport"]
    auth = payload.get("auth") or {}
    if auth.get("type"):
        server.auth_type = auth["type"]
    if auth.get("key"):
        server.api_key = auth["key"]
    if auth.get("token"):
        server.auth_token = auth["token"]
    if auth.get("header"):
        server.auth_header = auth["header"]
    if auth.get("headers"):
        server.headers = dict(auth["headers"])

    result = await health(server)
    await mcp_registry.update_health(server_id, result["status"], result.get("error"))
    return {"server_id": server_id, **result}


@router.post("/{server_id}/auth")
async def authenticate(server_id: str, payload: Dict[str, Any], _: dict = Depends(get_current_user)):
    server = await mcp_registry.get_server(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="MCP server not found")

    method = str(payload.get("method") or "none").lower()
    credentials = payload.get("credentials") or {}
    server.auth_type = method

    if method == "api_key":
        server.api_key = credentials.get("key") or credentials.get("api_key")
        server.auth_header = credentials.get("header") or server.auth_header
    elif method in {"bearer", "oauth", "oauth2", "access_token"}:
        server.auth_token = credentials.get("token") or credentials.get("access_token")
        server.api_key = None
    elif method == "none":
        server.api_key = None
        server.auth_token = None

    if method != "none" and not (server.api_key or server.auth_token):
        raise HTTPException(status_code=400, detail="Authentication credentials are required")

    result = await health(server)
    await mcp_registry.update_health(server_id, result["status"], result.get("error"))
    if result["status"] not in {"healthy", "ready"}:
        return {"success": False, **result}
    return {"success": True, **result}


@router.get("/{server_id}/tools")
async def tools(server_id: str, _: dict = Depends(get_current_user)):
    server = await mcp_registry.get_server(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="MCP server not found")
    try:
        discovered = await list_tools(server)
        await mcp_registry.register_tools(server_id, discovered)
        await mcp_registry.update_health(server_id, "healthy")
        return {"tools": discovered}
    except MCPClientError as exc:
        await mcp_registry.update_health(server_id, "auth_required" if "authentication" in str(exc).lower() else "unhealthy", str(exc))
        raise HTTPException(status_code=401 if "authentication" in str(exc).lower() else 502, detail=str(exc)) from exc


@router.post("/{server_id}/register-tools")
async def register_tools(server_id: str, payload: Dict[str, Any], _: dict = Depends(get_current_user)):
    if await mcp_registry.get_server(server_id) is None:
        raise HTTPException(status_code=404, detail="MCP server not found")
    tools_payload = payload.get("tools") or []
    if not isinstance(tools_payload, list):
        raise HTTPException(status_code=400, detail="tools must be a list")
    count = await mcp_registry.register_tools(server_id, tools_payload)
    return {"registered": count}


@router.get("/{server_id}/health")
async def health_check(server_id: str, _: dict = Depends(get_current_user)):
    server = await mcp_registry.get_server(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="MCP server not found")
    result = await health(server)
    await mcp_registry.update_health(server_id, result["status"], result.get("error"))
    return result


@router.post("/register")
async def register(config: MCPServerConfig, _: dict = Depends(get_current_user)):
    created = await mcp_registry.register_server(config)
    if not created:
        raise HTTPException(status_code=409, detail=f"Server ID '{config.server_id}' already exists")

    # Registration is intentionally non-blocking with respect to credentials.
    # A server can be registered first and authenticated through the standard
    # auth endpoint when its provider requires credentials.
    return {"status": "success", "server_id": config.server_id}


@router.get("/servers")
async def servers(_: dict = Depends(get_current_user)):
    registered = await mcp_registry.get_all_servers()
    return {"servers": [_public_server(server) for server in registered]}


@router.delete("/{server_id}")
async def delete(server_id: str, _: dict = Depends(get_current_user)):
    deleted = await mcp_registry.unregister_server(server_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="MCP server not found")
    return {"deleted": True, "server_id": server_id}


@router.post("/{server_id}/invoke")
async def invoke(server_id: str, payload: Dict[str, Any], _: dict = Depends(get_current_user)):
    server = await mcp_registry.get_server(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="MCP server not found")

    method = payload.get("method")
    if method != "tools/call":
        raise HTTPException(status_code=400, detail="Only tools/call is supported by the gateway")

    params = payload.get("params") or {}
    name = params.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Tool name is required")

    registered = await mcp_registry.get_tools(server_id)
    if registered and name not in registered:
        raise HTTPException(status_code=404, detail=f"Tool '{name}' is not registered")

    try:
        result = await call_tool(server, name, params.get("arguments") or {})
        return {"jsonrpc": "2.0", "id": payload.get("id"), "result": result}
    except MCPClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
