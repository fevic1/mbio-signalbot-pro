#!/usr/bin/env python3

from pathlib import Path
import yaml
from templates import write

ROOT = Path(__file__).parent
CFG = yaml.safe_load((ROOT / "manifest.yaml").read_text())

def mkdir(name):
    (ROOT / name).mkdir(parents=True, exist_ok=True)

for path in CFG["output"].values():
    mkdir(path)

for skill in CFG.get("skills", []):
    mkdir(f"skills/{skill}")
    write(ROOT,"skills",skill)

for workflow in CFG.get("workflows", []):
    mkdir(f"workflows/{workflow}")
    write(ROOT,"workflows",workflow)

for command in CFG.get("commands", []):
    mkdir(f"commands/{command}")
    write(ROOT,"commands",command)

print("✓ Superpowers generated")
