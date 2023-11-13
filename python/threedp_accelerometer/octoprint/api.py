import logging

import requests


class OctoApi:

    def __init__(self, api_key: str, address: str, port: int):
        self.host: str = address
        self.session: requests.Session = requests.Session()
        self.session.headers.update({'X-Api-Key': api_key, 'Content-Type': 'application/json'})
        self.url = f"http://{address}:{port}"

    def send_commands(self, commands):
        api_url = f"{self.url}/api/printer/command"

        logging.info(f"sending {commands} to {api_url}")
        response = self.session.post(api_url, json=commands)
        logging.info(response)

        return 0 if 204 == response.status_code else -1
