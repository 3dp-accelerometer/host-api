import logging
import time
from collections.abc import Callable
from typing import TextIO, Optional

from .api import (Adxl345)
from .constants import OutputDataRate, OutputDataRateDelay


class BackgroundDecoder(Callable):
    def __init__(self,
                 controller_serial: str,
                 timelapse_s: float,
                 record_timeout_s: float,
                 sensor_output_data_rate: OutputDataRate,
                 out_filename: Optional[str],
                 do_dry_run: bool = False) -> None:
        self.timelapse_s: float = timelapse_s
        self.record_timeout_s: float = record_timeout_s
        self.do_dry_run = do_dry_run
        self.dev: Optional[Adxl345] = None

        if not self.do_dry_run:
            self.file: Optional[TextIO] = None
            if out_filename is not None:
                self.file = open(out_filename, "w")

            self.dev: Adxl345 = Adxl345(controller_serial)
            self.dev.open()
            if sensor_output_data_rate is not None:
                self.dev.set_output_data_rate(sensor_output_data_rate)
            odr = self.dev.get_output_data_rate()
        else:
            odr = OutputDataRate.ODR3200

        sample_delay_s = OutputDataRateDelay[odr]
        samples_per_second = 1.0 / sample_delay_s
        samples_total = samples_per_second * self.timelapse_s

        self.max_samples: int = int(samples_total + (1 if 1 == samples_total % 2 else 0))

        logging.info(f"device {controller_serial} opened with requested_odr={sensor_output_data_rate} (effective_odr={odr}) time_lapse_s={timelapse_s} and num_samples={samples_total}")

        pass

    def start_sampling(self):
        logging.info(f"send command: start sampling n={self.max_samples}")
        if not self.do_dry_run:
            self.dev.start_sampling(self.max_samples)

    def __call__(self) -> int:
        logging.debug(f"decoding ...")

        if not self.do_dry_run:
            self.dev.decode(return_on_stop=True, timeout_s=self.record_timeout_s, file=self.file)
            self.dev.close()
            if self.file is not None:
                self.file.close()
                logging.info(f"data saved to {self.file.name}")
        else:
            time.sleep(self.timelapse_s)

        logging.debug(f"decoding ... done")
        return 0
