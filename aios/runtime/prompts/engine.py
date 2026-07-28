
class PromptEngine:

    def __init__(self):
        self.templates = {}

    def register(self, name, template):
        self.templates[name] = template

    def render(self, name, context=None):
        template = self.templates[name]

        return template.format(
            **(context or {})
        )

    def get(self, name):
        return self.templates.get(name)

    def remove(self, name):
        return self.templates.pop(
            name,
            None
        )

    def list(self):
        return tuple(self.templates)
