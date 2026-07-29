import os
import ast
import json
from pathlib import Path
from datetime import datetime, timezone


class AIOSSystemAuditor:

    def __init__(self, root="aios"):

        self.root = Path(root)

        self.report = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "system": "AIOS",

            "modules": {},

            "connections": [],

            "warnings": [],

            "errors": [],

            "summary": {},
        }


    def scan_files(self):

        files = []

        for path in self.root.rglob("*.py"):

            files.append(
                str(path)
            )

        self.report["modules"]["python_files"] = len(files)

        return files



    def scan_imports(self, files):

        imports = {}

        for file in files:

            try:

                tree = ast.parse(
                    Path(file).read_text()
                )

                imports[file] = [
                    node.module
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom)
                    and node.module
                ]

            except Exception as exc:

                self.report["errors"].append(
                    {
                        "file": file,
                        "error": str(exc),
                    }
                )


        self.report["modules"]["imports"] = imports



    def scan_classes(self, files):

        classes = {}

        for file in files:

            try:

                tree = ast.parse(
                    Path(file).read_text()
                )

                classes[file] = [
                    node.name
                    for node in ast.walk(tree)
                    if isinstance(
                        node,
                        ast.ClassDef
                    )
                ]

            except Exception:
                continue


        self.report["modules"]["classes"] = classes



    def scan_runtime_symbols(self):

        targets = [

            "CapabilityExecutor",
            "CapabilityRegistry",
            "CapabilityHealthManager",
            "LLMRouter",
            "ModelRegistry",
            "ProviderPool",
            "EventBus",
            "PersistentMemoryRouter",
            "DecisionEngine",
            "ExecutionAuditHandler",

        ]


        for target in targets:

            found = []

            for path in self.root.rglob("*.py"):

                try:

                    text = path.read_text()

                    if target in text:

                        found.append(
                            str(path)
                        )

                except Exception:
                    pass


            self.report["connections"].append(
                {
                    "component": target,
                    "locations": found,
                    "count": len(found),
                }
            )



    def scan_duplicates(self):

        names = {}

        for path in self.root.rglob("*.py"):

            try:

                tree = ast.parse(
                    path.read_text()
                )

                for node in ast.walk(tree):

                    if isinstance(
                        node,
                        ast.ClassDef
                    ):

                        names.setdefault(
                            node.name,
                            []
                        ).append(
                            str(path)
                        )

            except Exception:
                pass


        for name, locations in names.items():

            if len(locations) > 1:

                self.report["warnings"].append(
                    {
                        "duplicate_class": name,
                        "locations": locations,
                    }
                )



    def run(self):

        files = self.scan_files()

        self.scan_imports(files)

        self.scan_classes(files)

        self.scan_runtime_symbols()

        self.scan_duplicates()


        self.report["summary"] = {

            "files_scanned":
                len(files),

            "connections_checked":
                len(
                    self.report["connections"]
                ),

            "warnings":
                len(
                    self.report["warnings"]
                ),

            "errors":
                len(
                    self.report["errors"]
                ),
        }


        return self.report



    def save(self, output):

        Path(output).write_text(
            json.dumps(
                self.report,
                indent=2,
            )
        )


if __name__ == "__main__":

    auditor = AIOSSystemAuditor()

    auditor.run()

    auditor.save(
        "aios_system_audit.json"
    )

    print(
        "AIOS audit complete:"
        " aios_system_audit.json"
    )
