"""Generic OAuth orchestration for standard MCP servers.

The official MCP SDK owns OAuth discovery, PKCE, client registration/CIMD,
token exchange, refresh, and retry. MBIO only supplies encrypted storage and
the browser callback bridge.
"""

from __future__ import annotations

import asyncio
import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional

import httpx
from cryptography.fernet import Fernet
from key_value.aio.stores.disk import DiskStore
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper
from mcp import ClientSession
from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.auth import (
    OAuthClientInformationFull,
    OAuthClientMetadata,
    OAuthToken,
)


class OAuthCallbackError(RuntimeError):
    """Raised when the browser returns an OAuth error."""


class EncryptedMCPTokenStorage(TokenStorage):
    """Encrypted persistent OAuth storage, scoped by MCP server ID."""

    def __init__(self, server_id: str) -> None:
        if not server_id.strip():
            raise ValueError("server_id is required")

        root = Path(
            os.getenv("MCP_OAUTH_STORAGE_DIR", "data/mcp/oauth")
        )
        self.root = root / server_id
        self.root.mkdir(parents=True, exist_ok=True)

        self.key_file = self.root / "storage.key"

        env_key = os.getenv("MCP_OAUTH_STORAGE_KEY")
        if env_key:
            key = env_key.encode()
        elif self.key_file.exists():
            key = self.key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
            self.key_file.chmod(0o600)

        self.store = FernetEncryptionWrapper(
            key_value=DiskStore(
                directory=str(self.root / "tokens")
            ),
            fernet=Fernet(key),
        )

    async def get_tokens(self):
        data = await self.store.get("oauth_tokens")
        if not data:
            return None
        return OAuthToken.model_validate(data)

    async def set_tokens(self, tokens) -> None:
        await self.store.put(
            "oauth_tokens",
            tokens.model_dump(mode="json"),
        )

    async def get_client_info(self):
        data = await self.store.get("oauth_client_info")
        if not data:
            return None
        return OAuthClientInformationFull.model_validate(data)

    async def set_client_info(self, client_info) -> None:
        await self.store.put(
            "oauth_client_info",
            client_info.model_dump(mode="json"),
        )


@dataclass
class OAuthTransaction:
    transaction_id: str
    server_id: str
    config: Any
    redirect_uri: str

    authorization_url: Optional[str] = None
    status: str = "authorizing"
    error: Optional[str] = None
    result: Optional[dict[str, Any]] = None

    auth_ready: asyncio.Event = field(
        default_factory=asyncio.Event
    )
    callback_future: asyncio.Future = field(
        default_factory=lambda: asyncio.get_running_loop().create_future()
    )
    task: Optional[asyncio.Task] = None


class OAuthTransactionManager:
    def __init__(self) -> None:
        self._items: dict[str, OAuthTransaction] = {}
        self._lock = asyncio.Lock()

    async def create(
        self,
        *,
        server_id: str,
        config: Any,
        redirect_uri: str,
    ) -> OAuthTransaction:
        tx = OAuthTransaction(
            transaction_id=secrets.token_urlsafe(24),
            server_id=server_id,
            config=config,
            redirect_uri=redirect_uri,
        )
        async with self._lock:
            self._items[tx.transaction_id] = tx
        return tx

    async def get(self, transaction_id: str) -> OAuthTransaction | None:
        async with self._lock:
            return self._items.get(transaction_id)

    async def remove(self, transaction_id: str) -> None:
        async with self._lock:
            self._items.pop(transaction_id, None)


oauth_transactions = OAuthTransactionManager()


async def _oauth_redirect_handler(
    tx: OAuthTransaction,
    authorization_url: str,
) -> None:
    tx.authorization_url = authorization_url
    tx.auth_ready.set()


def _base_headers(config: Any) -> dict[str, str]:
    headers = dict(getattr(config, "headers", {}) or {})
    auth_type = str(
        getattr(config, "auth_type", "none") or "none"
    ).lower()

    if auth_type in {"bearer", "oauth", "oauth2", "access_token"}:
        token = (
            getattr(config, "auth_token", None)
            or getattr(config, "api_key", None)
        )
        if token:
            headers.setdefault(
                "Authorization",
                f"Bearer {token}",
            )

    elif auth_type == "api_key":
        key = getattr(config, "api_key", None)
        if key:
            headers.setdefault(
                getattr(config, "auth_header", None)
                or "X-API-Key",
                key,
            )

    return headers


def _callback_handler(tx: OAuthTransaction):
    async def callback() -> tuple[str, str | None]:
        code, state = await tx.callback_future
        return code, state

    return callback


async def run_oauth_transaction(
    tx: OAuthTransaction,
    *,
    on_ready: Callable[
        [OAuthTransaction, list[dict[str, Any]]],
        Awaitable[dict[str, Any]],
    ],
) -> None:
    try:
        metadata = OAuthClientMetadata(
            redirect_uris=[tx.redirect_uri],
            token_endpoint_auth_method="none",
            grant_types=[
                "authorization_code",
                "refresh_token",
            ],
            response_types=["code"],
            client_name="MBIO SignalBot Pro",
            software_id="mbio-signalbot-pro",
            software_version="1.0",
        )

        provider = OAuthClientProvider(
            server_url=tx.config.endpoint,
            client_metadata=metadata,
            storage=EncryptedMCPTokenStorage(
                tx.server_id
            ),
            redirect_handler=lambda url: _oauth_redirect_handler(
                tx,
                url,
            ),
            callback_handler=_callback_handler(tx),
        )

        headers = _base_headers(tx.config)

        async with httpx.AsyncClient(
            headers=headers,
            follow_redirects=True,
            auth=provider,
        ) as client:
            async with streamable_http_client(
                tx.config.endpoint,
                http_client=client,
            ) as (
                read_stream,
                write_stream,
                _,
            ):
                async with ClientSession(
                    read_stream,
                    write_stream,
                ) as session:
                    await session.initialize()

                    tools = await session.list_tools()

                    tool_list = [
                        tool.model_dump(mode="json")
                        for tool in tools.tools
                    ]

                    await session.send_ping()

                    tx.result = await on_ready(
                        tx,
                        tool_list,
                    )
                    tx.status = "ready"

    except asyncio.CancelledError:
        tx.status = "cancelled"
        raise
    except Exception as exc:
        tx.status = "error"
        tx.error = str(exc)
        tx.auth_ready.set()


async def wait_for_authorization_url(
    tx: OAuthTransaction,
    timeout: float = 10.0,
) -> str:
    try:
        await asyncio.wait_for(
            tx.auth_ready.wait(),
            timeout=timeout,
        )
    except asyncio.TimeoutError as exc:
        raise RuntimeError(
            "OAuth authorization URL was not produced"
        ) from exc

    if not tx.authorization_url:
        raise RuntimeError(
            tx.error or
            "OAuth flow failed before authorization URL"
        )

    return tx.authorization_url
