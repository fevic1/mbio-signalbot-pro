import hmac
import os

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

from aios.skills.core.models import Skill
from core.mcp_registry import MCPServerConfig, mcp_registry


router = APIRouter(prefix="/aios/settings", tags=["aios-settings"])


class MCPServerInput(BaseModel):
    server_id: str
    name: str
    description: str = ""
    endpoint: str | None = None
    server_api_key: str | None = None
    rate_limit_per_min: int = Field(default=60, ge=1, le=10000)


class SkillInput(BaseModel):
    name: str
    domain: str
    description: str = ""
    capabilities: list[str] = Field(default_factory=list)
    version: str = "1.0"


def require_admin_key(x_api_key: str = Header(..., alias="X-API-Key")):
    expected = os.getenv("AIOS_ADMIN_API_KEY")

    if not expected:
        raise HTTPException(
            status_code=503,
            detail="AIOS_ADMIN_API_KEY is not configured",
        )

    if not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid admin key")


def services_for(request: Request):
    return getattr(request.app.state.aios, "services", {})


@router.get("/mcp-servers")
async def list_mcp_servers(_: None = require_admin_key):
    servers = await mcp_registry.get_all_servers()

    return {
        "servers": [
            {
                "server_id": server.server_id,
                "name": server.name,
                "description": server.description,
                "endpoint": server.endpoint,
                "enabled": server.enabled,
                "rate_limit_per_min": server.rate_limit_per_min,
            }
            for server in servers
        ]
    }


@router.post("/mcp-servers")
async def add_mcp_server(
    payload: MCPServerInput,
    _: None = require_admin_key,
):
    success = await mcp_registry.register_server(
        MCPServerConfig(
            server_id=payload.server_id,
            name=payload.name,
            description=payload.description,
            endpoint=payload.endpoint,
            api_key=payload.server_api_key,
            rate_limit_per_min=payload.rate_limit_per_min,
        )
    )

    if not success:
        raise HTTPException(status_code=409, detail="Server ID already exists")

    return {"success": True, "server_id": payload.server_id}


@router.delete("/mcp-servers/{server_id}")
async def remove_mcp_server(
    server_id: str,
    _: None = require_admin_key,
):
    if not await mcp_registry.unregister_server(server_id):
        raise HTTPException(status_code=404, detail="Server not found")

    return {"success": True}


@router.get("/skills")
async def list_skills(
    request: Request,
    _: None = require_admin_key,
):
    skill_registry = services_for(request).get("skill_registry")

    return {
        "skills": (
            skill_registry.list_skills()
            if skill_registry else []
        )
    }


@router.post("/skills")
async def add_skill(
    request: Request,
    payload: SkillInput,
    _: None = require_admin_key,
):
    skill_registry = services_for(request).get("skill_registry")

    if skill_registry is None:
        raise HTTPException(
            status_code=503,
            detail="Skill registry unavailable",
        )

    skill = Skill(
        name=payload.name,
        domain=payload.domain,
        description=payload.description,
        capabilities=payload.capabilities,
        version=payload.version,
    )
    skill.activate()
    skill_registry.register(skill)

    return {"success": True, "skill": skill.describe()}


@router.delete("/skills/{name}")
async def remove_skill(
    request: Request,
    name: str,
    _: None = require_admin_key,
):
    skill_registry = services_for(request).get("skill_registry")

    if skill_registry is None or skill_registry.remove(name) is None:
        raise HTTPException(status_code=404, detail="Skill not found")

    return {"success": True}
