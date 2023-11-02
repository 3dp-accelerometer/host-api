from device_constants import TransportHeaderId


class TxFrame:
    def __init__(self, header_id: TransportHeaderId, payload: bytes):
        self.header_id = header_id
        self.payload = payload

    def pack(self) -> bytes:
        """
        Packs header_id + payload into bytes: [header_id, byte1, byte2, ...]
        :return:
        """
        return bytes([int(self.header_id.value), self.payload[0]])
