from .template import PromptTemplate


class PromptEngine:

    def __init__(self):
        self._templates: dict[str, PromptTemplate] = {}

    def register(self, template: PromptTemplate):
        self._templates[template.name] = template
        return template

    def unregister(self, name: str):
        return self._templates.pop(name, None)

    def get(self, name: str):
        return self._templates[name]

    def exists(self, name: str):
        return name in self._templates

    def render(self, name: str, **context):
        return self.get(name).render(**context)

    def list(self):
        return tuple(sorted(self._templates))

    def __len__(self):
        return len(self._templates)
