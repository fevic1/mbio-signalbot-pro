from dataclasses import dataclass, field


@dataclass(slots=True)
class PromptTemplate:
    name: str
    template: str
    metadata: dict = field(default_factory=dict)

    def render(self, **context):
        return self.template.format(**context)
