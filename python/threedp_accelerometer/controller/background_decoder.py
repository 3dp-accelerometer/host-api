import logging
import os
from typing import TextIO

from .api import (Adxl345)
from .constants import OutputDataRate, OutputDataRateDelay


class BackgroundDecoder:
    def __init__(self, controller_serial: str, timelapse_s: float, sensor_output_data_rate: OutputDataRate, out_filename: str | None):
        self.file: TextIO | None = None
        if out_filename is not None:
            self.file = open(out_filename, "w")

        self.dev: Adxl345 = Adxl345(controller_serial)
        self.dev.open()
        if sensor_output_data_rate is not None:
            self.dev.set_output_data_rate(sensor_output_data_rate)
        odr = self.dev.get_output_data_rate()
        sample_delay_s = OutputDataRateDelay[odr]
        samples_per_second = 1.0 / sample_delay_s
        samples_total = samples_per_second * timelapse_s
        self.max_samples: int = int(samples_total + (1 if 1 == samples_total % 2 else 0))

        logging.info(f"device {controller_serial} opened with requested_odr={sensor_output_data_rate} (effective_odr={odr}) time_lapse_s={timelapse_s} and num_samples={samples_total}")

        pass

    def start_sampling(self):
        logging.info(f"send command: start sampling n={self.max_samples}...")
        self.dev.start_sampling(self.max_samples)
        logging.info(f"send command: start sampling n={self.max_samples}... done")

    def __call__(self) -> int:
        logging.info(f"decoding ...")
        self.dev.decode(return_on_stop=True, file=self.file)
        self.dev.close()
        if self.file is not None:
            self.file.close()
        logging.info(f"data saved to {self.file.name}")
        logging.info(f"decoding ... done")
        return 0
