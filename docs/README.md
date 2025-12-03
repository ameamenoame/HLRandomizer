# Hyper Light Drifter Randomizer 
[(click here to download)
](https://github.com/ameamenoame/HLRandomizer/releases/download/0.8/HyperLightDrifterRandomizer_08.zip)

![](https://github.com/user-attachments/assets/ea152c8f-5fa8-45a6-80fa-c0acb87107a0)

# Features

- Item randomization
- Enemy randomization
- Presets
- Room randomization

# Setup

Basic setup:
- Unzip the downloaded file
- Open the HyperLightDrifterRandomizer.exe
- If the Windows Defender warning is shown, click on 'More info' then press 'Run anyway'
- A window for specifying the game installation location will be shown.
- Specify the location of your Hyper Light Drifter game installation in the text box entry. By default it is located at 'C:\Program Files (x86)\Steam\steamapps\common\HyperLightDrifter' but change this if your installation location is different. When done, press 'Set path'.
- Open HyperLightDrifterRandomizer.exe again
- This time the randomizer settings window will be shown.
- Press 'Set up Randomizer'. You should only run this once. Wait for it to finish.
- The setup is done. Now you can start randomization.

# Usage

The default randomizer settings is recommended but if you're using enemy randomizer, you can change the enemy pool settings to your liking.

Important differences to the base game on default settings:
- There are only 16 modules.
- There's only 1 key, all key doors have 1 key as requirement
- There's only 1 laser gun (randomly chosen)
- Module doors are randomized and can require 1 or 3 modules.
- The laser gun and the 1 key are required to finish the game according to logic.
	
Randomization:
- Set seed, options to your liking
- Press 'Generate'
- If successful the changes should be in the game without having to restart the game.

Un-randomize:
- To revert the game to normal, press the 'Revert to normal' button in the bottom left corner.

Check solution:
- If you are stuck, you should check out the Logic section first to find out how the randomizer places progression items. 
- If you want to see the location of all the progression items in the seed, press the 'Check solution' button in the bottom left corner.

Useful tip: Skip the intro by pressing /skip or by holding all the face buttons and left+right trigger on controller.

# Options

Randomize rooms:
- Randomizes room transitions.
- Note that using room rando will disable the effect of all other randomize options including item location pool except for enemy randomizer.

Randomize pistol for NG option:
- Does not give pistol on start for NG drifter.
- Pistol's location is randomized in the world.
- Pistol is required to finish the game and is expected to be acquired before the laser gun.
- The monolith room now counts as a check.

Randomize shops:
- Randomize all the shops across the world.
- The dash shop's chain dash upgrade is required to finish the game.

Enemy pool: Enables editing how enemies are randomized. Usage: click on an enemy name in the list and change it with Enable / Disable or setting its weight in the Weight number entry on the right
- Enable / Disable -> Allow / stop an enemy from spawning in
- Weight : set how likely this enemy can spawn (the higher the weight, the more often the enemy spawns)
- Toggle rando protection: 'protect' an enemy - meaning don't randomize all the spots where that enemy would spawn (if dirks are protected, all base game spots where dirks would spawn will spawn dirks)

# Logic
- Every seed will follow a standard progression logic. The player is expected to complete all 'layers' in this logic in order to complete the game. Though the layers don't change, each seed will mix the order in which these 'layers' are done.
- The first layer will always be: In each region, activate 1 or 2 modules to unlock the first unlockable module door (modules_layer_1)
- The following layers can be mixed depending on the seed: find laser gun (lasers), find enough modules to unlock the 3-module door (modules_layer_2), find 1 key (keys)
	- Optional layer: pistols, dash shop
- The final layer will always be: In each region, activate the 4th and final module. (final_module)

- Example: if the layers are: modules_layer_1 -> keys -> modules_layer_2 -> lasers -> final_module, the expected progression will be:
	- In each region, find 1/2 modules in order to unlock the first unlockable module door. (example: the module door leading to North boss will be unlocked after 2 modules are found in hand arena and crusher arena)
	- In each region, in rooms that the first unlockable module door leads to, a key may be found. (ex: the key may be found after defeating North boss at the normal laser gun spot or it may be in another region behind that region's first module door)
	- In each region, the 3rd module will be behind one of the key doors in that region, activating the 3rd module will unlock the 3-module door in that region. (ex: the north's 3rd module will be behind the key door in TitanVista)
	- In each region, in rooms that the 3-module door leads to, the laser gun may be found. (ex: because the first module door led to North boss, the 3-module door left in North leads to GapHallway (the normal 8-module door route) so the laser may be located there)
	- In each region, the laser gun will be required to activate the laser trigger in that region and find the 4th module (ex: use the laser to find the 4th module at the bird rush module)
	- Go down the abyss elevator and finish the game.

- The usual 'go mode' condition will be having the laser gun and a key.

# Check location pools
The term 'check' will be referring to a location where an item appears in the base game but may contain another item or nothing in the randomizer. For example, a 'key check' would be referring to a check where in the base game that location would have contained a key but may contain any item in the randomizer.

Generally the more checks there are, the more locations you will have to check (hence the name) to find progression items making the run longer to complete.

Helpful info:
- All base game module locations: https://steamcommunity.com/sharedfiles/filedetails/?id=658523495
- All key locations: https://steamcommunity.com/sharedfiles/filedetails/?id=657710841
- All outfit locations: https://steamcommunity.com/sharedfiles/filedetails/?id=659081549
- All weapon locations: https://steamcommunity.com/sharedfiles/filedetails/?id=659638654
- Full interactive map: https://hyper-light-drifter-map.de/t/
- Room names for use when seeing the solution:
     - North: https://docs.google.com/document/d/1yHZbnH6RWwW6MiNUEv2ff8siBloLv4eHYoHpkfMsaAI/edit?usp=sharing
     - East: https://docs.google.com/document/d/1pGHI0L5mUVXwvTxYQr06G0cq0c_GOZoDPtzHPrjiJrk/edit?usp=sharing
     - West: https://docs.google.com/document/d/1Sy7dmVj5yCj4qF9o8YkQD9BtUTn8ObyO-24JWB6-a1Q/edit?usp=sharing
     - South: https://docs.google.com/document/d/1joqm0TAkUgh-ou-HAL7rYKSV1qKAtuqo8EyusIwif_Y/edit?usp=sharing

## Modules Extended (39 checks)
- Progression items can appear at the normal 32 module checks and some extra checks:
	- All checks behind key doors (north titan vista, east flame lab / plaza access lab / big bog lab, west crystal lake / deadwood, south mimic route spiders room).
	- All checks behind laser triggers (north bird rush module, east dash challenge, south scythe route big room, west slow lab)
	- Most key checks. Excluded key checks: north bird cave / first crusher room / monolith room, east plaza access lab (same room as key door) / big bog lab, west thin forest, all south keys except exploding barrels room.
	- Outfit checks. Excluded outfit checks: dash shop, horde room, north monolith room, east flame lab, pink drifter.
	- Weapon checks. Excluded weapon checks: intro pistol check.
	- No tablet checks.

- The rationale for removing specific checks for this setting is to limit redundant checks that are not interesting to see or is already on a route to another check.

## Key items (63 checks)
- Progression items can appear at the normal 32 module checks and keys / outfits / weapons checks:
	- All checks behind key doors.
	- All checks behind laser triggers.
	- All key checks.
	- Outfit checks. Excluded outfit checks: dash shop, horde room, pink drifter.
	- Weapon checks. 
	- No tablet checks.

## Key items + tablets (82 checks)
- Progression items can appear at the normal 32 module checks and all keys / outfits / weapons / tablet checks:
	- All checks behind key doors.
	- All checks behind laser triggers.
	- All key checks.
	- Outfit checks. Excluded outfit checks: dash shop, horde room, pink drifter.
	- Weapon checks. 
	- All tablet checks.

## Free (252 checks)
- Progression items can appear at all item checks including enemy drops.
	- Excluded check locations: dash shop, horde room, monolith room.

# Presets

Presets: Start with certain cloaks and upgrades depending on the preset. The current presets:
- Nimble: Movement-focused. Starts with the effects of purple + yellow + pink drifter cloaks (doubled stamina, increased movement speed, faster stamina recharge) and chain dash.
- Vagabond: Sword-focused fighting. Starts with all sword upgrades and the effects of blue + fuchsia + pink drifter cloaks (faster attacks, more ammo from sword slashes, faster stamina recharge)
- Gunslinger: Gun-focused fighting. Starts with all guns, grenade, and the effects of fuchsia + yellow + orange cloaks (more ammo from sword slashes, faster movement, faster grenade recharge)
- Speedrun: Speedrun-focused. Starts with chain dashing and the effects of white + purple + pink cloaks.
- Seeker:  Recommended for beginners to the randomizer. Starts with the sky blue companion that helps track secrets and yellow + ochre cloak effects (faster movement and +1 health).
- Naked: Only works for NG. Starts with nothing, not even pistol. Shops are randomized. Must go into teleporter straight into town at the starting campfire. Pistol and chain dashing is required to finish the game. 
- Random start: Random starting room and shops. Go back to the drifter's house to get map to unlock warping. Might softlock because there is no logic at the beginning but if you can get to a warp it's fine. If playing on NG drifter you should also turn on 'Randomize pistol' option to have pistol spawn in the world.

Presets work by modifying an existing save file at the bottom (4th) save file location (IF YOU ALREADY HAVE A SAVE HERE, YOU MAY LOSE SAVE DATA). To use presets, you must first create a new save file at the bottom save location. After generation, the save name will have the name of the preset. Open the save to play the preset.
<img width="1097" height="1036" alt="image" src="https://github.com/user-attachments/assets/e97707d8-8c1e-42f0-8bc4-d764f7892ec9" />

# Item tracker

Tracks progression items as you play. Works the same as presets by reading your bottom save at regular intervals.

# Updating from a previous version
If you are updating from a previous randomizer version, be sure to revert Hyper Light Drifter to normal first using the previous randomizer by pressing the 'Revert to normal' button before changing to the newer randomizer version.

***

Randomizer by sakhezech, neonflowr. Save editing code by SpringSylvi. Big thanks to MechanicalSnail for compiling the room list.