import pytest

from core.mcp_client import _headers, _transport
from core.mcp_registry import MCPRegistry, MCPServerConfig


def test_api_key_headers_are_provider_agnostic():
    config = MCPServerConfig(
        server_id="example",
        name="Example",
        endpoint="https://example.test/mcp",
        auth_type="api_key",
        api_key="secret",
        auth_header="Authorization",
    )
    assert _headers(config) == {"Authorization": "secret"}


def test_bearer_headers_use_standard_authorization():
    config = MCPServerConfig(
        server_id="example",
        name="Example",
        endpoint="https://example.test/mcp",
        auth_type="bearer",
        auth_token="token",
    )
    assert _headers(config) == {"Authorization": "Bearer token"}


def test_transport_aliases():
    config = MCPServerConfig(server_id="a", name="A", transport="http")
    assert _transport(config) == "streamable_http"
    config.transport = "sse"
    assert _transport(config) == "sse"


@pytest.mark.asyncio
async def test_registry_preserves_credentials_and_tools_on_update():
    registry = MCPRegistry()
    original = MCPServerConfig(
        server_id="example",
        name="Example",
        endpoint="https://example.test/mcp",
        api_key="secret",
    )
    assert await registry.register_server(original)
    assert await registry.register_tool("example", "ping", {"name": "ping"})

    updated = MCPServerConfig(
        server_id="example",
        name="Example Updated",
        endpoint="https://example.test/mcp",
    )
    assert await registry.update_server("example", updated)

    server = await registry.get_server("example")
    assert server is not None
    assert server.api_key == "secret"
    assert "ping" in await registry.get_tools("example")
