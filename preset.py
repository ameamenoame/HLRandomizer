from enum import Enum
from hldlib import HLDObj, HLDLevel, HLDType, HLDBasics
from hldlib.hldbasics import ModuleCount
from save_edit import *


DEFAULT_SAVE_EDIT_NUMBER: int = 3


class PresetType(str, Enum):
    NONE = "None"
    SEEKER = "Seeker"
    NIMBLE = "Nimble"
    VAGABOND = "Vagabond"
    SPEEDRUN = "Speedrun"
    GUNSLINGER = "Gunslinger"
    BITBOUND = "Bitbound"
    NAKED = "Naked"


class Preset:
    save_edit_number:int = DEFAULT_SAVE_EDIT_NUMBER
    real_levels = None
    description = "No preset selected"


    def __init__(self, real_levels, edit_number: int = DEFAULT_SAVE_EDIT_NUMBER):
        self.save_edit_number = edit_number
        self.real_levels = real_levels

    @classmethod
    def execute_changes(cls):
        return

    @classmethod
    def set_save_data_field(cls, field_name: str, val):
        metadata = SaveMetadata(None, HLDBasics.find_save_path())
        savedata_map = savedata_load(metadata, [0, cls.save_edit_number])
        savedata_set(savedata_map, [0, field_name, val])
        savedata_write(savedata_map, metadata, [0, cls.save_edit_number])

    @staticmethod
    def get_preset_from_name(name: PresetType):
        if name == PresetType.NIMBLE:
            return PresetNimble
        elif name == PresetType.VAGABOND:
            return PresetVagabond
        elif name == PresetType.SPEEDRUN:
            return PresetSpeedrun
        elif name == PresetType.GUNSLINGER:
            return PresetGunslinger
        elif name == PresetType.SEEKER:
            return PresetSeeker
        elif name == PresetType.BITBOUND:
            return PresetBitbound
        elif name == PresetType.NAKED:
            return PresetNaked
        return Preset

    @classmethod
    def set_options(cls, options): # Passes the entire tkinter window object. Should rework presets to be based on config files instead
        options.random_shops.set(False)
        options.random_pistol.set(False)
        options.random_enemies.set(False)
        options.module_count_optionsvar.set(ModuleCount.MINIMUM)
  
class PresetNimble(Preset):
    description = "Movement-focused. Starts with the effects of purple + yellow + pink drifter cloaks (doubled stamina, increased movement speed, faster stamina recharge) and chain dash."

    @classmethod
    def execute_changes(cls):
        # Set cape  for  player
        # Indexes here are 1 less than what it would be in level files
        print("Setting cape")
        cls.set_save_data_field("cape", 10)
        cls.set_save_data_field("compShell", 7)
        cls.set_save_data_field("sword", 4)
        cls.set_save_data_field("cCapes", "0+10+4+7+")
        cls.set_save_data_field("cShells", "0+10+4+7+")
        cls.set_save_data_field("cSwords", "0+10+4+7+")
        cls.set_save_data_field("skill", "4+")
        cls.set_save_data_field("gameName", "NIMBLE")

    
class PresetVagabond(Preset):
    description = "Sword-focused fighting. Starts with all sword upgrades and the effects of blue + fuchsia + pink drifter cloaks (faster attacks, more ammo from sword slashes, faster stamina recharge)"

    @classmethod
    def execute_changes(cls):
        cls.set_save_data_field("cape", 1)
        cls.set_save_data_field("compShell", 2)
        cls.set_save_data_field("sword", 7)
        cls.set_save_data_field("cCapes", "0+1+2+7+")
        cls.set_save_data_field("cShells", "0+1+2+7+")
        cls.set_save_data_field("cSwords", "0+1+2+7+")
        cls.set_save_data_field("skill", "1+2+3+")
        cls.set_save_data_field("gameName", "Vagabond")

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.randon_enemies.set(True)

class PresetGunslinger(Preset):
    description = "Gun-focused fighting. Starts with all guns, grenade, and the effects of fuchsia + yellow + orange cloaks (more ammo from sword slashes, faster movement, faster grenade recharge) "

    @classmethod
    def execute_changes(cls):
        cls.set_save_data_field("cape", 2)
        cls.set_save_data_field("compShell", 4)
        cls.set_save_data_field("sword", 5)

        cls.set_save_data_field("cCapes", "0+2+4+5+")
        cls.set_save_data_field("cShells", "0+2+4+5+")
        cls.set_save_data_field("cSwords", "0+2+4+5+")
  

        cls.set_save_data_field("sc", "23+41+43+1+21+2+")
        cls.set_save_data_field("scUp", "23+41+43+1+21+2+")
        cls.set_save_data_field("specialUp", 2)
        cls.set_save_data_field("gameName", "Gunslinger")

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.randon_enemies.set(True)

    
class PresetSpeedrun(Preset):
    description = "Speedrun-focused. Starts with chain dashing and the effects of white + purple + pink cloaks."

    @classmethod
    def execute_changes(cls):
        cls.set_save_data_field("cape", 3)
        cls.set_save_data_field("compShell", 10)
        cls.set_save_data_field("sword", 7)

        cls.set_save_data_field("cCapes", "0+3+10+7+")
        cls.set_save_data_field("cShells", "0+3+10+7+")
        cls.set_save_data_field("cSwords", "0+3+10+7+")
  
        cls.set_save_data_field("skill", "4+")
        cls.set_save_data_field("gameName", "Speedrun")

  
class PresetBitbound(Preset):
    description = "Starts with 64 gearbits (16 complete bits) but the shops are randomized. Yellow + white + green-blue cloaks."

    @classmethod
    def execute_changes(cls):
        cls.set_save_data_field("cape", 4)
        cls.set_save_data_field("compShell", 3)
        cls.set_save_data_field("sword", 6)

        cls.set_save_data_field("cCapes", "0+4+3+6+")
        cls.set_save_data_field("cShells", "0+4+3+6+")
        cls.set_save_data_field("cSwords", "0+4+3+6+")

        cls.set_save_data_field("gear", 64)

        cls.set_save_data_field("gameName", "Bitbound")

class PresetSeeker(Preset):
    description = "Recommended for beginners to the randomizer. Starts with the sky blue companion that helps track secrets and yellow + ochre cloak effects (faster movement and +1 health). Note: Only works on newer patches."

    @classmethod
    def execute_changes(cls):
        cls.set_save_data_field("cape", 9)
        cls.set_save_data_field("compShell", 12)
        cls.set_save_data_field("sword", 4)

        cls.set_save_data_field("cCapes", "0+9+")
        cls.set_save_data_field("cShells", "0+12+")
        cls.set_save_data_field("cSwords", "0+4+")

        cls.set_save_data_field("gameName", "Seeker")

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.random_enemies.set(False)
        options.module_count_optionsvar.set(ModuleCount.ALL)


class PresetNaked(Preset):
    description = "Starts with nothing. Not even pistol. Shops are randomized. Only works for NG."

    @classmethod
    def execute_changes(cls):
        cls.set_save_data_field("gameName", "Naked")
        cls.set_save_data_field("sc", "")
        cls.set_save_data_field("scK", "")
        cls.set_save_data_field("scUp", "")

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.random_shops.set(True)
        options.random_pistol.set(True)
