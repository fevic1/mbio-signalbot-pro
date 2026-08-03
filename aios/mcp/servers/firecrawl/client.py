
import requests

from .config import FirecrawlConfig

class FirecrawlClient:

    def __init__(self):
        self.cfg=FirecrawlConfig()

    def post(self,path,payload):

        r=requests.post(
            self.cfg.base_url+path,
            json=payload,
            headers={
                "Authorization":
                f"Bearer {self.cfg.api_key}"
            },
            timeout=self.cfg.timeout,
        )

        r.raise_for_status()

        return r.json()
