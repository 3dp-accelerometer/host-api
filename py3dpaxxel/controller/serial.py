from typing import Optional

import serial
from serial import Serial


class CdcSerial:
    def __init__(self, ser_dev_name: str,
                 read_timeout: float,
                 write_timeout: float) -> None:
        self.dev: Optional[Serial] = None
        self.ser_dev_name = ser_dev_name
        self.read_timeout: float = read_timeout
        self.write_timeout: float = write_timeout

    def write_byte(self, tx_byte: int) -> None:
        assert tx_byte < 255
        self.dev.write(bytes([tx_byte]))

    def write_bytes(self, tx_bytes: bytes, timeout: Optional[float] = None) -> int:
        if timeout:
            self.dev.write_timeout = timeout
            tx_len = self.dev.write(tx_bytes)
            self.dev.write_timeout = self.write_timeout
            return tx_len
        return self.dev.write(tx_bytes)

    def read_bytes(self, num_bytes: int, timeout: Optional[float] = None) -> bytes:
        if timeout:
            self.dev.timeout = timeout
            rx_bytes = self.dev.read(num_bytes)
            self.dev.timeout = self.read_timeout
            return rx_bytes
        return self.dev.read(num_bytes)

    def open(self) -> None:
        self.dev = Serial(port=self.ser_dev_name,
                          timeout=self.read_timeout,
                          write_timeout=self.write_timeout,
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
