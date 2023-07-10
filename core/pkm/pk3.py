"""Gen 3 pokemon format"""

from ..util import SPECIES_MAP

BLOCK_POSITION = [
    0, 1, 2, 3,
    0, 1, 3, 2,
    0, 2, 1, 3,
    0, 3, 1, 2,
    0, 2, 3, 1,
    0, 3, 2, 1,
    1, 0, 2, 3,
    1, 0, 3, 2,
    2, 0, 1, 3,
    3, 0, 1, 2,
    2, 0, 3, 1,
    3, 0, 2, 1,
    1, 2, 0, 3,
    1, 3, 0, 2,
    2, 1, 0, 3,
    3, 1, 0, 2,
    2, 3, 0, 1,
    3, 2, 0, 1,
    1, 2, 3, 0,
    1, 3, 2, 0,
    2, 1, 3, 0,
    3, 1, 2, 0,
    2, 3, 1, 0,
    3, 2, 1, 0,
    0, 1, 2, 3,
    0, 1, 3, 2,
    0, 2, 1, 3,
    0, 3, 1, 2,
    0, 2, 3, 1,
    0, 3, 2, 1,
    1, 0, 2, 3,
    1, 0, 3, 2,
]


class PK3:
    """Gen 3 pokemon format"""
    def __init__(self, buf: bytearray) -> None:
        self.buf = bytearray(buf)
        self.decrypt()

    def read_uint(self, offset: int, length: int) -> int:
        """Read unsigned integer from offset"""
        return int.from_bytes(self.buf[offset:offset + length], 'little')

    def write_uint(self, offset: int, value: int, length: int):
        """Write unsigned integer to offset"""
        self.buf[offset:offset + length] = int.to_bytes(value, length, 'little')

    def decrypt(self) -> None:
        """Decrypt EK3"""
        pid = self.read_uint(0, 4)
        otid = self.read_uint(4, 4)
        key = pid ^ otid
        for i in range(0x20, 0x50, 4):
            self.write_uint(i, self.read_uint(i, 4) ^ key, 4)
        self.shuffle()

    def shuffle(self) -> None:
        """Shuffle blocks of a PK3"""
        data_copy = self.buf.copy()
        index = (self.read_uint(0, 4) % 24) * 4
        for block in range(4):
            ofs = BLOCK_POSITION[index + block]
            data_copy[0x20 + (12 * block):0x20 + (12 * (block + 1))] = \
                self.buf[0x20 + (12 * ofs):0x20 + (12 * (ofs + 1))]
        self.buf = data_copy

    @property
    def pid(self) -> int:
        """Personality value"""
        return self.read_uint(0, 4)

    @property
    def otid(self) -> int:
        """32-bit IDs"""
        return self.read_uint(4, 4)

    @property
    def psv(self) -> int:
        """Pokemon shiny value"""
        temp = self.pid ^ self.otid
        return (temp ^ (temp >> 16)) & 0xFFFF

    @property
    def shiny(self) -> bool:
        """Pokemon shininess"""
        return self.psv < 8

    @property
    def iv32(self) -> int:
        """32 bit individual values"""
        return self.read_uint(0x48, 4)

    @property
    def ivs(self) -> tuple[int, int, int, int, int, int]:
        """Individial values"""
        iv32 = self.iv32
        return (
            iv32 & 0x1F,
            (iv32 >> 5) & 0x1F,
            (iv32 >> 10) & 0x1F,
            (iv32 >> 20) & 0x1F,
            (iv32 >> 25) & 0x1F,
            (iv32 >> 15) & 0x1F,
        )

    @property
    def species(self) -> int:
        """Species index"""
        try:
            return SPECIES_MAP[self.read_uint(0x20, 2)]
        except IndexError:
            return 0
