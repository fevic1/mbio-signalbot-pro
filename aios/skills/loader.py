from importlib import import_module
from pathlib import Path

from .registry import SkillRegistry


class SkillLoader:

    def __init__(self):
        self.registry = SkillRegistry()

    def load(self):
        base = Path(__file__).parent

        for manifest in base.glob("*/manifest.yaml"):
            package = manifest.parent.name

            module = import_module(
                f"aios.skills.{package}.workflow"
            )

            for obj in module.__dict__.values():
                if (
                    isinstance(obj, type)
                    and hasattr(obj, "id")
                    and hasattr(obj, "execute")
                ):
                    self.registry.register(obj())

        return self.registry
