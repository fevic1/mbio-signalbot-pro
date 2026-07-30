import ast
from pathlib import Path


class DependencyScanner:

    def __init__(self):
        self.excluded = {
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
        }

    def _python_files(self):

        for path in Path("aios").rglob("*.py"):

            if any(
                part in self.excluded
                for part in path.parts
            ):
                continue

            # skip generated/huge files
            if path.stat().st_size > 500_000:
                continue

            yield path


    def scan(self, component):

        results = {
            "imports": [],
            "constructors": [],
        }

        aliases = {}

        component_name = (
            component.split(".")[-1]
        )

        for path in self._python_files():

            try:
                source = path.read_text(
                    encoding="utf-8"
                )

            except Exception:
                continue

            # fast filter before AST parse
            if (
                component not in source
                and component_name not in source
            ):
                continue

            try:
                tree = ast.parse(source)

            except SyntaxError:
                continue


            for node in ast.walk(tree):

                if isinstance(node, ast.ImportFrom):

                    module = node.module or ""

                    if component in module:

                        for item in node.names:

                            local = (
                                item.asname or item.name
                            )

                            aliases[local] = (
                                module,
                                item.name,
                            )

                        results["imports"].append(
                            {
                                "file": str(path),
                                "import": module,
                            }
                        )


                elif isinstance(node, ast.Call):

                    if isinstance(node.func, ast.Name):

                        name = node.func.id

                        if name in aliases:

                            module, symbol = aliases[name]

                            results["constructors"].append(
                                {
                                    "file": str(path),
                                    "class": name,
                                    "resolved": (
                                        f"{module}.{symbol}"
                                    ),
                                }
                            )

        return results
