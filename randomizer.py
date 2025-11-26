from __future__ import annotations
from hldlib import HLDObj, HLDLevel, HLDType, HLDBasics
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable
from os import path
import json
import os
import random


JSON_DIR = "jsons"
# GRAPH_JSON =    path.abspath(os.path.join(path.dirname(__file__),JSON_DIR, "out_graph.json"))  # "jsons\\out_graph.json"
# DOOR_JSON =     path.abspath(os.path.join(path.dirname(__file__),JSON_DIR, "out_door.json"))  # "jsons\\out_door.json"
# CONNECT_JSON =  path.abspath(os.path.join(path.dirname(__file__),JSON_DIR, "out_connect.json"))  # "jsons\\out_connect.json"
# CONNECT2_JSON = path.abspath(os.path.join(path.dirname(__file__),JSON_DIR, "out_connect2.json"))  # "jsons\\out_connect2.json"
# MANUAL_JSON =   path.abspath(os.path.join(path.dirname(__file__),JSON_DIR, "out_manual.json"))  # "jsons\\out_manual.json"
# MANUAL2_JSON =  path.abspath(os.path.join(path.dirname(__file__),JSON_DIR, "out_manual2.json"))  # "jsons\\out_manual2.json"


# Temporarily don't use the packed path
GRAPH_JSON =    os.path.join(JSON_DIR, "out_graph.json")  # "jsons\\out_graph.json"
DOOR_JSON =     os.path.join(JSON_DIR, "out_door.json")  # "jsons\\out_door.json"
CONNECT_JSON =  os.path.join(JSON_DIR, "out_connect.json")  # "jsons\\out_connect.json"
CONNECT2_JSON = os.path.join(JSON_DIR, "out_connect2.json")  # "jsons\\out_connect2.json"
CONNECT_MODULE_DOOR_DISABLED_JSON = os.path.join(JSON_DIR, "out_connect_mod_door_disabled.json")  
MANUAL_JSON =   os.path.join(JSON_DIR, "out_manual.json")  # "jsons\\out_manual.json"
MANUAL2_JSON =  os.path.join(JSON_DIR, "out_manual2.json")  # "jsons\\out_manual2.json"

OUTPUT_PATH = "game_files"
BACKUP_FOLDER_NAME = "backup"
ITEMLESS_FOLDER_NAME = "itemless"
DOORLESS_FOLDER_NAME = "doorless"
PATH_TO_ITEMLESS = os.path.join(OUTPUT_PATH, ITEMLESS_FOLDER_NAME)
PATH_TO_DOORLESS = os.path.join(OUTPUT_PATH, DOORLESS_FOLDER_NAME)
COUNTER = HLDBasics.Counter()

BASE_LIST_OF_ENEMIES = [
    "slime", "Birdman", "SmallCrystalSpider", "spider", "Grumpshroom",
    "Wolf", "dirk",  "SpiralBombFrog", "RifleDirk",
    "NinjaStarFrog", "TanukiGun", "CultBird", "missiledirk", "TanukiSword",
    "Melty", "GhostBeamBird", "Leaper", "Dirkommander", "BlaDirk", "CrystalBaby"
]
BASE_ENEMY_PROTECT_POOL = ["Birdman"]
BASE_ENEMY_WEIGHTS = [
    1.0 for i in range(len(BASE_LIST_OF_ENEMIES))
]

class ItemPlacementRestriction(str, Enum):
    def __str__(self):
        return self.value
    NONE = "Don't randomize" # Module placements unchanged
    FREE = "Free" # Randomize module placements across every possible item - bits, outfits, keys, weapons, tablets (except for enemy drops)
    KEY_ITEMS = "Key items" # Module can only appear at key item places - outfits, keys, weapons, tablets
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
    MINIMUM = 4
    ALL = 16

class RandomizerType(str, Enum):
    def __str__(self):
        return self.value
    CHECK = "check"
    MODULE = "module"
    TABLET = "tablet"
    GEARBIT = "gearbit"
    OUTFIT = "outfit"
    KEY = "key"
    WEAPON = "weapon"
    SHOP = "shop"
    PYLON = "pylon"
    DOOR = "door"
    TELEVATOR = "televator"
    TELEPORTER = "teleporter"


class Direction(str, Enum):
    def __str__(self):
        return self.value
    NORTH = "North"
    EAST = "East"
    WEST = "West"
    SOUTH = "South"
    CENTRAL = "Central"
    INTRO = "Intro"
    ABYSS = "Abyss"


def glue_on_direction(string: str, dir_: Direction):
    return f"{dir_.__str__().lower()}_{string}"


class CoolJSON:

    class_name = "class_name"

    @classmethod
    def dump(cls, obj: any, path: str):
        def encode_custom(custom: any):
            jsonable_custom = custom.__dict__
            jsonable_custom[cls.class_name] = custom.__class__.__name__
            return jsonable_custom
        with open(path, "w") as out:
            json.dump(obj, out, indent=4, default=encode_custom)

    @classmethod
    def load(cls, path: str):
        def decode_custom(custom: dict):
            if cls.class_name in custom:
                name = custom.pop(cls.class_name)
                return globals()[name](**custom)
            return custom
        with open(path) as in_:
            to_return = json.load(in_, object_hook=decode_custom)
            return to_return


class LayerTypes(str, Enum):
    def __str__(self):
        return self.value
    LASER = "Laser"
    MOD_3 = "3 modules"
    MOD_4 = "Module 4"
    KEYS = "Keys"
    PYLON = "Pylon"
    

class Layer:
    type_: LayerTypes

    @classmethod
    def passes_requirements(cls, inventory: Inventory):
        return


class Inventory:

    reached_checks: list[FakeObject] = []

    full = {
        "keys": KeyCount.ALL,
        # "lasers": 2,
        "lasers": 1,
        "north_modules": 8,
        "east_modules": 8,
        "west_modules": 8,
        "south_modules": 8,
        "north_pylons": 0,
        "east_pylons": 0,
        "west_pylons": 0,
        "south_pylons": 0,
        "dash_shops": 1,

        "central_modules": 0,
        "intro_modules": 0,
        "abyss_modules": 0,
    }

    current = dict(full)

    temporary = dict(full)

    @classmethod
    def reset_temporary(cls):
        cls.temporary = dict(cls.current)

    @classmethod
    def reset_current(cls):
        cls.current = dict(cls.full)

    @classmethod
    def reset_reached_checks(cls):
        cls.reached_checks: list[FakeObject] = list()
    
    @classmethod
    def reset(cls):
        cls.reset_reached_checks()
        cls.reset_current()
        cls.reset_temporary()

    @classmethod
    def set_module_requirements(cls, count: int = 8):
        cls.full["north_modules"] = count
        cls.full["east_modules"] = count
        cls.full["west_modules"] = count
        cls.full["south_modules"] = count
        cls.current = dict(cls.full)

    @classmethod
    def set_key_requirements(cls, count: KeyCount = KeyCount.ALL):
        cls.full["keys"] = count
        cls.current = dict(cls.full)

    @classmethod
    def pick_up_item(cls, obj: FakeObject):
        def _pick_up_module():
            cls.temporary[glue_on_direction("modules", obj.dir_)] += 1

        def _pick_up_weapon():
            if obj.extra_info["weapon_id"] in [21, 23]:
                cls.temporary["lasers"] += 1

        def _pick_up_key():
            cls.temporary["keys"] += 1

        def _pick_up_shop():
            if obj.extra_info["shop_id"] == "UpgradeDash":
                cls.temporary["dash_shops"] += 1

        def _pick_up_pylon():
            cls.temporary[glue_on_direction("pylons", obj.dir_)] += 1

        pick_up_map = {
            RandomizerType.MODULE: _pick_up_module,
            RandomizerType.WEAPON: _pick_up_weapon,
            RandomizerType.KEY: _pick_up_key,
            RandomizerType.SHOP: _pick_up_shop,
            RandomizerType.PYLON: _pick_up_pylon,
        }
        pick_up_func = pick_up_map.get(obj.type)
        if pick_up_func is not None:
            pick_up_func()

    @classmethod
    def place_check_in_reached(cls, obj: FakeObject):
        cls.reached_checks.append(obj)


@dataclass
class FakeLevel:
    name: str
    dir_: Direction | str
    passed: bool = False
    fake_object_list: list[FakeObject] = field(default_factory=list)
    real_object_list: list[HLDObj] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)
    extra_info: dict = field(default_factory=dict)

    def ping_all(self):
        self.passed = True
        for check in self.fake_object_list:
            check.ping_object()

        for connection in self.connections:
            connection.ping_connection()

    def convert_fake_objects_into_real(self):
        for fake_object in self.fake_object_list:
            real_object = fake_object.get_real_object()
            self.real_object_list.extend(real_object)


@dataclass
class FakeObject:
    type: RandomizerType
    original_type: str
    dir_: Direction | str
    x: int
    y: int
    requirements: dict
    manual_shift_x: int
    manual_shift_y: int
    enemy_id: int | str
    passed: bool = False
    extra_info: dict = field(default_factory=dict)

    @property
    def passes_requirements(self):
        return all([self.requirements[key] <= Inventory.temporary[key] for key in self.requirements if key != "modules"]) and \
               self.requirements["modules"] <= Inventory.temporary[glue_on_direction("modules", self.dir_)] and not self.passed

    def ping_object(self):
        if self.passes_requirements:
            self.passed = True
            if self.type == RandomizerType.CHECK:
                Inventory.place_check_in_reached(self)
            else:
                Inventory.pick_up_item(self)

    def get_real_object(self) -> list[HLDObj]:
        in_offset_map = {
            "MODULE": {"x": 0, "y": 0},
            "GEARBOX": {"x": -17, "y": 0},
            "TABLET": {"x": -1, "y": 7},
            "BONES": {"x": 0, "y": 0},
            "SHOP": {"x": -8, "y": 20},

            "PYLON": {"x": 0, "y": 0},
            " GEARBIT ENEMY": {"x": 0, "y": 0},  # TODO: CLEAN THIS
            "GEARBIT ENEMY": {"x": 0, "y": 0},
            " ENEMY GEARBIT": {"x": 0, "y": 0},
            "KEY": {"x": 0, "y": 0},
        }

        out_offset_map = {
            RandomizerType.MODULE: {"x": 0, "y": 0},
            RandomizerType.TABLET: {"x": -1, "y": 0},
            RandomizerType.GEARBIT: {"x": -17, "y": 0},
            RandomizerType.OUTFIT: {"x": -12, "y": 14},
            RandomizerType.KEY: {"x": -12, "y": 14},
            RandomizerType.WEAPON: {"x": -12, "y": 14},

            RandomizerType.SHOP: {
                "body": {"x": -8, "y": 0},
                "spirit": {"x": -18, "y": 20},
            },
        }

        def _get_module(obj: FakeObject):
            to_return = HLDObj(
                type=HLDType.MODULESOCKET,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["y"],
                attrs={},
                uid=COUNTER.use(),
            )
            return to_return

        def _get_tablet(obj: FakeObject):
            to_return = HLDObj(
                type=HLDType.LIBRARIANTABLET,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["y"],
                attrs={
                    "m": obj.extra_info["tablet_id"]
                },
                uid=COUNTER.use(),
            )
            return to_return

        def _get_gearbit(obj: FakeObject):
            to_return = HLDObj(
                type=HLDType.SPAWNER,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["y"],
                attrs={
                    "-1": "GearbitCrate",
                    "-2": -999999,
                    "-4": 1,
                    "-5": 0,
                    "-6": -1,
                    "-7": 0,
                    "-8": 0,
                },
                uid=COUNTER.use(),
            )
            if obj.enemy_id:
                to_return.middle_string = f"1,{obj.enemy_id}"
                to_return.attrs["-1"] = "Gearbit"
            return to_return

        def _get_outfit(obj: FakeObject):
            outfit_sprite_map = {
                11: 0, # Purple
                9: 36, # Black 
                6: 37,
                4: 35,
                3: 33, # Fuchsia
                2: 31, # Blue
                5: 32,
                7: 38,
                8: 34, # Pink drifter's,
                12: 0, # Black
                13:0, # Sky blue
            }
            to_return = HLDObj(
                type=HLDType.DRIFTERBONES_OUTFIT,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["y"],
                attrs={
                    "spr": "spr_DrifterBones",
                    "i": outfit_sprite_map[obj.extra_info["cape_id"]],
                    "f": 0,
                    "k": 0,
                    "w": -999999,
                    "g": obj.extra_info["companion_id"],
                    "c": obj.extra_info["cape_id"],
                    "s": obj.extra_info["sword_id"],
                },
                uid=COUNTER.use(),
            )
            if obj.enemy_id:
                to_return.middle_string = f"1,{obj.enemy_id},caseScript,4,1,-999999,0"
            return to_return

        def _get_key(obj: FakeObject):
            key_sprite_index_list = [5, 17, 28, 26, 15, 24, 3, 18, 8]
            to_return = HLDObj(
                type=HLDType.DRIFTERBONES_KEY,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["y"],
                attrs={
                    "spr": "spr_DrifterBones",
                    "i": random.choice(key_sprite_index_list),
                    "f": 0,
                    "k": 1,
                    "w": -999999,
                    "g": 0,
                    "c": 0,
                    "s": 0,
                },
                uid=COUNTER.use(),
            )
            if obj.enemy_id:
                to_return.middle_string = f"1,{obj.enemy_id},caseScript,4,1,-999999,0"
            return to_return

        def _get_weapon(obj: FakeObject):
            weapon_sprite_index_map = {
                1: 1,
                2: 75,
                8: 22,
                21: 12,
                23: 0,
                41: 6,
                43: 20,
            }
            to_return = HLDObj(
                type=HLDType.DRIFTERBONES_WEAPON,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["y"],
                attrs={
                    "spr": "spr_DrifterBones",
                    "i": weapon_sprite_index_map[obj.extra_info["weapon_id"]],
                    "f": 0,
                    "k": 0,
                    "w": obj.extra_info["weapon_id"],
                    "g": 0,
                    "c": 0,
                    "s": 0,
                },
                uid=COUNTER.use(),
            )
            if obj.enemy_id:
                to_return.middle_string = f"1,{obj.enemy_id},caseScript,4,1,-999999,0"
            return to_return

        def _get_shop(obj: FakeObject):
            body_to_return = HLDObj(
                type=HLDType.SCENERY,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["body"]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["body"]["y"],
                attrs={
                    "0": "spr_C_dummy",
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "k": 0,
                    "p": -4,
                    "fp": 0,
                    "4": 0,
                    "5": 0,
                    "f": 0,
                    "l": 0,
                },
                uid=COUNTER.use(),
            )
            spirit_to_return = HLDObj(
                type=obj.extra_info["shop_id"],
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["spirit"]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["spirit"]["y"],
                attrs={},
                uid=COUNTER.use(),
            )
            return [body_to_return, spirit_to_return]

        def _get_door(obj: FakeObject):
            to_return = HLDObj(
                type=HLDType.DOOR,
                x=obj.x,
                y=obj.y,
                middle_string=f"1,{obj.extra_info['area_id']},caseScript,3,1,-999999,0",
                attrs={
                    "rm": obj.extra_info["room_id"],
                    "dr": obj.extra_info["door_id"],
                    "ed": obj.extra_info["angle"],
                },
                uid=obj.extra_info["self_id"]
            )
            return to_return

        def _get_teleporter(obj: FakeObject):
            to_return = HLDObj(
                type=HLDType.TELEPORTER,
                x=obj.x,
                y=obj.y,
                attrs={
                    "r": obj.extra_info["room_id"],
                    "d": obj.extra_info["door_id"],
                    "t": 1,
                    "i": 0,
                },
                uid=obj.extra_info["self_id"]
            )
            return to_return

        def _get_televator(obj: FakeObject):
            televator_to_return = HLDObj(
                type=HLDType.TELEVATOR,
                x=obj.x,
                y=obj.y,
                attrs={
                    "rm": obj.extra_info["room_id"],
                    "dr": obj.extra_info["door_id"],
                    "ed": obj.extra_info["vertical"],
                    "m": 0,
                    "v": 1,
                    "a": 0,
                    "trn": 4,
                },
                uid=COUNTER.use()
            )
            door_to_return = HLDObj(
                type=HLDType.DOOR,
                x=obj.x,
                y=obj.y,
                attrs={
                    "rm": "<undefined>",
                    "dr": 1,
                    "ed": 0,
                },
                uid=obj.extra_info["self_id"]
            )
            return [televator_to_return, door_to_return]

        def _get_pylon(obj: FakeObject): return []

        type_map = {
            RandomizerType.MODULE: _get_module,
            RandomizerType.TABLET: _get_tablet,
            RandomizerType.GEARBIT: _get_gearbit,
            RandomizerType.OUTFIT: _get_outfit,
            RandomizerType.KEY: _get_key,
            RandomizerType.WEAPON: _get_weapon,
            RandomizerType.SHOP: _get_shop,
            RandomizerType.PYLON: _get_pylon,
            RandomizerType.DOOR: _get_door,
            RandomizerType.TELEPORTER: _get_teleporter,
            RandomizerType.TELEVATOR: _get_televator,
            "check": lambda _: [], # For empty checks, return nothing
        }

        real_object = type_map[self.type](self)
        if not isinstance(real_object, list):
            real_object = [real_object]
        return real_object


@dataclass
class Connection:
    pointer_to_level: FakeLevel
    dir_: Direction | str
    requirements: dict = field(default_factory=dict)

    @property
    def passes_requirements(self):
        return all([self.requirements[key] <= Inventory.temporary[key] for key in self.requirements if key != "modules"]) and \
               self.requirements["modules"] <= Inventory.temporary[glue_on_direction("modules", self.dir_)] and not self.pointer_to_level.passed

    def ping_connection(self):
        if self.passes_requirements:
            self.pointer_to_level.ping_all()


class LevelHolder(list[HLDLevel | FakeLevel]):
    is_randomized = False

    def dump_all(self, path: str):
        for level in self:
            level.dump_level(os.path.join(path, level.dir_))

    def find_by_name(self, name: str) -> HLDLevel | FakeLevel | None:
        for level in self:
            if level.name == name:
                return level
        else:
            return None

    def find_first_by_partial_name(self, name: str) -> HLDLevel | FakeLevel | None:
        for level in self:
            if name in level.name:
                return level
        else:
            return None

    def find_all_by_partial_name(self, name: str) -> list[HLDLevel | FakeLevel]:
        to_return = []
        for level in self:
            if level.name.startswith(name):
                to_return.append(level)
        return to_return

    def connect_levels_from_list(self, list_: list):
        for connect_info in list_:
            from_ = self.find_by_name(connect_info["from"])
            to_ = self.find_by_name(connect_info["to"])
            from_.connections.append(
                Connection(
                    pointer_to_level=to_,
                    dir_=from_.dir_,
                    requirements=connect_info["requirements"]
                )
            )

    #################################################################################
    # GET EMPTY CHECK
    ####################################################################################
    def get_empty_object(self, filter_lambda: Callable):
        inventory_before = False
        inventory_after = True

        def _ping_and_clear():
            self[0].ping_all()
            for level in self:
                level.passed = False

        while inventory_before != inventory_after:
            inventory_before = inventory_after
            _ping_and_clear()
            inventory_after = Inventory.temporary

        _ping_and_clear()
        _ping_and_clear()

        for level in self:
            for check in level.fake_object_list:
                check.passed = False

        filtered_checks = [check for check in Inventory.reached_checks if filter_lambda(check, check.extra_info["parent_room_name_real"], Inventory, self)]
        random_check: FakeObject = random.choice(filtered_checks)

        Inventory.reset_reached_checks()
        return random_check

    def debug_empty_finder(self):
        to_return = []
        for level in self:
            for check in level.fake_object_list:
                if check.type == RandomizerType.CHECK:
                    to_return.append([check, level])
        return to_return


def get_randomized_doors(levels: list[FakeLevel]):
    # THIS IS THE DOOR RANDO LOGIC
    # AND THIS IS UNREADABLE I'M SORRY
    for level in levels:
        for door in level.fake_object_list:
            door.extra_info["parent_room"] = level.name

    normal_levels = []
    cap_levels = []
    combined_levels = []

    for level in levels:
        if not level.extra_info["cut"]:
            if level_in_combined := [c_level for c_level in combined_levels if level.name.split("/")[0] == c_level.name]:
                level_in_combined[0].fake_object_list += level.fake_object_list
            else:
                level.name = level.name.split("/")[0]
                combined_levels.append(level)
        else:
            combined_levels.append(level)

    origin = combined_levels.pop(0)
    origin.passed = True
    normal_levels.append(origin)

    for level in combined_levels:
        if len(level.fake_object_list) > 1:
            normal_levels.append(level)
        else:
            cap_levels.append(level)

    def _connecting_doors(door1: FakeObject, door2: FakeObject):
        door1.extra_info["connected_to"] = door2
        door2.extra_info["connected_to"] = door1
        door1.passed = True
        door2.passed = True

    def _merge_lists(args: list[list[FakeObject]]):
        to_return = []
        for arg in args:
            to_return.extend(arg)
        return to_return

    while not all([level.passed for level in normal_levels]):
        # PLACE ALL ROOMS DOWN
        origin: FakeLevel = random.choice([level for level in normal_levels if level.passed and not all([door.passed for door in level.fake_object_list])])
        not_connected_doors = [door for door in origin.fake_object_list if not door.passed]
        not_connected_door = random.choice(not_connected_doors)
        not_placed_rooms = [level for level in normal_levels if not level.passed]
        not_placed_room: FakeLevel = random.choice(not_placed_rooms)
        if priority_doors := [priority_door for priority_door in not_placed_room.fake_object_list if priority_door.extra_info["priority"]]:
            priority_door = random.choice(priority_doors)
            _connecting_doors(priority_door, not_connected_door)
            not_placed_room.passed = True
        else:
            aaa = random.choice(not_placed_room.fake_object_list)
            _connecting_doors(aaa, not_connected_door)
            not_placed_room.passed = True

    while len([door for door in _merge_lists([level.fake_object_list for level in normal_levels]) if not door.passed]) > len(cap_levels):
        # CONNECT ALL DOORS IN PLACED ROOMS AND LEAVE SPACE FOR CAPS
        random_door1 = random.choice([door for door in _merge_lists([level.fake_object_list for level in normal_levels]) if not door.passed])
        random_door2 = random.choice([door for door in _merge_lists([level.fake_object_list for level in normal_levels]) if not door.passed and not door == random_door1])
        _connecting_doors(random_door1, random_door2)

    # PLACE CAPS
    random.shuffle(normal_levels)
    random.shuffle(cap_levels)
    for level in normal_levels:
        not_passed_doors = [door for door in level.fake_object_list if not door.passed]
        for not_passed_door in not_passed_doors:
            to_be_connected = cap_levels.pop()
            cap_door = to_be_connected.fake_object_list[0]
            _connecting_doors(cap_door, not_passed_door)
            to_be_connected.passed = True
            normal_levels.append(to_be_connected)

    return normal_levels


def prepare_and_merge_randomized_doors(graph_levels: LevelHolder, door_levels: list[FakeLevel]):
    def _min_requirements(req1: dict, req2: dict) -> dict:
        to_return = {}
        for key in req1.keys():
            to_return[key] = max(req1[key], req2[key])
        return to_return

    connection_list = []
    for level in door_levels:
        for door in level.fake_object_list:
            door.extra_info["self_id"] = COUNTER.use()
    for level in door_levels:
        for door in level.fake_object_list:
            door.extra_info["room_id"] = door.extra_info["connected_to"].extra_info["parent_room"].split("/")[0]
            door.extra_info["door_id"] = door.extra_info["connected_to"].extra_info["self_id"]
            connection_list.append(
                {
                    "from": door.extra_info["parent_room"],
                    "to": door.extra_info["connected_to"].extra_info["parent_room"],
                    "requirements": _min_requirements(door.requirements, door.extra_info["connected_to"].requirements)#door.requirements
                }
            )
        merge_into = graph_levels.find_first_by_partial_name(level.name.split("/")[0])
        merge_into.fake_object_list += level.fake_object_list
    graph_levels.connect_levels_from_list(connection_list)


def randomize_enemies(levels: LevelHolder, list_of_enemies: list[str], weights: list[float], protect_list: list[str]):
    for level in levels:
        for obj in level.object_list:
            if obj.type == HLDType.SPAWNER:
                if obj.attrs["-1"] in BASE_LIST_OF_ENEMIES and obj.attrs["-1"] not in protect_list:
                    obj.attrs["-1"] = random.choices(list_of_enemies, weights)[0]
                    obj.attrs["-2"] = 0
                    obj.attrs["-4"] = 1
                    obj.attrs["-5"] = 0
                    obj.attrs["-6"] = -1
                    obj.attrs["-7"] = 0
                    obj.attrs["-8"] = 0


def place_all_items(levels: LevelHolder, 
                    module_option: ItemPlacementRestriction = ItemPlacementRestriction.KEY_ITEMS, 
                    limit_one_module_per_room: bool = True,
                    key_placement_option: ItemPlacementRestriction = ItemPlacementRestriction.KEY_ITEMS,
                    laser_placement_option: ItemPlacementRestriction = ItemPlacementRestriction.KEY_ITEMS,
                    mod_door_mix_data: dict = {},
                    module_count: ModuleCount = ModuleCount.MINIMUM,
                    key_count: KeyCount = KeyCount.MINIMUM,
                    key_door_mix_data: dict = {}
                    ):

    tablets = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    lasers = [random.choice([21, 23])] 
    # lasers = [21, 23]
    shotguns = [2, 41, 43, 1]
    shops = ["UpgradeSword", "UpgradeWeapon", "UpgradeHealthPack", "UpgradeSpecial"]
    capes = [2, 3, 4, 5, 6, 7, 8, 9, 11]; random.shuffle(capes)
    swords = [2, 3, 4, 5, 6, 7, 8, 9, 11]; random.shuffle(swords) # Additional capes: 12 (NG+ black outfit), 13 (Sky blue Switch-exclusive cape)
    companions = [2, 3, 4, 5, 6, 7, 8, 9, 11]; random.shuffle(companions)

    def place_important(inventory_key: str, place_func: Callable, 
                        lambda_filter: Callable = (lambda x, _, inventory, levels: True), 
                        after_each_place_callback: Callable = (lambda _: True),
                        place_count: int = -1
                        ):
        def _place():
            Inventory.current[inventory_key] -= 1
            Inventory.reset_temporary()

            empty_check =  levels.get_empty_object(lambda_filter)
            place_func(empty_check)
            after_each_place_callback(empty_check)
        if place_count == -1:
            while Inventory.current[inventory_key] > 0:
                _place()
        else:
            for i in range(place_count):
                _place()

    def place_unimportant(i: int, place_func: Callable, lambda_filter: Callable = lambda x, _, __, c: True):
        for _ in range(i):
            Inventory.reset_temporary()
            empty_check = levels.get_empty_object(lambda_filter)
            place_func(empty_check)

    def _place_module(check: FakeObject):
        check.type = RandomizerType.MODULE

    def _place_key(check: FakeObject):
        check.type = RandomizerType.KEY

    def _place_dash_shop(check: FakeObject):
        check.type = RandomizerType.SHOP
        check.extra_info["shop_id"] = "UpgradeDash"

    def _place_generic_shop(check: FakeObject):
        check.type = RandomizerType.SHOP
        check.extra_info["shop_id"] = shops.pop()

    def _place_tablet(check: FakeObject):
        check.type = RandomizerType.TABLET
        check.extra_info["tablet_id"] = tablets.pop()

    def _place_laser(check: FakeObject):
        check.type = RandomizerType.WEAPON
        check.extra_info["weapon_id"] = lasers.pop()

    def _place_shotgun(check: FakeObject):
        check.type = RandomizerType.WEAPON
        check.extra_info["weapon_id"] = shotguns.pop()

    def _place_outfit(check: FakeObject):
        check.type = RandomizerType.OUTFIT
        check.extra_info["cape_id"] = capes.pop()
        check.extra_info["sword_id"] = swords.pop()
        check.extra_info["companion_id"] = companions.pop()

    def _place_gearbit(check: FakeObject):
        check.type = RandomizerType.GEARBIT

    def _get_place_module_requirements(empty_check, parent_room, dir):
        if not (empty_check.dir_ == dir and not empty_check.enemy_id): return False

        # Instead of doing this, would rather have the randomized check be the randomized level -> check flow instead of check -> level
        if module_option == ItemPlacementRestriction.KEY_ITEMS:
            # Limit to one module per room if not using room randomization
            if not levels.is_randomized and limit_one_module_per_room:
                current_room_fake_levels = levels.find_all_by_partial_name(parent_room)
                for level in current_room_fake_levels:
                    for obj in level.fake_object_list:
                        if obj.type == RandomizerType.MODULE:
                            return False

            return empty_check.original_type in ["MODULE", "TABLET", "BONES"]
        elif module_option == ItemPlacementRestriction.NONE:
            return empty_check.original_type == "MODULE"
        elif module_option == ItemPlacementRestriction.FREE:
            return True
        return False

    def _get_placement_restriction(empty_check, parent_room, obj_type: str, restriction_type: ItemPlacementRestriction):
        if parent_room in ["rm_C_Ven_Dash", "rm_PAX_Staging", "rm_IN_BackerTablet"]: return False # Don't put important items in the dash shop

        if restriction_type == ItemPlacementRestriction.KEY_ITEMS:
            return empty_check.original_type in ["MODULE", "TABLET", "BONES"]
        elif restriction_type == ItemPlacementRestriction.NONE:
            return empty_check.original_type == obj_type
        elif restriction_type == ItemPlacementRestriction.FREE:
            return True
        return False
        

    # THESE ARE PLACED BY RESTRICTIVENESS OF THEIR PLACEMENT
    # SO MOST RESTRICTIVE FIRST LEAST RESTRICTIVE LAST
    # AND IMPORTANT FIRST UNIMPORTANT LAST


    def _get_module_layer_requirement(check, inventory, levels: LevelHolder, amount_to_place: int, check_amount : int = 3, max_amount: int = 4):
        if check.dir_ in ["Intro", "Central"]: return False
        if at_least_one_blocker_placed["modules"]["value"]: 
            # return at_least_one_blocker_placed["modules"]["can_still_place"]
            return True

        level_name: str = check.extra_info["parent_room_name_fake"]
        level: FakeLevel = levels.find_by_name(level_name)

        def _find_module_door_connection(level: FakeLevel):
            # Need to find whether this level is behind a module door

            nonlocal mod_door_mix_data

            north_boss_behind_module_rooms = [
                HLDLevel.Names.RM_NL_ALTARTHRONE,
                HLDLevel.Names.RM_NX_SPIRALSTAIRCASE,
                HLDLevel.Names.RM_NX_JERKPOPE,
            ]
            north_gap_behind_module_rooms = [
                HLDLevel.Names.RM_NL_GAPHALLWAY,
                HLDLevel.Names.RM_NL_RISINGARENA
            ]

            east_behind_module_rooms = [
                HLDLevel.Names.RM_EB_BOGSTREET,
                HLDLevel.Names.RM_EC_BIGBOGLAB,
                HLDLevel.Names.RM_EA_BOGTEMPLECAMP,
                HLDLevel.Names.RM_EA_FROGBOSS,
            ]
            east_leaper_behind_module_rooms = [
                HLDLevel.Names.RM_EB_MELTYLEAPERARENA
            ]

            west_behind_module_rooms = [
                HLDLevel.Names.RM_WB_BIGBATTLE,
                HLDLevel.Names.RM_WC_BIGMEADOWVAULT,
                HLDLevel.Names.RM_WC_MEADOWCAVECROSSING,
                HLDLevel.Names.RM_WB_TANUKITROUBLE,
                HLDLevel.Names.RM_WX_BOSS,
                HLDLevel.Names.RM_WA_MULTIENTRANCELAB,
            ]
            west_bottom_behind_module_rooms = [
                HLDLevel.Names.RM_WB_TREETREACHERY,
                HLDLevel.Names.RM_WL_WESTDRIFTERVAULT,
            ]

            south_baker_behind_module_rooms = [
                HLDLevel.Names.RM_CH_TABIGONE,
                HLDLevel.Names.RM_CH_CGATEBLOCK,
                HLDLevel.Names.RM_CH_TLONGESTROAD,
                HLDLevel.Names.RM_CH_CENDHALL,
            ]
            south_archer_behind_module_rooms = [
                HLDLevel.Names.RM_CH_APILLARBIRD,
                HLDLevel.Names.RM_CH_CSPIRAL,
            ]
            south_gauntlet_behind_module_rooms = [
                HLDLevel.Names.RM_S_GAUNTLETEND
            ]

            full = north_boss_behind_module_rooms + north_gap_behind_module_rooms + east_behind_module_rooms + east_leaper_behind_module_rooms \
                + west_behind_module_rooms + west_bottom_behind_module_rooms + south_archer_behind_module_rooms + south_baker_behind_module_rooms + south_gauntlet_behind_module_rooms

            name = level.name + ".lvl"

            if name not in full: return False

            area: str = None
            if level.dir_ == Direction.NORTH:
                if name in north_boss_behind_module_rooms:
                    area = "rm_NX_MoonCourtyard/3:rm_NX_CathedralEntrance"
                elif name in north_gap_behind_module_rooms:
                    area ="rm_NX_MoonCourtyard/3:rm_NL_GapOpening/1"
            elif level.dir_ == Direction.EAST:
                if name in east_behind_module_rooms:
                    area = "rm_EC_ThePlaza/2"
                elif name in east_leaper_behind_module_rooms:
                    area = "rm_EC_EastLoop/1"
            elif level.dir_ == Direction.WEST:
                if name in west_behind_module_rooms:
                    area = "rm_WA_Vale/1"
                elif name in west_bottom_behind_module_rooms:
                    area = "rm_WA_EntSwitch"
            else:
                if name in south_archer_behind_module_rooms:
                    area = "rm_CH_ACorner"
                elif name in south_baker_behind_module_rooms:
                    area = "rm_CH_BDirkDemolition"
                elif name in south_gauntlet_behind_module_rooms:
                    area = "rm_SX_TowerSouth/1"
            
            return area != None and mod_door_mix_data[area] >= check_amount and mod_door_mix_data[area] <= max_amount

        is_valid = _find_module_door_connection(level)
        if is_valid:
            at_least_one_blocker_placed["modules"]["can_still_place"] = amount_to_place > 1
        return is_valid

    def _get_laser_layer_requirement(check, inventory, level, amount_to_place: int):
        if not at_least_one_blocker_placed["lasers"]["value"]:
            is_blocked = check.requirements["lasers"] > 0 or check.extra_info["parent_room_name_real"] in ["rm_NL_StairAscent", "rm_WT_SlowLab"]
            if is_blocked:
                at_least_one_blocker_placed["lasers"]["can_still_place"] = amount_to_place > 1
            return is_blocked
        return True

    def _get_key_layer_requirement(check, inventory, level, amount_to_place: int):
        nonlocal key_door_mix_data
        if not at_least_one_blocker_placed["keys"]["value"]:
            mapping: dict = {
                "rm_NL_CaveVAULT": key_door_mix_data["rm_NX_TitanVista"],
        "rm_WC_CrystalLakeVault": key_door_mix_data["rm_WC_CrystalLake"],
        "rm_EB_FlamePitLAB": key_door_mix_data["rm_EB_MeltyMashArena"],
        "rm_WA_Grotto_buffIntro": key_door_mix_data["rm_WA_Deadwood"],
        "rm_WB_BigBattle": key_door_mix_data["rm_WB_BigBattle"],
        "rm_CH_Bfps":  key_door_mix_data["rm_CH_Bfps"],
        "rm_EC_PlazaAccessLAB": key_door_mix_data["rm_EC_PlazaAccessLAB"],
        "rm_EC_BigBogLAB": key_door_mix_data["rm_EC_BigBogLAB"],
            }
            level_name: str = check.extra_info["parent_room_name_real"]
            if level_name not in mapping.keys(): return False

            is_blocked = mapping[level_name] > 0
            if level_name in ["rm_EC_PlazaAccessLAB", "rm_EC_BigBogLAB"]:
                is_blocked = is_blocked and check.requirements["keys"] > 0
            if is_blocked:
                at_least_one_blocker_placed["keys"]["can_still_place"] = amount_to_place > 1
            return is_blocked
        return True

    def _place_3_modules(next_layer):
        print("Place 3 modules")
        def _place_module_in_dir(area, direction):
            nonlocal next_layer
            place_important(area, _place_module,  
                            lambda empty_check, parent_room, inventory, levels: 
                                _get_place_module_requirements(empty_check, parent_room, direction) 
                                and 
                                next_layer["req"](empty_check, inventory, levels, module_count),

                            (lambda _: next_layer["finish_callback"]()),
                            3)
            next_layer["reset_callback"]()

        _place_module_in_dir("north_modules", Direction.NORTH)
        _place_module_in_dir("east_modules", Direction.EAST)
        _place_module_in_dir("west_modules", Direction.WEST)
        _place_module_in_dir("south_modules", Direction.SOUTH)

    def _place_final_module(next_layer):
        print("Place final module")
        def _place_module_in_dir(area, direction):
            nonlocal next_layer
            place_important(area, _place_module,  
                            lambda empty_check, parent_room, inventory, levels: 
                                _get_place_module_requirements(empty_check, parent_room, direction) 
                                and 
                                next_layer["req"](empty_check, inventory, levels, module_count),

                            (lambda _: next_layer["finish_callback"]()),
                            1)
            next_layer["reset_callback"]()

        _place_module_in_dir("north_modules", Direction.NORTH)
        _place_module_in_dir("east_modules", Direction.EAST)
        _place_module_in_dir("west_modules", Direction.WEST)
        _place_module_in_dir("south_modules", Direction.SOUTH)

        # random.shuffle(directions)
        # for d in directions:
        #     _place_module_in_dir(glue_on_direction("modules", d), d)

    def _place_keys(next_layer):
        print("Place keys")
        place_important("keys", _place_key, 
                        (lambda e, p, i, l: 
                            _get_placement_restriction(e, p, "BONES", key_placement_option) 
                            and 
                            next_layer["req"](e, i, l, key_count)),
                        lambda _: next_layer["finish_callback"]()
                        ) # TODO: Need to separate bones into weapons / outfits/ keys

    def _place_lasers(next_layer):
        print("Place lasers")
        place_important("lasers", _place_laser, 
                        (lambda e, p, i, l: 
                            _get_placement_restriction(e, p, "BONES", laser_placement_option) 
                            and 
                            next_layer["req"](e, i, l, len(lasers))),
                        lambda _: next_layer["finish_callback"]()
                            )

        
    def _set_blocker_placed(key: str, val: bool = True):
        at_least_one_blocker_placed[key]["value"] = val
        return val

    layers: list[dict] = [
        { "names": "modules", 
         "func": _place_3_modules,
         "req": _get_module_layer_requirement,
         "finish_callback": lambda: _set_blocker_placed("modules"),
         "reset_callback": lambda: _set_blocker_placed("modules")
         }, 
        { "names": "lasers", "func": _place_lasers,
         "req": _get_laser_layer_requirement,
         "finish_callback": lambda: _set_blocker_placed("lasers"),
         "reset_callback": lambda: _set_blocker_placed("lasers"),
         },
        {"names": "keys",
         "func": _place_keys,
         "req": _get_key_layer_requirement,
         "finish_callback": lambda: _set_blocker_placed("keys"),
         "reset_callback": lambda: _set_blocker_placed("keys", False),
         }, 
        ]

    random.shuffle(layers)
    layers.insert( # Final module always the final layer
    0,
        { "names": "final_module", 
         "func": _place_final_module,
         "req": lambda c, i, l, a: _get_module_layer_requirement(c,i, l,a, check_amount=3, max_amount=3),
         "finish_callback": lambda: _set_blocker_placed("final_module"),
         "reset_callback": lambda: _set_blocker_placed("final_module", False)
         } 
    )

    at_least_one_blocker_placed = {
        "modules": {
            "value": False,
            "can_still_place": True
        },
        "final_module": {
            "value": False,
            "can_still_place": False
        },
        "keys": {
            "value": False,
            "can_still_place": True
        },
        "lasers": {
            "value": False,
            "can_still_place": True
        },
    }
    print("Layers")
    print([l["names"] for l in layers])
    length = len(layers)
    for i in range(length):
        if i < length - 1:
            layers[i]["func"](layers[i+1])
        else:
            layers[i]["func"](
                {
                    "func": lambda a, b, c, d: True, # Need to match the arg count with the other next_layer functions
                    "req": lambda a, b, c, d: True,
                    "finish_callback": lambda: True,
                    "reset_callback": lambda: True,
                }
                ) 

    # _place_all_modules()
    place_important("dash_shops", _place_dash_shop, lambda x, a, b, c: not x.enemy_id)
    place_unimportant(16, _place_tablet, lambda x, a, b, c: not x.enemy_id)
    place_unimportant(4, _place_generic_shop, lambda x, a, b, c: not x.enemy_id)
    # _place_keys()
    place_important("dash_shops", _place_dash_shop)
    # _place_lasers()
    place_unimportant(4, _place_shotgun)
    place_unimportant(9, _place_outfit)
    place_unimportant(165, _place_gearbit) # Original count: 165. Reduced to 164 to make space for pistol

    return [e["names"] for e in layers]


###############################################################
# MAIN RANDO LOGIC
###############################################################

def main(random_doors: bool = False, random_enemies: bool = False, output: bool = True, random_seed: str | None = None, 
         output_folder_name: str = "out", 
         list_of_enemies=BASE_LIST_OF_ENEMIES, enemy_weights=BASE_ENEMY_WEIGHTS, protect_list=BASE_ENEMY_PROTECT_POOL, 
         module_placement: ItemPlacementRestriction = ItemPlacementRestriction.FREE, limit_one_module_per_room : bool = True, module_door_option: ModuleDoorOptions = ModuleDoorOptions.NONE, module_count: ModuleCount = ModuleCount.ALL,
         key_count:  KeyCount = KeyCount.MINIMUM
         ):
    print("Seed: " + str(random_seed))
    random.seed(random_seed)

    Inventory.set_module_requirements(4 if module_count == ModuleCount.MINIMUM else 8)
    Inventory.set_key_requirements(key_count)

    fake_levels = LevelHolder(CoolJSON.load(GRAPH_JSON))
    fake_levels.connect_levels_from_list(CoolJSON.load(CONNECT_JSON))

    for level in fake_levels:
        for o in level.fake_object_list:
            o.extra_info["parent_room_name_real"] = level.name.split("/")[0]
            o.extra_info["parent_room_name_fake"] = level.name 

    module_door_mix_data: dict
    key_mix_data: dict
    if random_doors:
        intermediary_door_levels = get_randomized_doors(CoolJSON.load(DOOR_JSON))
        fake_levels.is_randomized = True
        prepare_and_merge_randomized_doors(fake_levels, intermediary_door_levels)
    else:
        fake_levels.is_randomized = False

        path: str
        if module_door_option == ModuleDoorOptions.DISABLED:
            path = CONNECT_MODULE_DOOR_DISABLED_JSON
        else:
            path = CONNECT2_JSON

        connections_data = CoolJSON.load(path)

        if module_door_option == ModuleDoorOptions.MIX:
            module_door_mix_data = _mix_fake_module_doors(connections_data)
            print("Module door Mix data")
            print(module_door_mix_data)

        if key_count == KeyCount.MINIMUM:
            key_mix_data =_mix_fake_key_doors(connections_data, fake_levels, key_count)
            print("Key door mix data")
            print(key_mix_data)
            
            
        fake_levels.connect_levels_from_list(connections_data)

    fake_levels.find_by_name("rm_NX_TowerLock/2").fake_object_list[0].type = RandomizerType.PYLON
    fake_levels.find_by_name("rm_EC_TempleIshVault").fake_object_list[0].type = RandomizerType.PYLON
    fake_levels.find_by_name("rm_WA_TowerEnter").fake_object_list[0].type = RandomizerType.PYLON
    fake_levels.find_by_name("rm_SX_TowerSouth/3").fake_object_list[0].type = RandomizerType.PYLON

    layers = place_all_items(fake_levels, module_placement, limit_one_module_per_room,
                    mod_door_mix_data=module_door_mix_data,
                    module_count=module_count,
                    key_count=key_count,
                    key_door_mix_data=key_mix_data
                    )

    real_levels = LevelHolder(HLDBasics.omega_load(PATH_TO_DOORLESS if random_doors else PATH_TO_ITEMLESS))

    for fake_level in fake_levels:
        fake_level.convert_fake_objects_into_real()
        found = real_levels.find_by_name(fake_level.name.split("/")[0] + ".lvl")
        found.object_list += fake_level.real_object_list
        
        
    #####  
    # REAL LEVEL CHANGES
    #####

    manual_changes = CoolJSON.load(MANUAL_JSON)
    for level in manual_changes:
        real_levels.find_by_name(level["name"]).object_list += level["object_list"]

    if random_doors:
        manual_changes2 = CoolJSON.load(MANUAL2_JSON)
        for level in manual_changes2:
            real_levels.find_by_name(level["name"]).object_list += level["object_list"]

    if random_enemies:
        randomize_enemies(real_levels, list_of_enemies, enemy_weights, protect_list)

    if module_door_option == ModuleDoorOptions.DISABLED:
        _manual_disable_module_doors(real_levels)
    elif module_door_option == ModuleDoorOptions.MIX:
        _manual_mix_real_module_doors(real_levels, module_door_mix_data)
       
    if key_count == KeyCount.MINIMUM: 
        _manual_mix_real_key_doors(real_levels, key_mix_data)

    Inventory.reset()

    if output:
        real_levels.dump_all(os.path.join(OUTPUT_PATH, output_folder_name))

    return layers

        
def _mix_fake_key_doors(connections_data: list, level_data: list, max_key_count: KeyCount):
    mix_data: dict = {}
    def _mix_key_doors_connections(levels_to_change: list, high_door_count = max_key_count):
        nonlocal connections_data
        nonlocal mix_data
        high_door_placed = False
        for name in levels_to_change:
            for level in connections_data:
                if level['requirements']['keys'] != 0 and level["from"].startswith(name):
                    roll = random.randint(0, 1)
                    to_place: int
                    if roll == 1 and not high_door_placed:
                        high_door_placed = True
                        to_place = high_door_count
                    # elif roll == 0:
                    #     to_place = 0
                    else:
                        to_place = 0
                    level['requirements']['keys'] = to_place
                    mix_data[level["from"].split("/")[0]] = to_place
                    break

    def _mix_key_doors_checks(checks: list, high_door_count = max_key_count):
        nonlocal level_data
        nonlocal mix_data

        for name in checks:
            level: FakeLevel
            for level in level_data:
                if level.name.startswith(name):
                    obj: HLDObj
                    for obj in level.fake_object_list:
                        if obj.requirements['keys'] > 0:
                            roll = random.randint(0, 1)
                            to_place: int
                            if roll == 1:
                                to_place = high_door_count
                            # elif roll == 0:
                            #     to_place = 0
                            else:
                                to_place = 0
                            obj.requirements['keys'] = to_place
                            mix_data[level.name.split("/")[0]] = to_place

    # These doors lead to transitions so the connections have to be edited
    north_key_door_levels = ["rm_NX_TitanVista"]
    east_key_door_levels = ["rm_EB_MeltyMashArena"]
    west_key_door_levels = ["rm_WC_CrystalLake", "rm_WA_Deadwood"]

    # These doors don't leave to transition so the checks have to be edited
    key_required_checks = ["rm_EC_PlazaAccessLAB", "rm_WB_BigBattle", "rm_CH_Bfps", "rm_EC_BigBogLAB"]

    _mix_key_doors_connections(north_key_door_levels)
    _mix_key_doors_connections(west_key_door_levels)
    _mix_key_doors_connections(east_key_door_levels)

    _mix_key_doors_checks(key_required_checks)

    return mix_data

def _mix_fake_module_doors(level_data: list):
    mix_data: dict = {}
    def _mix_doors_in_level(levels_to_change: list, x_door_count = 3, high_door_count = 4):
        nonlocal level_data
        nonlocal mix_data
        high_door_placed = False
        for name in levels_to_change:
            for level in level_data:
                if level['requirements']['modules'] != 0 and (level['from'] == name) and \
                ((name != "rm_NX_MoonCourtyard/3") or (name == "rm_NX_MoonCourtyard/3" and level['to'] in ["rm_NX_CathedralEntrance", "rm_NL_GapOpening/1"])): # Because north has a level with 2 module doors
                    roll = random.randint(0, 2)
                    to_place: int
                    if roll == 1 and not high_door_placed: # Limit only one 4-module door
                        high_door_placed = True
                        to_place = high_door_count
                    elif roll == 0:
                        to_place = 0
                    else:
                        to_place = x_door_count
                    level['requirements']['modules'] = to_place

                    if name != "rm_NX_MoonCourtyard/3":
                        mix_data[level["from"]] = to_place
                    else:
                        mix_data[level["from"] + ":" + level["to"]] = to_place

    north_module_door_levels = ["rm_NX_MoonCourtyard/3"]
    west_module_door_levels = ["rm_WA_EntSwitch", "rm_WA_Vale/1"]
    east_module_door_levels = ["rm_EC_ThePlaza/2", "rm_EC_EastLoop/1"]
    south_module_door_levels = ["rm_SX_TowerSouth/1", "rm_CH_BDirkDemolition", "rm_CH_ACorner"]

    _mix_doors_in_level(north_module_door_levels)
    _mix_doors_in_level(west_module_door_levels)
    _mix_doors_in_level(east_module_door_levels)
    _mix_doors_in_level(south_module_door_levels)

    return mix_data

def _manual_mix_real_key_doors(real_levels: LevelHolder, mix_data: dict):
    def _change_key_door_in_level(level_name: str, count: int):
        obj: HLDObj
        obj_list = real_levels.find_by_name(level_name).object_list
        to_remove = []
        for obj in obj_list:
            if obj.type == HLDType.DRIFTERVAULTDOOR:
                if count == 0:
                    to_remove.append(obj)
                else:
                    obj.attrs['c'] = count
        for o in to_remove:
            obj_list.remove(o)

    levels = [HLDLevel.Names.RM_NX_TITANVISTA, HLDLevel.Names.RM_EB_MELTYMASHARENA, HLDLevel.Names.RM_WC_CRYSTALLAKE, HLDLevel.Names.RM_WA_DEADWOOD, HLDLevel.Names.RM_EC_PLAZAACCESSLAB, HLDLevel.Names.RM_WB_BIGBATTLE, HLDLevel.Names.RM_CH_BFPS, HLDLevel.Names.RM_EC_BIGBOGLAB]

    for l in levels:
        name = l.replace(".lvl", "")
        _change_key_door_in_level(l, mix_data[name])

    return


def _manual_mix_real_module_doors(real_levels: LevelHolder, mix_data: dict):
    def _change_mod_door_in_level(level_name: str, count: int, skip: int =0):
        obj: HLDObj
        obj_list = real_levels.find_by_name(level_name).object_list
        to_remove = []
        for obj in obj_list:
            if obj.type == HLDType.MODULEDOOR:
                if skip > 0: 
                    skip -= 1
                    continue

                if count == 0:
                    to_remove.append(obj)
                else:
                    obj.attrs['c'] = count

            # East manual changes in Plaza
            if level_name == HLDLevel.Names.RM_EC_THEPLAZA:
                special_remove_ids = [
                    3548, 4248, 1682, # Remove the blocks to PlazaToLoop
                    5404, 7128, 7095, 1702, 95, 5193, 93, 7830]  # Remove the blocks below the warp pad
                if obj.uid in special_remove_ids:
                    to_remove.append(obj)
        for o in to_remove:
            obj_list.remove(o)

    _change_mod_door_in_level(HLDLevel.Names.RM_WA_ENTSWITCH, mix_data["rm_WA_EntSwitch"])
    _change_mod_door_in_level(HLDLevel.Names.RM_WA_VALE, mix_data["rm_WA_Vale/1"])
    _change_mod_door_in_level(HLDLevel.Names.RM_EC_THEPLAZA, mix_data["rm_EC_ThePlaza/2"])
    _change_mod_door_in_level(HLDLevel.Names.RM_EC_EASTLOOP, mix_data["rm_EC_EastLoop/1"])
    _change_mod_door_in_level(HLDLevel.Names.RM_CH_BDIRKDEMOLITION, mix_data["rm_CH_BDirkDemolition"])
    _change_mod_door_in_level(HLDLevel.Names.RM_CH_ACORNER, mix_data["rm_CH_ACorner"])
    _change_mod_door_in_level(HLDLevel.Names.RM_SX_TOWERSOUTH, mix_data["rm_SX_TowerSouth/1"])
    _change_mod_door_in_level(HLDLevel.Names.RM_NX_MOONCOURTYARD, mix_data["rm_NX_MoonCourtyard/3:rm_NL_GapOpening/1"]) # skip is kinda buggy so ordering matters here
    _change_mod_door_in_level(HLDLevel.Names.RM_NX_MOONCOURTYARD, mix_data["rm_NX_MoonCourtyard/3:rm_NX_CathedralEntrance"], 1)

    return

    
def _manual_disable_module_doors(real_levels: LevelHolder):
    def _remove_mod_door_in_level(level_name: str):
        obj: HLDObj
        obj_list = real_levels.find_by_name(level_name).object_list
        to_remove = []
        for obj in obj_list:
            if obj.type == "ModuleDoor":
                to_remove.append(obj)

            # East manual changes in Plaza
            if level_name == HLDLevel.Names.RM_EC_THEPLAZA:
                special_remove_ids = [
                    3548, 4248, 1682, # Remove the blocks to PlazaToLoop
                    5404, 7128, 7095, 1702, 95, 5193, 93, 7830]  # Remove the blocks below the warp pad
                if obj.uid in special_remove_ids:
                    to_remove.append(obj)
        for o in to_remove:
            obj_list.remove(o)

    _remove_mod_door_in_level(HLDLevel.Names.RM_WA_ENTSWITCH)
    _remove_mod_door_in_level(HLDLevel.Names.RM_WA_VALE)
    _remove_mod_door_in_level(HLDLevel.Names.RM_NX_MOONCOURTYARD)
    _remove_mod_door_in_level(HLDLevel.Names.RM_EC_THEPLAZA)
    _remove_mod_door_in_level(HLDLevel.Names.RM_EC_EASTLOOP)
    _remove_mod_door_in_level(HLDLevel.Names.RM_CH_BDIRKDEMOLITION)
    _remove_mod_door_in_level(HLDLevel.Names.RM_CH_ACORNER)
    _remove_mod_door_in_level(HLDLevel.Names.RM_SX_TOWERSOUTH)

