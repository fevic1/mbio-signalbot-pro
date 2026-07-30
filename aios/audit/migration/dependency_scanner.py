import ast
from pathlib import Path


class DependencyScanner:

    def scan(self, component):

        results = {
            "imports": [],
            "constructors": [],
        }

        targets = [
            component.replace(".", "/") + ".py",
        ]

        root = Path(".")

        for path in root.rglob("*.py"):

            try:
                source = path.read_text()
                tree = ast.parse(source)

            except Exception:
                continue

            for node in ast.walk(tree):

                if isinstance(node, ast.Import):

                    for item in node.names:
                        if component in item.name:
                            results["imports"].append(
                                {
                                    "file": str(path),
                                    "import": item.name,
                                }
                            )

                elif isinstance(node, ast.ImportFrom):

                    module = node.module or ""

                    if component in module:
                        results["imports"].append(
                            {
                                "file": str(path),
                                "import": module,
                            }
                        )

        return results
