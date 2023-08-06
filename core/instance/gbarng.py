"""GBA RNG Instance"""

from enum import IntEnum
import logging
import dearpygui.dearpygui as dpg
from numba_pokemon_prngs.data import SPECIES_EN

from ..hook.mgba_hook import MGBAHook
from ..util import lcrng_distance, load_sprite
from ..pkm.pk3 import PK3

class GBA:
    """GBA RNG Instance"""

    # TODO: support other gba emus?
    KEY_WORD = "mgba"

    class GameVersion(IntEnum):
        """Gen 3 game version"""
        RUBY = ord("V")
        SAPPHIRE = ord("P")
        FIRERED = ord("R")
        LEAFGREEN = ord("G")
        EMERALD = ord("E")

    RSE = (GameVersion.RUBY, GameVersion.SAPPHIRE, GameVersion.EMERALD)
    RS = (GameVersion.RUBY, GameVersion.SAPPHIRE)

    class GameLanguage(IntEnum):
        """Gen 3 game langauge"""
        EUR = 0
        USA = ord("E")
        JPN = ord("J")

        @classmethod
        def _missing_(cls, _value):
            return cls.EUR

    def __init__(self, rom_file_path: str) -> None:
        with open(rom_file_path, "rb") as rom_file:
            self.rom_file_data = rom_file.read(0x100)
        self.game_version = self.GameVersion(self.rom_file_data[0xAE])
        self.game_language = self.GameLanguage(self.rom_file_data[0xAF])
        self.game_revision = self.rom_file_data[0xBC]
        logging.info(
            f"Detected {self.game_language.name} {self.game_version.name} rev-{self.game_revision}"
        )
        self.get_addresses()
        self.hook = MGBAHook()

    def get_windows(self):
        """Set up windows and get update functions"""
        return (
            self.rng_info_window(),
            self.trainer_info_window(),
            self.party_info_window(0),
            self.party_info_window(1),
            self.party_info_window(2),
            self.party_info_window(3),
            self.party_info_window(4),
            self.party_info_window(5),
            self.wild_info_window(),
        )

    def get_addresses(self):
        """Get ram addresses based on game and language"""

        match self.game_version:
            case self.GameVersion.RUBY | self.GameVersion.SAPPHIRE:
                # TODO: further initial seed detection
                self.initial_seed = 0x5A0
                self.initial_seed_addr = None
                # TODO: add sav2 address when its needed
                self.sav2_addr = None
                match self.game_language:
                    case self.GameLanguage.JPN:
                        self.current_seed_addr = 0x03004748
                        self.party_addr = 0x03004290
                        self.wild_addr = 0x030044F0
                        self.id_addr = 0x02024C0E
                        self.vframe_addr = 0x03001790
                    case self.GameLanguage.USA:
                        self.current_seed_addr = 0x03004818
                        self.party_addr = 0x03004360
                        self.wild_addr = 0x030045C0
                        self.id_addr = 0x02024EAE
                        self.vframe_addr = 0x03001790
                    case self.GameLanguage.EUR:
                        self.current_seed_addr = 0x03004828
                        self.party_addr = 0x03004370
                        self.wild_addr = 0x030045D0
                        self.id_addr = 0x02024EAE
                        self.vframe_addr = 0x03001790
            case self.GameVersion.FIRERED | self.GameVersion.LEAFGREEN:
                self.initial_seed = 0
                self.initial_seed_addr = 0x02020000
                self.id_addr = None
                self.vframe_addr = None
                match self.game_language:
                    case self.GameLanguage.JPN:
                        if self.game_revision == 1:
                            self.current_seed_addr = 0x03004FA0
                            self.sav2_addr = 0x03004FAC
                        else:
                            self.current_seed_addr = 0x03005040
                            self.sav2_addr = 0x0300504C
                        self.party_addr = 0x020241E4
                        self.wild_addr = 0x02023F8C
                    case self.GameLanguage.USA:
                        self.current_seed_addr = 0x03005000
                        self.sav2_addr = 0x0300500C
                        self.party_addr = 0x02024284
                        self.wild_addr = 0x0202402C
                    case self.GameLanguage.EUR:
                        self.current_seed_addr = 0x03004F50
                        self.sav2_addr = 0x03004F5C
                        self.party_addr = 0x02024284
                        self.wild_addr = 0x0202402C
            case self.GameVersion.EMERALD:
                self.initial_seed = 0
                self.initial_seed_addr = 0x02020000
                self.id_addr = None
                match self.game_language:
                    case self.GameLanguage.JPN:
                        self.current_seed_addr = 0x03005AE0
                        self.party_addr = 0x02024190
                        self.wild_addr = 0x020243E8
                        self.sav2_addr = 0x03005AF0
                        self.vframe_addr = 0x03002384
                    case self.GameLanguage.USA | self.GameLanguage.EUR:
                        self.current_seed_addr = 0x03005D80
                        self.party_addr = 0x020244EC
                        self.wild_addr = 0x02024744
                        self.sav2_addr = 0x03005D90
                        self.vframe_addr = 0x030022E4

    def rng_info_window(self):
        """RNG seed info"""

        def detect_tid_seed():
            self.initial_seed = self.hook.read_uint(self.initial_seed_addr, 2)

        with dpg.window(label="RNG Info", width=240, height=150, no_close=True, pos=[1, 100 + 25]):
            if self.game_version in self.RSE:
                detect_tid_seed = dpg.add_button(label="Detect TID Seed", callback=detect_tid_seed)
            initial_seed_label = dpg.add_text("Initial Seed:")
            current_seed_label = dpg.add_text("Current Seed:")
            current_advance_label = dpg.add_text("Current Advance:")
            if self.game_version in self.RSE:
                painting_timer_label = dpg.add_text("Painting Timer:")

        def update():
            current_seed = self.hook.read_uint(self.current_seed_addr, 4)
            if self.game_version not in self.RSE:
                self.initial_seed = self.hook.read_uint(self.initial_seed_addr, 2)
            if self.vframe_addr is not None:
                vframe = self.hook.read_uint(self.vframe_addr, 4)
                # only 2 bytes used for reseeding
                painting_timer = vframe & 0xFFFF
                dpg.set_value(painting_timer_label, f"Painting Timer: {painting_timer:04X}")

                # vframe == 0 only happens on game restart or 32 bit overflow (lol)
                if vframe == 0 and self.game_version in self.RS:
                    self.initial_seed = self.hook.read_uint(self.current_seed_addr, 4)
                # painting_timer == current_seed on painting reseed or rare false positive
                if painting_timer == current_seed:
                    self.initial_seed = self.hook.read_uint(self.current_seed_addr, 4)
            current_advance = lcrng_distance(self.initial_seed, current_seed)
            dpg.set_value(initial_seed_label, f"Initial Seed: {self.initial_seed:08X}")
            dpg.set_value(current_seed_label, f"Current Seed: {current_seed:08X}")
            dpg.set_value(current_advance_label, f"Current Advance: {current_advance}")

        return update

    def pokemon_info_window(self, address: int, title: str, pos: list[int, int] = None):
        """Pokemon summary info"""

        with dpg.window(label=title, width=240, pos=pos or [], no_close=True):
            species_image = dpg.add_image(load_sprite(0, 0, False))
            species_label = dpg.add_text("Egg")
            pid_label = dpg.add_text("PID:")
            iv_label = dpg.add_text("IVs:")

        def update():
            pk3 = PK3(self.hook.read_bytes(address, 0x50))
            dpg.configure_item(species_image, texture_tag=load_sprite(pk3.species, 0, pk3.shiny))
            dpg.set_value(species_label, SPECIES_EN[pk3.species])
            dpg.set_value(pid_label, f"PID: {pk3.pid:08X}")
            dpg.set_value(iv_label, f"IVs: {'/'.join(map(str, pk3.ivs))}")

        return update

    def party_info_window(self, party_slot: int):
        """Party pokemon info"""
        return self.pokemon_info_window(
            self.party_addr + party_slot * 0x64,
            f"Party {party_slot + 1}",
            [800 - (240 * (2 - (party_slot // 3))), 160 * (party_slot % 3)]
        )

    def wild_info_window(self):
        """Wild pokemon info"""
        return self.pokemon_info_window(
            self.wild_addr,
            "Wild",
            [1, 201 + 25 + 25 + 25]
        )

    def trainer_info_window(self):
        """Trainer info"""

        with dpg.window(label="Trainer Info", width=240, no_close=True, pos=[1, 362 + 25 + 25 + 25]):
            tid_sid_label = dpg.add_text("TID/SID:")

        def update():
            id_addr = self.id_addr
            if id_addr is None:
                id_addr = self.hook.read_uint(self.sav2_addr, 4) + 0xA 
            tid, sid = self.hook.read_uint(id_addr, 2), self.hook.read_uint(id_addr + 2, 2)
            dpg.set_value(tid_sid_label, f"TID/SID: {tid}/{sid}")

        return update
