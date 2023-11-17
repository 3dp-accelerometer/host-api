import logging
import re
import time
from typing import TextIO, Union, Dict, List

from serial.tools.list_ports import comports

from .constants import Range, Scale, OutputDataRate
from .serial import CdcSerial
from .transfer_types import (TxFrame, RxFrame, RxUnknownResponse, RxOutputDataRate,
                             RxScale, RxRange, RxSamplingStopped, RxSamplingFinished, RxSamplingAborted,
                             RxAcceleration, RxSamplingStarted, RxFifoOverflow, RxDeviceSetup, TxGetOutputDataRate, TxSetOutputDataRate, TxGetScale, TxSetScale, TxGetRange, TxSetRange,
                             TxReboot,
                             TxSamplingStart, TxSamplingStop)


class ErrorFifoOverflow(IOError):
    """controller detected accelerometer FiFo overrun"""


class ErrorUnknownResponse(IOError):
    """received unknown response from controller"""


class Adxl345(CdcSerial):
    # see https://pid.codes/pids/
    DEVICE_VID = 0x1209
    DEVICE_PID = 0xE11A

    def __init__(self, ser_dev_name: str, timeout: float = 0.1) -> None:
        super().__init__(ser_dev_name, timeout)

    @staticmethod
    def get_devices_list_human_readable() -> List[str]:
        devices: List[str] = []
        for s in [cp for cp in comports() if cp.vid == Adxl345.DEVICE_VID and cp.pid == Adxl345.DEVICE_PID]:
            devices.append(s.device)
        return devices

    @staticmethod
    def get_devices_dict() -> Dict[str, Dict[str, str]]:
        devices: Dict[str, Dict[str, str]] = dict()
        for s in [cp for cp in comports() if cp.vid == Adxl345.DEVICE_VID and cp.pid == Adxl345.DEVICE_PID]:
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

    def reboot(self):
        self._send_frame(TxReboot())

    def start_sampling(self, num_samples: int = 0):
        assert (0 <= num_samples) and (num_samples <= 65535)
        self._send_frame(TxSamplingStart(num_samples))

    def stop_sampling(self):
        self._send_frame(TxSamplingStop())

    def decode(self, return_on_stop: bool = False, file: Union[None, TextIO] = None):
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
                    if isinstance(package, RxUnknownResponse):
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
