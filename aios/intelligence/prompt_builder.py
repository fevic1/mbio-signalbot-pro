class PromptBuilder:

    def build(
        self,
        capability,
        context,
    ):
        return {
            "system": f"Execute capability: {capability}",
            "context": context,
        }
