import logging
from typing import List

import requests

from py3dpaxxel.octoprint.api import OctoApi


class OctoRemoteApi(OctoApi):
    """
    Sends G-Code commands to OctoPrint by REST API. Requires API key.
    """

    def __init__(self, api_key: str, address: str, port: int, do_dry_run: bool) -> None:
        """

        :param api_key: API key do authenticate at OctoPrint
        :param address: OctoPrint IP-Address
        :param port: OctoPrint API port number
        :param do_dry_run: it true, will not attempt to send G-Code but only print in logs
        """
        self.host: str = address
        self.session: requests.Session = requests.Session()
        self.session.headers.update({'X-Api-Key': api_key, 'Content-Type': 'application/json'})
        self.url = f"http://{address}:{port}"
        self.do_dry_run: bool = do_dry_run

    def send_commands(self, commands: List[str]) -> int:
        """
        Sent commands to Octoprint.

        :param commands: list of G-Code commands to send
        :return: 0 in case OctoPrint returned 204 (no error)
        """
        api_url = f"{self.url}/api/printer/command"

        logging.debug(f"sending {commands} to {api_url}")
        if not self.do_dry_run:
            response = self.session.post(api_url, json={"commands": commands})
            logging.debug(response)
            return 0 if 204 == response.status_code else -1
        else:
            return 0
