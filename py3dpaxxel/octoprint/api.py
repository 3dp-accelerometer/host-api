from abc import ABCMeta, abstractmethod
from typing import List


class OctoApi:
    __metaclass__ = metaclass = ABCMeta

    @abstractmethod
    def send_commands(self, commands: List[str]) -> int:
        pass
