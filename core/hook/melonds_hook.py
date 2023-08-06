"""Class for hooking into melonDS"""

import logging
from .hook import Hook
from ..exceptions import AddressOutOfRange

class MelonDSHook(Hook):
    """Class for hooking into melonDS"""

    def __init__(self, pid: int = None) -> None:
        self.main_ram_base = None
        self.game_data = None
        super().__init__(pid)

    def detect_memory_bases(self) -> None:
        for minimum, maximum in self.process.list_mapped_regions():
            if maximum - minimum == 0x10dc000:
                self.main_ram_base = minimum
        if None in (self.main_ram_base,):
            logging.error("Error: Memory regions not found.")
        else:
            logging.info("Hooked successfully")
            self.is_initialized = True

    def convert_address(self, address: int) -> int:
        """Convert address to mem_edit address"""
        if 0x2000000 <= address < 0x3000000:
            # Main Memory
            return address - 0x2000000 + self.main_ram_base

        raise AddressOutOfRange(f"Address {address:X} out of range")
