from typing import Any


class Plugin:

    def initialize(self):
        pass

    def shutdown(self):
        pass

    def configure(self, **kwargs):
        return self

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.__class__.__name__,
        }
