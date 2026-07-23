from pathlib import Path


class PromptBuilder:

    def __init__(self):
        root = Path(__file__).parent / "templates"

        self.system_template = (
            root / "default.system.txt"
        ).read_text()

        self.user_template = (
            root / "default.user.txt"
        ).read_text()

    def build(
        self,
        capability,
        context,
    ):

        system = self.system_template.format(
            capability=capability,
            permission=context["permission"],
        )

        user = self.user_template.format(
            project=context.get("project_manager"),
            metadata=context.get("metadata"),
            results=context.get("results"),
            memory=context.get("memory"),
        )

        return {
            "system": system,
            "context": user,
        }
