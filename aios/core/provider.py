from typing import Any


class Provider:

    def initialize(self):
        pass

    def shutdown(self):
        pass

    def health(self) -> dict[str, Any]:
        return {"status": "healthy"}

    def capabilities(self) -> list[str]:
        return []
