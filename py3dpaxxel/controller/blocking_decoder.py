import logging
import threading
import time
from collections.abc import Callable
from typing import TextIO, Optional

from .api import (Py3dpAxxel)
from .constants import OutputDataRate, OutputDataRateDelay


class BlockingDecoder(Callable):
    """
    A blocking decoder implementation.

    This decoder allows to

    - tell the controller when sampling shall start, and
    - decode controllers' stream (blocking).

    The implementation is meant to be used threaded so that the decoding can be
    started (threaded) before sampling start is called.

    Note: the serial device acquisition is performed at construction time.
    """

    def __init__(self,
                 controller_serial: str,
                 timelapse_s: float,
                 record_timeout_s: float,
                 sensor_output_data_rate: OutputDataRate,
                 out_filename: Optional[str],
                 do_dry_run: bool = False,
                 do_abort_flag: threading.Event = threading.Event()) -> None:
        """
        Acquires required resources for later interaction with controller.

        :param controller_serial: i.e. "/dev/ttyACM0"
        :param timelapse_s: how long to record
        :param record_timeout_s: how long the controller shall record
        :param sensor_output_data_rate: which sample rate the controller shall be configured
        :param out_filename: decoded stream output file, leave None for not storage
        :param do_dry_run: if true, will not invoke controller neither write output file but timing will as without dry-run
        :param do_abort_flag: flag to externally shortcut the decoding loop
        """
        self.timelapse_s: float = timelapse_s
        self.record_timeout_s: float = record_timeout_s
        self.do_dry_run = do_dry_run
        self.dev: Optional[Py3dpAxxel] = None
        self.do_abort_flag: threading.Event = do_abort_flag

        if not self.do_dry_run:
            self.file: Optional[TextIO] = None
            if out_filename is not None:
                self.file = open(out_filename, "w")

            self.dev: Py3dpAxxel = Py3dpAxxel(controller_serial)
            self.dev.open()
            if sensor_output_data_rate is not None:
                self.dev.set_output_data_rate(sensor_output_data_rate)
            odr = self.dev.get_output_data_rate()
        else:
            odr = OutputDataRate.ODR3200

        sample_delay_s = OutputDataRateDelay[odr]
        samples_per_second = 1.0 / sample_delay_s
        samples_total = int(samples_per_second * self.timelapse_s)

        # snap to even number of samples for FFT
        self.max_samples: int = int(samples_total + (1 if 1 == samples_total % 2 else 0))

        logging.info(f"device {controller_serial} opened with requested_odr={sensor_output_data_rate} "
                     f"(effective_odr={odr}) time_lapse_s={timelapse_s} and num_samples={samples_total}")

    def start_sampling(self) -> None:
        """
        Tells the controller to start sampling, hence sent data stream to the host.

        :return: None
        """
        logging.info(f"send command: start sampling n={self.max_samples}")
        if not self.do_dry_run:
            try:
                self.dev.start_sampling(self.max_samples)
            except Exception as e:
                logging.warning("start sampling: release resources")
                if self.dev is not None:
                    self.dev.close()
                if self.file is not None:
                    self.file.close()
                raise e

    def __call__(self) -> None:
        """
        Starts decoding and waits until stream end is detected (success) or timeout occurred (error).

        The decoded stream is stored to file.
        In case of dry-run no controller and no output file is touched, but the timing is assured to be tha same as with not dry-run.

        :return: None
        """
        logging.debug("decoding ...")

        try:
            if not self.do_dry_run:
                self.dev.decode(return_on_stop=True,
                                message_timeout_s=self.record_timeout_s,
                                out_file=self.file,
                                do_stop_flag=self.do_abort_flag)
                self.dev.close()
                if self.file is not None:
                    self.file.close()
                    logging.info(f"data saved to {self.file.name}")
            else:
                time.sleep(self.timelapse_s)

        except Exception as e:
            logging.warning("decoding: release resources")
            if self.dev is not None:
                self.dev.close()
            if self.file is not None:
                self.file.close()
            raise e
