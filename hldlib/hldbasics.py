from hldlib.hldlevel import HLDLevel
from typing import Iterable
from enum import Enum
import os
import platform

class GoalType(str, Enum):
    def __str__(self):
        return self.value
    DEFAULT = "16 modules & 4 pillars"
    ALL_PILLARS = "4 pillars"
    ALL_BOSSES = "All bosses" 


class ItemPlacementRestriction(str, Enum):
    def __str__(self):
        return self.value

    NONE = "Don't randomize"  # Module placements unchanged
    FREE = "Free (252 checks)"  # Randomize module placements across every possible item - bits, outfits, keys, weapons, tablets (except for enemy drops)
    KEY_ITEMS = "Key items (63 checks)"  # Module can only appear at key item places - outfits, keys, weapons
    KEY_ITEMS_EXTENDED = "Key items + tablets (82 checks)"
    MODULES_EXTENDED = "Modules Extended (47 checks)"  # Only place where modules would be plus special key / outfit checks
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

class KeyCount(int, Enum):
    def __str__(self):
        return str(self.value)

    NONE = 0
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
                        hld_dir_file.readline()  # Skip first line
                        return hld_dir_file.readline().rstrip()
        raise ValueError("No hldDir.txt found.")

    @staticmethod
    def get_levels(path: str, dirs: Iterable[str]):
        for dir_ in dirs:
            for level in [
                level
                for level in os.listdir(os.path.join(path, dir_))
                if level.endswith(".lvl")
            ]:
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

    # Room IDs compiled by SpringSylvi
    room_names = {
        46: ("rm_in_01_brokenshallows", "Broken Shallows"),
        47: ("rm_in_02_tutorial", "Tutorial 1"),
        48: ("rm_in_03_tut_combat", "Tutorial Arena"),
        49: ("rm_in_horizoncliff", "Horizon Cliff"),
        50: ("rm_in_halucinationdeath", "Hallucination Death"),
        51: ("rm_in_drifterfire", "Drifter Fire"),
        52: ("rm_in_blackwaitroom", "Black Wait Room"),
        53: ("rm_in_backertablet", "Monolith Room"),
        55: ("rm_inl_secrets", "Secrets Tutorial (Unused)"),
        56: ("rm_lin_gaps", "Gaps Tutorial (Unused)"),
        57: ("rm_lin_combat", "Combat Tutorial (Unused)"),
        60: ("rm_c_drifterworkshop", "Drifter Workshop"),
        61: ("rm_c_central", "Town"),
        62: ("rm_c_dregs_n", "North Dregs"),
        63: ("rm_c_dregs_s", "South Dregs"),
        64: ("rm_c_dregs_e", "East Dregs"),
        65: ("rm_c_dregs_w", "West Dregs"),
        66: ("rm_c_ven_apoth", "Medkit Shop"),
        67: ("rm_c_ven_dash", "Dash Shop"),
        68: ("rm_c_ven_gun", "Gun Shop"),
        69: ("rm_c_ven_spec", "Grenade Shop"),
        70: ("rm_c_ven_sdojo", "Sword Shop"),
        71: ("rm_carena", "Soccer Field"),
        72: ("rm_pax_staging", "Horde Lobby"),
        73: ("rm_pax_arena1", "South Horde"),
        74: ("rm_pax_arena2", "North Horde"),
        75: ("rm_pax_arenae", "East Horde"),
        76: ("rm_pax_arenaw", "West Horde"),
        78: ("rm_c_backertabletx", "Backer Tablet"),
        79: ("rm_televatorshaft", "Elevator Cutscene"),
        84: ("rm_nl_entrancepath", "Entrance Path"),
        85: ("rm_nx_titanvista", "Titan Vista"),
        86: ("rm_nx_northhall", "North Dark Room"),
        87: ("rm_nl_cavevault", "Blue Cloak"),
        88: ("rm_nx_aftertitan", "Cliffs"),
        89: ("rm_nc_npchatchery", "NPC Hatchery"),
        90: ("rm_nx_shrinepath", "Shrine Path"),
        91: ("rm_nl_shrinepath2vault", "Shrine Path Vault"),
        92: ("rm_nx_cave01", "Cave 01"),
        93: ("rm_nx_shrinepath_2", "Shrine Path 2"),
        94: ("rm_nx_mooncourtyard", "Moon Courtyard"),
        95: ("rm_nx_towerlock", "North Pillar"),
        96: ("rm_nc_cliffcampfire", "Cliff Campfire"),
        97: ("rm_nl_tobrokenshallows", "Broken Shallows Stairs"),
        98: ("rm_nx_stairs03", "Stairs 03"),
        100: ("rm_nl_warproom", "Crusher Key"),
        101: ("rm_nl_crushwarphall", "Crush Warp Hall"),
        102: ("rm_nl_crushtransition", "Crush Transition"),
        103: ("rm_nl_crushbackloop", "Crush Loop"),
        104: ("rm_nc_crusharena", "Crush Arena"),
        106: ("rm_nl_dropspiralopen", "Drop Spiral"),
        107: ("rm_nl_droppits", "Drop Pits"),
        108: ("rm_nl_dropblockcultfight", "Drop Block Cult Fight"),
        109: ("rm_nl_droparena", "Drop Arena"),
        111: ("rm_nl_gapopening", "Waterfall 1"),
        112: ("rm_nx_gapwide", "Waterfall 2"),
        113: ("rm_nl_gaphallway", "Waterfall 3"),
        114: ("rm_nl_risingarena", "Waterfall Arena"),
        116: ("rm_nx_cathedralentrance", "Cathedral Entrance"),
        117: ("rm_nx_cathedralhall", "Cathedral Hall"),
        118: ("rm_nl_altarthrone", "Altar Throne"),
        119: ("rm_nx_spiralstaircase", "Cathedral Stairs"),
        120: ("rm_nx_librariantablet", "Librarian Tablet"),
        121: ("rm_nx_jerkpope", "Jerk Pope"),
        123: ("rm_nl_stairascent", "Birds Module"),
        124: ("rm_nl_crusharena", "Crush Arena 2 (Unused)"),
        128: ("rm_sx_southopening", "South Opening"),
        129: ("rm_ch_ctemplate", "Barrel Room"),
        130: ("rm_sx_towersouth", "South Warp"),
        131: ("rm_sx_npc", "South NPC"),
        132: ("rm_s_gauntlet_elevator", "South Dash Challenge"),
        133: ("rm_ch_bgunpillars", "Sky Factory 1"),
        134: ("rm_ch_bfinal", "Sky Factory 2"),
        135: ("rm_s_gauntletend", "Sky Factory 3"),
        137: ("rm_ch_bdirkdemolition", "South Left Elevator"),
        139: ("rm_ch_tabigone", "Baker Module 1"),
        140: ("rm_ch_cgateblock", "Baker Module 2"),
        141: ("rm_ch_bmaddash", "Baker Arena"),
        142: ("rm_ch_tlongestroad", "Baker Path 4"),
        143: ("rm_s_bulletbaker", "Bullet Baker"),
        144: ("rm_ch_cendhall", "Baker Module 3"),
        146: ("rm_ch_cturnhall", "Mimic Path 1"),
        147: ("rm_ch_bfps", "Mimic Path 2"),
        148: ("rm_ch_cbigggns", "Crusher Room"),
        149: ("rm_ch_cspawnground", "Mimic Arena"),
        150: ("rm_s_countaculard", "Mimic"),
        152: ("rm_ch_acorner", "South Right Elevator"),
        154: ("rm_ch_bdirkdeluge", "Scythe Path 1"),
        155: ("rm_ch_bpods", "Scythe Path 2"),
        156: ("rm_ch_bgundirkdash", "Scythe Arena"),
        157: ("rm_s_markscythe", "Mark Scythe"),
        158: ("rm_s_gauntletlinkup", "Gauntlet Linkup"),
        160: ("rm_ch_apillarbird", "Archer Path 1"),
        161: ("rm_ch_cspiral", "C Spiral"),
        162: ("rm_ch_tbirdstandoff", "Archer Path 3"),
        163: ("rm_ch_bleaperfall", "Leaper Fall"),
        164: ("rm_s_bennyarrow", "Archer"),
        165: ("rm_s_gauntlettitanfinale", "Gauntlet Titan"),
        171: ("rm_ea_eastopening", "East Opening"),
        172: ("rm_ec_swordbridge", "Sword Bridge"),
        173: ("rm_el_flameelevatorenter", "Flame Elevator"),
        174: ("rm_ea_watertunnellab", "Water Tunnel"),
        175: ("rm_ec_theplaza", "Plaza"),
        176: ("rm_ec_npcdrugden", "NPC Drug Den"),
        177: ("rm_ex_towereast", "Tower East"),
        178: ("rm_eb_bogstreet", "Bog Street"),
        179: ("rm_ec_plazatoloop", "Plaza to Loop"),
        181: ("rm_el_megahugelab", "Mega Huge Lab"),
        182: ("rm_eb_meltymasharena", "Melty Mash Arena"),
        183: ("rm_eb_flamepitlab", "Flame Room"),
        184: ("rm_el_flameelevatorexit", "Lab Elevator"),
        185: ("rm_eb_deadotterwalk", "Otter Walk"),
        187: ("rm_ec_plazaaccesslab", "White Cloak"),
        188: ("rm_ec_dockslab", "Docks Lab"),
        189: ("rm_ex_dockscampfire", "Docks Campfire"),
        190: ("rm_ev_docksbridge", "Docks"),
        191: ("rm_el_frogarena", "Frog Arena"),
        193: ("rm_ec_bigboglab", "Big Bog Lab"),
        194: ("rm_ea_bogtemplecamp", "Bog Temple Camp"),
        195: ("rm_ea_frogboss", "Toad"),
        196: ("rm_ec_templeishvault", "East Pillar"),
        198: ("rm_ec_eastloop", "East Loop"),
        199: ("rm_ec_looplab", "Loop Lab"),
        200: ("rm_eb_meltyleaperarena", "Loop Arena"),
        202: ("rm_ec_plazatodocks", "Plaza to Docks (Unused)"),
        203: ("rm_ea_dockfightlab", "Dock Fight Lab (Unused)"),
        204: ("rm_eb_underotterbigriflerumble", "Big Rifle Rumble (Unused)"),
        205: ("rm_eb_cleanershole", "Toad 2 (unused)"),
        209: ("rm_wa_entrance", "West Entrance"),
        210: ("rm_wl_prisonhalvault", "West Vault 1"),
        211: ("rm_wa_deadwood", "Dead Wood"),
        212: ("rm_wa_deadwoods1", "Well Room"),
        213: ("rm_wa_grotto_buffintro", "Grotto"),
        214: ("rm_wc_windingwood", "Winding Wood"),
        215: ("rm_wc_grottonpc", "Grotto NPC"),
        216: ("rm_wl_npctreehouse", "NPC Treehouse"),
        217: ("rm_wc_minilab", "Mini Lab"),
        218: ("rm_wt_thewood", "The Wood"),
        219: ("rm_wa_entswitch", "West Warp"),
        220: ("rm_wc_meadowoodcorner", "Dogs Module"),
        222: ("rm_wb_treetreachery", "Tree Treachery"),
        223: ("rm_wl_westdriftervault", "Blue-Green Outfit"),
        225: ("rm_wt_slowlab", "Slow Lab"),
        226: ("rm_wc_cliffsidecellsredux", "Cliffside Cells"),
        227: ("rm_wc_prisonhal", "Prison Arena"),
        229: ("rm_wc_thinforest", "Thin Forest"),
        230: ("rm_wc_simplepath", "Simple Path"),
        231: ("rm_wc_crystallake", "Crystal Lake"),
        232: ("rm_wc_crystallakevault", "Yellow Cloak"),
        233: ("rm_wc_prisonhallend", "Prison Hall"),
        234: ("rm_wc_thinforestlow", "Thin Forest Low"),
        235: ("rm_wc_thinforestlowsecret", "Thin Forest Secret"),
        236: ("rm_wa_titanfalls", "Titan Falls"),
        238: ("rm_wa_vale", "Vale"),
        239: ("rm_wc_bigmeadow", "Big Meadow"),
        240: ("rm_wc_bigmeadowvault", "Big Meadow Vault"),
        241: ("rm_wc_meadowcavecrossing", "Meadow Cave Crossing"),
        242: ("rm_wb_bigbattle", "Big Battle"),
        243: ("rm_wb_tanukitrouble", "Tanuki Trouble"),
        244: ("rm_wc_ruinclearing", "Ruin Clearing"),
        245: ("rm_wx_boss", "General"),
        246: ("rm_wa_towerenter", "West Pillar"),
        247: ("rm_wa_multientrancelab", "West Dark Room"),
        248: ("rm_wa_crsytaldescent", "Crystal Descent"),
        250: ("rm_wa_grottox", "Grotto X (Unused)"),
    }

    @classmethod
    def get_human_room_name(cls, room_name: str) -> str:
        name_mapping = HLDBasics.room_name_str_mapping()
        return HLDBasics.room_names[name_mapping[room_name.lower().split("/")[0]]][1]

    @classmethod
    def get_dir_from_room_name(cls, room_name: str) -> Direction:
        code = room_name.split("_")[1].lower()
        match code[0]:
            case "n":
                return Direction.NORTH
            case "w":
                return Direction.WEST
            case "e":
                return Direction.EAST
            case _:
                return Direction.SOUTH

    @classmethod
    def room_name_str_mapping(cls) -> dict:
        mapping = {}
        for i in cls.room_names.keys():
            mapping[cls.room_names[i][0]] = i 
        return mapping

if platform.system() in ("Linux", "Darwin"):
    HLDBasics.DIRS = tuple(dir_.lower() for dir_ in HLDBasics.DIRS)
