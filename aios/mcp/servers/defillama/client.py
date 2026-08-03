
import requests
from .config import DefiLlamaConfig

class DefiLlamaClient:

    def __init__(self):
        self.cfg=DefiLlamaConfig()

    def get(self,path):

        r=requests.get(
            self.cfg.base_url+path,
            timeout=self.cfg.timeout,
        )

        r.raise_for_status()

        return r.json()
