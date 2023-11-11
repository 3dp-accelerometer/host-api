import logging
import re
import time
from typing import TextIO

import serial
from serial import Serial

from lib.device_constants import Range, Scale, OutputDataRate
from lib.device_types import (TxFrame, RxFrame, UnknownResponse, RxOutputDataRate,
                              RxScale, RxRange, RxSamplingStopped, RxSamplingFinished, RxSamplingAborted,
                              RxAcceleration, RxSamplingStarted, RxFifoOverflow, RxDeviceSetup, TxGetOutputDataRate, TxSetOutputDataRate, TxGetScale, TxSetScale, TxGetRange, TxSetRange, TxReboot,
                              TxSamplingStart, TxSamplingStop)


class CdcSerial:
    def __init__(self, ser_dev_name: str, timeout: float):
        self.dev: None | Serial = None
        self.ser_dev_name = ser_dev_name
        self.timeout: float = timeout

    def write_byte(self, tx_byte: int) -> None:
        assert tx_byte < 255
        self.dev.write(bytes([tx_byte]))

    def write_bytes(self, tx_bytes: bytes) -> None:
        self.dev.write(tx_bytes)

    def read_bytes(self, num_bytes: int, timeout: None | float = None) -> bytes:
        if timeout:
            self.dev.timeout = timeout
            rx_bytes = self.dev.read(num_bytes)
            self.dev.timeout = self.timeout
            return rx_bytes
        return self.dev.read(num_bytes)

    def open(self) -> None:
        self.dev = Serial(port=self.ser_dev_name,
                          timeout=self.timeout,
                          bytesize=serial.EIGHTBITS,
                          parity=serial.PARITY_NONE,
                          stopbits=serial.STOPBITS_ONE,
                          xonxoff=False,
                          rtscts=False,
                          dsrdtr=False)
        self.dev.set_input_flow_control(False)
        self.dev.set_output_flow_control(False)

    def close(self) -> None:
        if self.dev:
            self.dev.close()
            self.dev = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ErrorFifoOverflow:
    def __str__(self):
        return "controller detected accelerometer FiFo overrun"


class ErrorUnknownResponse:
    def __str__(self):
        return "received unknown response from controller"


class Adxl345(CdcSerial):

    def __init__(self, ser_dev_name: str, timeout: float = 0.1):
        super().__init__(ser_dev_name, timeout)

    def _send_frame_then_receive(self, frame: TxFrame, rx_bytes_count: int) -> bytearray:
        self.write_bytes(frame.pack())
        return bytearray(self.read_bytes(rx_bytes_count))

    def _send_frame(self, frame: TxFrame) -> None:
        self.write_bytes(frame.pack())

    def get_output_data_rate(self) -> OutputDataRate:
        payload = self._send_frame_then_receive(TxGetOutputDataRate(), RxOutputDataRate.LEN)
        response = RxOutputDataRate(payload)
        return response.outputDataRate

    def set_output_data_rate(self, odr: OutputDataRate) -> None:
        self._send_frame(TxSetOutputDataRate(odr))

    def get_scale(self) -> Scale:
        payload = self._send_frame_then_receive(TxGetScale(), RxScale.LEN)
        response = RxScale(payload)
        return response.scale

    def set_scale(self, scale: Scale) -> None:
        self._send_frame(TxSetScale(scale))

    def get_range(self) -> Range:
        payload = self._send_frame_then_receive(TxGetRange(), RxRange.LEN)
        response = RxRange(payload)
        return response.range

    def set_range(self, data_range: Range) -> None:
        self._send_frame(TxSetRange(data_range))

    def reboot(self):
        self._send_frame(TxReboot())

    def start_sampling(self, num_samples: int = 0):
        assert (0 <= num_samples) and (num_samples <= 65535)
        self._send_frame(TxSamplingStart(num_samples))

    def stop_sampling(self):
        self._send_frame(TxSamplingStop())

    def decode(self, return_on_stop: bool = False, file: None | TextIO = None):
        data: bytearray = bytearray()
        run_count: int = 0
        sample_count: int = 0
        start = None
        elapsed = None
        while True:
            data.extend(self.read_bytes(1, 0.1))
            if len(data) >= 1:
                package = RxFrame(data).unpack()
                if package is not None:
                    if isinstance(package, UnknownResponse):
                        e = ErrorUnknownResponse()
                        logging.fatal(str(e))
                        raise e

                    if isinstance(package, RxFifoOverflow):
                        e = ErrorFifoOverflow()
                        logging.fatal(str(e))
                        raise e

                    if isinstance(package, RxSamplingStarted):
                        logging.info(package)
                        file.write("run sample x y z\n") if file is not None else logging.info("#run #sample x[mg] y[mg] z[mg]")
                        sample_count = 0
                        start = time.time()

                    if isinstance(package, RxAcceleration):
                        acceleration = f"{run_count:02} {package}"
                        assert sample_count == package.index
                        sample_count += 1
                        if sample_count > 65535:
                            sample_count = 0
                        file.write(acceleration + "\n") if file is not None else logging.info(acceleration)

                    if isinstance(package, RxDeviceSetup):
                        parameters = eval(re.search(RxDeviceSetup.REPR_FILTER_REGEX, str(package)).group(1))
                        file.write("# " + str(parameters) + "\n") if file is not None else logging.info("Device Setup: " + str(parameters))

                    if isinstance(package, (RxSamplingStopped, RxSamplingFinished, RxSamplingAborted)):
                        elapsed = time.time() - start
                        if isinstance(package, RxSamplingFinished):
                            logging.info(str(package) + f" at sample {sample_count}")

                    if isinstance(package, RxSamplingStopped):
                        logging.info(package)
                        logging.info(f"run {run_count:02}: processed {sample_count} samples in {elapsed:.6f} s "
                                     f"({(sample_count / elapsed):.1f} samples/s; "
                                     f"{((sample_count * RxAcceleration.LEN * 8) / elapsed):.1f} baud)")
                        run_count += 1

                        if return_on_stop or file is not None:
                            return
