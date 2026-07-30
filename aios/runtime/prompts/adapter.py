from aios.prompts import (
    PromptEngine as CanonicalPromptEngine,
    PromptTemplate,
)


class PromptEngineAdapter:

    def __init__(self):
        self.engine = CanonicalPromptEngine()

    def register(self, name, template):

        prompt = PromptTemplate(
            name=name,
            template=template,
        )

        return self.engine.register(prompt)


    def render(self, name, context=None):

        return self.engine.render(
            name,
            **(context or {})
        )


    def get(self, name):

        return self.engine.get(name)


    def remove(self, name):

        return self.engine.unregister(name)


    def list(self):

        return self.engine.list()
