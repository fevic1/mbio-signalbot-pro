import ast
from pathlib import Path


class DependencyScanner:

    def scan(self, component):

        results = {
            "imports": [],
            "constructors": [],
        }

        aliases = {}

        for path in Path(".").rglob("*.py"):

            try:
                source = path.read_text()
                tree = ast.parse(source)

            except Exception:
                continue

            for node in ast.walk(tree):

                if isinstance(node, ast.ImportFrom):

                    module = node.module or ""

                    if component in module:

                        for item in node.names:

                            local_name = item.asname or item.name

                            aliases[local_name] = (
                                module,
                                item.name,
                            )

                        results["imports"].append(
                            {
                                "file": str(path),
                                "import": module,
                            }
                        )

                elif isinstance(node, ast.Import):

                    for item in node.names:

                        if component in item.name:

                            aliases[
                                item.asname or item.name
                            ] = (
                                item.name,
                                None,
                            )

                            results["imports"].append(
                                {
                                    "file": str(path),
                                    "import": item.name,
                                }
                            )

            for node in ast.walk(tree):

                if isinstance(node, ast.Call):

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
                                        if symbol
                                        else module
                                    ),
                                }
                            )

        return results
