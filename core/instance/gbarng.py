"""GBA RNG Instance"""

from enum import IntEnum
from functools import partial
import dearpygui.dearpygui as dpg
from numba_pokemon_prngs.data import SPECIES_EN

from ..hook.mgba_hook import MGBAHook
from ..util import lcrng_distance, load_sprite
from ..pkm.pk3 import PK3

KEY_WORD = "mgba"

hook = MGBAHook()

class GameVersion(IntEnum):
    """Gen 3 game version"""
    RUBY = ord("V")
    SAPPHIRE = ord("P")
    FIRERED = ord("R")
    LEAFGREEN = ord("G")
    EMERALD = ord("E")

class GameLanguage(IntEnum):
    """Gen 3 game langauge"""
    EUR = 0
    USA = ord("E")
    JPN = ord("J")

    @classmethod
    def _missing_(cls, _value):
        return cls.EUR

def rng_info_window():
    """RNG seed info"""

    with dpg.window(label="RNG Info", width=240, no_close=True, pos=[1, 100 + 25]):
        initial_seed_label = dpg.add_text("Initial Seed:")
        current_seed_label = dpg.add_text("Current Seed:")
        current_advance_label = dpg.add_text("Current Advance:")

    def update():
        match GameVersion(hook.read_uint(0x080000AE, 1)):
            case GameVersion.RUBY | GameVersion.SAPPHIRE:
                # TODO: further init seed detection
                initial_seed = 0x5A0
                INITIAL_SEED_ADDR = None
                match GameLanguage(hook.read_uint(0x080000AF, 1)):
                    # JPN
                    case GameLanguage.JPN:
                        CURRENT_SEED_ADDR = 0x03004748
                    # USA
                    case GameLanguage.USA:
                        CURRENT_SEED_ADDR = 0x03004818
                    # EUR
                    case _:
                        CURRENT_SEED_ADDR = 0x03004828
            case GameVersion.FIRERED | GameVersion.LEAFGREEN:
                INITIAL_SEED_ADDR = 0x02020000
                match GameLanguage(hook.read_uint(0x080000AF, 1)):
                    # JPN
                    case GameLanguage.JPN:
                        # game revision
                        if hook.read_uint(0x080000BC, 1) == 1:
                            CURRENT_SEED_ADDR = 0x03004FA0
                        else:
                            CURRENT_SEED_ADDR = 0x03005040
                    # USA
                    case GameLanguage.USA:
                        CURRENT_SEED_ADDR = 0x03005000
                    # EUR
                    case _:
                        CURRENT_SEED_ADDR = 0x03004F50
            case GameVersion.EMERALD:
                # TODO: further init seed detection
                initial_seed = 0
                INITIAL_SEED_ADDR = None

                match GameLanguage(hook.read_uint(0x080000AF, 1)):
                    # JPN
                    case GameLanguage.JPN:
                        CURRENT_SEED_ADDR = 0x03005AE0
                    # EUR/USA
                    case _:
                        CURRENT_SEED_ADDR = 0x03005D80
        if INITIAL_SEED_ADDR is not None:
            initial_seed = hook.read_uint(INITIAL_SEED_ADDR, 2)
        current_seed = hook.read_uint(CURRENT_SEED_ADDR, 4)
        current_advance = lcrng_distance(initial_seed, current_seed)
        dpg.set_value(initial_seed_label, f"Initial Seed: {initial_seed:04X}")
        dpg.set_value(current_seed_label, f"Current Seed: {current_seed:08X}")
        dpg.set_value(current_advance_label, f"Current Advance: {current_advance}")

    return update

def pokemon_info_window(address_function, title: str, pos: list[int, int] = None):
    """Pokemon summary info"""

    with dpg.window(label=title, width=240, pos=pos or [], no_close=True):
        species_texture = load_sprite(0, 0, False)
        species_image = dpg.add_image(species_texture)
        species_label = dpg.add_text("Egg")
        pid_label = dpg.add_text("PID:")
        iv_label = dpg.add_text("IVs:")

    def update():
        addr = address_function()
        pk3 = PK3(hook.read_bytes(addr, 0x50))
        load_sprite(pk3.species, 0, pk3.shiny, species_texture)
        dpg.set_value(species_label, SPECIES_EN[pk3.species])
        dpg.set_value(pid_label, f"PID: {pk3.pid:08X}")
        dpg.set_value(iv_label, f"IVs: {'/'.join(map(str, pk3.ivs))}")

    return update

def get_party_addr(party_slot: int):
    """Get the address to the pokemon in the specified party slot"""
    match GameVersion(hook.read_uint(0x080000AE, 1)):
        case GameVersion.RUBY | GameVersion.SAPPHIRE:
            match GameLanguage(hook.read_uint(0x080000AF, 1)):
                # JPN
                case GameLanguage.JPN:
                    return 0x03004290 + (party_slot * 0x64)
                # USA
                case GameLanguage.USA:
                    return 0x03004360 + (party_slot * 0x64)
                # EUR
                case _:
                    return 0x03004370 + (party_slot * 0x64)
        case GameVersion.FIRERED | GameVersion.LEAFGREEN:
            match GameLanguage(hook.read_uint(0x080000AF, 1)):
                # JPN
                case GameLanguage.JPN:
                    return 0x020241E4 + (party_slot * 0x64)
                # USA
                case GameLanguage.USA:
                    return 0x02024284 + (party_slot * 0x64)
                # EUR
                case _:
                    return 0x02024284 + (party_slot * 0x64)
        case GameVersion.EMERALD:
            match GameLanguage(hook.read_uint(0x080000AF, 1)):
                # JPN
                case GameLanguage.JPN:
                    return 0x02024190 + (party_slot * 0x64)
                # USA/EUR
                case _:
                    return 0x020244EC + (party_slot * 0x64)

def get_wild_addr():
    """Get the address to the wild pokemon"""
    match GameVersion(hook.read_uint(0x080000AE, 1)):
        case GameVersion.RUBY | GameVersion.SAPPHIRE:
            match GameLanguage(hook.read_uint(0x080000AF, 1)):
                # JPN
                case GameLanguage.JPN:
                    return 0x030044F0
                # USA
                case GameLanguage.USA:
                    return 0x030045C0
                # EUR
                case _:
                    return 0x030045D0
        case GameVersion.FIRERED | GameVersion.LEAFGREEN:
            match GameLanguage(hook.read_uint(0x080000AF, 1)):
                # JPN
                case GameLanguage.JPN:
                    return 0x02023F8C
                # USA/EUR
                case _:
                    return 0x0202402C
        case GameVersion.EMERALD:
            match GameLanguage(hook.read_uint(0x080000AF, 1)):
                # JPN
                case GameLanguage.JPN:
                    return 0x020243E8
                # USA/EUR
                case _:
                    return 0x02024744

def party_info_window(party_slot: int):
    """Party pokemon info"""
    return pokemon_info_window(
        partial(get_party_addr, party_slot),
        f"Party {party_slot + 1}",
        [800 - (240 * (2 - (party_slot // 3))), 160 * (party_slot % 3)]
    )

def wild_info_window():
    """Wild pokemon info"""
    return pokemon_info_window(
        get_wild_addr,
        "Wild",
        [1, 201 + 25]
    )

def trainer_info_window():
    """Trainer info"""

    with dpg.window(label="Trainer Info", width=240, no_close=True, pos=[1, 362 + 25]):
        tid_sid_label = dpg.add_text("TID/SID:")

    def update():
        match GameVersion(hook.read_uint(0x080000AE, 1)):
            case GameVersion.RUBY | GameVersion.SAPPHIRE:
                match GameLanguage(hook.read_uint(0x080000AF, 1)):
                    # JPN
                    case GameLanguage.JPN:
                        ID_ADDR = 0x02024C0E
                    # USA/EUR
                    case _:
                        ID_ADDR = 0x02024EAE
            case GameVersion.FIRERED | GameVersion.LEAFGREEN:
                match GameLanguage(hook.read_uint(0x080000AF, 1)):
                    # JPN
                    case GameLanguage.JPN:
                        # game revision
                        if hook.read_uint(0x080000BC, 1) == 1:
                            ID_ADDR = hook.read_uint(0x03004FAC, 4) + 0xA
                        else:
                            ID_ADDR = hook.read_uint(0x0300504C, 4) + 0xA
                    # USA
                    case GameLanguage.USA:
                        ID_ADDR = hook.read_uint(0x0300500C, 4) + 0xA
                    # EUR
                    case _:
                        ID_ADDR = hook.read_uint(0x03004F5C, 4) + 0xA
            case GameVersion.EMERALD:
                match GameLanguage(hook.read_uint(0x080000AF, 1)):
                    # JPN
                    case GameLanguage.JPN:
                        ID_ADDR = hook.read_uint(0x03005AF0, 4) + 0xA
                    # USA/EUR
                    case _:
                        ID_ADDR = hook.read_uint(0x03005D90, 4) + 0xA
        tid, sid = hook.read_uint(ID_ADDR, 2), hook.read_uint(ID_ADDR + 2, 2)
        dpg.set_value(tid_sid_label, f"TID/SID: {tid}/{sid}")

    return update

def get_windows():
    """Set up windows and get update functions"""
    return (
        rng_info_window(),
        trainer_info_window(),
        party_info_window(0),
        party_info_window(1),
        party_info_window(2),
        party_info_window(3),
        party_info_window(4),
        party_info_window(5),
        wild_info_window(),
    )
