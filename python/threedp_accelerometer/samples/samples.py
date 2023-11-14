from typing import Union

from threedp_accelerometer.controller.constants import OutputDataRateDelay, OutputDataRate, Range, Scale


class Samples:
    def __init__(self):
        self.separation_s: Union[float, None] = None
        self.rate: OutputDataRate = OutputDataRateDelay[OutputDataRate.ODR3200]
        self.range: Union[Range, None] = None
        self.scale: Union[Scale, None] = None

        self.run = []
        self.index = []
        self.timestamp_ms = []

        self.x = []
        self.y = []
        self.z = []

    def __len__(self):
        return len(self.index)
