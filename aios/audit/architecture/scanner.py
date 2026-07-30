import ast
from pathlib import Path

from .report import ArchitectureReport


class ArchitectureScanner:


    def __init__(
        self,
        root="aios",
    ):
        self.root = Path(root)


    def scan(self):

        report = ArchitectureReport()

        classes = {}

        imports = {}

        for file in self.root.rglob(
            "*.py"
        ):

            try:

                source = file.read_text()

                tree = ast.parse(
                    source
                )

            except Exception:
                continue


            module = (
                str(file)
                .replace("/", ".")
                .replace(".py", "")
            )


            imports[module] = []


            for node in ast.walk(tree):

                if isinstance(
                    node,
                    ast.ClassDef,
                ):

                    classes.setdefault(
                        node.name,
                        []
                    ).append(
                        module
                    )


                if isinstance(
                    node,
                    ast.Import,
                ):

                    for item in node.names:
                        imports[module].append(
                            item.name
                        )


                if isinstance(
                    node,
                    ast.ImportFrom,
                ):

                    if node.module:
                        imports[module].append(
                            node.module
                        )


        report.duplicate_symbols = {
            name: locations
            for name, locations
            in classes.items()
            if len(locations) > 1
        }


        report.imports = imports

        return report
