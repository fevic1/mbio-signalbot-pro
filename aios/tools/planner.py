from core.mcp_registry import mcp_registry

from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class ToolCall:
    server: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    priority: int = 100


class ToolPlanner:

    async def plan(
        self,
        *,
        capability,
        query,
        available_tools,
        context,
    ):


        if not mcp_registry.list_runtime_servers():
            mcp_registry.discover_servers()

        available_tools = await mcp_registry.runtime_tools()

        plan = []


        q = (query or "").lower()

        # Runtime registry is now the source of truth.
        # available_tools already contains every discovered MCP tool.

        for tool in available_tools:


            name = tool.get("name","").lower()

            if "dex" in q and "dex" in name:
                plan.append(ToolCall(
                        server=tool["server"],
                        name=tool["name"],
                    ))

            elif "hyperliquid" in q and "hyperliquid" in name:
                plan.append(ToolCall(
                        server=tool["server"],
                        name=tool["name"],
                    ))

            elif "github" in q and "github" in name:
                plan.append(ToolCall(
                        server=tool["server"],
                        name=tool["name"],
                    ))

            elif capability == "research":

                if tool.get("category") != "research":
                    continue
                args = {}
                skip_tool = False

                for arg in tool.get("required_args", []):

                    if arg == "query":
                        args["query"] = query

                    elif arg == "url":

                        if not (
                            query.startswith("http://")
                            or
                            query.startswith("https://")
                        ):
                            skip_tool = True
                            break

                        args["url"] = query

                    elif arg == "prompt":
                        args["prompt"] = query

                    elif arg == "coin":
                        args["coin"] = query

                    elif arg == "symbol":
                        args["symbol"] = query

                    elif arg == "token":
                        args["token"] = query

                    elif arg == "chain":
                        args["chain"] = query

                    elif arg == "protocol":
                        args["protocol"] = query

                    elif arg == "urls":
                        args = None
                        break

                if skip_tool or args is None:
                    continue

                plan.append(

                    ToolCall(
                        server=tool["server"],
                        name=tool["name"],
                        arguments=args,
                    )
                )

        return sorted(plan,key=lambda x:x.priority)
