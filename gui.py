import threading
from tkinter import *
from tkinter import ttk, messagebox
from time import time
from hldlib import HLDBasics, HLDLevel
from randomizer import main, OUTPUT_PATH, BACKUP_FOLDER_NAME, ITEMLESS_FOLDER_NAME, DOORLESS_FOLDER_NAME, Inventory, BASE_LIST_OF_ENEMIES, BASE_ENEMY_PROTECT_POOL, ItemPlacementRestriction, ModuleCount, ModuleDoorOptions
from solution import check_solution
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
    layers = []

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

    def show_solution(self):
        solution = check_solution(self.layers)
        messagebox.showinfo(message=solution, title="Solution")

    def set_weekly_seed(self):
        import datetime
        import hashlib
        import base64
        def short_base64_hash_week():
            year, week, _ = datetime.date.today().isocalendar()
            data = f"{year}-{week}".encode()
            digest = hashlib.md5(data).digest()
            return base64.urlsafe_b64encode(digest)[:12].decode()

        seed = short_base64_hash_week()
        self.random_seed.set(seed)

    def open_link(self, url: str):
        import webbrowser
        webbrowser.open_new(url)

        
    @staticmethod
    def thread_do_work(
        random_seed,
        enemy_data,
        random_pistol,
        random_shops,
        OUT_FOLDER_NAME,
        NO_PISTOL_RANDO_MANUAL_CHANGE,
        PISTOL_RANDO_MANUAL_CHANGE,
        SHOP_RANDO_MANUAL_CHANGE,
        random_doors,
        random_enemies,
        enemy_protect_pool,
        module_optionsvar,
        limit_one_module_per_room,
        module_door_optionsvar,
        module_count_optionsvar,
        PATH_TO_HLD,
        root,
        results
    ):
        def do_gen(
            random_seed,
            enemy_data,
            random_pistol,
            random_shops,
            OUT_FOLDER_NAME,
            NO_PISTOL_RANDO_MANUAL_CHANGE,
            PISTOL_RANDO_MANUAL_CHANGE,
            SHOP_RANDO_MANUAL_CHANGE,
            random_doors,
            random_enemies,
            enemy_protect_pool,
            module_optionsvar,
            limit_one_module_per_room,
            module_door_optionsvar,
            module_count_optionsvar,
                ):
            """
            Starts the randomized level files creation sequence
            Leave random seed empty if you don't wish to use a seed
            At the end creates a folder named 'randomized' in 'game_files'
            """


            output = True
            output_folder_name = OUT_FOLDER_NAME

            success = False

            _delete_if_exists(PATH_TO_MANUAL, NO_PISTOL_RANDO_MANUAL_CHANGE)
            _delete_if_exists(PATH_TO_MANUAL, PISTOL_RANDO_MANUAL_CHANGE)
            if not random_pistol:
                _append_if_missing(PATH_TO_MANUAL, NO_PISTOL_RANDO_MANUAL_CHANGE)
            else:
                _append_if_missing(PATH_TO_MANUAL, PISTOL_RANDO_MANUAL_CHANGE)

            if not random_shops:
                _append_if_missing(PATH_TO_MANUAL, SHOP_RANDO_MANUAL_CHANGE)
            else:
                _delete_if_exists(PATH_TO_MANUAL, SHOP_RANDO_MANUAL_CHANGE)

            generate_all_jsons()

            layers = []

            using_preset_seed = random_seed

            bound = 1000000000000
            count = 0
            while count < 1000:
                count+=1
                try:
                    if not using_preset_seed:
                        random_seed = str(randrange(-bound, bound))

                    final_enemy_list = []
                    for e in enemy_data:
                        if not e["enabled"]: continue
                        final_enemy_list.append(e["name"])
                    final_enemy_weights = []
                    for e in enemy_data:
                        if not e["enabled"]: continue
                        final_enemy_weights.append(e["weight"])


                    layers = main(
                        random_doors=random_doors,
                        random_enemies=random_enemies,
                        output=output,
                        output_folder_name=output_folder_name if output_folder_name else OUT_FOLDER_NAME,
                        random_seed=random_seed if random_seed else None,
                        list_of_enemies=final_enemy_list,
                        enemy_weights=final_enemy_weights,
                        protect_list=enemy_protect_pool,
                        module_placement=module_optionsvar,
                        limit_one_module_per_room=limit_one_module_per_room,
                        module_door_option=module_door_optionsvar,
                        module_count=module_count_optionsvar,
                        randomize_pistol=random_pistol,
                        randomize_shop=random_shops,
                    )
                    success = True
                    break
                except IndexError as e:
                    if not using_preset_seed:
                        print("Retrying!")
                        Inventory.reset()
                    else:
                        print(f"We've encountered an '{e}' error. Try again or try another seed if seed used.")
                        break 

            return (success, random_seed, layers)
    
        def do_push(OUT_FOLDER_NAME, PATH_TO_HLD):
            """
            Pushes selected levels to HLD installation folder
            Usage example: push randomized
            ^ Pushes a folder named 'randomized' from 'game_files' to the HLD installation folder
            """
            folder_to_push = OUT_FOLDER_NAME
            if folder_to_push not in os.listdir(OUTPUT_PATH):
                messagebox.showerror(message="Output folder not found.")
                return False
            else:
                start_time = time()
                shutil.copytree(os.path.join(OUTPUT_PATH, folder_to_push), PATH_TO_HLD, dirs_exist_ok=True)
                end_time = time()
                print(f"Done in {end_time-start_time:.2f} s")
                return True

        gen_result = do_gen(
            random_seed,
            enemy_data,
            random_pistol,
            random_shops,
            OUT_FOLDER_NAME,
            NO_PISTOL_RANDO_MANUAL_CHANGE,
            PISTOL_RANDO_MANUAL_CHANGE,
            SHOP_RANDO_MANUAL_CHANGE,
            random_doors,
            random_enemies,
            enemy_protect_pool,
            module_optionsvar,
            limit_one_module_per_room,
            module_door_optionsvar,
            module_count_optionsvar
        )
        do_push(
            OUT_FOLDER_NAME,
            PATH_TO_HLD
        )

        # Definitely not thread safe
        results['success']= gen_result[0]
        results['final_seed'] = gen_result[1]
        results['layers'] = gen_result[2]

        root.event_generate('<<GenerationComplete>>')

    def randomize(self):
        def center_subwindow(parent, subwindow):
            parent.update_idletasks()  # Ensure parent dimensions are accurate
            subwindow.update_idletasks() # Ensure subwindow dimensions are accurate

            # Get parent window's position and dimensions
            parent_x = parent.winfo_x()
            parent_y = parent.winfo_y()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()

            # Get subwindow's dimensions
            subwindow_width = subwindow.winfo_width()
            subwindow_height = subwindow.winfo_height()

            # Calculate subwindow's position to center it
            x = parent_x + (parent_width - subwindow_width) // 2
            y = parent_y + (parent_height - subwindow_height) // 2

            # Set the subwindow's geometry
            subwindow.geometry(f"{subwindow_width}x{subwindow_height}+{x}+{y}")

        self.subwindow = Toplevel(self.root, padx=20, pady=10)
        self.subwindow.title("Generating")
        self.subwindow.iconbitmap("icon.ico")

        self.progressbar = ttk.Progressbar(self.subwindow, orient=HORIZONTAL, length=200, mode='indeterminate')
        self.progressbar.grid(column=0, row=0, sticky=EW, columnspan=4)
        self.subwindow.grid_rowconfigure(0, weight=1)

        self.subwindow.transient(self.root)
        self.subwindow.grab_set()

        center_subwindow(self.root, self.subwindow)
        self.progressbar.grid()
        self.progressbar.start()

        self.results = {
            'success': False,
            'final_seed': ""
        }
        self.t = threading.Thread(target=MainRandomizerUI.thread_do_work, args=[
            self.random_seed.get(),
            self.enemy_data,
            self.random_pistol.get(),
            self.random_shops.get(),
            self.OUT_FOLDER_NAME,
            self.NO_PISTOL_RANDO_MANUAL_CHANGE,
            self.PISTOL_RANDO_MANUAL_CHANGE,
            self.SHOP_RANDO_MANUAL_CHANGE,
            self.random_doors.get(),
            self.random_enemies.get(),
            self.enemy_protect_pool,
            self.module_optionsvar.get(),
            self.limit_one_module_per_room.get(),
            self.module_door_optionsvar.get(),
            int(self.module_count_optionsvar.get()),
            self.PATH_TO_HLD,
            root,
            self.results
        ])
        self.t.daemon=True
        self.t.start()

        # self.subwindow.protocol("WM_DELETE_WINDOW", lambda: True)

        self.root.wait_window(self.subwindow)

    def gen_finish(self, e):
        self.progressbar.stop()
        if self.results['success']: 
            self.random_seed.set(self.results["final_seed"])
            messagebox.showinfo(message=f"Generation successful!\n\nSeed: " + str(self.results['final_seed']), title="Success")
            self.layers = self.results['layers']
        else: messagebox.showerror(message=f"Could not generate seed. Try again or try another seed if a seed was set.", title="Error")
        self.progressbar.grid_remove()
        self.subwindow.destroy()

    def __init__(self, root, path):
        self.root = root
        root.title("Hyper Light Drifter Randomizer")
        self.PATH_TO_HLD = path

        if not os.path.isdir('game_files'):
            setup_frame = ttk.Frame(root)
            setup_frame.grid(column=0, row=0, sticky=NE)
            ttk.Button(setup_frame, text="Set up Randomizer", command=self.do_install).grid(column=0, row=0, sticky=W, pady=5)
            ttk.Label(setup_frame, text="(Do this once if you haven't)").grid(column=1, row=0, sticky=W)
            return

            
        # Header #

        header_frame = ttk.Frame(root)
        header_frame.grid(column=0, row=1, sticky=NSEW,padx=10)

        ttk.Label(header_frame, text="Settings", justify=LEFT, font=("TkHeadingFont", 20)).grid(column=0, row=0, sticky=NW)
        header_frame.grid_columnconfigure(0, weight=1)

        sr_link = ttk.Label(header_frame, text="Speedrun Discord", justify=RIGHT, 
                                font=("TkDefaultFont", 10, "underline"),
                                foreground="blue",
                                cursor="hand2",
                            )
        sr_link.grid(column=4, row=0, sticky=E)
        sr_link.bind("<Button-1>", lambda e: self.open_link("https://discord.gg/gXFaGQd"))

        hm_link = ttk.Label(header_frame, text="Heart Machine Discord", justify=RIGHT,
                                font=("TkDefaultFont", 10, "underline"),
                                foreground="blue",
                                cursor="hand2",
                            )
        hm_link.grid(column=3, row=0, sticky=E)
        hm_link.bind("<Button-1>", lambda e: self.open_link("https://discord.gg/heartmachine"))


        # Seed settings #
        seed_frame = ttk.LabelFrame(root, text="Seed")
        seed_frame.grid(column=0, row=2, sticky=EW)

        self.random_seed = StringVar(value=None)
        ttk.Label(seed_frame, text="Seed (leave empty for a random seed)").grid(column=0, row=3, pady=5, padx=5)
        seed_entry = ttk.Entry(seed_frame, textvariable=self.random_seed, width=30)
        seed_entry.grid(column=1, row=3, sticky=EW, pady=5, padx=5)

        ttk.Button(seed_frame, text="Clear", command=lambda: self.random_seed.set("")).grid(column=2, row=3, sticky=NE, pady=5, padx=5)
        ttk.Button(seed_frame, text="Try weekly seed", command=self.set_weekly_seed).grid(column=1, row=4, sticky=NW, pady=5, padx=5)


        # Options settings #

        options_frame = ttk.LabelFrame(root, text="Options")
        options_frame.grid(column=0, row=3, sticky=EW)
        
        self.random_doors = BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text='Randomize rooms', 
	    variable=self.random_doors,
	    onvalue=True, offvalue= False).grid(column=0, row=4, sticky=W, pady=5, padx=5)

        self.random_enemies = BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text='Randomize enemies', 
	    variable=self.random_enemies,
	    onvalue=True, offvalue= False).grid(column=0, row=5, sticky=W, pady=5, padx=5)

        self.random_shops = BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text='Randomize shops (if unset, shops will stay in town)', 
	    variable=self.random_shops,
	    onvalue=True, offvalue= False).grid(column=1, row=4, sticky=W)

        self.random_pistol = BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text='Randomize pistol for NG', 
	    variable=self.random_pistol,
	    onvalue=True, offvalue= False).grid(column=1, row=5, sticky=W)

        
        # Progression settings #
        progression_frame = ttk.LabelFrame(root, text="Progression")
        progression_frame.grid(column=0, row=4, sticky=EW)
        ttk.Label(progression_frame, text="Progression item placement location pool").grid(column=0, row=6, sticky=E, pady=5, padx=5)
        module_options = [e.value for e in ItemPlacementRestriction]
        self.module_optionsvar = StringVar(value=ItemPlacementRestriction.MODULES_EXTENDED)
        module_settings_list = ttk.Combobox(progression_frame, textvariable=self.module_optionsvar, values=module_options, width=32)
        module_settings_list.grid(column=1, row=6, sticky=W, columnspan=3)
        module_settings_list.state(["readonly"])

        self.limit_one_module_per_room = BooleanVar(value=True)
        ttk.Checkbutton(progression_frame, text='Limit 1 module per room', 
	    variable=self.limit_one_module_per_room,
	    onvalue=True, offvalue= False).grid(column=1, row=7, sticky=W)

        self.module_door_label = ttk.Label(progression_frame, text="Module door")
        module_door_options = [e.value for e in ModuleDoorOptions]
        self.module_door_optionsvar = StringVar(value=ModuleDoorOptions.MIX)
        self.module_door_list = ttk.Combobox(progression_frame, textvariable=self.module_door_optionsvar, values=module_door_options)
        self.module_door_list.state(["readonly"])
        self.module_door_label.grid(column=0, row=9, sticky=E, padx=5, pady=5)
        self.module_door_list.grid(column=1, row= 9, sticky=W)

        self.module_count_label = ttk.Label(progression_frame, text="Module count")
        module_count_options = [e.value for e in ModuleCount]
        self.module_count_optionsvar = StringVar(value=ModuleCount.MINIMUM)
        self.module_count_list = ttk.Combobox(progression_frame, textvariable=self.module_count_optionsvar, values=module_count_options)
        self.module_count_list.state(["readonly"])

        self.module_count_label.grid(column=0, row =10, sticky=E, padx=5, pady=5)
        self.module_count_list.grid(column=1, row=10, sticky=W)

        # Enemy settings #
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
        
        enemy_pool_frame = ttk.LabelFrame(root, height=90, text="Enemies")
        enemy_pool_frame.grid(column=0, row=5, sticky=EW)

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
        buttons_frame.grid(column=0, row=6, columnspan=2)
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


        for child in enemy_pool_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)


        # Bottom buttons #
        bottom_frame = Frame(root)
        bottom_frame.grid(column=0, row=8, sticky=NSEW)


        # ttk.Button(bottom_frame, text="Push to HLD", command=self.do_push).grid(column=2,row=0)
        ttk.Button(bottom_frame, text="Check solution", command=self.show_solution).grid(column=1, row=0)
        ttk.Button(bottom_frame, text="Revert game to normal", command=self.do_revert).grid(column=0, row=0)
        # ttk.Button(bottom_frame, text="Close", command=root.destroy).grid(column=4, row=0)
        ttk.Button(bottom_frame, 
                   text="Generate", 
                   padding=10,
                   command= self.randomize).grid(column=3, row=0, sticky=NE)
        bottom_frame.grid_columnconfigure(3, weight=1)

        for child in bottom_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        

        # Frames configurations #

        root.bind("<<GenerationComplete>>", self.gen_finish)

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(1, weight=1)
        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(3, weight=1)
        root.grid_rowconfigure(4, weight=1)
        root.grid_rowconfigure(5, weight=1)
        for child in root.winfo_children(): 
            child.grid_configure(padx=15, pady=5)

root = Tk()
root.iconbitmap("icon.ico")

try:
    PATH_TO_HLD = HLDBasics.find_path()
    MainRandomizerUI(root, PATH_TO_HLD)
except ValueError as e:
    GamePathSetup(root)

root.mainloop()