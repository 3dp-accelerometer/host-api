from typing import Dict, Type, Union, Optional

from .constants import TransportHeaderId, OutputDataRate, Scale, Range, FaultCode


class Frame:
    """
    TxFrame base class.
    """

    def __init__(self, header_id: TransportHeaderId, payload: bytearray) -> None:
        self.header_id: TransportHeaderId = header_id
        self.payload: bytearray = payload


class TxFrame(Frame):
    """
    Request base class.
    """

    def __init__(self, header_id: TransportHeaderId, payload: bytearray = bytearray()) -> None:
        super().__init__(header_id, payload)

    def pack(self) -> bytes:
        """
        Packs header_id + payload into bytes: [header_id, byte1, byte2, ...]
        :return:
        """
        values = [int(self.header_id.value)]
        values.extend(self.payload)
        return bytes(values)


class TxGetFirmwareVersion(TxFrame):
    """
    Request package to retrieve the firmware version from device.
    """

    def __init__(self) -> None:
        super().__init__(TransportHeaderId.TX_GET_FIRMWARE_VERSION)


class TxSetOutputDataRate(TxFrame):
    """
    Request package to configure the device ODR.
    """

    def __init__(self, odr: OutputDataRate) -> None:
        super().__init__(TransportHeaderId.TX_SET_OUTPUT_DATA_RATE, bytearray([int(odr.value)]))


class TxGetOutputDataRate(TxFrame):
    """
    Request package to receive the current device ODR.
    """

    def __init__(self) -> None:
        super().__init__(TransportHeaderId.TX_GET_OUTPUT_DATA_RATE)


class TxSetRange(TxFrame):
    """
    Request package to configure the device range (min/max g).
    """

    def __init__(self, data_range: Range) -> None:
        super().__init__(TransportHeaderId.TX_SET_RANGE, bytearray([int(data_range.value)]))


class TxGetRange(TxFrame):
    """
    Request package to receive the device range (min/max g).
    """

    def __init__(self) -> None:
        super().__init__(TransportHeaderId.TX_GET_RANGE)


class TxSetScale(TxFrame):
    """
    Request package to configure the device scale (g scale of LSB).
    """

    def __init__(self, scale: Scale) -> None:
        super().__init__(TransportHeaderId.TX_SET_SCALE, bytearray([int(scale.value)]))


class TxGetScale(TxFrame):
    """
    Request package to receive the device scale (g scale of LSB).
    """

    def __init__(self) -> None:
        super().__init__(TransportHeaderId.TX_GET_SCALE)


class TxReboot(TxFrame):
    """
    Request package to perform a device reboot.
    """

    def __init__(self) -> None:
        super().__init__(TransportHeaderId.TX_DEVICE_REBOOT)


class TxSamplingStart(TxFrame):
    """
    Request package to start sampling stream.
    """

    def __init__(self, num_samples: int = 0) -> None:
        payload = [num_samples & 0x00ff, (num_samples & 0xff00) >> 8]
        super().__init__(TransportHeaderId.TX_SAMPLING_START, bytearray(payload))


class TxSamplingStop(TxFrame):
    """
    Request package to stop a running stream.
    """

    def __init__(self) -> None:
        super().__init__(TransportHeaderId.TX_SAMPLING_STOP)


class TxGetUptime(TxFrame):
    """
    Request package to retrieve the device uptime [ms] since boot.
    """

    def __init__(self) -> None:
        super().__init__(TransportHeaderId.TX_GET_UPTIME)


class TxGetBufferStatus(TxFrame):
    """
    Request package to retrieve the buffer status since last sampling-start.
    """

    def __init__(self) -> None:
        super().__init__(TransportHeaderId.TX_GET_BUFFER_STATUS)


class RxFrame:
    """
    Response base class.
    """

    LEN = 0

    def consume_all(self, payload: bytearray):
        for i in range(0, self.LEN):
            payload.pop(0)


class FirmwareVersion:
    """
    The device firmware information.
    """

    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0):
        self.major: int = major
        self.minor: int = minor
        self.patch: int = patch
        self.string: str = f"{major}.{minor}.{patch}"

    def __str__(self) -> str:
        return self.string

    @staticmethod
    def from_string(version: str) -> "FirmwareVersion":
        major, minor, patch = version.split(".")
        return FirmwareVersion(major, minor, patch)


class RxFirmwareVersion(RxFrame):
    """
    Response from controller transporting the firmware version.
    """

    LEN = 1 + 1 + 1 + 1

    def __init__(self, payload: bytearray) -> None:
        major: int = int.from_bytes([payload[1]], byteorder="little", signed=False)
        minor: int = int.from_bytes([payload[2]], byteorder="little", signed=False)
        patch: int = int.from_bytes([payload[3]], byteorder="little", signed=False)
        self.version: FirmwareVersion = FirmwareVersion(major, minor, patch)
        self.consume_all(payload)

    def __str__(self) -> str:
        return f"Firmware Version v={self.version}"


class RxOutputDataRate(RxFrame):
    """
    Response from controller transporting the currently used ODR.
    """

    LEN = 1 + 1

    def __init__(self, payload: bytearray) -> None:
        self.outputDataRate: OutputDataRate = OutputDataRate(payload[1])
        self.consume_all(payload)

    def __str__(self) -> str:
        return f"Device OutputDataRate rate={self.outputDataRate}"


class RxRange(RxFrame):
    """
    Response from controller transporting the currently used range (min/max g).
    """

    LEN = 1 + 1

    def __init__(self, payload: bytearray) -> None:
        self.range: Range = Range(payload[1])
        self.consume_all(payload)

    def __str__(self) -> str:
        return f"Device Range range={self.range}"


class RxScale(RxFrame):
    """
    Response from controller transporting the currently used scale (g scale of MSB).
    """

    LEN = 1 + 1

    def __init__(self, payload: bytearray) -> None:
        self.scale: Scale = Scale(int.from_bytes([payload[1]], byteorder="little", signed=False))
        self.consume_all(payload)

    def __str__(self) -> str:
        return f"Device Scale scale={self.scale}"


class RxDeviceSetup(RxFrame):
    """
    Response from controller transporting the currently used configuration: ODR, Range and Scale.
    This package is received at the end of stream.
    """

    LEN = 1 + 1
    REPR_FILTER_REGEX: str = '^Device Setup.*({.*})$'

    def __init__(self, payload: bytearray) -> None:
        self.outputDataRate: Optional[OutputDataRate] = None
        payload_byte: int = payload[1]
        self.outputDataRate: OutputDataRate = OutputDataRate(payload_byte & 0b0001111)
        self.range: Range = Range((payload_byte & 0b010000) >> 4)
        self.scale: Scale = Scale((payload_byte & 0b100000) >> 5)
        self.consume_all(payload)

    def __str__(self) -> str:
        return f'Device Setup {{"rate":"{self.outputDataRate.name}", "range":"{self.range.name}", "scale":"{self.scale.name}"}}'


class RxFifoOverflow(RxFrame):
    """
    Response from controller indicating that the acceleration sensor's Fifo could not be consumed/read in time, thus an overrun occurred.
    """

    LEN = 1

    def __init__(self, payload: bytearray) -> None:
        self.consume_all(payload)

    def __str__(self) -> str:
        return "Fifo Overflow"


class RxBufferOverflow(RxFrame):
    """
    Response from controller indicating that the circular buffer overflowed.
    """

    LEN = 1

    def __init__(self, payload: bytearray) -> None:
        self.consume_all(payload)

    def __str__(self) -> str:
        return "Buffer Overflow"


class RxTransmissionError(RxFrame):
    """
    Response from controller indicating that the transmission to the host was erroneous (while sampling).
    """

    LEN = 1

    def __init__(self, payload: bytearray) -> None:
        self.consume_all(payload)

    def __str__(self) -> str:
        return "Transmission Error"


class RxSamplingStarted(RxFrame):
    """
    Response from controller indicating that sampling has been started just before this response was issued.
    This package is received at the start of stream.
    """

    LEN = 3

    def __init__(self, payload: bytearray) -> None:
        self.maxSamples: int = int.from_bytes(payload[1:3], "little", signed=False)
        self.consume_all(payload)

    def __str__(self) -> str:
        return f"Sampling Started maxSamples={self.maxSamples}"


class RxSamplingStopped(RxFrame):
    """
    Response from controller indicating that the sampling has been stopped (for whatever reason).
    """

    LEN = 1

    def __init__(self, payload: bytearray) -> None:
        self.consume_all(payload)

    def __str__(self) -> str:
        return "Sampling Stopped"


class RxSamplingFinished(RxFrame):
    """
    Response from controller indicating that sampling has been finished successfully.
    This package is received at the end of stream.
    When this response is received, the sampling stream has been successfully transferred:

    - stream is complete and
    - without HW errors.
    """

    LEN = 1

    def __init__(self, payload: bytearray) -> None:
        self.consume_all(payload)

    def __str__(self) -> str:
        return "Sampling Finished"


class RxSamplingAborted(RxFrame):
    """
    Response from controller indicating that the sampling has been aborted upon user request.
    """

    LEN = 1

    def __init__(self, payload: bytearray) -> None:
        self.consume_all(payload)

    def __str__(self) -> str:
        return "Sampling Aborted"


class RxUnknownResponse:
    """
    Response is issued whenever a controller message could not be parsed successfully.
    """

    def __init__(self, unknown_header_id: int) -> None:
        self.unknown_header_id: int = unknown_header_id

    def __str__(self) -> str:
        return f"Unknown Response header_id={self.unknown_header_id}"


class RxAcceleration(RxFrame):
    """
    Response from controller transporting the currently measured acceleration data.
    It contains

    - the sample counter (which shall always be +1 larger than previous counter) and
    - the scaled acceleration data (controller must be in :class:`py3dpaxxel.controller.constant.Scale.FULL_RES_4MG_LSB` scale mode)
    """

    LEN = 9
    FULL_RESOLUTION_LSB_SCALE = 3.9  # (min, typ, max) = (3.5, 3.9, 4.3), ADXL 345 Datasheet, rev. G, Tale 1., parameter SENSITIVITY

    def __init__(self, payload: bytearray) -> None:
        self.index: int = int.from_bytes(payload[1:3], "little", signed=False)
        self.x: float = RxAcceleration.FULL_RESOLUTION_LSB_SCALE * int.from_bytes(payload[3:5], "little", signed=True)
        self.y: float = RxAcceleration.FULL_RESOLUTION_LSB_SCALE * int.from_bytes(payload[5:7], "little", signed=True)
        self.z: float = RxAcceleration.FULL_RESOLUTION_LSB_SCALE * int.from_bytes(payload[7:9], "little", signed=True)
        self.consume_all(payload)

    def __str__(self) -> str:
        return f"{self.index:05} {self.x:+09.3f} {self.y:+09.3f} {self.z:+09.3f}"


class RxUptime(RxFrame):
    """
    Response to get uptime transporting the elapsed milliseconds since last boot.
    """

    LEN = 5

    def __init__(self, payload: bytearray) -> None:
        self.elapsed_ms: int = int.from_bytes(payload[1:4], "little", signed=False)
        self.consume_all(payload)

    def __str__(self) -> str:
        return f"Uptime ms={self.elapsed_ms}"


class RxBufferStatus(RxFrame):
    """
    Response to get buffer status transporting buffer information since last sampling-start.
    """

    LEN = (1 + 2 + 2 + 2 + 2 + 2 + 2)

    def __init__(self, payload: bytearray) -> None:
        self.size_bytes: int = int.from_bytes(payload[1:3], "little", signed=False)
        self.capacity_total: int = int.from_bytes(payload[3:5], "little", signed=False)
        self.capacity_used_max: int = int.from_bytes(payload[5:7], "little", signed=False)
        self.put_count: int = int.from_bytes(payload[7:9], "little", signed=False)
        self.take_count: int = int.from_bytes(payload[9:11], "little", signed=False)
        self.largest_tx_chunk_bytes: int = int.from_bytes(payload[11:13], "little", signed=False)
        self.consume_all(payload)

    def __str__(self) -> str:
        return (f"BufferStatus "
                f"size_bytes={self.size_bytes} "
                f"capacity_total={self.capacity_total} "
                f"capacity_used_max={self.capacity_used_max} "
                f"put_count={self.put_count} "
                f"take_count={self.take_count} "
                f"largest_tx_chunk_bytes={self.largest_tx_chunk_bytes}")


class BufferStatus:
    """
    Buffer status as received by RxBufferStatus.
    """

    def __init__(self, size_bytes: int = 0,
                 capacity_total: int = 0,
                 capacity_used_max: int = 0,
                 put_count: int = 0,
                 take_count: int = 0,
                 largest_tx_chunk_bytes: int = 0):
        self.size_bytes: int = size_bytes
        self.capacity_total: int = capacity_total
        self.capacity_used_max: int = capacity_used_max
        self.put_count: int = put_count
        self.take_count: int = take_count
        self.largest_tx_chunk_bytes: int = largest_tx_chunk_bytes


class RxFault(RxFrame):
    """
    Response is issued whenever a controller fault occurred but the controller was still capable to transmit this message.
    """

    LEN = 1 + 1

    def __init__(self, payload: bytearray) -> None:
        self.code: FaultCode = FaultCode(int.from_bytes(payload[1:2], "little", signed=False))
        self.consume_all(payload)

    def __str__(self) -> str:
        return f"Fault code={self.code.name}"


class RxFrameFromHeaderId:
    """
    Parse response from bytes.
    """

    MAPPING: Dict[TransportHeaderId, Type[Union[RxOutputDataRate, RxRange, RxScale, RxSamplingStarted, RxSamplingStopped, RxSamplingFinished, RxSamplingAborted, RxUnknownResponse]]] = {
        TransportHeaderId.RX_OUTPUT_DATA_RATE: RxOutputDataRate,
        TransportHeaderId.RX_RANGE: RxRange,
        TransportHeaderId.RX_SCALE: RxScale,
        TransportHeaderId.RX_DEVICE_SETUP: RxDeviceSetup,
        TransportHeaderId.RX_SAMPLING_FIFO_OVERFLOW: RxFifoOverflow,
        TransportHeaderId.RX_SAMPLING_BUFFER_OVERFLOW: RxBufferOverflow,
        TransportHeaderId.RX_SAMPLING_STARTED: RxSamplingStarted,
        TransportHeaderId.RX_SAMPLING_STOPPED: RxSamplingStopped,
        TransportHeaderId.RX_SAMPLING_FINISHED: RxSamplingFinished,
        TransportHeaderId.RX_SAMPLING_ABORTED: RxSamplingAborted,
        TransportHeaderId.RX_FIRMWARE_VERSION: RxFirmwareVersion,
        TransportHeaderId.RX_ACCELERATION: RxAcceleration,
        TransportHeaderId.RX_UPTIME: RxUptime,
        TransportHeaderId.RX_BUFFER_STATUS: RxBufferStatus,
        TransportHeaderId.RX_FAULT: RxFault,
        TransportHeaderId.RX_TRANSMISSION_ERROR: RxTransmissionError,
    }

    def __init__(self, payload: bytearray) -> None:
        self.payload: bytearray = payload

    def unpack(self) -> Union[
        RxOutputDataRate,
        RxRange,
        RxScale,
        RxDeviceSetup,
        RxFifoOverflow,
        RxBufferOverflow,
        RxSamplingStarted,
        RxSamplingStopped,
        RxSamplingFinished,
        RxSamplingAborted,
        RxFirmwareVersion,
        RxUnknownResponse,
        RxUptime,
        RxBufferStatus,
        RxFault,
        RxTransmissionError,
        None
    ]:
        header_id_int: int = int.from_bytes([self.payload[0]], "little", signed=False)

        try:
            header_id = TransportHeaderId(header_id_int)
            if header_id in RxFrameFromHeaderId.MAPPING:
                clazz = RxFrameFromHeaderId.MAPPING[header_id]
                return clazz(self.payload) if len(self.payload) >= clazz.LEN else None
            else:
                return RxUnknownResponse(header_id.value)
        except ValueError as _e:
            return RxUnknownResponse(header_id_int)
