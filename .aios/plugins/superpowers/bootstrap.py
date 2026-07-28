#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

registry = json.loads((ROOT / "registry.json").read_text())

PLUGINS = {
    "skills": {},
    "workflows": {},
    "commands": {}
}

for kind, items in registry.items():
    for item in items:
        PLUGINS[kind][item] = ROOT / kind / item

if __name__ == "__main__":
    print("✓ Superpowers Bootstrapped")
    print(f"Skills     : {len(PLUGINS['skills'])}")
    print(f"Workflows  : {len(PLUGINS['workflows'])}")
    print(f"Commands   : {len(PLUGINS['commands'])}")
