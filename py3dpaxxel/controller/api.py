import logging
import re
import threading
import time
from typing import TextIO, Dict, List, Optional, Union

from serial.tools.list_ports import comports

from .constants import Range, Scale, OutputDataRate, FaultCode
from .serial import CdcSerial
from .transfer_types import (TxFrame, RxUnknownResponse, RxOutputDataRate,
                             RxScale, RxRange, RxSamplingStopped, RxSamplingFinished, RxSamplingAborted,
                             RxAcceleration, RxSamplingStarted, RxFifoOverflow, RxDeviceSetup, TxGetOutputDataRate, TxSetOutputDataRate, TxGetScale, TxSetScale, TxGetRange, TxSetRange,
                             TxReboot,
                             TxSamplingStart, TxSamplingStop, RxFrameFromHeaderId, TxGetFirmwareVersion, RxFirmwareVersion, FirmwareVersion, RxFault, RxUptime, TxGetUptime, TxGetBufferStatus,
                             RxBufferStatus, BufferStatus, RxBufferOverflow, RxTransmissionError)


class ErrorFifoOverflow(IOError):
    """controller detected accelerometer FiFo overrun"""

    def __init__(self):
        super().__init__("controller detected FiFo overrun in the accelerometer sensor")


class ErrorBufferOverflow(IOError):
    """circular buffer overrun while sampling"""

    def __init__(self):
        super().__init__("ringbuffer overflow while sampling stream")


class ErrorTransmissionError(IOError):
    """transmission error to host occurred"""

    def __init__(self):
        super().__init__("transmission to host error occurred while sampling stream")


class ErrorControllerFault(IOError):
    """controller went to fault handler most likely remaining in endless loop; device reboot recommended"""

    def __init__(self, code: FaultCode):
        super().__init__(f"controller fault code={code.name}")


class ErrorUnknownResponse(IOError):
    """received unknown response from controller"""

    def __init__(self, response):
        super().__init__(f"unknown response received :{response}")


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

    def __init__(self, ser_dev_name: str, serial_read_timeout_s: float = 0.1, serial_write_timeout_s: float = 1) -> None:
        """

        :param ser_dev_name: i.e. "/dev/ttyACM0"
        :param serial_read_timeout_s: how long to wait for incoming bytes until next decoding attempt
        """
        super().__init__(ser_dev_name, serial_read_timeout_s, serial_write_timeout_s)

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
        Example:

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

    def get_firmware_version(self) -> FirmwareVersion:
        payload = self._send_frame_then_receive(TxGetFirmwareVersion(), RxFirmwareVersion.LEN)
        response: RxFirmwareVersion = RxFrameFromHeaderId(payload).unpack()
        return response.version

    def get_output_data_rate(self) -> OutputDataRate:
        payload = self._send_frame_then_receive(TxGetOutputDataRate(), RxOutputDataRate.LEN)
        response: RxOutputDataRate = RxFrameFromHeaderId(payload).unpack()
        return response.outputDataRate

    def set_output_data_rate(self, odr: OutputDataRate) -> None:
        self._send_frame(TxSetOutputDataRate(odr))

    def get_scale(self) -> Scale:
        payload = self._send_frame_then_receive(TxGetScale(), RxScale.LEN)
        response: RxScale = RxFrameFromHeaderId(payload).unpack()
        return response.scale

    def set_scale(self, scale: Scale) -> None:
        self._send_frame(TxSetScale(scale))

    def get_range(self) -> Range:
        payload = self._send_frame_then_receive(TxGetRange(), RxRange.LEN)
        response: RxRange = RxFrameFromHeaderId(payload).unpack()
        return response.range

    def set_range(self, data_range: Range) -> None:
        self._send_frame(TxSetRange(data_range))

    def reboot(self) -> None:
        self._send_frame(TxReboot())

    def start_sampling(self, num_samples: int = 0) -> None:
        assert (0 <= num_samples) and (num_samples <= 65535), f"samples count out of bounds: 0 < {num_samples} < 65535"
        self._send_frame(TxSamplingStart(num_samples))

    def stop_sampling(self) -> None:
        self._send_frame(TxSamplingStop())

    def get_uptime(self) -> int:
        payload = self._send_frame_then_receive(TxGetUptime(), RxUptime.LEN)
        response: RxUptime = RxFrameFromHeaderId(payload).unpack()
        return response.elapsed_ms

    def get_buffer_status(self) -> BufferStatus:
        payload = self._send_frame_then_receive(TxGetBufferStatus(), RxBufferStatus.LEN)
        response: RxBufferStatus = RxFrameFromHeaderId(payload).unpack()
        return BufferStatus(response.size_bytes, response.capacity, response.max_items_count)

    def decode(self, return_on_stop: bool = False,
               message_timeout_s: float = 10.0,
               out_file: Optional[TextIO] = None,
               do_stop_flag: threading.Event = threading.Event()) -> None:
        """
        Decodes incoming stream from controller.

        Example:

        .. code-block::

            run sample x y z
            00 00000 +0553.800 +0179.400 +0616.200
            00 00001 +0538.200 +0179.400 +0592.800
            ...
            00 06398 +0546.000 +0187.200 +0616.200
            00 06399 +0530.400 +0187.200 +0639.600
            # {'rate': 'ODR3200', 'range': 'G4', 'scale': 'FULL_RES_4MG_LSB'}

        In the above example `6400` samples were received with sequence/stream number `0`.
        The sensor had an output data rate of ODR3200 (`3,2kSamples/s`),
        range of `4g` and the scale was set at full resolution (`1LSB=3.9mg`).

        :param return_on_stop: Whether to return when first :class:`.RxSamplingStopped` package was seen or not.
            If false, the sequence counter `seq` increases with each stream.
        :param message_timeout_s: how long to wait until next message, :class:`.ErrorReadTimeout` is thrown, set to 0.0 to disable
        :param out_file: where to save the decoded stream, set to None to disable
        :param do_stop_flag: aborts decoder loop if set
        :return: None
        """
        stream_meta_data: Dict[str, Union[str, any]] = {}
        data: bytearray = bytearray()
        sequence: int = 0
        num_samples_requested = 0
        num_samples_received: int = 0
        start_time = Optional[float]
        elapsed_time = Optional[float]
        timestamp_last_message_seen: float = time.time()
        while not do_stop_flag.is_set():
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
                        logging.fatal(f"rx: {str(e)}")
                        raise e

                    if isinstance(package, RxBufferOverflow):
                        e = ErrorBufferOverflow()
                        logging.fatal(f"rx: {str(e)}")
                        raise e

                    if isinstance(package, RxTransmissionError):
                        e = ErrorTransmissionError()
                        logging.fatal(f"rx: {str(e)}")
                        raise e

                    if isinstance(package, RxFault):
                        e = ErrorControllerFault(package.code)
                        logging.fatal(f"rx: {str(e)}")
                        raise e

                    if isinstance(package, RxSamplingStarted):
                        logging.info(f"rx: {package}")
                        out_file.write("seq sample x y z\n") if out_file is not None else logging.info("#seq #sample x[mg] y[mg] z[mg]")
                        num_samples_received = 0
                        start_time = time.time()
                        num_samples_requested = package.maxSamples

                    if isinstance(package, RxFirmwareVersion):
                        stream_meta_data.update({"firmware": {"version": package.version.string}})
                        logging.info(f"rx: {package}")

                    if isinstance(package, RxBufferStatus):
                        stream_meta_data.update({"buffer": {
                            "size_bytes": f"{package.size_bytes}",
                            "capacity": f"{package.capacity}",
                            "max_items_count": f"{package.max_items_count}"
                        }})
                        logging.info(f"rx: {package}")

                    if isinstance(package, RxAcceleration):
                        acceleration = f"{sequence:02} {package}"
                        assert num_samples_received == package.index, f"sequence error: expected={num_samples_received} vs current={package.index}"
                        num_samples_received += 1
                        if num_samples_received > 65535:
                            num_samples_received = 0
                        out_file.write(acceleration + "\n") if out_file is not None else logging.info(f"rx: {acceleration}")

                    if isinstance(package, RxDeviceSetup):
                        stream_meta_data.update({"sensor": eval(re.search(RxDeviceSetup.REPR_FILTER_REGEX, str(package)).group(1))})
                        stream_meta_data.update({"samples": {
                            "requested": f"{num_samples_requested}",
                            "received": f"{num_samples_received}",
                        }})
                        out_file.write("# " + str(stream_meta_data).replace("'", '"') + "\n") if out_file is not None else logging.info("rx: Device Setup: " + str(stream_meta_data))

                    if isinstance(package, (RxSamplingStopped, RxSamplingFinished, RxSamplingAborted)):
                        elapsed_time = time.time() - start_time
                        if isinstance(package, RxSamplingFinished):
                            logging.info(f"rx: {str(package)} at sample {num_samples_received}")

                    if isinstance(package, RxSamplingStopped):
                        logging.info(f"rx: {package}")
                        logging.info(f"sequence {sequence:02}: processed {num_samples_received} samples in {elapsed_time:.6f} s "
                                     f"({(num_samples_received / elapsed_time):.1f} samples/s; "
                                     f"{((num_samples_received * RxAcceleration.LEN * 8) / elapsed_time):.1f} baud)")
                        sequence += 1

                        if return_on_stop or out_file is not None:
                            return

        logging.warning(f"decoder stops ahead of time after {num_samples_received} samples because stop flag was set")
