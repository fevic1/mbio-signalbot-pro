import json

from aios.audit.architecture import (
    ArchitectureScanner,
    OwnershipAnalyzer,
    MigrationQueue,
)


def run(strict=False):

    scan = ArchitectureScanner().scan()

    components = OwnershipAnalyzer().analyze(
        scan.duplicate_symbols
    )

    queue = MigrationQueue().build(
        components
    )

    unknown = [
        item.name
        for item in components
        if item.status == "untracked"
    ]

    result = {
        "components": len(components),
        "migration_queue": queue,
        "unknown": unknown,
        "healthy": len(unknown) == 0,
    }

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    if strict and unknown:
        raise SystemExit(1)

    return result
