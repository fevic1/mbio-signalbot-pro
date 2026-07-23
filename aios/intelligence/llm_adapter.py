from .assembler import ContextAssembler
from .prompt_builder import PromptBuilder


class LLMAdapter:

    def __init__(
        self,
        router,
        system=None,
    ):
        self.router = router
        self.system = system
        self.assembler = ContextAssembler()
        self.prompt_builder = PromptBuilder()

    def build(
        self,
        capability,
        request,
    ):
        context = self.assembler.assemble(
            self.system,
            capability,
            request,
        )

        return self.prompt_builder.build(
            capability,
            context,
        )

    def choose(
        self,
        task_type,
    ):
        model = self.router.select_model(
            task_type
        )

        if model is None:
            return {
                "status": "no_model",
                "task": task_type,
            }

        return {
            "status": "selected",
            "model": model.name,
            "provider": model.provider,
        }
