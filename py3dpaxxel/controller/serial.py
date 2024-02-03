import os
import select
import termios
from typing import Optional

import serial
from serial import Serial


class CdcPySerial:
    def __init__(self, ser_dev_name: str,
                 read_timeout: float,
                 write_timeout: float) -> None:
        self.dev: Optional[Serial] = None
        self.ser_dev_name = ser_dev_name
        self.read_timeout: float = read_timeout
        self.write_timeout: float = write_timeout

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


class CdcOsSerial:
    """
    Alternative read/write to PySerial based CdcPySerial.

    Note: this class is highly OS dependent and shall be only used for development
    purpose only where pyserial shall be omitted (i.e. performance test of native
    vs. Pyserial throughput).
    """

    def __init__(self, ser_dev_name: str,
                 read_timeout: float,
                 write_timeout: float) -> None:
        self.fd: int = -1
        self.ser_dev_name = ser_dev_name
        self.read_timeout: float = read_timeout
        self.write_timeout: float = write_timeout

    def write_bytes(self, tx_bytes: bytes, _timeout: Optional[float] = None) -> int:
        ret = os.write(self.fd, tx_bytes)
        termios.tcdrain(self.fd)
        return ret

    def read_bytes(self, num_bytes: int, timeout: Optional[float] = None) -> bytes:
        timeout = self.read_timeout if timeout is None else timeout
        bs = bytes()
        while len(bs) < num_bytes:
            r, w, e = select.select([self.fd], [], [], timeout)
            if self.fd in r:
                bs += os.read(self.fd, num_bytes)
            else:
                return bs
        return bs

    def open(self) -> None:
        """
        Proudly stolen implementation details from serialposix.py
        """
        self.fd = os.open(self.ser_dev_name, os.O_RDWR | os.O_NOCTTY)  # | os.O_NONBLOCK

        orig_attr = termios.tcgetattr(self.fd)
        iflag, oflag, cflag, lflag, ispeed, ospeed, cc = orig_attr

        # set up raw mode / no echo / binary
        cflag |= (termios.CLOCAL | termios.CREAD)
        lflag &= ~(termios.ICANON | termios.ECHO | termios.ECHOE |
                   termios.ECHOK | termios.ECHONL |
                   termios.ISIG | termios.IEXTEN)  # | termios.ECHOPRT

        for flag in ('ECHOCTL', 'ECHOKE'):  # netbsd workaround for Erk
            if hasattr(termios, flag):
                lflag &= ~getattr(termios, flag)

        oflag &= ~(termios.OPOST | termios.ONLCR | termios.OCRNL)
        iflag &= ~(termios.INLCR | termios.IGNCR | termios.ICRNL | termios.IGNBRK)

        if hasattr(termios, 'IUCLC'):
            iflag &= ~termios.IUCLC
        if hasattr(termios, 'PARMRK'):
            iflag &= ~termios.PARMRK

        if [iflag, oflag, cflag, lflag, ispeed, ospeed, cc] != orig_attr:
            termios.tcsetattr(
                self.fd,
                termios.TCSANOW,
                [iflag, oflag, cflag, lflag, ispeed, ospeed, cc])

    def close(self) -> None:
        if self.fd < 0:
            os.close(self.fd)
            self.fd = -1

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


__dev_flag_no_pyserial: bool = False


class CdcSerial(CdcOsSerial if __dev_flag_no_pyserial else CdcPySerial):
    pass
