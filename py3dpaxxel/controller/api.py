import logging
import re
import time
from typing import TextIO, Dict, List, Optional

from serial.tools.list_ports import comports

from .constants import Range, Scale, OutputDataRate
from .serial import CdcSerial
from .transfer_types import (TxFrame, RxUnknownResponse, RxOutputDataRate,
                             RxScale, RxRange, RxSamplingStopped, RxSamplingFinished, RxSamplingAborted,
                             RxAcceleration, RxSamplingStarted, RxFifoOverflow, RxDeviceSetup, TxGetOutputDataRate, TxSetOutputDataRate, TxGetScale, TxSetScale, TxGetRange, TxSetRange,
                             TxReboot,
                             TxSamplingStart, TxSamplingStop, RxFrameFromHeaderId)


class ErrorFifoOverflow(IOError):
    """controller detected accelerometer FiFo overrun"""

    def __init__(self):
        super().__init__("controller detected FiFo overrun in the accelerometer sensor")


class ErrorUnknownResponse(IOError):
    """received unknown response from controller"""

    def __init__(self, response):
        super().__init__(f"received unknown response from controller :{response}")


class ErrorReadTimeout(IOError):
    """timeout error: no message received since timeout-limit"""

    def __init__(self, timeout_limit, current_timeout_value):
        super().__init__(f"timeout occurred: no message received since timeout_limit_s={timeout_limit} current_timeout_s={current_timeout_value}")


class Py3dpAxxel(CdcSerial):
    """
    Implementation to manipulate the py3dpaxxel controller (firmware).

    The implementation establishes the communication with the controller (tx/rx) and encoding + decoding of data packets.
    Since the controller communicates in CDC mode, the data packets are very naive and consist only of header ID and payload.
    No CRC, dynamic data length packet or escape sequence is considered.
    """

    DEVICE_VID = 0x1209
    "see https://pid.codes/1209/"
    DEVICE_PID = 0xE11A
    "see https://pid.codes/1209/411A/"

    def __init__(self, ser_dev_name: str, serial_read_timeout_s: float = 0.1) -> None:
        """

        :param ser_dev_name: i.e. "/dev/ttyACM0"
        :param serial_read_timeout_s: how long to wait for incoming bytes until next decoding attempt
        """
        super().__init__(ser_dev_name, serial_read_timeout_s)

    @staticmethod
    def get_devices_list_human_readable() -> List[str]:
        """

        :return: list of devices, i.e. ["/dev/ttyACM0", ...]
        """
        devices: List[str] = []
        for s in [cp for cp in comports() if cp.vid == Py3dpAxxel.DEVICE_VID and cp.pid == Py3dpAxxel.DEVICE_PID]:
            devices.append(s.device)
        return devices

    @staticmethod
    def get_devices_dict() -> Dict[str, Dict[str, str]]:
        """
        .. code-block::

            dict of devices:
                {
                    "/dev/ttyACM0": {
                         "manufacturer": "3DP Accelerometer",
                         "product": "3dpaxxel",
                         "vendor_id": 4617,
                         "product_id": 57626,
                         "serial": "3472348C3334"
                    }, ...
                }

        :return: dict of devices
        """
        devices: Dict[str, Dict[str, str]] = dict()
        for s in [cp for cp in comports() if cp.vid == Py3dpAxxel.DEVICE_VID and cp.pid == Py3dpAxxel.DEVICE_PID]:
            devices[s.device] = {"manufacturer": s.manufacturer, "product": s.product, "vendor_id": s.vid, "product_id": s.pid, "serial": s.serial_number}
        return devices

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

    def reboot(self) -> None:
        self._send_frame(TxReboot())

    def start_sampling(self, num_samples: int = 0) -> None:
        assert (0 <= num_samples) and (num_samples <= 65535)
        self._send_frame(TxSamplingStart(num_samples))

    def stop_sampling(self) -> None:
        self._send_frame(TxSamplingStop())

    def decode(self, return_on_stop: bool = False, message_timeout_s: float = 10.0, out_file: Optional[TextIO] = None) -> None:
        """
        Decodes incoming stream from controller.

        :param return_on_stop: whether to return when first :class:`.RxSamplingStopped` package was seen
        :param message_timeout_s: how long to wait until next message, :class:`.ErrorReadTimeout` is thrown, set to 0.0 to disable
        :param out_file: where to save the decoded stream, set to None to disable
        :return: None
        """
        data: bytearray = bytearray()
        run_count: int = 0
        sample_count: int = 0
        start_time = Optional[float]
        elapsed_time = Optional[float]
        timestamp_last_message_seen: float = time.time()
        while True:
            received_bytes: bytes = self.read_bytes(1, 0.1)

            if len(received_bytes) > 0:
                timestamp_last_message_seen = time.time()
            elif message_timeout_s != 0.0:
                current_delay_s: float = time.time() - timestamp_last_message_seen
                if current_delay_s > message_timeout_s:
                    raise ErrorReadTimeout(message_timeout_s, current_delay_s)

            data.extend(received_bytes)
            if len(data) >= 1:
                package = RxFrameFromHeaderId(data).unpack()
                if package is not None:
                    if isinstance(package, RxUnknownResponse):
                        e = ErrorUnknownResponse(package.unknown_header_id)
                        logging.fatal(f"rx: {str(e)}")
                        raise e

                    if isinstance(package, RxFifoOverflow):
                        e = ErrorFifoOverflow()
                        logging.fatal("rx: {str(e)}")
                        raise e

                    if isinstance(package, RxSamplingStarted):
                        logging.info(f"rx: {package}")
                        out_file.write("run sample x y z\n") if out_file is not None else logging.info("#run #sample x[mg] y[mg] z[mg]")
                        sample_count = 0
                        start_time = time.time()

                    if isinstance(package, RxAcceleration):
                        acceleration = f"{run_count:02} {package}"
                        assert sample_count == package.index
                        sample_count += 1
                        if sample_count > 65535:
                            sample_count = 0
                        out_file.write(acceleration + "\n") if out_file is not None else logging.info(f"rx: {acceleration}")

                    if isinstance(package, RxDeviceSetup):
                        parameters = eval(re.search(RxDeviceSetup.REPR_FILTER_REGEX, str(package)).group(1))
                        out_file.write("# " + str(parameters) + "\n") if out_file is not None else logging.info("rx: Device Setup: " + str(parameters))

                    if isinstance(package, (RxSamplingStopped, RxSamplingFinished, RxSamplingAborted)):
                        elapsed_time = time.time() - start_time
                        if isinstance(package, RxSamplingFinished):
                            logging.info(f"rx: {str(package)} at sample {sample_count}")

                    if isinstance(package, RxSamplingStopped):
                        logging.info(f"rx: {package}")
                        logging.info(f"run {run_count:02}: processed {sample_count} samples in {elapsed_time:.6f} s "
                                     f"({(sample_count / elapsed_time):.1f} samples/s; "
                                     f"{((sample_count * RxAcceleration.LEN * 8) / elapsed_time):.1f} baud)")
                        run_count += 1

                        if return_on_stop or out_file is not None:
                            return
