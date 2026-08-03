
import requests
from .config import CoinGeckoConfig

class CoinGeckoClient:

    def __init__(self):
        self.cfg=CoinGeckoConfig()

    def get(self,path,params=None):

        r=requests.get(
            self.cfg.base_url+path,
            params=params,
            timeout=self.cfg.timeout,
        )

        r.raise_for_status()

        return r.json()
