"""
MBIO remote DefiLlama MCP client.

Endpoint:
    https://mcp.defillama.com/mcp

Authentication:
    OAuth 2.1 via FastMCP.

OAuth credentials are persisted in encrypted local storage.
"""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

from cryptography.fernet import Fernet
from fastmcp import Client
from fastmcp.client.auth import OAuth
from key_value.aio.stores.disk import DiskStore
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper


DEFILLAMA_MCP_URL = "https://mcp.defillama.com/mcp"
OAUTH_STORAGE_DIR = Path("data/mcp/defillama/oauth")
OAUTH_KEY_FILE = OAUTH_STORAGE_DIR / "storage.key"


def _storage_key() -> bytes:
    OAUTH_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    env_key = os.getenv("DEFILLAMA_OAUTH_STORAGE_KEY")
    if env_key:
        return env_key.encode()

    if OAUTH_KEY_FILE.exists():
        return OAUTH_KEY_FILE.read_bytes()

    key = Fernet.generate_key()
    OAUTH_KEY_FILE.write_bytes(key)
    OAUTH_KEY_FILE.chmod(0o600)

    return key


def _token_storage():
    return FernetEncryptionWrapper(
        key_value=DiskStore(
            directory=str(OAUTH_STORAGE_DIR / "tokens")
        ),
        fernet=Fernet(_storage_key()),
    )


def create_client() -> Client:
    oauth = OAuth(
        mcp_url=DEFILLAMA_MCP_URL,
        client_name="MBIO SignalBot Pro",
        token_storage=_token_storage(),
        callback_port=8765,
    )

    return Client(
        DEFILLAMA_MCP_URL,
        auth=oauth,
    )


async def verify() -> None:
    client = create_client()

    async with client:
        tools = await client.list_tools()
        names = {tool.name for tool in tools}

        print(f"DefiLlama tools discovered: {len(names)}")

        if "get_market_totals" not in names:
            raise RuntimeError(
                "DefiLlama MCP is reachable but get_market_totals "
                "was not discovered"
            )

        result = await client.call_tool(
            "get_market_totals",
            {},
        )

        if result.is_error:
            raise RuntimeError(
                f"get_market_totals returned MCP error: {result.content}"
            )

        print("PASS: DefiLlama MCP authenticated")
        print("PASS: tools/list")
        print("PASS: get_market_totals")
        print("RESULT:")
        print(
            result.data
            if result.data is not None
            else result.content
        )


async def list_tools() -> None:
    client = create_client()

    async with client:
        tools = await client.list_tools()

        print(f"DefiLlama tools discovered: {len(tools)}")
        for tool in tools:
            print(f"- {tool.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("verify", "list-tools"),
    )

    args = parser.parse_args()

    if args.command == "verify":
        asyncio.run(verify())
    else:
        asyncio.run(list_tools())


if __name__ == "__main__":
    main()
