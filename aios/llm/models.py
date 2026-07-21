from dataclasses import dataclass, field


@dataclass
class LLMModel:

    name: str

    provider: str

    capabilities: list = field(
        default_factory=list
    )

    cost_level: str = "medium"

    speed: str = "medium"

    context_window: int = 0

    enabled: bool = True



class ModelRegistry:


    def __init__(self):

        self.models = {}


    def register(
        self,
        model: LLMModel
    ):

        self.models[
            model.name
        ] = model

        return True


    def get(
        self,
        name
    ):

        return self.models.get(
            name
        )


    def list_models(
        self
    ):

        return [

            {

                "name": model.name,

                "provider":
                    model.provider,

                "capabilities":
                    model.capabilities,

                "enabled":
                    model.enabled

            }

            for model in self.models.values()

        ]


    def find_by_capability(
        self,
        capability
    ):

        return [

            model

            for model in self.models.values()

            if capability
            in model.capabilities

            and model.enabled

        ]
