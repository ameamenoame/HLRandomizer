from hldlib.hldlevel import HLDLevel
from typing import Iterable
from enum import Enum
import os
import platform

class ItemPlacementRestriction(str, Enum):
    def __str__(self):
        return self.value
    NONE = "Don't randomize" # Module placements unchanged
    FREE = "Free (252 checks)" # Randomize module placements across every possible item - bits, outfits, keys, weapons, tablets (except for enemy drops)
    KEY_ITEMS = "Key items (63 checks)" # Module can only appear at key item places - outfits, keys, weapons
    KEY_ITEMS_EXTENDED = "Key items + tablets (82 checks)" 
    MODULES_EXTENDED = "Modules Extended (39 checks)" # Only place where modules would be plus special key / outfit checks
    # KEY_ITEMS_EXTENDED = "Key items extended" # Module can only appear at key items plus some specially designated bits that are hard to get to

class ModuleDoorOptions(str, Enum):
    def __str__(self):
        return self.value
    NONE = "Don't randomize"
    MIX = "Mix"
    DISABLED = "Disabled"

class ModuleCount(int, Enum):
    def __str__(self):
        return str(self.value)
    MINIMUM = 16
    ALL = 32

class KeyCount(int, Enum):
    def __str__(self):
        return str(self.value)
    MINIMUM = 1
    ALL = 16

class HLDBasics:
    @staticmethod
    def find_path() -> str:
        for dir_path, dir_names, file_names in os.walk("."):
            for file_name in file_names:
                if file_name.lower() == "hlddir.txt":
                    with open(os.path.join(dir_path, file_name)) as hld_dir_file:
                        return hld_dir_file.readline().rstrip()
        raise ValueError("No hldDir.txt found.")

    @staticmethod
    def find_save_path() -> str:
        for dir_path, dir_names, file_names in os.walk("."):
            for file_name in file_names:
                if file_name.lower() == "hlddir.txt":
                    with open(os.path.join(dir_path, file_name)) as hld_dir_file:
                        hld_dir_file.readline() # Skip first line
                        return hld_dir_file.readline().rstrip()
        raise ValueError("No hldDir.txt found.")

    @staticmethod
    def get_levels(path: str, dirs: Iterable[str]):
        for dir_ in dirs:
            for level in [level for level in os.listdir(os.path.join(path, dir_)) if level.endswith(".lvl")]:
                filepath: str = os.path.join(path, dir_, level)
                yield filepath, dir_, level

    class Counter:
        def __init__(self, val: int = 10000):
            self._val = val

        def use(self) -> int:
            self._val += 1
            return self._val

    @staticmethod
    def omega_load(path: str):
        loaded: list[HLDLevel] = []
        for level_path, dir_, level_name in HLDBasics.get_levels(path, HLDBasics.DIRS):
            lvl = HLDLevel.from_file(level_path)
            loaded.append(lvl)
        return loaded

    DIRS = (
        "North",
        "East",
        "West",
        "South",
        "Central",
        "Intro",
        "Abyss",
    )
if platform.system() in ('Linux', 'Darwin'):
    HLDBasics.DIRS = tuple(dir_.lower() for dir_ in HLDBasics.DIRS)
