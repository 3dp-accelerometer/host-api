from typing import Union, Optional

from py3dpaxxel.controller.constants import OutputDataRateDelay, OutputDataRate, Range, Scale


class Samples:
    def __init__(self) -> None:
        self.separation_s: Optional[float] = None
        "time separation in-between samples (`1/sample_rate`)"
        self.rate: OutputDataRate = OutputDataRateDelay[OutputDataRate.ODR3200]
        "sample rate, ODR (output data rate)"
        self.range: Optional[Range] = None
        "sensor range in `g`"
        self.scale: Optional[Scale,] = None
        "sensor scale: 10bit or full scale (each LSB is 3.9mg)"

        self.run = []
        "series number"
        self.index = []
        "index of sample in stream (this series)"
        self.timestamp_ms = []
        "recomputed `time_stamp` (offset) from first sample (`time_stamp=0`)"

        self.x = []
        "measured x-acceleration in mg"
        self.y = []
        "measured y-acceleration in mg"
        self.z = []
        "measured z-acceleration in mg"

    def __len__(self):
        return len(self.index)
