import json
from pathlib import Path

HISTORY_FILE = Path(".aios/state/provider_history.json")


class ProviderHistory:

    def __init__(self):
        self.data = {}
        self.load()

    def load(self):
        if HISTORY_FILE.exists():
            self.data = json.loads(HISTORY_FILE.read_text())
        else:
            self.data = {}

    def save(self):
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(json.dumps(self.data, indent=2))

    def update(self, provider, score):
        self.data[provider] = score
        self.save()

    def get(self, provider):
        return self.data.get(provider, 50.0)


history = ProviderHistory()

