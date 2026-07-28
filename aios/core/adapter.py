from typing import Any


class Adapter:

    def initialize(self):
        pass

    def shutdown(self):
        pass

    def invoke(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def supports(self, capability: str) -> bool:
        return False
