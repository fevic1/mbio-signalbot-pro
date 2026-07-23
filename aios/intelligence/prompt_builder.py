class PromptBuilder:

    def build(
        self,
        capability,
        context,
    ):

        system = "\n".join(
            [
                f"Capability: {capability}",
                f"Permission: {context['permission']}",
                "Return structured JSON.",
                "Use AIOS context when available.",
            ]
        )

        user = {
            "project": context.get("project_manager"),
            "metadata": context.get("metadata"),
            "results": context.get("results"),
            "memory": context.get("memory"),
        }

        return {
            "system": system,
            "context": user,
        }
