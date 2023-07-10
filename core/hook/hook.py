"""Abstract class for hooking into a process"""

from abc import abstractmethod
import contextlib
import logging
import ctypes
import struct
import mem_edit

class Hook:
    """Base class for hooking into a process"""

    def __init__(self, pid: int = None) -> None:
        self.process = None
        self.is_initialized = False
        if pid is not None:
            self.hook(pid)

    def hook(self, pid: int) -> None:
        """Hook to the specified pid"""
        if self.process is not None:
            self.is_initialized = False
            self.process.close()
        self.process = mem_edit.Process(pid)

        self.detect_memory_bases()

    @abstractmethod
    def detect_memory_bases(self) -> None:
        """Detect base addresses for memory sections"""

    @abstractmethod
    def convert_address(self, address: int) -> int:
        """Convert address to mem_edit address"""

    def read_bytes(self, address: int, length: int) -> bytes:
        """Read bytes at specified address"""
        return_buffer = (ctypes.c_ubyte * length)()
        return bytes(
            self.process.read_memory(
                self.convert_address(address),
                return_buffer
            )
        )

    def read_struct(self, address: int, schema: str):
        """Read struct at address"""
        return struct.unpack(
            schema,
            self.read_bytes(address, struct.calcsize(schema))
        )

    def read_ctype(self, address: int, ctype):
        """Read ctype type at address"""
        # TODO: validation
        return self.process.read_memory(self.convert_address(address), ctype())

    def read_int(self, address: int, length: int) -> int:
        """Read integer at specified address"""
        return int.from_bytes(
            self.read_bytes(address, length),
            'little',
            signed=True
        )

    def read_uint(self, address: int, length: int) -> int:
        """Read unsigned integer at specified address"""
        return int.from_bytes(
            self.read_bytes(address, length),
            'little',
            signed=False
        )

    def __del__(self) -> None:
        if self.process is not None:
            with contextlib.suppress(ChildProcessError):
                self.process.close()
