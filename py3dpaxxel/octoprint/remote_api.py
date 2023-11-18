import logging
from typing import List

import requests

from py3dpaxxel.octoprint.api import OctoApi


class OctoRemoteApi(OctoApi):

    def __init__(self, api_key: str, address: str, port: int, do_dry_run: bool) -> None:
        self.host: str = address
        self.session: requests.Session = requests.Session()
        self.session.headers.update({'X-Api-Key': api_key, 'Content-Type': 'application/json'})
        self.url = f"http://{address}:{port}"
        self.do_dry_run: bool = do_dry_run

    def send_commands(self, commands: List[str]) -> int:
        api_url = f"{self.url}/api/printer/command"

        logging.info(f"sending {commands} to {api_url}")
        if not self.do_dry_run:
            response = self.session.post(api_url, json={"commands": commands})
            logging.info(response)
            return 0 if 204 == response.status_code else -1
        else:
            return 0
