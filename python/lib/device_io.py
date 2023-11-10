import logging
import time
from typing import List, TextIO

import serial
from serial import Serial

from lib.device_constants import Range, Scale, OutputDataRate
from lib.device_types import TransportHeaderId, TxFrame, RxFrame, Acceleration, SamplingStopped, SamplingStarted, FifoOverflow, SamplingFinished, SamplingAborted, UnknownResponse


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
    pass


class ErrorUnknownResponse:
    pass


class Adxl345(CdcSerial):

    def __init__(self, ser_dev_name: str, timeout: float = 0.1):
        super().__init__(ser_dev_name, timeout)

    def _send_header_then_receive(self, request: TransportHeaderId, rx_bytes_count: int) -> bytes:
        b = bytearray()
        b.append(request.value)
        self.write_bytes(b)
        return self.read_bytes(rx_bytes_count)

    def _send_header(self, header_id: TransportHeaderId) -> None:
        self.write_byte(header_id.value)

    def _send_header_and_payload(self, header_id: TransportHeaderId, value: List[int]) -> None:
        self.write_bytes(TxFrame(header_id, bytearray(value)).pack())

    def get_output_data_rate(self) -> OutputDataRate:
        o = self._send_header_then_receive(TransportHeaderId.GET_OUTPUT_DATA_RATE, 1)[0]
        return OutputDataRate(o)

    def set_output_data_rate(self, odr: OutputDataRate) -> None:
        self._send_header_and_payload(TransportHeaderId.SET_OUTPUT_DATA_RATE, [odr.value])

    def get_scale(self) -> Scale:
        s = self._send_header_then_receive(TransportHeaderId.GET_SCALE, 1)[0]
        return Scale(s)

    def set_scale(self, scale: Scale) -> None:
        self._send_header_and_payload(TransportHeaderId.SET_SCALE, [scale.value])

    def get_range(self) -> Range:
        r = self._send_header_then_receive(TransportHeaderId.GET_RANGE, 1)[0]
        return Range(r)

    def set_range(self, value: Range) -> None:
        self._send_header_and_payload(TransportHeaderId.SET_RANGE, [value.value])

    def reboot(self):
        self._send_header(TransportHeaderId.DEVICE_REBOOT)

    def start_sampling(self, num_samples: int = 0):
        assert (0 <= num_samples) and (num_samples <= 65535)
        self._send_header_and_payload(TransportHeaderId.SAMPLING_START, [num_samples & 0x00ff, (num_samples & 0xff00) >> 8])

    def stop_sampling(self):
        self._send_header(TransportHeaderId.SAMPLING_STOP)

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
                        raise ErrorUnknownResponse

                    if isinstance(package, FifoOverflow):
                        raise ErrorFifoOverflow

                    if isinstance(package, SamplingStarted):
                        logging.info(package)
                        file.write("run sample x y z\n") if file is not None else logging.info("#run #sample x[mg] y[mg] z[mg]")
                        run_count += 1
                        sample_count = 0
                        start = time.time()

                    if isinstance(package, Acceleration):
                        sample_count += 1
                        acceleration = f"{run_count:02} {sample_count:05} {package}"
                        file.write(acceleration + "\n") if file is not None else logging.info("#" + acceleration)

                    if isinstance(package, (SamplingStopped, SamplingFinished, SamplingAborted)):
                        elapsed = time.time() - start
                        if isinstance(package, SamplingFinished):
                            logging.info(str(package) + f" at {sample_count} samples")

                    if isinstance(package, SamplingStopped):
                        logging.info(package)
                        logging.info(f"run {run_count:02}: processed {sample_count} samples in {elapsed:.9f} seconds "
                                     f"({(sample_count / elapsed):.3f} samples per second; "
                                     f"{((sample_count * Acceleration.LEN * 8) / elapsed):.3f} baud)")

                        if return_on_stop or file is not None:
                            return
