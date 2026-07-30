import json

from aios.audit.migration import MigrationAnalyzer
from aios.audit.migration.models import MigrationManifest


def run(manifest_data):

    manifest = MigrationManifest(
        **manifest_data
    )

    report = MigrationAnalyzer().analyze(
        manifest
    )

    print(
        json.dumps(
            report,
            indent=2,
        )
    )
