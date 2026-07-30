from .dependency_scanner import DependencyScanner


class MigrationAnalyzer:

    def __init__(self):
        self.scanner = DependencyScanner()

    def analyze(self, manifest):

        implementations = []

        for implementation in manifest.implementations:

            dependencies = self.scanner.scan(
                implementation
            )

            implementations.append(
                {
                    "implementation": implementation,
                    "dependencies": dependencies,
                }
            )

        return {
            "component": manifest.component,
            "canonical": manifest.canonical,
            "owner": manifest.owner,
            "risk": manifest.risk,
            "implementations": implementations,
            "adapter_required": self._adapter_required(
                manifest
            ),
            "status": manifest.status,
        }

    def _adapter_required(self, manifest):

        return len(
            manifest.implementations
        ) > 1
