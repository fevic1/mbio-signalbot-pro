import uuid

import pytest
from fastapi import HTTPException

from core.mcp_registry import MCPServerConfig, mcp_registry
from routes import dashboard_api


def make_config(server_id: str, *, enabled: bool = True) -> MCPServerConfig:
    return MCPServerConfig(
        server_id=server_id,
        name="Test MCP",
        description="Dashboard MCP regression test",
        api_key="test-api-key-1234567890",
        rate_limit_per_min=60,
        endpoint="https://example.test/mcp",
        enabled=enabled,
    )


@pytest.mark.asyncio
async def test_dashboard_uses_canonical_mcp_singleton():
    assert dashboard_api.mcp_registry is mcp_registry


@pytest.mark.asyncio
async def test_dashboard_registers_through_canonical_registry():
    server_id = f"test-mcp-{uuid.uuid4().hex[:10]}"
    config = make_config(server_id)

    try:
        result = await dashboard_api.register_mcp_server(
            config,
            {"email": "test@mbio.com"},
        )

        assert result == {
            "status": "success",
            "server_id": server_id,
        }

        registered = await mcp_registry.get_server(server_id)

        assert registered is not None
        assert registered.server_id == server_id
        assert registered.name == config.name
        assert registered.description == config.description
        assert registered.api_key == config.api_key

        with pytest.raises(HTTPException) as exc:
            await dashboard_api.register_mcp_server(
                config,
                {"email": "test@mbio.com"},
            )

        assert exc.value.status_code == 409

    finally:
        await mcp_registry.unregister_server(server_id)


@pytest.mark.asyncio
async def test_dashboard_lists_registry_metadata_without_api_key():
    server_id = f"test-mcp-{uuid.uuid4().hex[:10]}"
    config = make_config(server_id)

    try:
        assert await mcp_registry.register_server(config)

        result = await dashboard_api.get_mcp_servers(
            {"email": "test@mbio.com"}
        )

        server = next(
            item
            for item in result["servers"]
            if item["server_id"] == server_id
        )

        assert server == {
            "server_id": server_id,
            "name": "Test MCP",
            "description": "Dashboard MCP regression test",
            "rate_limit_per_min": 60,
            "endpoint": "https://example.test/mcp",
            "is_active": True,
        }
        assert "api_key" not in server

    finally:
        await mcp_registry.unregister_server(server_id)


@pytest.mark.asyncio
async def test_dashboard_preserves_disabled_server_state():
    server_id = f"test-mcp-{uuid.uuid4().hex[:10]}"
    config = make_config(server_id, enabled=False)

    try:
        assert await mcp_registry.register_server(config)

        result = await dashboard_api.get_mcp_servers(
            {"email": "test@mbio.com"}
        )

        server = next(
            item
            for item in result["servers"]
            if item["server_id"] == server_id
        )

        assert server["is_active"] is False

    finally:
        await mcp_registry.unregister_server(server_id)


@pytest.mark.asyncio
async def test_dashboard_unregisters_through_canonical_registry():
    server_id = f"test-mcp-{uuid.uuid4().hex[:10]}"

    try:
        result = await dashboard_api.register_mcp_server(
            make_config(server_id),
            {"email": "test@mbio.com"},
        )

        assert result["status"] == "success"

        result = await dashboard_api.unregister_mcp_server(
            server_id,
            {"email": "test@mbio.com"},
        )

        assert result == {"status": "success"}
        assert await mcp_registry.get_server(server_id) is None

    finally:
        await mcp_registry.unregister_server(server_id)


@pytest.mark.asyncio
async def test_dashboard_unregister_missing_server_returns_404():
    server_id = f"missing-mcp-{uuid.uuid4().hex[:10]}"

    with pytest.raises(HTTPException) as exc:
        await dashboard_api.unregister_mcp_server(
            server_id,
            {"email": "test@mbio.com"},
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_dashboard_updates_server_and_preserves_existing_api_key():
    server_id = f"test-mcp-{uuid.uuid4().hex[:10]}"
    config = make_config(server_id)

    try:
        assert await mcp_registry.register_server(config)

        updated = MCPServerConfig(
            server_id=server_id,
            name="Updated MCP",
            description="Updated dashboard MCP",
            api_key=None,
            rate_limit_per_min=120,
            endpoint="https://updated.example.test/mcp",
            enabled=False,
        )

        result = await dashboard_api.update_mcp_server(
            server_id,
            updated,
            {"email": "test@mbio.com"},
        )

        assert result == {
            "status": "success",
            "server_id": server_id,
        }

        registered = await mcp_registry.get_server(server_id)

        assert registered is not None
        assert registered.name == "Updated MCP"
        assert registered.description == "Updated dashboard MCP"
        assert registered.rate_limit_per_min == 120
        assert registered.endpoint == "https://updated.example.test/mcp"
        assert registered.enabled is False
        assert registered.api_key == config.api_key

    finally:
        await mcp_registry.unregister_server(server_id)


@pytest.mark.asyncio
async def test_dashboard_update_missing_server_returns_404():
    server_id = f"missing-mcp-{uuid.uuid4().hex[:10]}"

    with pytest.raises(HTTPException) as exc:
        await dashboard_api.update_mcp_server(
            server_id,
            make_config(server_id),
            {"email": "test@mbio.com"},
        )

    assert exc.value.status_code == 404


def test_dashboard_mcp_routes_are_registered():
    routes = {
        (method, route.path)
        for route in dashboard_api.router.routes
        for method in getattr(route, "methods", set())
    }

    assert ("GET", "/api/dashboard/mcp/servers") in routes
    assert ("POST", "/api/dashboard/mcp/register") in routes
    assert ("PUT", "/api/dashboard/mcp/servers/{server_id}") in routes
    assert ("POST", "/api/dashboard/mcp/unregister/{server_id}") in routes


def test_dashboard_mcp_uses_only_canonical_registry_api():
    source = open(
        "routes/dashboard_api.py",
        encoding="utf-8",
    ).read()

    assert "core.mcp_models" not in source
    assert "mcp_registry.list_servers" not in source
    assert "mcp_registry.get_all_servers" in source
    assert "mcp_registry.register_server" in source
    assert "mcp_registry.unregister_server" in source
