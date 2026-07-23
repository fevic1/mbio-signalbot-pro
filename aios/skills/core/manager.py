from pathlib import Path
import yaml


class SkillManager:

    def __init__(self, root):
        self.root = Path(root)

    def manifests(self):
        for manifest in self.root.glob("*/manifest.yaml"):
            data = yaml.safe_load(manifest.read_text())
            data["path"] = manifest.parent
            yield data

    def enabled(self):
        return [
            m
            for m in self.manifests()
            if m.get("enabled", True)
        ]
