"""
Dynamic MCP Gateway
Routes MCP protocol requests to the appropriate registered server module.
"""
import logging
import json
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Any, Dict
from pydantic import BaseModel

from core.mcp_registry import mcp_registry, MCPServerConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["mcp-gateway"])

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any]
    id: str | int

def verify_mcp_auth(x_api_key: str = Header(..., alias="X-API-Key")):
    """Dependency to validate API key against registered servers."""
    return x_api_key

@router.post("/{server_id}/invoke")
async def invoke_mcp_tool(
    server_id: str,
    request: MCPRequest,
    api_key: str = Depends(verify_mcp_auth)
):
    """
    Dynamic endpoint to invoke a tool on a specific registered MCP server.
    Example POST: /mcp/vibe-trading/invoke
    """
    # 1. Validate Server
    server_config = await mcp_registry.get_server(server_id)
    if not server_config or not server_config.is_active:
        raise HTTPException(status_code=404, detail=f"MCP Server '{server_id}' not found or inactive")
    
    # 2. Validate API Key
    if not await mcp_registry.verify_api_key(server_id, api_key):
        raise HTTPException(status_code=401, detail="Invalid API key for this MCP server")

    # 3. Route to Tool
    if request.method == "tools/call":
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        
        # Check if tool exists
        tools = await mcp_registry.get_tools_for_server(server_id)
        if not tools or tool_name not in tools:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found on server '{server_id}'")
        
        # Execute tool
        try:
            # Log tool call for audit trail
            logger.info(f"MCP Tool Call: {server_id} -> {tool_name} (Params: {arguments})")
            
            # Execute the tool
            result = await tools[tool_name](**arguments)
            
            # Return success response
            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result)}],
                    "isError": False
                }
            }
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")
    
    elif request.method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {"resources": []}
        }
    
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported MCP method: {request.method}")

@router.get("/servers")
async def list_mcp_servers(api_key: str = Depends(verify_mcp_auth)):
    """List all registered MCP servers (metadata only, no API keys)."""
    servers = await mcp_registry.get_all_active_servers()
    return {
        "servers": [
            {
                "server_id": s.server_id,
                "name": s.name,
                "description": s.description,
                "rate_limit_per_min": s.rate_limit_per_min
            }
            for s in servers
        ]
    }

@router.post("/admin/register-server")
async def register_mcp_server(
    config: MCPServerConfig,
    api_key: str = Header(..., alias="X-API-Key")
):
    """Admin endpoint to register a new MCP server (requires admin API key)."""
    # In production, verify admin API key here
    success = await mcp_registry.register_server(config)
    if not success:
        raise HTTPException(status_code=409, detail="Server ID already exists")
    return {"status": "success", "server_id": config.server_id}

@router.post("/admin/unregister-server/{server_id}")
async def unregister_mcp_server(
    server_id: str,
    api_key: str = Header(..., alias="X-API-Key")
):
    """Admin endpoint to unregister an MCP server (requires admin API key)."""
    # In production, verify admin API key here
    success = await mcp_registry.unregister_server(server_id)
    if not success:
        raise HTTPException(status_code=404, detail="Server not found")
    return {"status": "success"}
