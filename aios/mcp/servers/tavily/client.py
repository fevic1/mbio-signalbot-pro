
import requests

from .config import TavilyConfig

class TavilyClient:

    def __init__(self):
        self.cfg=TavilyConfig()

    def post(self,path,payload):

        payload["api_key"]=self.cfg.api_key

        r=requests.post(
            self.cfg.base_url+path,
            json=payload,
            timeout=self.cfg.timeout,
        )

        r.raise_for_status()

        return r.json()
