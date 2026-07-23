from pathlib import Path


class PromptBuilder:

    def __init__(self):
        root = Path(__file__).parent / "templates"

        self.root = root

        self.user_template = (
            root / "default.user.txt"
        ).read_text()

    def build(
        self,
        capability,
        context,
    ):

        system_file = (
            self.root
            / "capabilities"
            / f"{capability}.system.txt"
        )

        if system_file.exists():
            system_template = system_file.read_text()
        else:
            system_template = (
                self.root
                / "default.system.txt"
            ).read_text()

        system = system_template.format(
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
