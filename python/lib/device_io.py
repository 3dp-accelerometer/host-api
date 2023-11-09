from typing import List

import serial
from serial import Serial

from lib.device_constants import Range, Scale, OutputDataRate
from lib.device_types import TransportHeaderId, TxFrame, RxFrame, Acceleration


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
        self._send_header_and_payload(TransportHeaderId.SAMPLING_START, [num_samples & 0x00ff, num_samples & 0xff00])

    def stop_sampling(self):
        self._send_header(TransportHeaderId.SAMPLING_STOP)

    def decode(self):
        data: bytearray = bytearray()
        acc_count: int = 0
        while True:
            data.extend(self.read_bytes(1, 0.1))
            if len(data) >= 1:
                package = RxFrame(data).unpack()
                if package is not None:
                    if isinstance(package, Acceleration):
                        acc_count += 1
                        print(f"{acc_count:05} ", end="")
                    print(package)
