from typing import Dict, Type

from .constants import TransportHeaderId, OutputDataRate, Scale, Range


class Frame:
    def __init__(self, header_id: TransportHeaderId, payload: bytearray):
        self.header_id: TransportHeaderId = header_id
        self.payload: bytearray = payload


class TxFrame(Frame):
    def __init__(self, header_id: TransportHeaderId, payload: bytearray = bytearray()):
        super().__init__(header_id, payload)

    def pack(self) -> bytes:
        """
        Packs header_id + payload into bytes: [header_id, byte1, byte2, ...]
        :return:
        """
        values = [int(self.header_id.value)]
        values.extend(self.payload)
        return bytes(values)


class TxSetOutputDataRate(TxFrame):
    def __init__(self, odr: OutputDataRate):
        super().__init__(TransportHeaderId.TX_SET_OUTPUT_DATA_RATE, bytearray([int(odr.value)]))


class TxGetOutputDataRate(TxFrame):
    def __init__(self):
        super().__init__(TransportHeaderId.TX_GET_OUTPUT_DATA_RATE)


class TxSetRange(TxFrame):
    def __init__(self, data_range: Range):
        super().__init__(TransportHeaderId.TX_SET_RANGE, bytearray([int(data_range.value)]))


class TxGetRange(TxFrame):
    def __init__(self):
        super().__init__(TransportHeaderId.TX_GET_RANGE)


class TxSetScale(TxFrame):
    def __init__(self, scale: Scale):
        super().__init__(TransportHeaderId.TX_SET_SCALE, bytearray([int(scale.value)]))


class TxGetScale(TxFrame):
    def __init__(self):
        super().__init__(TransportHeaderId.TX_GET_SCALE)


class TxReboot(TxFrame):
    def __init__(self):
        super().__init__(TransportHeaderId.TX_DEVICE_REBOOT)


class TxSamplingStart(TxFrame):
    def __init__(self, num_samples: int = 0):
        payload = [num_samples & 0x00ff, (num_samples & 0xff00) >> 8]
        super().__init__(TransportHeaderId.TX_SAMPLING_START, bytearray(payload))


class TxSamplingStop(TxFrame):
    def __init__(self):
        super().__init__(TransportHeaderId.TX_SAMPLING_STOP)


class RxOutputDataRate:
    LEN = 2

    def __init__(self, payload: bytearray):
        self.outputDataRate: OutputDataRate | None = None
        payload.pop(0)
        self.outputDataRate: OutputDataRate = OutputDataRate(payload[0])
        payload.pop(0)

    def __str__(self) -> str:
        return f"Device OutputDataRate rate={self.outputDataRate}"


class RxFrame:
    LEN = 0

    def consume_all(self, payload: bytearray):
        for i in range(0, self.LEN):
            payload.pop(0)


class RxRange(RxFrame):
    LEN = 2

    def __init__(self, payload: bytearray):
        self.range: Range = Range(payload[1])
        self.consume_all(payload)

    def __str__(self) -> str:
        return f"Device Range range={self.range}"


class RxScale(RxFrame):
    LEN = 2

    def __init__(self, payload: bytearray):
        self.scale: Scale = Scale(int.from_bytes([payload[1]], byteorder="little", signed=False))
        self.consume_all(payload)

    def __str__(self) -> str:
        return f"Device Scale scale={self.scale}"


class RxDeviceSetup(RxFrame):
    LEN = 2
    REPR_FILTER_REGEX: str = '^Device Setup.*({.*})$'

    def __init__(self, payload: bytearray):
        self.outputDataRate: OutputDataRate | None = None
        payload_byte: int = payload[1]
        self.outputDataRate: OutputDataRate = OutputDataRate(payload_byte & 0b0001111)
        self.range: Range = Range((payload_byte & 0b010000) >> 4)
        self.scale: Scale = Scale((payload_byte & 0b100000) >> 5)
        self.consume_all(payload)

    def __str__(self) -> str:
        return f"Device Setup {{'rate':'{self.outputDataRate.name}', 'range':'{self.range.name}', 'scale':'{self.scale.name}'}}"


class RxFifoOverflow(RxFrame):
    LEN = 1

    def __init__(self, payload: bytearray):
        self.consume_all(payload)

    def __str__(self) -> str:
        return "Fifo Overflow"


class RxSamplingStarted(RxFrame):
    LEN = 3

    def __init__(self, payload: bytearray):
        self.maxSamples: int = int.from_bytes(payload[1:2], "little", signed=False)
        self.consume_all(payload)

    def __str__(self) -> str:
        return f"Sampling Started maxSamples={self.maxSamples}"


class RxSamplingStopped(RxFrame):
    LEN = 1

    def __init__(self, payload: bytearray):
        self.consume_all(payload)

    def __str__(self) -> str:
        return "Sampling Stopped"


class RxSamplingFinished(RxFrame):
    LEN = 1

    def __init__(self, payload: bytearray):
        self.consume_all(payload)

    def __str__(self) -> str:
        return "Sampling Finished"


class RxSamplingAborted(RxFrame):
    LEN = 1

    def __init__(self, payload: bytearray):
        self.consume_all(payload)

    def __str__(self) -> str:
        return "Sampling Aborted"


class RxUnknownResponse:
    def __init__(self):
        pass

    def __str__(self) -> str:
        return "Unknown Response"


class RxAcceleration(RxFrame):
    LEN = 9
    FULL_RESOLUTION_LSB_SCALE = 3.9  # (min, typ, max) = (3.5, 3.9, 4.3), ADXL 345 Datasheet, rev. G, Tale 1., parameter SENSITIVITY

    def __init__(self, payload: bytearray):
        self.index: int = int.from_bytes(payload[1:3], "little", signed=False)
        self.x: float = RxAcceleration.FULL_RESOLUTION_LSB_SCALE * int.from_bytes(payload[3:5], "little", signed=True)
        self.y: float = RxAcceleration.FULL_RESOLUTION_LSB_SCALE * int.from_bytes(payload[5:7], "little", signed=True)
        self.z: float = RxAcceleration.FULL_RESOLUTION_LSB_SCALE * int.from_bytes(payload[7:9], "little", signed=True)
        self.consume_all(payload)

    def __str__(self) -> str:
        return f"{self.index:05} {self.x:+09.3f} {self.y:+09.3f} {self.z:+09.3f}"


class RxFrame:
    MAPPING: Dict[TransportHeaderId, Type[RxOutputDataRate | RxRange | RxScale | RxSamplingStarted | RxSamplingStopped | RxSamplingFinished | RxSamplingAborted | RxUnknownResponse]] = {
        TransportHeaderId.RX_OUTPUT_DATA_RATE: RxOutputDataRate,
        TransportHeaderId.RX_RANGE: RxRange,
        TransportHeaderId.RX_SCALE: RxScale,
        TransportHeaderId.RX_DEVICE_SETUP: RxDeviceSetup,
        TransportHeaderId.RX_SAMPLING_FIFO_OVERFLOW: RxFifoOverflow,
        TransportHeaderId.RX_SAMPLING_STARTED: RxSamplingStarted,
        TransportHeaderId.RX_SAMPLING_STOPPED: RxSamplingStopped,
        TransportHeaderId.RX_SAMPLING_FINISHED: RxSamplingFinished,
        TransportHeaderId.RX_SAMPLING_ABORTED: RxSamplingAborted,
        TransportHeaderId.RX_ACCELERATION: RxAcceleration,
    }

    def __init__(self, payload: bytearray):
        self.payload: bytearray = payload

    def unpack(self) -> RxSamplingStarted | RxSamplingStopped | RxSamplingFinished | RxSamplingAborted | RxUnknownResponse | None:
        header_id = TransportHeaderId(int.from_bytes([self.payload[0]], "little", signed=False))
        if header_id in RxFrame.MAPPING:
            clazz = RxFrame.MAPPING[header_id]
            return clazz(self.payload) if len(self.payload) >= clazz.LEN else None
        else:
            return RxUnknownResponse()
