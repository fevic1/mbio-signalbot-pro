from aios.runtime.prompt_loader import PromptLoader


class ChatContextBuilder:

    def __init__(
        self,
    ):

        self.loader = PromptLoader()


    def build(
        self,
        agent_name,
        history,
    ):

        context = self.loader.assemble_context(
            agent_name
        )

        return {
            "system_prompt":
                context.system_prompt,

            "permissions":
                context.permissions.level.value,

            "prompt_hash":
                context.metadata.get(
                    "prompt_hash"
                ),

            "history":
                history,
        }
