# Find seed solutions 
# Find mod 4
# Find keys
# Find 3 mods 
# Find laser
# Find module doors

import os
from hldlib import HLDObj, HLDLevel, HLDType, HLDBasics
from typing import Callable, Iterable
from pathlib import Path

def _scan_directory_lines(
    directory: str,
    file_extensions: Iterable[str] = (".lvl",),
    callback: Callable[[str, int, str], None] = None
):
    """
    Scan all files in a directory and invoke a callback for each line.

    Args:
        directory (str): Path to directory.
        file_extensions (Iterable[str]): Only process files with these extensions.
        callback (Callable[[str, int, str], None]): Function called as callback(filename, line_number, line_text).
    """
    if callback is None:
        callback = lambda fname, num, line: None

    for root, _, files in os.walk(directory):
        for filename in files:
            if not filename.lower().endswith(tuple(file_extensions)):
                continue

            full_path = os.path.join(root, filename)

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        callback(filename, i, line.rstrip("\n"))
            except Exception as e:
                print(f"[ERROR] Could not read {full_path}: {e}")



def check_solution(layers, path=Path("game_files") / "randomized"):
	return_text = "Layers: " + "<-".join(layers) + "\n\n"

	north_solution = ""
	east_solution =""
	west_solution = ""
	south_solution = ""
	central_solution = ""

 
	key_rooms = {
		"rm_NL_CaveVAULT.lvl": 10,
"rm_WC_CrystalLakeVault.lvl": 12,
"rm_EB_FlamePitLAB.lvl": 1,
"rm_WA_Grotto_buffIntro.lvl": 3,
"rm_WB_BigBattle.lvl": 4,
"rm_CH_Bfps.lvl": 16,
HLDLevel.Names.RM_EC_PLAZAACCESSLAB: 8,
"rm_EC_BigBogLAB": 3,
	}

	laser_checks = [
		HLDLevel.Names.RM_NL_STAIRASCENT,
		HLDLevel.Names.RM_WT_SLOWLAB,
		HLDLevel.Names.RM_EB_DEADOTTERWALK,
		HLDLevel.Names.RM_CH_BDIRKDELUGE
	]

	def _parse_line(level_name, _lineno, line):
		nonlocal return_text
		nonlocal east_solution
		nonlocal west_solution
		nonlocal south_solution
		nonlocal north_solution
		nonlocal central_solution

		def add_to_dir_solution(n, text, obj: HLDObj):
			nonlocal east_solution
			nonlocal west_solution
			nonlocal south_solution
			nonlocal north_solution
			nonlocal central_solution
			area = n.split("_")[1]

			if n in key_rooms.keys() and not text.startswith(HLDType.DRIFTERVAULTDOOR):
				text = text.replace("\n", "")
				text += " (May be behind key door)\n" 
			elif n in laser_checks:
				text = text.replace("\n", "")
				text += " (Behind laser check)\n"
   
			if area.startswith("N"):
				north_solution += text
			elif area.startswith("E"):
				east_solution += text
			elif area.startswith("W"):
				west_solution += text
			elif area.startswith("CH") or area.startswith("S"):
				south_solution += text
			else:
				central_solution += text

		obj_type = line.split(",")[1]
		match obj_type:
			case "DrifterBones_Weapon":
				obj = HLDObj.from_line(line)
				if obj.attrs['w'] in [21, 23]: 
					text = "Laser (%d) found at %s" % (obj.attrs['w'], level_name)
					text += "\n"
					add_to_dir_solution(level_name, text, obj)
				elif obj.attrs['w'] == 1:
					text = "Pistol found at %s" % (level_name)
					text += "\n"
					add_to_dir_solution(level_name, text, obj)
			case HLDType.UPGRADEDASH:
				text = "Dash shop found at %s\n" % level_name
				add_to_dir_solution(level_name, text, None)
			case "DrifterBones_Key":
				text = "Key found at " + level_name
				text += "\n"
				add_to_dir_solution(level_name, text, HLDObj.from_line(line))
			case "ModuleSocket":
				text = "Module found at " + level_name
				text += "\n"
				add_to_dir_solution(level_name, text, HLDObj.from_line(line))
			case HLDType.DRIFTERVAULTDOOR:
				obj = HLDObj.from_line(line)
				text = "DrifterVaultDoor (%d key door) found at %s" % (obj.attrs['c'], level_name)
				text += "\n"
				add_to_dir_solution(level_name, text, obj)
			case "ModuleDoor":
				obj = HLDObj.from_line(line)
				text = "DoorModule (%d) found at %s" % (obj.attrs['c'], level_name)
				text += "\n"
				add_to_dir_solution(level_name, text, obj)
			case _:
				pass
		return
	_scan_directory_lines(path,('.lvl'), _parse_line)

	result = []
	for s in [north_solution, east_solution, west_solution , south_solution , central_solution]:
		lines = s.split("\n")
		sorted_lines = sorted(lines, key=lambda line: line[0:2] if line else "")
		result.append("\n".join(sorted_lines))

	result[0] = "\nNorth" + result[0]
	result[1] = "\nEast" + result[1]
	result[2] = "\nWest" + result[2]
	result[3] = "\nSouth" + result[3]
	result[4] = "\nCentral" + result[4]

	return_text += '\n'.join(result)
	return return_text
