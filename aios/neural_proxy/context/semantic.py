from aios.neural_proxy.protocol import AIOSRequest


class SemanticContextProcessor:


    def process(
        self,
        request: AIOSRequest,
    ):

        context = {
            "intent": request.intent,
            "memory": request.memory,
            "tools": request.tools,
            "constraints": request.constraints,
        }


        if not request.messages:

            request.messages = []


        import json

        request.messages.append(
            {
                "role": "system",
                "content": json.dumps(
                    {
                        "aios_context": context,
                    },
                    ensure_ascii=False,
                ),
            }
        )


        return request
