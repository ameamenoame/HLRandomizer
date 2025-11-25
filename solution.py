# Find seed solutions 
# Find mod 4
# Find keys
# Find 3 mods 
# Find laser
# Find module doors

import os
from hldlib import HLDObj, HLDLevel, HLDType, HLDBasics
from typing import Callable, Iterable

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



def check_solution(path="./game_files/randomized"):
	return_text = ""

	north_solution = "North\n"
	east_solution ="East\n"
	west_solution = "West\n"
	south_solution = "South\n"
	central_solution = "Central\n"

	def _parse_line(level_name, _lineno, line):
		nonlocal return_text
		nonlocal east_solution
		nonlocal west_solution
		nonlocal south_solution
		nonlocal north_solution
		nonlocal central_solution

		def add_to_dir_solution(n, text):
			nonlocal east_solution
			nonlocal west_solution
			nonlocal south_solution
			nonlocal north_solution
			nonlocal central_solution
			area = n.split("_")[1]
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
					add_to_dir_solution(level_name, text)
			case "DrifterBones_Key":
				text = "Key found at " + level_name
				text += "\n"
				add_to_dir_solution(level_name, text)
			case "ModuleSocket":
				text = "Module found at " + level_name
				text += "\n"
				add_to_dir_solution(level_name, text)
			case "ModuleDoor":
				obj = HLDObj.from_line(line)
				text = "Module door (%d) found at %s" % (obj.attrs['c'], level_name)
				text += "\n"
				add_to_dir_solution(level_name, text)
			case _:
				pass
		return
	_scan_directory_lines(path,('.lvl'), _parse_line)

	return_text = '\n'.join([north_solution, east_solution, west_solution , south_solution , central_solution])
	return return_text
