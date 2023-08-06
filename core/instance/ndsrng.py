"""GBA RNG Instance"""

from enum import IntEnum
import logging
import dearpygui.dearpygui as dpg
from numba_pokemon_prngs.data import SPECIES_EN

from ..hook.melonds_hook import MelonDSHook
from ..util import lcrng_distance, load_sprite
# from ..pkm.pk3 import PK3

class NDS:
    """NDS RNG Instance"""

    # TODO: support other nds emus?
    KEY_WORD = "melonds"

    def __init__(self, rom_file_path: str) -> None:
        with open(rom_file_path, "rb") as rom_file:
            self.rom_file_data = rom_file.read(0x100)
        # self.game_version = self.GameVersion(self.rom_file_data[0xAE])
        # self.game_language = self.GameLanguage(self.rom_file_data[0xAF])
        # self.game_revision = self.rom_file_data[0xBC]
        # logging.info(
        #     f"Detected {self.game_language.name} {self.game_version.name} rev-{self.game_revision}"
        # )
        self.get_addresses()
        self.hook = MelonDSHook()

    def get_windows(self):
        """Set up windows and get update functions"""
        return (
            self.rng_info_window(),
            # self.trainer_info_window(),
            # self.party_info_window(0),
            # self.party_info_window(1),
            # self.party_info_window(2),
            # self.party_info_window(3),
            # self.party_info_window(4),
            # self.party_info_window(5),
            # self.wild_info_window(),
        )

    def get_addresses(self):
        """Get ram addresses based on game and language"""
        self.current_seed_addr = 0x021D0AE8 + 0xAC0

        # match self.game_version:

    def rng_info_window(self):
        """RNG seed info"""

        with dpg.window(label="RNG Info", width=240, height=150, no_close=True, pos=[1, 100 + 25]):
            # initial_seed_label = dpg.add_text("Initial Seed:")
            current_seed_label = dpg.add_text("Current Seed:")
            # current_advance_label = dpg.add_text("Current Advance:")

        def update():
            current_seed = self.hook.read_uint(self.current_seed_addr, 4)
            # self.initial_seed = self.hook.read_uint(self.initial_seed_addr, 2)
            # current_advance = lcrng_distance(self.initial_seed, current_seed)
            # dpg.set_value(initial_seed_label, f"Initial Seed: {self.initial_seed:08X}")
            dpg.set_value(current_seed_label, f"Current Seed: {current_seed:08X}")
            # dpg.set_value(current_advance_label, f"Current Advance: {current_advance}")

        return update

    def pokemon_info_window(self, address: int, title: str, pos: list[int, int] = None):
        """Pokemon summary info"""

        # with dpg.window(label=title, width=240, pos=pos or [], no_close=True):
        #     species_image = dpg.add_image(load_sprite(0, 0, False))
        #     species_label = dpg.add_text("Egg")
        #     pid_label = dpg.add_text("PID:")
        #     iv_label = dpg.add_text("IVs:")

        # def update():
        #     pk3 = PK3(self.hook.read_bytes(address, 0x50))
        #     dpg.configure_item(species_image, texture_tag=load_sprite(pk3.species, 0, pk3.shiny))
        #     dpg.set_value(species_label, SPECIES_EN[pk3.species])
        #     dpg.set_value(pid_label, f"PID: {pk3.pid:08X}")
        #     dpg.set_value(iv_label, f"IVs: {'/'.join(map(str, pk3.ivs))}")

        # return update

    def party_info_window(self, party_slot: int):
        """Party pokemon info"""
        # return self.pokemon_info_window(
        #     self.party_addr + party_slot * 0x64,
        #     f"Party {party_slot + 1}",
        #     [800 - (240 * (2 - (party_slot // 3))), 160 * (party_slot % 3)]
        # )

    def wild_info_window(self):
        """Wild pokemon info"""
        # return self.pokemon_info_window(
        #     self.wild_addr,
        #     "Wild",
        #     [1, 201 + 25 + 25 + 25]
        # )

    def trainer_info_window(self):
        """Trainer info"""

        # with dpg.window(label="Trainer Info", width=240, no_close=True, pos=[1, 362 + 25 + 25 + 25]):
        #     tid_sid_label = dpg.add_text("TID/SID:")

        # def update():
        #     id_addr = self.id_addr
        #     if id_addr is None:
        #         id_addr = self.hook.read_uint(self.sav2_addr, 4) + 0xA 
        #     tid, sid = self.hook.read_uint(id_addr, 2), self.hook.read_uint(id_addr + 2, 2)
        #     dpg.set_value(tid_sid_label, f"TID/SID: {tid}/{sid}")

        # return update
