from pathlib import Path
import importlib


class SkillLoader:

    def __init__(
        self,
        registry,
    ):

        self.registry = registry


    def load_builtin(self):

        root = Path(
            "aios/skills/builtin"
        )

        for folder in root.iterdir():

            if not folder.is_dir():
                continue

            module = importlib.import_module(
                f"aios.skills.builtin.{folder.name}.manifest"
            )

            self.registry.register(
                module.skill
            )
