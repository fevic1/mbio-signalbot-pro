from .config import MemoryConfig


class MemoryManager:

    def __init__(self):
        self.config = MemoryConfig()

    def initialize(self):
        self.config.validate()

        return {
            "status": "ready",
            "memory": str(
                self.config.memory_path
            ),
            "vault": str(
                self.config.vault_path
            )
        }

    def validate(self):
        return self.config.validate()

