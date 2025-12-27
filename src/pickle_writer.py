import struct


class PickleWriter:
    def __init__(self) -> None:
        self.data = bytearray()

    def write_uint32(self, value) -> None:
        self.data.extend(struct.pack("<I", value))

    def write_string16(self, s) -> None:
        """
        Writes a String16:
        - Length: uint32 (Number of CHARACTERS)
        - Data: UTF-16 LE bytes
        - Padding: Align to 4 bytes
        """
        encoded = s.encode("utf-16-le")
        char_count = len(encoded) // 2
        self.write_uint32(char_count)
        self.data.extend(encoded)

        # Padding
        padding = (4 - (len(encoded) % 4)) % 4
        if padding > 0:
            self.data.extend(b"\x00" * padding)

    def get_payload(self) -> bytes:
        return bytes(self.data)
