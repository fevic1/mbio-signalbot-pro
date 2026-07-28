#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path(__file__).parent

registry = {
    "skills": [],
    "workflows": [],
    "commands": []
}

for section in registry:
    directory = ROOT / section
    if directory.exists():
        registry[section] = sorted(
            d.name for d in directory.iterdir() if d.is_dir()
        )

(ROOT / "registry.json").write_text(
    json.dumps(registry, indent=2)
)

print("✓ Registry updated")
