from enum import Enum
from tkinter import StringVar
from hldlib import HLDObj, HLDLevel, HLDType, HLDBasics
from hldlib.hldbasics import ItemPlacementRestriction, KeyCount, ModuleCount, ModuleDoorOptions, GoalType
from save_edit import *
import random


DEFAULT_SAVE_EDIT_NUMBER: int = 3


class PresetType(str, Enum):
    NONE = "None"
    STREAMLINED = "Streamlined"
    # NIMBLE = "Nimble"
    VAGABOND = "Vagabond"
    SPEEDRUN = "Nimble"
    GUNSLINGER = "Gunslinger"
    BITBOUND = "Bitbound"
    NAKED = "Naked"
    RANDOM_START = "Random start"
    BINGO = "Bingo"
    NO_LOGIC = "No logic"
    SEEKER = "Seeker"


class Preset:
    save_edit_number: int = DEFAULT_SAVE_EDIT_NUMBER
    real_levels = None
    description = "No preset selected"
    seed = "seed"

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
        if name == PresetType.VAGABOND:
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
        elif name == PresetType.RANDOM_START:
            return PresetRandomStart
        elif name == PresetType.BINGO:
            return PresetBingo
        elif name == PresetType.STREAMLINED:
            return PresetStreamlined
        elif name == PresetType.NO_LOGIC:
            return PresetNoLogic
        return Preset

    @classmethod
    def set_options(
        cls, options
    ):  # Passes the entire tkinter window object. Should rework presets to be based on config files instead
        options.random_shops.set(False)
        options.random_pistol.set(False)
        options.random_enemies.set(True)
        options.module_count_optionsvar.set(ModuleCount.ALL)
        options.limit_one_module_per_room.set(True)
        options.even_item_distribution.set(False)
        options.use_chain_logic.set(False)
        options.module_optionsvar.set(
            ItemPlacementRestriction.FREE
        )
        options.key_countvar.set(KeyCount.ALL)
        options.module_door_optionsvar.set(ModuleDoorOptions.MIX)
        options.no_logicvar.set(False)

    @classmethod 
    def random_outfit(cls):
        choices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        cape = random.choice(choices)
        sword = random.choice(choices)
        companion = random.choice(choices)

        # Speedrun preset stuff
        cls.set_save_data_field("cape", cape)
        cls.set_save_data_field("compShell", companion)
        cls.set_save_data_field("sword", sword)

        outfit_str = "0+%d+%d+%d+" % (cape, companion, sword)
        cls.set_save_data_field("cCapes", outfit_str)
        cls.set_save_data_field("cShells", outfit_str)
        cls.set_save_data_field("cSwords", outfit_str)

    @classmethod
    def random_skill(cls):
        skill_choice = random.choice(["skill", "grenade"])
        if skill_choice == "grenade":
            cls.set_save_data_field("specialUp", random.choice([1, 2]))
        else:
            cls.set_save_data_field("skill", "%d+" % random.choice([1, 2, 3, 4, 5, 6]))

    @classmethod
    def random_start(cls, no_logic: bool = False):
        room_choice = None
        x = None
        y = None
        keys = list(HLDBasics.room_names.keys())

        while not room_choice:
            c = random.choice(keys)
            if not no_logic:
                if "unused" in HLDBasics.room_names[c][1].lower() \
                    or HLDBasics.room_names[c][0].startswith("rm_in") \
                    or HLDBasics.room_names[c][0].startswith("rm_c_") \
                    or HLDBasics.room_names[c][0].startswith("rm_pax") \
                    or HLDBasics.room_names[c][0] in ["rm_carena", "rm_televatorshaft"] \
                    or c >= 220 \
                    or c in [132, 133, 134, 135, 183, 232, 123, 250, 86, 184]:
                    continue
            else:
                if "unused" in HLDBasics.room_names[c][1].lower() \
                    or HLDBasics.room_names[c][0].startswith("rm_in") \
                    or HLDBasics.room_names[c][0].startswith("rm_c_") \
                    or HLDBasics.room_names[c][0].startswith("rm_pax") \
                    or HLDBasics.room_names[c][0] in ["rm_carena", "rm_televatorshaft"]:
                    continue

            obj_list = cls.real_levels.find_by_name(
                HLDBasics.room_names[c][0]+".lvl"
            ).object_list
            doors = []
            for o in obj_list:
                if o.uid in [ 
                             5643,  # MoonCourtyard -> gapopening televator
                            7652,  # TowerSouth -> BGunPillars televator 
                            94304,  # EastLoop -> LoopLAB televator   
                            6897, # MoonCourtyard -> CliffCampfile door
                           ]:
                    continue
                if o.type in [HLDType.DOOR, HLDType.TELEVATOR]:
                    doors.append(o)
            if doors == []: continue
            door = random.choice(doors)
            x = door.x
            y = door.y
            offset_amount = 32
            if door.type == HLDType.DOOR:
                if door.attrs["ed"] == 90:
                    y -= offset_amount
                elif door.attrs["ed"] == 180:
                    x -= offset_amount
                elif door.attrs["ed"] == 270:
                    y += offset_amount
                else:
                    x += offset_amount
            else:
                # Spawn in the middle of the televator
                y -= 15
                x += 15
            room_choice = c
            print("Random start: " + HLDBasics.room_names[room_choice][0] + " - " + HLDBasics.room_names[room_choice][1])

        cls.set_save_data_field(
            "checkRoom",room_choice
        )

        cls.set_save_data_field("checkX", x)
        cls.set_save_data_field("checkY", y)

        cls.set_save_data_field("warp", "")
        cls.set_save_data_field("hasMap", 1)
        cls.set_save_data_field("cues", "-1383674+") # Remove the starting town square camera cue

        # Remove the warp blocks in town
        obj_list = cls.real_levels.find_by_name(
            HLDLevel.Names.RM_C_CENTRAL
        ).object_list
        for o in obj_list:
            if o.uid in [1270, 3911, 766]:
                obj_list.remove(o)
                break

        # cls.set_save_data_field("events",
        #     "336860+363992+-1054677+" # Open the path to vale from thinforest
        #                         )
        cls.set_save_data_field("events",
            "-1392839+"  # Skip the house map cutscene
        )
        cls.set_save_data_field("permaS",
            "-1052455=2>-1073029=2>" # Open up north main path arenas
                                )
        # Remove teleporter in brokenshallows
        obj_list = cls.real_levels.find_by_name(
            HLDLevel.Names.RM_IN_01_BROKENSHALLOWS
        ).object_list
        for o in obj_list:
            if o.type == HLDType.TELEPORTER:
                obj_list.remove(o)
                break




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
        cls.set_save_data_field("gameName", "Vagabond" + "_" + cls.seed)

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.random_enemies.set(True)


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
        cls.set_save_data_field("gameName", "Gunslinger" + "_" + cls.seed)

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.random_enemies.set(True)


class PresetSpeedrun(Preset):
    description = "Speedrun-focused. Starts with chain dashing and the effects of white + purple + pink cloaks. Activate all pillars to open the abyss elevator."

    @classmethod
    def execute_changes(cls):
        cls.set_save_data_field("cape", 3)
        cls.set_save_data_field("compShell", 10)
        cls.set_save_data_field("sword", 7)
        cls.set_save_data_field("cCapes", "0+3+10+7+")
        cls.set_save_data_field("cShells", "0+3+10+7+")
        cls.set_save_data_field("cSwords", "0+3+10+7+")
        cls.set_save_data_field("skill", "4+")
        cls.set_save_data_field("gameName", "Speedrun" + "_" + cls.seed)
        cls.random_start()
        cls.set_save_data_field("halluc", 99)

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.random_enemies.set(False)
        options.even_item_distribution.set(False)
        options.no_logicvar.set(False)
        options.random_pistol.set(True)
        options.random_shops.set(False)
        options.random_dungeon_entrances.set(True)
        options.use_chain_logic.set(False)
        options.module_optionsvar.set(
            ItemPlacementRestriction.MODULES_EXTENDED
        )
        options.limit_one_module_per_room.set(False)
        options.key_countvar.set(4)
        options.module_count_optionsvar.set(ModuleCount.MINIMUM)
        options.module_door_optionsvar.set(ModuleDoorOptions.NONE)
        options.shuffle_parallax.set(True)
        options.shuffle_music.set(True)
        options.goal_optionvar.set(GoalType.ALL_PILLARS)
    
    
        


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

        cls.set_save_data_field("gameName", "Bitbound"+ "_" + cls.seed)

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.random_shops.set(True)


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

        cls.set_save_data_field("gameName", "Seeker"+ "_" + cls.seed)

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.random_enemies.set(False)
        options.module_count_optionsvar.set(ModuleCount.ALL)


class PresetNaked(Preset):
    description = "Starts with nothing, not even pistol. Shops are randomized. Must go into teleporter straight into town at the starting campfire. Pistol and chain dashing is required to finish the game. Only works for NG."

    @classmethod
    def execute_changes(cls):
        cls.set_save_data_field("gameName", "Naked" + "_" + cls.seed)
        cls.set_save_data_field("sc", "")
        cls.set_save_data_field("scK", "")
        cls.set_save_data_field("scUp", "")

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.random_shops.set(True)
        options.random_pistol.set(True)


class PresetRandomStart(Preset):
    description = "Random starting room and shops. Go back to the drifter's house to get map to unlock warping. Might softlock because there is no logic."

    @classmethod
    def execute_changes(cls):
        cls.set_save_data_field("gameName", "RandomStart" + "_" + cls.seed)

        cls.random_start()

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.random_shops.set(True)


class PresetBingo(Preset):
    description = "Meant for playing bingo. Even item distribution and more checks."

    @classmethod
    def execute_changes(cls):
        cls.set_save_data_field("gameName", "Bingo" + "_" + cls.seed)

        # Speedrun preset stuff
        cls.set_save_data_field("cape", 3)
        cls.set_save_data_field("compShell", 10)
        cls.set_save_data_field("sword", 7)

        cls.set_save_data_field("cCapes", "0+3+10+7+")
        cls.set_save_data_field("cShells", "0+3+10+7+")
        cls.set_save_data_field("cSwords", "0+3+10+7+")

        cls.set_save_data_field("skill", "4+")

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.even_item_distribution.set(True)
        options.random_enemies.set(True)
        options.use_chain_logic.set(False)
        options.module_optionsvar.set(
            ItemPlacementRestriction.KEY_ITEMS
        )
        options.limit_one_module_per_room.set(True)
        options.key_countvar.set(KeyCount.ALL)
        options.module_count_optionsvar.set(ModuleCount.ALL)
        options.module_door_optionsvar.set(ModuleDoorOptions.MIX)


class PresetStreamlined(Preset):
    description = "Streamlined for quick playing. Random start. Random starting skill given in addition to chain dash. Random starting outfit."

    @classmethod
    def execute_changes(cls):
        cls.set_save_data_field("gameName", "Streamlined" + "_" + cls.seed)
        cls.random_outfit()
        cls.random_skill()
        cls.random_start()
        cls.set_save_data_field("halluc", 99)

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.even_item_distribution.set(False)
        options.random_enemies.set(False)
        options.random_pistol.set(True)
        options.random_shops.set(False)
        options.random_dungeon_entrances.set(True)
        options.use_chain_logic.set(False)
        options.module_optionsvar.set(
            ItemPlacementRestriction.MODULES_EXTENDED
        )
        options.limit_one_module_per_room.set(False)
        options.key_countvar.set(4)
        options.module_count_optionsvar.set(ModuleCount.MINIMUM)
        options.module_door_optionsvar.set(ModuleDoorOptions.MIX)
        options.shuffle_parallax.set(True)
        options.shuffle_music.set(True)


class PresetNoLogic(Preset):
    description = "No logic. Random starting position. Good luck."

    @classmethod
    def execute_changes(cls):
        cls.set_save_data_field("gameName", "NoLogic" + "_" + cls.seed)
        cls.random_start(True)

    @classmethod
    def set_options(cls, options):
        super().set_options(options)
        options.even_item_distribution.set(False)
        options.no_logicvar.set(True)
        options.random_enemies.set(True)
        options.random_pistol.set(True)
        options.random_shops.set(True)
        options.random_dungeon_entrances.set(True)
        options.use_chain_logic.set(False)
        options.module_optionsvar.set(
            ItemPlacementRestriction.MODULES_EXTENDED
        )
        options.limit_one_module_per_room.set(False)
        options.key_countvar.set(4)
        options.module_count_optionsvar.set(ModuleCount.MINIMUM)
        options.module_door_optionsvar.set(ModuleDoorOptions.MIX)
        options.shuffle_parallax.set(True)
        options.shuffle_music.set(True)