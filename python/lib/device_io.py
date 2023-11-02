from serial import Serial

from device_constants import Range, Scale, OutputDataRate
from lib.device_types import TransportHeaderId, TxFrame


class CdcSerial:
    def __init__(self, ser_dev_name: str, timeout: float):
        self.dev: None | Serial = None
        self.ser_dev_name = ser_dev_name
        self.timeout = timeout

    def write_bytes(self, tx_bytes: bytes) -> None:
        self.dev.write(tx_bytes)

    def read_bytes(self, num_bytes: int, timeout: None | int = None) -> bytes:
        if timeout:
            self.dev.timeout = timeout
            rx_bytes = self.dev.read(num_bytes)
            self.dev.timeout = self.timeout
            return rx_bytes
        return self.dev.read(num_bytes)

    def open(self) -> None:
        self.dev = Serial(self.ser_dev_name, self.timeout)

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

    def send_request(self, request: TransportHeaderId, rx_bytes_count: int = 0) -> bytes | None:
        b = bytearray()
        b.append(request.value)
        self.write_bytes(b)
        return None if rx_bytes_count == 0 else self.read_bytes(rx_bytes_count)

    def send_set_flag(self, request: TransportHeaderId, value: int) -> None:
        self.write_bytes(TxFrame(request, bytes([value])).pack())

    def get_output_data_rate(self) -> OutputDataRate:
        o = self.send_request(TransportHeaderId.GetOutputDataRate, 1)[0]
        return OutputDataRate(o)

    def set_output_data_rate(self, odr: OutputDataRate) -> None:
        self.send_set_flag(TransportHeaderId.SetOutputDataRate, odr.value)

    def get_scale(self) -> Scale:
        s = self.send_request(TransportHeaderId.GetScale, 1)[0]
        return Scale(s)

    def set_scale(self, scale: Scale) -> None:
        self.send_set_flag(TransportHeaderId.SetScale, scale.value)

    def get_range(self) -> Range:
        r = self.send_request(TransportHeaderId.GetRange, 1)[0]
        return Range(r)

    def set_range(self, value: Range) -> None:
        self.send_set_flag(TransportHeaderId.SetRange, value.value)
