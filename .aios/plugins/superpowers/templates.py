from pathlib import Path

SKILL = """# {name}

version: 1.0.0
"""

WORKFLOW = """# {name}

steps: []
"""

COMMAND = """# {name}

execute: ""
"""

def write(root: Path, kind: str, name: str):
    target = root / kind / name
    target.mkdir(parents=True, exist_ok=True)

    if kind == "skills":
        (target / "README.md").write_text(SKILL.format(name=name))

    elif kind == "workflows":
        (target / "README.md").write_text(WORKFLOW.format(name=name))

    elif kind == "commands":
        (target / "README.md").write_text(COMMAND.format(name=name))
