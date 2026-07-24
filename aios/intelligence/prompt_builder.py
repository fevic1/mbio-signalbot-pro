from pathlib import Path
import json


class PromptBuilder:

    def __init__(self):
        root = Path(__file__).parent / "templates"

        self.root = root

        self.user_template = (
            root / "default.user.txt"
        ).read_text()

    def build(
        self,
        capability,
        context,
    ):

        system_file = (
            self.root
            / "capabilities"
            / f"{capability}.system.txt"
        )

        if system_file.exists():
            system_template = system_file.read_text()
        else:
            system_template = (
                self.root
                / "default.system.txt"
            ).read_text()

        system = system_template.format(
            capability=capability,
            permission=context.get("permission", ""),
        )

        user = self.user_template.format(
            project=context.get("project_manager"),
            metadata=context.get("metadata"),
            results=context.get("results"),
            memory=context.get("memory"),
        )

        if capability == "market_analysis":

            market_data = (
                context.get("market_data")
                or context.get("metadata", {})
                .get("market_data", {})
            )

            user += (
                "\n\nMARKET DATA:\n"
                + str(market_data)
            )

        schema_file = (
            self.root.parent
            / "schemas"
            / f"{capability}.json"
        )

        schema = (
            schema_file.read_text()
            if schema_file.exists()
            else "{}"
        )

        try:
            schema_fields = json.loads(schema).get(
                "required",
                []
            )
        except Exception:
            schema_fields = []

        system += (
            "\n\nOutput requirements:\n"
            "Return ONLY valid JSON.\n"
            "Required fields: "
            + ", ".join(schema_fields)
        )

        return {
            "system": system,
            "context": user,
            "schema": schema,
        }
