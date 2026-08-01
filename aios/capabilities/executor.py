import json
import re
from time import perf_counter

from aios.intelligence.llm_adapter import LLMAdapter
from aios.providers.router import chat
from aios.providers.router import provider_pool
from aios.neural_proxy.protocol import AIOSRequest
from aios.capabilities.policy import CapabilityPolicyEngine
from aios.capabilities.errors import CapabilityExecutionError

from .request import CapabilityRequest

class CapabilityExecutor:

    def __init__(
        self,
        system,
    ):
        self.system = system

        self.adapter = LLMAdapter(
            provider_pool,
            system,
        )

        self.policy = CapabilityPolicyEngine(
            provider_pool
        )

    def _get_capability_definition(self, name):

        registry = self.system.capability_registry

        if registry is None:
            raise CapabilityExecutionError(
                "Capability registry unavailable"
            )

        capability = registry.get(name)

        if capability is None:
            raise CapabilityExecutionError(
                f"Unknown capability: {name}"
            )

        return capability



    def _validate_capability_policy(
        self,
        capability,
    ):

        return self.policy.validate(
            capability
        )


    async def execute(
        self,
        request: CapabilityRequest,
    ):

        capability = self._get_capability_definition(
            request.capability
        )

        self._validate_capability_policy(
            capability
        )

        last_error = None

        for attempt in range(
            request.retry_limit + 1
        ):

            try:
                return await self._execute_once(
                    request,
                    attempt,
                )

            except Exception as error:
                last_error = error

        raise CapabilityExecutionError(
            f"{request.capability}: {last_error}"
        ) from last_error

    async def _execute_once(
        self,
        request: CapabilityRequest,
        attempt: int,
    ):

        prompt = self.adapter.build(
            request.capability,
            request,
        )

        mcp_client = None
        tools = []

        services = getattr(self.system, "services", None)
        if services:
            mcp_client = services.get("mcp_client")

        if mcp_client:
            tools = await mcp_client.list_tools()

        aios_request = AIOSRequest(
            capability=request.capability,
            messages=[
                {
                    "role": "system",
                    "content": prompt["system"],
                },
                {
                    "role": "user",
                    "content": str(prompt["context"]),
                },
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get(
                            "inputSchema",
                            {"type": "object"},
                        ),
                    },
                }
                for tool in tools
            ],
            constraints={
                "temperature": 0.2,
                "max_tokens": 256,
                "allowed_models": (
                    self._get_capability_definition(
                        request.capability
                    )
                    .metadata
                    .get("allowed_models")
                ),
            },
        )

        start = perf_counter()

        allowed_models = (
            self._get_capability_definition(
                request.capability
            )
            .metadata
            .get("allowed_models")
        )

        selected_model = None

        if allowed_models:

            llm_router = getattr(
                self.system,
                "llm_router",
                None,
            )

            if llm_router:

                selected_model = llm_router.select_model(
                    request.capability,
                    allowed_models=allowed_models,
                )

        if selected_model:
            aios_request.constraints["model"] = selected_model.name

        response = await self.system.neural_proxy.execute(
            aios_request
        )

        for _ in range(3):
            raw = response.metadata.get("raw", {})
            message = (
                raw.get("choices", [{}])[0]
                .get("message", {})
            )
            tool_calls = message.get("tool_calls") or []

            if not tool_calls or not mcp_client:
                break

            aios_request.messages.append(message)

            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name")
                arguments = function.get("arguments", "{}")

                try:
                    arguments = json.loads(arguments)
                except Exception:
                    arguments = {}

                try:
                    tool_result = await mcp_client.call_tool(
                        tool_name,
                        arguments,
                    )
                except Exception as error:
                    tool_result = {
                        "success": False,
                        "error": str(error),
                    }

                aios_request.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id"),
                    "name": tool_name,
                    "content": json.dumps(
                        tool_result,
                        default=str,
                    ),
                })

            response = await self.system.neural_proxy.execute(
                aios_request
            )

        latency = perf_counter() - start

        content = response.content

        parsed = {}

        if isinstance(content, str):
            cleaned = re.sub(
                r"```json\\s*|```",
                "",
                content,
            )

            start = cleaned.find("{")
            end = cleaned.rfind("}")

            if start != -1 and end > start:
                try:
                    parsed = json.loads(
                        cleaned[start:end + 1]
                    )
                except Exception:
                    parsed = {}

        content = response.content

        if isinstance(content, str):
            try:
                content = json.loads(content)
            except Exception:
                pass

        final_content = parsed or content

        if isinstance(final_content, dict):

            confidence = final_content.get(
                "confidence"
            )

            if confidence is not None:

                if confidence == 0:
                    final_content["confidence"] = 0.5

                elif confidence > 1:
                    final_content["confidence"] = confidence / 100

        return {
            "success": True,
            "capability": request.capability,
            "provider": response.provider,
            "model": response.model,
            "selected_model": (
                selected_model.name
                if selected_model
                else None
            ),
            "content": final_content,
            "latency": latency,
            "cost": 0.0,
            "attempt": attempt,
        }
