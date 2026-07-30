class ArchitecturePolicy:


    def validate(self, items):

        violations = []
        warnings = []
        backlog = []


        for item in items:

            risk = getattr(
                item,
                "risk",
                "unknown",
            )


            if risk == "runtime":
                violations.append(
                    {
                        "component": item["component"],
                        "issue": "runtime ownership unresolved",
                        "implementations": item["implementations"],
                    }
                )


            elif risk == "legacy":
                warnings.append(
                    {
                        "component": item["component"],
                        "issue": "legacy implementation",
                        "implementations": item["implementations"],
                    }
                )


            elif risk == "review":
                backlog.append(
                    {
                        "component": item["component"],
                        "issue": "requires architecture review",
                        "implementations": item["implementations"],
                    }
                )


        return {
            "violations": violations,
            "warnings": warnings,
            "backlog": backlog,
        }
