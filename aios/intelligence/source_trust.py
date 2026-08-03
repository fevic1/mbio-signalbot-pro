class SourceTrust:

    def evaluate(self, tool_results):

        trust = {}

        for item in tool_results:

            server = item["server"]

            trust.setdefault(
                server,
                {
                    "calls":0,
                    "success":0,
                },
            )

            trust[server]["calls"] += 1

            if item.get("success"):
                trust[server]["success"] += 1

        for server,data in trust.items():

            data["trust"] = round(
                data["success"] / data["calls"],
                3,
            )

        return trust
