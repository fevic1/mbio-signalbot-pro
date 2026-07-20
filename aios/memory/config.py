from pathlib import Path


class MemoryConfig:

    def __init__(self):
        self.root = Path(".aios")
        self.memory_path = self.root / "memory"
        self.vault_path = Path("docs/obsidian")
        self.history_path = self.root / "history"
        self.logs_path = self.root / "logs"

    def validate(self):
        required = [
            self.root,
            self.memory_path,
        ]

        missing = [
            str(path)
            for path in required
            if not path.exists()
        ]

        if missing:
            raise RuntimeError(
                f"Missing AIOS paths: {missing}"
            )

        return True
