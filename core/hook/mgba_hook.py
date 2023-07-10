"""Class for hooking into mGBA"""

import logging
from .hook import Hook

class MGBAHook(Hook):
    """Class for hooking into mGBA"""

    def __init__(self, pid: int = None, file_name: str = None, *args, **kwargs) -> None:
        self.wram_base = None
        self.iram_base = None
        self.file_name = file_name
        self.game_data = None
        super().__init__(pid)

    def hook(self, pid: int, file_name = None, *args, **kwargs) -> None:
        self.file_name = file_name or self.file_name

        with open(file_name, "rb") as game_rom:
            self.game_data = game_rom.read(0x100)

        return super().hook(pid, *args, **kwargs)

    def detect_memory_bases(self) -> None:
        for minimum, maximum in self.process.list_mapped_regions():
            if maximum - minimum == 0x48000:
                self.wram_base = minimum
                self.iram_base = minimum + 0x40000
            elif maximum - minimum == 0x60000:
                self.wram_base = minimum + 0x18000
                self.iram_base = minimum + 0x58000
        if None in (self.wram_base, self.iram_base):
            logging.error("Error: Memory regions not found.")
        else:
            logging.info("Hooked successfully")
            self.is_initialized = True

    def convert_address(self, address: int) -> int:
        """Convert address to mem_edit address"""
        if 0x2000000 <= address < 0x3000000:
            # WRAM
            return address - 0x2000000 + self.wram_base
        if 0x3000000 <= address < 0x4000000:
            # IRAM
            return address - 0x3000000 + self.iram_base
        # if 0x8000000 <= address < 0xA000000:
        #     # GAME
        #     return address - 0x8000000 + self.game_base

        raise NotImplementedError(f"Address {address:X} out of range")

    def read_bytes(self, address: int, length: int) -> bytes:
        if 0x8000000 <= address < 0xA000000:
            # game rom address
            ofs = address - 0x8000000
            return self.game_data[ofs:ofs+length]
        return super().read_bytes(address, length)
