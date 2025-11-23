from tkinter import *
from tkinter import ttk, messagebox
from time import time
from hldlib import HLDBasics, HLDLevel
from randomizer import main, OUTPUT_PATH, BACKUP_FOLDER_NAME, ITEMLESS_FOLDER_NAME, DOORLESS_FOLDER_NAME, Inventory, BASE_LIST_OF_ENEMIES, BASE_ENEMY_PROTECT_POOL, ModulePlacementType
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

    PISTOL_RANDO_MANUAL_CHANGE = """
Room,Intro,rm_IN_01_brokenshallows,
obj,Map,9001,273,270,0,-999999,++,,
obj,PlayerHasMapCheck,9002,0,0,0,-999999,++,c=9,
obj,RecessingScenery,9008,321,454,0,1,9002,caseScript,3,0,-999999,0,++,0=spr_WLabBlock16b,1=0,2=0,3=0,k=0,p=-4,fp=0,4=0,5=0,f=0,l=0,
obj,RecessingScenery,9009,305,454,0,1,9002,caseScript,3,0,-999999,0,++,0=spr_WLabBlock16b,1=0,2=0,3=0,k=0,p=-4,fp=0,4=0,5=0,f=0,l=0,
obj,RecessingScenery,9010,289,454,1,1,9002,caseScript,3,0,-999999,0,++,0=spr_WLabBlock16b,1=0,2=0,3=0,k=0,p=-4,fp=0,4=0,5=0,f=0,l=0,
obj,RecessingScenery,9005,321,438,0,1,9004,caseScript,3,0,-999999,0,++,0=spr_WLabBlock16b,1=0,2=0,3=0,k=0,p=-4,fp=0,4=0,5=0,f=0,l=0,
obj,RecessingScenery,9006,305,438,0,1,9004,caseScript,3,0,-999999,0,++,0=spr_WLabBlock16b,1=0,2=0,3=0,k=0,p=-4,fp=0,4=0,5=0,f=0,l=0,
obj,RecessingScenery,9007,289,438,0,1,9004,caseScript,3,0,-999999,0,++,0=spr_WLabBlock16b,1=0,2=0,3=0,k=0,p=-4,fp=0,4=0,5=0,f=0,l=0,
obj,Teleporter,9008,241,351,0,-999999,++,r=rm_C_DrifterWorkshop,d=9009,t=1,i=0,
Room,Central,rm_C_DrifterWorkshop,
obj,Teleporter,9009,220,160,0,-999999,++,r=rm_IN_01_brokenshallows,d=9008,t=1,i=0,
"""
    NO_PISTOL_RANDO_MANUAL_CHANGE = """
Room,Intro,rm_IN_01_brokenshallows,
obj,Map,9001,273,270,0,-999999,++,,
obj,PlayerHasMapCheck,9002,0,0,0,-999999,++,c=9,
obj,DrifterBones_Weapon,9003,268,245,0,-999999,++,spr=spr_DrifterBones,i=31,f=0,k=0,w=1,g=0,c=0,s=0,
obj,Spawner,9004,150,446,18,-999999,++,-1=ToggleSwitch,-2=-999999,-4=1,-5=0,-6=-1,-7=0,-8=0,a=-999999,1=0,
obj,RecessingScenery,9008,321,454,0,1,9002,caseScript,3,0,-999999,0,++,0=spr_WLabBlock16b,1=0,2=0,3=0,k=0,p=-4,fp=0,4=0,5=0,f=0,l=0,
obj,RecessingScenery,9009,305,454,0,1,9002,caseScript,3,0,-999999,0,++,0=spr_WLabBlock16b,1=0,2=0,3=0,k=0,p=-4,fp=0,4=0,5=0,f=0,l=0,
obj,RecessingScenery,9010,289,454,0,1,9002,caseScript,3,0,-999999,0,++,0=spr_WLabBlock16b,1=0,2=0,3=0,k=0,p=-4,fp=0,4=0,5=0,f=0,l=0,
obj,RecessingScenery,9005,321,438,0,1,9004,caseScript,3,0,-999999,0,++,0=spr_WLabBlock16b,1=0,2=0,3=0,k=0,p=-4,fp=0,4=0,5=0,f=0,l=0,
obj,RecessingScenery,9006,305,438,0,1,9004,caseScript,3,0,-999999,0,++,0=spr_WLabBlock16b,1=0,2=0,3=0,k=0,p=-4,fp=0,4=0,5=0,f=0,l=0,
obj,RecessingScenery,9007,289,438,0,1,9004,caseScript,3,0,-999999,0,++,0=spr_WLabBlock16b,1=0,2=0,3=0,k=0,p=-4,fp=0,4=0,5=0,f=0,l=0,
obj,Scenery,9011,147,463,18,-999999,++,0=spr_WRockBlock16,1=0,2=0,3=0,k=0,p=-4,fp=0,4=0,5=0,f=1,l=0,
obj,Region,9012,0,0,0,-999999,++,0=400,1=460,p2=0,
obj,TutorialInfiniteSlime,9013,250,305,0,1,9012,caseScript,3,1,-999999,0,++,,
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



        _delete_if_exists(PATH_TO_MANUAL, self.NO_PISTOL_RANDO_MANUAL_CHANGE)
        _delete_if_exists(PATH_TO_MANUAL, self.PISTOL_RANDO_MANUAL_CHANGE)
        if not self.random_pistol.get():
            _append_if_missing(PATH_TO_MANUAL, self.NO_PISTOL_RANDO_MANUAL_CHANGE)
        else:
            _append_if_missing(PATH_TO_MANUAL, self.PISTOL_RANDO_MANUAL_CHANGE)

        if not self.random_shops.get():
            _append_if_missing(PATH_TO_MANUAL, self.SHOP_RANDO_MANUAL_CHANGE)
        else:
            _delete_if_exists(PATH_TO_MANUAL, self.SHOP_RANDO_MANUAL_CHANGE)

        generate_all_jsons()

        using_preset_seed = self.random_seed.get()

        bound = 1000000000000
        while True:
            try:
                if not using_preset_seed:
                    self.random_seed.set(str(randrange(-bound, bound)))

                    
                final_enemy_list = []
                for e in self.enemy_data:
                    if not e["enabled"]: continue
                    final_enemy_list.append(e["name"])
                final_enemy_weights = []
                for e in self.enemy_data:
                    if not e["enabled"]: continue
                    final_enemy_weights.append(e["weight"])

                main(
                    random_doors=self.random_doors.get(),
                    random_enemies=self.random_enemies.get(),
                    output=output,
                    output_folder_name=output_folder_name if output_folder_name else self.OUT_FOLDER_NAME,
                    random_seed=self.random_seed.get() if self.random_seed.get() else None,
                    list_of_enemies=final_enemy_list,
                    enemy_weights=final_enemy_weights,
                    protect_list=self.enemy_protect_pool,
                    module_placement=self.module_optionsvar.get(),
                    limit_one_module_per_room=self.limit_one_module_per_room.get()
                )
                success = True
                break
            except IndexError as e:
                if not using_preset_seed:
                    print("Retrying!")
                    Inventory.reset()
                else:
                    messagebox.showerror(message=f"We've encountered an '{e}' error. Try again or try another seed if seed used.")
                    self.random_seed.set("")
                    break

        if success: messagebox.showinfo(message=f"Randomization successful! Close this dialog and press 'Push to HLD' to save the randomized levels to Hyper Light Drifter.\n\nSeed: " + str(self.random_seed.get()), title="Success")

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

            
    def disable_enemy(self):
        current_index = self.enemy_list.curselection()
        if current_index != (): 
            i = current_index[0]
            if self.enemy_data[i]["enabled"]:
                self.enemy_choices[i] = "(DISABLED) " +  self.enemy_data[i]["name"] 
            self.enemy_data[i]["enabled"] = False
            self.enemy_choicesvar.set(self.enemy_choices)
            return

    def enable_enemy(self):
        current_index = self.enemy_list.curselection()
        if current_index != (): 
            i = current_index[0]
            if not self.enemy_data[i]["enabled"]:
                self.enemy_choices[i] = self.enemy_data[i]["name"]
            self.enemy_data[i]["enabled"] = True
            self.enemy_choicesvar.set(self.enemy_choices)
            return

    def protect_enemy(self):
        current_index = self.enemy_list.curselection()
        if current_index != (): 
            i = current_index[0]
            self.enemy_data[i]["protected"] = not self.enemy_data[i]["protected"]
            if not self.enemy_data[i]["protected"]:
                self.enemy_protect_pool.remove(self.enemy_data[i]["name"])
            else:
                self.enemy_protect_pool.append(self.enemy_data[i]["name"])
            self.enemy_protect_poolvar.set(self.enemy_protect_pool)
            return

    def onenemyselect(self, _b):
        current_index = self.enemy_list.curselection()
        if current_index != (): 
            i = current_index[0]
            self.current_weightvar.set(str(self.enemy_data[i]["weight"]))
        return

    def onspinboxchanged(self):
        current_index = self.enemy_list.curselection()
        if current_index != (): 
            i = current_index[0]
            weightnum = float(self.current_weightvar.get())
            self.enemy_data[i]["weight"] = weightnum
            self.enemy_choices[i] = "(%s) %s" % (weightnum, self.enemy_data[i]["name"])
            self.enemy_choicesvar.set(self.enemy_choices)
        return

    def onspinboxreturn(self, _a):
        self.current_weightvar.set(self.spinbox.get()) 
        self.onspinboxchanged()
        self.enemy_list.focus()

    def __init__(self, root, path):
        root.title("Hyper Light Drifter Randomizer")
        self.PATH_TO_HLD = path

        setup_frame = ttk.Frame(root)
        setup_frame.grid(column=0, row=0, sticky=NE)
        ttk.Button(setup_frame, text="Set up Randomizer", command=self.do_install).grid(column=0, row=0, sticky=W, pady=5)
        ttk.Label(setup_frame, text="(Do this once if you haven't)").grid(column=1, row=0, sticky=W)

        mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))
        mainframe.grid(column=0, row=1, sticky=NSEW)

        ttk.Separator(mainframe, orient='horizontal').grid(column=0, row=0, sticky=EW, columnspan=8)

        ttk.Label(mainframe, text="Settings", justify=CENTER, font=("TkHeadingFont", 20)).grid(column=0, row=2, sticky=N)

        self.random_seed = StringVar(value=None)
        ttk.Label(mainframe, text="Seed (leave empty for a random seed)").grid(column=0, row=3)
        seed_entry = ttk.Entry(mainframe, textvariable=self.random_seed, width=30)
        seed_entry.grid(column=1, row=3, sticky=EW, columnspan=2)
        
        self.random_doors = BooleanVar(value=False)
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

        self.random_pistol = BooleanVar(value=False)
        ttk.Checkbutton(mainframe, text='Randomize pistol for NG', 
	    variable=self.random_pistol,
	    onvalue=True, offvalue= False).grid(column=1, row=5, sticky=W)

        
        # Module placement settings
        ttk.Label(mainframe, text="Module placement").grid(column=0, row=6, sticky=E)
        module_options = [e.value for e in ModulePlacementType]
        self.module_optionsvar = StringVar(value=ModulePlacementType.FREE)
        module_settings_list = ttk.Combobox(mainframe, textvariable=self.module_optionsvar, values=module_options)
        module_settings_list.grid(column=1, row=6, sticky=W)
        module_settings_list.state(["readonly"])

        self.limit_one_module_per_room = BooleanVar(value=True)
        ttk.Checkbutton(mainframe, text='Limit 1 module per room', 
	    variable=self.limit_one_module_per_room,
	    onvalue=True, offvalue= False).grid(column=1, row=7, sticky=W)

        # Enemy pool listbox
        self.enemy_choices = BASE_LIST_OF_ENEMIES.copy()
        self.enemy_choicesvar = StringVar(value=self.enemy_choices)

        self.enemy_data = [{
           "name": e,
           "weight": 1.0,
           "enabled": True,
           "protected": False
        } for e in self.enemy_choices]
        for e in self.enemy_data:
            if e["name"] == "Birdman": e["protected"] = True
        
        enemy_pool_frame = ttk.Frame(root, height=90)
        enemy_pool_frame.grid(column=0, row=2, sticky=NSEW)
        ttk.Label(enemy_pool_frame, text="Enemy pool", justify=CENTER, font=("TkHeadingFont")).grid(column=0, row=0, sticky=NE)
        self.enemy_list = Listbox(enemy_pool_frame, listvariable=self.enemy_choicesvar, width=27)
        self.enemy_list.configure(exportselection=False)
        self.enemy_list.grid(column=1, row=0, sticky=W, rowspan=2)
        self.enemy_list.bind('<<ListboxSelect>>', self.onenemyselect)

        s = ttk.Scrollbar(enemy_pool_frame, orient=VERTICAL, command=self.enemy_list.yview)
        self.enemy_list.configure(yscrollcommand=s.set)
        s.grid(column=1, row=0, sticky=(N, S, E), rowspan=2)


        # Weight spinbox
        weight_frame = ttk.Frame(enemy_pool_frame)
        weight_frame.grid(column=2, row=0)
        ttk.Label(weight_frame, text="Weight").grid(column=0, row=0, sticky=NW)
        self.current_weightvar= StringVar()
        self.spinbox = ttk.Spinbox(weight_frame, from_=0.0, to=100.0, textvariable=self.current_weightvar, width=5, command=self.onspinboxchanged, increment=.1)
        self.spinbox.grid(column=1, row=0, sticky=NW, padx=5)
        self.spinbox.bind("<Return>", self.onspinboxreturn)


        # Pool edit buttons
        buttons_frame = ttk.Frame(enemy_pool_frame)
        buttons_frame.grid(column=0, row=3, columnspan=2)
        ttk.Button(buttons_frame, text="Enable", command=self.enable_enemy).grid(column=0,row=0,)
        ttk.Button(buttons_frame, text="Disable", command=self.disable_enemy).grid(column=1,row=0, padx=5)
        ttk.Button(buttons_frame, text="Toggle rando protection", command=self.protect_enemy).grid(column=2,row=0, padx=5)


        # Protect pool
        protect_pool_frame = ttk.Frame(enemy_pool_frame)
        protect_pool_frame.grid(column=2, row=1, sticky=NW)
        ttk.Label(protect_pool_frame,text="Protect pool").grid(column=0, row=0, sticky=NW)

        self.enemy_protect_pool = BASE_ENEMY_PROTECT_POOL.copy()
        self.enemy_protect_poolvar = StringVar(value=self.enemy_protect_pool)
        self.protect_list = Listbox(protect_pool_frame, listvariable=self.enemy_protect_poolvar)
        self.protect_list.grid(column=1, row=0, sticky=W, rowspan=2)


        ttk.Separator(root, orient='horizontal').grid(column=0, row=4, sticky=EW, columnspan=8)

        # Bottom buttons
        bottom_frame = Frame(root)
        bottom_frame.grid(column=0, row=5, sticky=NE)


        ttk.Button(bottom_frame, text="Randomize", command=self.do_gen).grid(column=0, row=0)
        ttk.Button(bottom_frame, text="Push to HLD", command=self.do_push).grid(column=1,row=0)
        ttk.Button(bottom_frame, text="Revert to normal", command=self.do_revert).grid(column=2, row=0)
        ttk.Button(bottom_frame, text="Close", command=root.destroy).grid(column=3, row=0)


        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(1, weight=1)
        root.grid_rowconfigure(2, weight=1)
        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
        for child in enemy_pool_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
        for child in bottom_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

root = Tk()


try:
    PATH_TO_HLD = HLDBasics.find_path()
    MainRandomizerUI(root, PATH_TO_HLD)
except ValueError as e:
    GamePathSetup(root)

root.mainloop()