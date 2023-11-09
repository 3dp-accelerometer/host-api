from typing import Dict, Type

from lib.device_constants import TransportHeaderId


class Frame:
    def __init__(self, header_id: TransportHeaderId, payload: bytearray):
        self.header_id: TransportHeaderId = header_id
        self.payload: bytearray = payload


class TxFrame(Frame):
    def __init__(self, header_id: TransportHeaderId, payload: bytearray):
        super().__init__(header_id, payload)

    def pack(self) -> bytes:
        """
        Packs header_id + payload into bytes: [header_id, byte1, byte2, ...]
        :return:
        """
        values = [int(self.header_id.value)]
        values.extend(self.payload)
        return bytes(values)


class FifoOverflow:
    LEN = 1

    def __init__(self, payload: bytearray):
        payload.pop(0)

    def __str__(self) -> str:
        return "Fifo Overflow"


class SamplingStarted:
    LEN = 1

    def __init__(self, payload: bytearray):
        payload.pop(0)

    def __str__(self) -> str:
        return "Sampling Started"


class SamplingStopped:
    LEN = 1

    def __init__(self, payload: bytearray):
        payload.pop(0)

    def __str__(self) -> str:
        return "Sampling Stopped"


class SamplingFinished:
    LEN = 1

    def __init__(self, payload: bytearray):
        payload.pop(0)

    def __str__(self) -> str:
        return "Sampling Finished"


class SamplingAborted:
    LEN = 1

    def __init__(self, payload: bytearray):
        payload.pop(0)

    def __str__(self) -> str:
        return "Sampling Aborted"


class UnknownResponse:
    def __init__(self):
        pass

    def __str__(self) -> str:
        return "Unknown Response"


class Acceleration:
    LEN = 7
    FULL_RESOLUTION_LSB_SCALE = 3.9  # (min, typ, max) = (3.5, 3.9, 4.3), ADXL 345 Datasheet, rev. G, Tale 1., parameter SENSITIVITY

    def __init__(self, payload: bytearray):
        payload.pop(0)
        self.x = Acceleration.FULL_RESOLUTION_LSB_SCALE * int.from_bytes(payload[0:2], "little", signed=True)
        self.y = Acceleration.FULL_RESOLUTION_LSB_SCALE * int.from_bytes(payload[2:4], "little", signed=True)
        self.z = Acceleration.FULL_RESOLUTION_LSB_SCALE * int.from_bytes(payload[4:6], "little", signed=True)
        payload.pop(0)
        payload.pop(0)
        payload.pop(0)
        payload.pop(0)
        payload.pop(0)
        payload.pop(0)

    def __str__(self) -> str:
        return f"{self.x:+09.3f} {self.y:+09.3f} {self.z:+09.3f}"


class RxFrame:
    MAPPING: Dict[TransportHeaderId, Type[SamplingStarted | SamplingStopped | SamplingFinished | SamplingAborted | UnknownResponse]] = {
        TransportHeaderId.SAMPLING_FIFO_OVERFLOW: FifoOverflow,
        TransportHeaderId.SAMPLING_STARTED: SamplingStarted,
        TransportHeaderId.SAMPLING_STOPPED: SamplingStopped,
        TransportHeaderId.SAMPLING_FINISHED: SamplingFinished,
        TransportHeaderId.SAMPLING_ABORTED: SamplingAborted,
        TransportHeaderId.ACCELERATION: Acceleration,
    }

    def __init__(self, payload: bytearray):
        self.payload: bytearray = payload

    def unpack(self) -> SamplingStarted | SamplingStopped | SamplingFinished | SamplingAborted | UnknownResponse | None:
        header_id = TransportHeaderId(self.payload[0])
        if header_id in RxFrame.MAPPING:
            clazz = RxFrame.MAPPING[header_id]
            return clazz(self.payload) if len(self.payload) >= clazz.LEN else None
        else:
            return UnknownResponse()
