from pathlib import Path
import json

from aios.audit.architecture import (
    ArchitectureScanner,
)


OUTPUT = Path(
    ".aios/governance/component_ownership.json"
)


def bootstrap():

    if OUTPUT.exists():
        data = json.loads(
            OUTPUT.read_text()
        )
    else:
        data = {}


    scan = ArchitectureScanner().scan()


    for name, locations in scan.duplicate_symbols.items():

        if name not in data:

            data[name] = {
                "canonical": None,
                "risk": "review",
                "owner": None,
                "status": "review_required",
                "implementations": locations,
            }


    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            data,
            indent=2,
        )
    )


    print(
        "Ownership records:",
        len(data)
    )


if __name__ == "__main__":
    bootstrap()
