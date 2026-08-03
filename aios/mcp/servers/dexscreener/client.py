import requests

from .config import DexConfig

class DexClient:

    def __init__(self):
        self.cfg = DexConfig()

    def get(self, endpoint):

        r = requests.get(
            self.cfg.base_url + endpoint,
            timeout=self.cfg.timeout,
        )

        r.raise_for_status()

        return r.json()
