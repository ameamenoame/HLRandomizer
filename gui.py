from tkinter import *
from tkinter import ttk, messagebox
from time import time
from hldlib import HLDBasics, HLDLevel
from randomizer import main, OUTPUT_PATH, BACKUP_FOLDER_NAME, ITEMLESS_FOLDER_NAME, DOORLESS_FOLDER_NAME, Inventory
from random import randrange
import shutil
import os
from json_generators import generate_all_jsons, PATH_TO_MANUAL

def _append_if_missing(filepath, text):
    try:
        with open(filepath, "r") as f:
            contents = f.read()
    except FileNotFoundError:
        contents = ""

    if text not in contents:
        with open(filepath, "a") as f:
            f.writelines(text)
        return True 
    return False 

def _delete_if_exists(filepath, text):
    try:
        with open(filepath, "r") as f:
            contents = f.read()
    except FileNotFoundError:
        return False  

    if text not in contents:
        return False 

    updated = contents.replace(text, "")

    with open(filepath, "w") as f:
        f.writelines(updated)

    return True

class GamePathSetup:
    def set_path(self, *args):
        try:
            path = self.game_path.get().strip()
            with open("hlddir.txt", "w") as f:
                f.write(path)
            messagebox.showinfo(message="Game path set to " + path + "\nPlease close the randomizer and open it again to start the randomizer.", title="Success")
        except:
            messagebox.showerror(message="Could not set game path.")

    def __init__(self, root):
        root.title("Hyper Light Drifter Randomizer Path Setup")

        mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        self.game_path = StringVar(value="C:\Program Files (x86)\Steam\steamapps\common\HyperLightDrifter")
        game_path_entry = ttk.Entry(mainframe, textvariable=self.game_path, width=64)
        game_path_entry.grid(column=2, row=1, sticky=(W, E))

        ttk.Label(mainframe, text="Please specify the path to the game on disk (default is on the C drive but if you changed the installation location copy the path to it here)").grid(column=2, row=0, sticky=W)
        ttk.Button(mainframe, text="Set path", command=self.set_path).grid(column=3, row=1, sticky=W)

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        mainframe.columnconfigure(2, weight=1)
        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)


class MainRandomizerUI:
    PATH_TO_HLD = ""
    OUT_FOLDER_NAME = "randomized"

    SHOP_RANDO_MANUAL_CHANGE = """
Room,Central,rm_C_Ven_Dash,
obj,UpgradeDash,932,88,334,4,-999999,++,
obj,NPCGeneric,155,104,326,4,-999999,++,wlb=1,wl=-999999,32=spr_none,300=spr_NPC_teddy_idleSup,301=spr_NPC_teddy_idleSup,302=spr_none,310=spr_NPC_teddy_idleSup,xs=-1,bi=0,tr=5,tg=1,
Room,Central,rm_C_Ven_Apoth,
obj,UpgradeHealthPack,1398,240,120,3,-999999,++,
obj,NPCGeneric,155,248,128,3,-999999,++,wlb=1,wl=-999999,32=spr_none,300=spr_NPC_akashecary_idleGrind,301=spr_none,302=spr_none,310=spr_NPC_akashecary_idleGrind,xs=-1,bi=0,tr=1,tg=1,
Room,Central,rm_C_Ven_Gun,
obj,UpgradeWeapon,4426,331,152,3,-999999,++,
obj,NPCGeneric,155,344,136,3,-999999,++,wlb=1,wl=-999999,32=spr_none,300=spr_NPC_Fatso,301=spr_none,302=spr_none,310=spr_NPC_Fatso,xs=-1,bi=0,tr=8,tg=1,
Room,Central,rm_C_Ven_SDojo,
obj,NPCGeneric,155,330,144,3,-999999,++,wlb=1,wl=-999999,32=spr_none,300=spr_NPC_beau_idleTap,301=spr_NPC_beau_idleBonk_00,302=spr_none,310=spr_NPC_beau_idleTap,xs=-1,bi=0,tr=1,tg=1,
obj,UpgradeSword,92,272,144,3,-999999,++,
Room,Central,rm_C_Ven_Spec,
obj,UpgradeSpecial,4153,144,144,3,-999999,++,
obj,NPCGeneric,155,160,144,3,-999999,++,wlb=1,wl=-999999,32=spr_none,300=spr_NPC_seanguin_idleThink,301=spr_NPC_seanguin_idleAnim,302=spr_none,310=spr_NPC_seanguin_idleThink,xs=-1,bi=0,tr=0,tg=1,
"""

    def do_install(self, *args):
        """
        Makes a backup of HLD levels and makes itemless and doorless copies of levels
        """

        ITEMS = [",ModuleSocket", ",LibrarianTablet", ",DrifterBones_Outfit", "=GearbitCrate", ",DrifterBones_Key",
                 ",DrifterBones_Weapon", "=Gearbit",
                 ",NoCombat", ",NoShoot", ",Upgrade", "spr_NPC_teddy_idleSup", "spr_NPC_Fatso",
                 "spr_NPC_akashecary_idleGrind", "spr_NPC_seanguin_idleThink", "spr_NPC_beau_idleTap"]
        DOORS = ["j,door,", "j,Televator", "j,Teleporter", ",h=128,cs=3,"]
        start_time = time()
        levels = HLDBasics.omega_load(self.PATH_TO_HLD)

        def _remove_and_dump(levels: list[HLDLevel], objects_to_exclude: list[str], output_folder: str):
            for level in levels:
                objs_to_remove = []
                for obj in level.object_list:
                    if any(item in obj.get_line() for item in objects_to_exclude):
                        objs_to_remove.append(obj)
                for obj in objs_to_remove:
                    level.object_list.remove(obj)
                level.dump_level(os.path.join(OUTPUT_PATH, output_folder, level.dir_))

        # REAL BACKUP
        for level_path, dir_, level_name in HLDBasics.get_levels(self.PATH_TO_HLD, HLDBasics.DIRS):
            os.makedirs(path_to_save := os.path.join(OUTPUT_PATH, BACKUP_FOLDER_NAME, dir_), exist_ok=True)
            shutil.copy(level_path, path_to_save)
        # FAKE BACKUP
        # _remove_and_dump(levels, ["DO NOT EXCLUDE ANYTHING"], BACKUP_FOLDER_NAME)
        _remove_and_dump(levels, ITEMS, ITEMLESS_FOLDER_NAME)
        _remove_and_dump(levels, DOORS, DOORLESS_FOLDER_NAME)


        end_time = time()
        print(f"Done in {end_time-start_time:.2f} s")
        messagebox.showinfo(message=f"Setup finished. You can now start randomization.", title="Done")

    def do_gen(self, *args):
        """
        Starts the randomized level files creation sequence
        Leave random seed empty if you don't wish to use a seed
        At the end creates a folder named 'randomized' in 'game_files'
        """

        output = True  # get_y_n("Output?")
        output_folder_name = self.OUT_FOLDER_NAME

        success = False

        if self.random_seed.get() == "":
            self.random_seed.set(str(randrange(1, 10000000)))

        if not self.random_shops.get():
            _append_if_missing(PATH_TO_MANUAL, self.SHOP_RANDO_MANUAL_CHANGE)
        else:
            _delete_if_exists(PATH_TO_MANUAL, self.SHOP_RANDO_MANUAL_CHANGE)

        generate_all_jsons()

        while True:
            try:
                main(
                    random_doors=self.random_doors.get(),
                    random_enemies=self.random_enemies.get(),
                    output=output,
                    output_folder_name=output_folder_name if output_folder_name else self.OUT_FOLDER_NAME,
                    random_seed=self.random_seed.get() if self.random_seed.get() else None
                )
                success = True
                break
            except IndexError as e:
                if self.random_doors.get() and not self.random_seed.get():
                    print("Retrying!")
                    Inventory.reset()
                else:
                    messagebox.showerror(message=f"We've encountered an '{e}' error. Try again or try another seed if seed used.")
                    self.random_seed.set("")
                    break

        if success: messagebox.showinfo(message=f"Randomization successful! Close this dialog and press 'Push to HLD' to save the randomized levels to Hyper Light Drifter.\n\nSeed: " + self.random_seed.get(), title="Success")

    def do_del(self):
        """
        Deletes a folder in 'game_files'
        Usage example: del randomized
        """
        folder_to_del = self.OUT_FOLDER_NAME
        if folder_to_del not in os.listdir(OUTPUT_PATH):
            messagebox.showerror(message="Output folder to delete not found.")
        else:
            start_time = time()
            shutil.rmtree(os.path.join(OUTPUT_PATH, folder_to_del))
            end_time = time()
            print(f"Done in {end_time-start_time:.2f} s")
            messagebox.showinfo(message="Generated files deleted")

    def do_push(self):
        """
        Pushes selected levels to HLD installation folder
        Usage example: push randomized
        ^ Pushes a folder named 'randomized' from 'game_files' to the HLD installation folder
        """
        folder_to_push = self.OUT_FOLDER_NAME
        if folder_to_push not in os.listdir(OUTPUT_PATH):
            messagebox.showerror(message="Output folder not found.")
        else:
            start_time = time()
            shutil.copytree(os.path.join(OUTPUT_PATH, folder_to_push), self.PATH_TO_HLD, dirs_exist_ok=True)
            end_time = time()
            print(f"Done in {end_time-start_time:.2f} s")
            messagebox.showinfo(message="Randomized levels saved to Hyper Light Drifter")

    def do_revert(self):
        folder_to_push = "backup"
        if folder_to_push not in os.listdir(OUTPUT_PATH):
            messagebox.showerror(message="Output folder not found.")
        else:
            start_time = time()
            shutil.copytree(os.path.join(OUTPUT_PATH, folder_to_push), self.PATH_TO_HLD, dirs_exist_ok=True)
            end_time = time()
            print(f"Done in {end_time-start_time:.2f} s")
            messagebox.showinfo(message="Reverted Hyper Light Drifter to normal")

    def __init__(self, root, path):
        root.title("Hyper Light Drifter Randomizer")
        self.PATH_TO_HLD = path

        mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        ttk.Button(mainframe, text="Set up Randomizer", command=self.do_install).grid(column=2, row=0, sticky=W)
        ttk.Label(mainframe, text="(Do this once if you haven't)").grid(column=3, row=0, sticky=W)

        ttk.Separator(mainframe, orient='horizontal').grid(column=0, row=1, sticky=EW, columnspan=8)

        ttk.Label(mainframe, text="Settings", justify=CENTER, font=("TkHeadingFont", 20)).grid(column=0, row=2, sticky=N)

        self.random_seed = StringVar(value=None)
        ttk.Label(mainframe, text="Seed (leave empty for a random seed)").grid(column=0, row=3)
        seed_entry = ttk.Entry(mainframe, textvariable=self.random_seed, width=30)
        seed_entry.grid(column=1, row=3, sticky=EW, columnspan=2)
        
        self.random_doors = BooleanVar(value=True)
        ttk.Checkbutton(mainframe, text='Randomize rooms', 
	    variable=self.random_doors,
	    onvalue=True, offvalue= False).grid(column=0, row=4, sticky=W)

        self.random_enemies = BooleanVar(value=True)
        ttk.Checkbutton(mainframe, text='Randomize enemies', 
	    variable=self.random_enemies,
	    onvalue=True, offvalue= False).grid(column=0, row=5, sticky=W)

        self.random_shops = BooleanVar(value=False)
        ttk.Checkbutton(mainframe, text='Randomize shops (if unset, shops will stay in town)', 
	    variable=self.random_shops,
	    onvalue=True, offvalue= False).grid(column=1, row=4, sticky=W)

        ttk.Button(mainframe, text="Randomize", command=self.do_gen).grid(column=3, row=6, sticky=E)
        ttk.Button(mainframe, text="Push to HLD", command=self.do_push).grid(column=4, row=6, sticky=E)

        # ttk.Button(mainframe, text="Delete generated files", command=self.do_del).grid(column=5, row=6, sticky=E)
        ttk.Button(mainframe, text="Revert to normal", command=self.do_revert).grid(column=5, row=6, sticky=E)
        ttk.Button(mainframe, text="Close", command=root.destroy).grid(column=6, row=6, sticky=E)

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        mainframe.columnconfigure(2, weight=1)
        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

root = Tk()


try:
    PATH_TO_HLD = HLDBasics.find_path()
    MainRandomizerUI(root, PATH_TO_HLD)
except ValueError as e:
    GamePathSetup(root)

root.mainloop()