from .dependency_scanner import DependencyScanner


class MigrationAnalyzer:


    def __init__(self):

        self.scanner = DependencyScanner()


    def analyze(self, manifest):

        dependencies = []

        for implementation in manifest.implementations:

            dependencies.append(
                {
                    "implementation": implementation,
                    "dependencies":
                        self.scanner.scan(
                            implementation
                        ),
                }
            )

        return {
            "component":
                manifest.component,

            "canonical":
                manifest.canonical,

            "owner":
                manifest.owner,

            "risk":
                manifest.risk,

            "dependencies":
                dependencies,

            "status":
                manifest.status,
        }
