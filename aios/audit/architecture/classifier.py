from pathlib import Path


class ComponentClassifier:


    def classify(self, item):

        implementations = item.implementations

        result = {
            "component": item.name,
            "implementations": implementations,
            "risk": "unknown",
        }


        if any(
            ".runtime." in x
            for x in implementations
        ):
            result["risk"] = "runtime"


        if any(
            "__init__" in x
            for x in implementations
        ):
            result["risk"] = "reexport"


        if any(
            "legacy" in x
            for x in implementations
        ):
            result["risk"] = "legacy"


        if result["risk"] == "unknown":
            result["risk"] = "review"


        return result
