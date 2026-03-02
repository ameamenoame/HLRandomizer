import threading
from tkinter import *
from tkinter import ttk, messagebox, scrolledtext
from time import time
from preset import PresetType, Preset, DEFAULT_SAVE_EDIT_NUMBER
from hldlib import HLDBasics, HLDLevel, HLDType
from hldlib.hldbasics import Direction
from randomizer import (
    VERSION_NUMBER,
    main,
    OUTPUT_PATH,
    BACKUP_FOLDER_NAME,
    ITEMLESS_FOLDER_NAME,
    DOORLESS_FOLDER_NAME,
    Inventory,
    BASE_LIST_OF_ENEMIES,
    BASE_ENEMY_PROTECT_POOL,
    ItemPlacementRestriction,
    ModuleCount,
    ModuleDoorOptions,
)
from solution import check_solution
from random import randrange
from save_edit import *
import shutil
from save_edit import autofill_path
import os
from json_generators import generate_all_jsons, PATH_TO_MANUAL
import platform
import getpass
from PIL import Image, ImageTk


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
            save_path = self.save_path.get().strip()
            with open("hlddir.txt", "w") as f:
                f.write("\n".join([path, save_path]))
            messagebox.showinfo(
                message="Game path set to "
                + path
                + "\nPlease close the randomizer and open it again to start the randomizer.",
                title="Success",
            )
            self.root.destroy()
        except:
            messagebox.showerror(message="Could not set game path.")

    def __init__(self, root):
        self.root = root
        root.title("Hyper Light Drifter Randomizer Path Setup")

        mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        system = platform.system()
        username = getpass.getuser()
        if system == "Linux":
            game_path = f"/home/{username}/.local/share/Steam/steamapps/common/HyperLightDrifter/assets"
        elif system == "Darwin":
            game_path = f"/Users/{username}/Library/Application Support/Steam/SteamApps/common/HyperLightDrifter/HyperLightDrifter.app/Contents/Resources"
        else:
            # defaulting to Windows
            game_path = (
                "C:\\Program Files (x86)\\Steam\\steamapps\\common\\HyperLightDrifter"
            )
        self.game_path = StringVar(value=game_path)
        game_path_entry = ttk.Entry(mainframe, textvariable=self.game_path, width=64)
        game_path_entry.grid(column=2, row=1, sticky=(W, E))

        ttk.Label(
            mainframe,
            text="Please specify the path to the game on disk (default is on the C drive but if you changed the installation location copy the path to it here)",
        ).grid(column=2, row=0, sticky=W)
        ttk.Button(mainframe, text="Set path", command=self.set_path, width=50).grid(
            column=1, row=4, sticky=NSEW, columnspan=2
        )

        ttk.Label(mainframe, text="Specify save path").grid(column=2, row=2, sticky=W)
        self.save_path = StringVar(value=autofill_path(None))
        save_path_entry = ttk.Entry(mainframe, textvariable=self.save_path, width=64)
        save_path_entry.grid(column=2, row=3, sticky=(W, E))

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
obj,Teleporter,9008,241,351,0,-999999,++,r=rm_C_DrifterWorkshop,d=9009,t=1,i=0,
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
    dungeon_mix_data = []
    final_mod_map = {}
    graph_data = None

    def do_install(self, *args):
        """
        Makes a backup of HLD levels and makes itemless and doorless copies of levels
        """

        ITEMS = [
            ",ModuleSocket",
            ",LibrarianTablet",
            ",DrifterBones_Outfit",
            "=GearbitCrate",
            ",DrifterBones_Key",
            ",DrifterBones_Weapon",
            "=Gearbit",
            ",NoCombat",
            ",NoShoot",
            ",Upgrade",
            "spr_NPC_teddy_idleSup",
            "spr_NPC_Fatso",
            "spr_NPC_akashecary_idleGrind",
            "spr_NPC_seanguin_idleThink",
            "spr_NPC_beau_idleTap",
        ]
        DOORS = ["j,door,", "j,Televator", "j,Teleporter", ",h=128,cs=3,"]
        start_time = time()
        levels = HLDBasics.omega_load(self.PATH_TO_HLD)

        def _remove_and_dump(
            levels: list[HLDLevel], objects_to_exclude: list[str], output_folder: str
        ):
            for level in levels:
                objs_to_remove = []
                for obj in level.object_list:
                    if any(item in obj.get_line() for item in objects_to_exclude):
                        objs_to_remove.append(obj)
                for obj in objs_to_remove:
                    level.object_list.remove(obj)
                level.dump_level(os.path.join(OUTPUT_PATH, output_folder, level.dir_))

        # REAL BACKUP
        for level_path, dir_, level_name in HLDBasics.get_levels(
            self.PATH_TO_HLD, HLDBasics.DIRS
        ):
            os.makedirs(
                path_to_save := os.path.join(OUTPUT_PATH, BACKUP_FOLDER_NAME, dir_),
                exist_ok=True,
            )
            shutil.copy(level_path, path_to_save)
        # FAKE BACKUP
        # _remove_and_dump(levels, ["DO NOT EXCLUDE ANYTHING"], BACKUP_FOLDER_NAME)
        _remove_and_dump(levels, ITEMS, ITEMLESS_FOLDER_NAME)
        _remove_and_dump(levels, DOORS, DOORLESS_FOLDER_NAME)

        end_time = time()
        print(f"Done in {end_time-start_time:.2f} s")
        messagebox.showinfo(
            message=f"Setup finished. You can now start randomization.", title="Done"
        )

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
            shutil.copytree(
                os.path.join(OUTPUT_PATH, folder_to_push),
                self.PATH_TO_HLD,
                dirs_exist_ok=True,
            )
            end_time = time()
            print(f"Done in {end_time-start_time:.2f} s")
            messagebox.showinfo(message="Reverted Hyper Light Drifter to normal")

    def disable_enemy(self):
        current_index = self.enemy_list.curselection()
        if current_index != ():
            i = current_index[0]
            if self.enemy_data[i]["enabled"]:
                self.enemy_choices[i] = "(DISABLED) " + self.enemy_data[i]["name"]
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

    def on_key_count_spinbox_changed(self):
        return

    def onspinboxreturn(self, _a):
        self.current_weightvar.set(self.spinbox.get())
        self.onspinboxchanged()
        self.enemy_list.focus()

    def show_solution(self):
        solution = check_solution(self.layers, self.final_mod_map, self.dungeon_mix_data)
        subwindow = Toplevel(self.root, padx=20, pady=10)
        subwindow.title("Solution")
        # .ico icons don't work on other platforms, skip for now
        if platform.system() == "Windows":
            subwindow.iconbitmap("icon.ico")

        text = scrolledtext.ScrolledText(subwindow)
        text.grid(sticky=NSEW)
        text.insert(INSERT, solution)
        text.configure(state='disabled')
        subwindow.rowconfigure(0, weight=1)

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
        preset,
        PATH_TO_HLD,
        root,
        results,
        use_chain_logic,
        key_count: int,
        even_item_distribution: bool = False,
        random_dungeon_entrances: bool = False,
        save_number: int = DEFAULT_SAVE_EDIT_NUMBER,
        shuffle_parallax: bool = False,
        shuffle_music: bool = False,
        no_logic: bool = False,
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
            preset,
            use_chain_logic,
            key_count: int,
            even_item_distribution: bool = False,
            random_dungeon_entrances: bool = False,
            save_number: int = DEFAULT_SAVE_EDIT_NUMBER,
            shuffle_parallax: bool = False,
            shuffle_music: bool = False,
            no_logic: bool = False,
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
            final_mod_map = None
            dungeon_mix_data = None
            graph_data = None

            using_preset_seed = random_seed

            bound = 1000000000000
            count = 0
            while count < 10:
                count += 1
                try:
                    if not using_preset_seed:
                        random_seed = str(randrange(-bound, bound))

                    final_enemy_list = []
                    for e in enemy_data:
                        if not e["enabled"]:
                            continue
                        final_enemy_list.append(e["name"])
                    final_enemy_weights = []
                    for e in enemy_data:
                        if not e["enabled"]:
                            continue
                        final_enemy_weights.append(e["weight"])

                    layers, final_mod_map, dungeon_mix_data, graph_data = main(
                        random_doors=random_doors,
                        random_enemies=random_enemies,
                        output=output,
                        output_folder_name=(
                            output_folder_name
                            if output_folder_name
                            else OUT_FOLDER_NAME
                        ),
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
                        preset=preset,
                        use_chain_logic=use_chain_logic,
                        key_count=key_count,
                        even_item_distribution=even_item_distribution,
                        random_dungeon_entrances=random_dungeon_entrances,
                        preset_save_number=save_number,
                        shuffle_parallax=shuffle_parallax,
                        shuffle_music=shuffle_music,
                        no_logic=no_logic
                    )
                    success = True
                    break
                except Exception as e:
                    if not using_preset_seed:
                        print("Retrying!")
                        print(str(e))
                        Inventory.reset()
                    else:
                        print(
                            f"We've encountered an '{e}' error. Try again or try another seed if seed used."
                        )
                        break

            return (success, random_seed, layers, final_mod_map, dungeon_mix_data, graph_data)

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
                shutil.copytree(
                    os.path.join(OUTPUT_PATH, folder_to_push),
                    PATH_TO_HLD,
                    dirs_exist_ok=True,
                )
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
            module_count_optionsvar,
            preset,
            use_chain_logic,
            key_count,
            even_item_distribution=even_item_distribution,
            random_dungeon_entrances=random_dungeon_entrances,
            save_number=save_number,
            shuffle_parallax=shuffle_parallax,
            shuffle_music=shuffle_music,
            no_logic=no_logic
        )

        # Definitely not thread safe
        results["success"] = gen_result[0]
        results["final_seed"] = gen_result[1]
        results["layers"] = gen_result[2]
        results["final_mod_map"] = gen_result[3]
        results["dungeon_mix_data"] = gen_result[4]
        results["graph_data"] = gen_result[5]

        if results["success"]:
            do_push(OUT_FOLDER_NAME, PATH_TO_HLD)

        root.event_generate("<<GenerationComplete>>")

    @staticmethod
    def center_subwindow(parent, subwindow):
        parent.update_idletasks()  # Ensure parent dimensions are accurate
        subwindow.update_idletasks()  # Ensure subwindow dimensions are accurate

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

    def randomize(self):

        self.subwindow = Toplevel(self.root, padx=20, pady=10)
        self.subwindow.title("Generating")
        # .ico icons don't work on other platforms, skip for now
        if platform.system() == "Windows":
            self.subwindow.iconbitmap("icon.ico")

        self.progressbar = ttk.Progressbar(
            self.subwindow, orient=HORIZONTAL, length=200, mode="indeterminate"
        )
        self.progressbar.grid(column=0, row=0, sticky=EW, columnspan=4)
        self.subwindow.grid_rowconfigure(0, weight=1)

        self.subwindow.transient(self.root)
        self.subwindow.grab_set()

        self.center_subwindow(self.root, self.subwindow)
        self.progressbar.grid()
        self.progressbar.start()

        self.results = {"success": False, "final_seed": ""}
        self.t = threading.Thread(
            target=MainRandomizerUI.thread_do_work,
            args=[
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
                self.preset_optionsvar.get(),
                self.PATH_TO_HLD,
                root,
                self.results,
                self.use_chain_logic.get(),
                int(self.key_countvar.get()),
                self.even_item_distribution.get(),
                self.random_dungeon_entrances.get(),
                int(self.save_numbervar.get()) - 1,
                self.shuffle_parallax.get(),
                self.shuffle_music.get(),
                self.no_logicvar.get(),
            ],
        )
        self.t.daemon = True
        self.t.start()

        # self.subwindow.protocol("WM_DELETE_WINDOW", lambda: True)

        self.root.wait_window(self.subwindow)

    def gen_finish(self, e):
        self.progressbar.stop()
        if self.results["success"]:
            self.random_seed.set(self.results["final_seed"])
            messagebox.showinfo(
                message=f"Generation successful!\n\nSeed: "
                + str(self.results["final_seed"]),
                title="Success",
            )
            self.layers = self.results["layers"]
            self.final_mod_map = self.results["final_mod_map"]
            self.dungeon_mix_data = self.results["dungeon_mix_data"]
            self.graph_data = self.results["graph_data"]
        else:
            messagebox.showerror(
                message=f"Could not generate seed. Try again or try another seed if a seed was set.",
                title="Error",
            )
        self.progressbar.grid_remove()
        self.subwindow.destroy()

    def _on_preset_selection(self, a, b, c):
        p: Preset = Preset.get_preset_from_name(self.preset_optionsvar.get())
        self.preset_description_label["text"] = (
            p.description
            + "\n\nPresets work by modifying an existing save file (YOU MAY LOSE SAVE DATA WHEN DOING THIS). To use presets, you must first create a new save file at a save slot (1-4). After generation, open the save to play the preset."
        )
        p.set_options(self)
        self.save_num_label.grid()
        self.save_number_picker.grid()

    def show_tracker(self):
        self.tracker = ItemTracker(
            self.root, HLDBasics.find_save_path(), self.random_shops, self.random_pistol, int(self.save_numbervar.get()) - 1, self.dungeon_mix_data != {}, self.dungeon_mix_data,
            self.final_mod_map, self.graph_data
        )
    def show_check_tracker(self):
        if not self.graph_data: 
            messagebox.showinfo(
                message="Generate a seed to use the check tracker",
                title="No generated seed found",
            )
            return
        window = Toplevel(self.root)
        window.title("Check Tracker")

        # .ico icons don't work on other platforms, skip for now
        if platform.system() == "Windows":
            window.iconbitmap("icon.ico")

        # Check tracker
        checks_frame = ttk.Frame(window, padding=(10, 10, 10, 10))
        checks_frame.grid(row=1, column=2, sticky=N, columnspan=4)

        count = 0
        levels_with_checks = {}
        dir_levels = {}
        for level in self.graph_data:
            for o in level.fake_object_list:
                if o.original_type.lower() in ["module", "bones"]:
                    name = level.name.lower().split("/")[0]
                    if name not in ["rm_c_central/out", "rm_c_central/hordedoor", "rm_pax_staging", "rm_c_ven_dash"]:
                        count+= 1
                        name = level.name.split("/")[0]

                        dir = HLDBasics.get_dir_from_room_name(name)
                        if "backertablet" in name.lower() :
                            dir = Direction.NORTH

                        if levels_with_checks.get(name):
                            levels_with_checks[name].append(o.original_type)
                        else:
                            levels_with_checks[name] = [o.original_type]

                        if not dir_levels.get(dir):
                            dir_levels[dir] = [name]
                        else:
                            if name not in dir_levels[dir]: dir_levels[dir].append(name)
                pass

        check_row = 0
        check_col = 0
        col = 0
        for d in [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]:
            d_frame = ttk.LabelFrame(checks_frame, text=d)
            d_frame.grid(row=1, column=col, padx=5, ipadx=5, ipady=5, sticky=NSEW)
            col+=1

            for l in dir_levels[d]:
                ttk.Label(d_frame, text=HLDBasics.get_human_room_name(l), font=("TkHeadingFont", 10, "bold")).grid(row=check_row, column=check_col, sticky=NW)
                check_row+=1
                for i in levels_with_checks[l]:
                    ttk.Checkbutton(d_frame, text=i + " check", onvalue=True, offvalue=False).grid(row=check_row, column=check_col, sticky=NW, padx=5)
                    check_row+=1
                ttk.Label(d_frame, text="").grid(row=check_row, column=check_col, sticky=NW, pady=3)
                check_row+=1
                if check_row >= 15:
                    check_row = 0
                    check_col += 1
            check_col += 1
            check_row = 0

        ttk.Label(checks_frame, text="Check tracker (manual) (%d checks) \n---------------" % count, font=("TkDefaultFont", 12)).grid(sticky=NW, row=0, column=0)

        return

    def __init__(self, root, path):
        self.root = root
        root.title("Hyper Light Drifter Randomizer")
        self.PATH_TO_HLD = path

        if not os.path.isdir("game_files"):
            self.setup_frame = ttk.Frame(root)
            self.setup_frame.grid(column=0, row=0, sticky=NE)
            ttk.Button(
                self.setup_frame,
                text="Set up Randomizer",
                command=lambda: self.do_install() or self.setup_frame.grid_forget(),
            ).grid(column=0, row=0, sticky=W, pady=5)
            ttk.Label(self.setup_frame, text="(Do this once if you haven't)").grid(
                column=1, row=0, sticky=W
            )

        # Header #

        header_frame = ttk.Frame(root)
        header_frame.grid(column=0, row=1, sticky=NSEW, padx=10, columnspan=2)

        ttk.Label(
            header_frame, text=VERSION_NUMBER, justify=LEFT, font=("TkHeadingFont", 20)
        ).grid(column=0, row=0, sticky=NW)
        header_frame.grid_columnconfigure(0, weight=1)

        sr_link = ttk.Label(
            header_frame,
            text="Speedrun Discord",
            justify=RIGHT,
            font=("TkDefaultFont", 10, "underline"),
            foreground="blue",
            cursor="hand2",
        )
        sr_link.grid(column=4, row=0, sticky=E)
        sr_link.bind(
            "<Button-1>", lambda e: self.open_link("https://discord.gg/gXFaGQd")
        )

        hm_link = ttk.Label(
            header_frame,
            text="Heart Machine Discord",
            justify=RIGHT,
            font=("TkDefaultFont", 10, "underline"),
            foreground="blue",
            cursor="hand2",
        )
        hm_link.grid(column=3, row=0, sticky=E)
        hm_link.bind(
            "<Button-1>", lambda e: self.open_link("https://discord.gg/heartmachine")
        )

        kb_link = ttk.Label(
            header_frame,
            text="Knowledge Base",
            justify=RIGHT,
            font=("TkDefaultFont", 10, "underline"),
            foreground="blue",
            cursor="hand2",
        )
        kb_link.grid(column=5, row=0, sticky=E)
        kb_link.bind(
            "<Button-1>",
            lambda e: self.open_link("https://ameamenoame.github.io/HLRandomizer/#/"),
        )

        for child in header_frame.winfo_children():
            child.grid_configure(padx=2, pady=5)

        # Seed settings #
        seed_frame = ttk.LabelFrame(root, text="Seed")
        seed_frame.grid(column=0, row=2, sticky=(N,W,E))

        self.random_seed = StringVar(value=None)
        ttk.Label(seed_frame, text="Seed (leave empty for a random seed)").grid(
            column=0, row=3, padx=5, sticky=(N,W,E)
        )
        seed_entry = ttk.Entry(seed_frame, textvariable=self.random_seed, width=30)
        seed_entry.grid(column=1, row=3, sticky=(N, E, W))

        ttk.Button(
            seed_frame, text="Clear", command=lambda: self.random_seed.set("")
        ).grid(column=2, row=3, sticky=NW, padx=5)
        ttk.Button(
            seed_frame, text="Try weekly seed", command=self.set_weekly_seed
        ).grid(column=1, row=4, sticky=NW, pady=5, padx=5)

        # Options settings #

        options_frame = ttk.LabelFrame(root, text="Options")
        options_frame.grid(column=0, row=3, sticky=(N, W, E))

        self.random_doors = BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Shuffle rooms",
            variable=self.random_doors,
            onvalue=True,
            offvalue=False,
        ).grid(column=0, row=4, sticky=W, pady=5, padx=5)

        self.random_enemies = BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Shuffle enemies",
            variable=self.random_enemies,
            onvalue=True,
            offvalue=False,
        ).grid(column=0, row=5, sticky=W, pady=5, padx=5)

        self.random_shops = BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Shuffle shops",
            variable=self.random_shops,
            onvalue=True,
            offvalue=False,
        ).grid(column=1, row=4, sticky=W)

        self.random_pistol = BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Shuffle pistol for NG",
            variable=self.random_pistol,
            onvalue=True,
            offvalue=False,
        ).grid(column=1, row=5, sticky=W)

        self.random_dungeon_entrances = BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Shuffle dungeon entrances",
            variable=self.random_dungeon_entrances,
            onvalue=True,
            offvalue=False,
        ).grid(column=0, row=6, sticky=W, padx=5, pady=5)

        self.shuffle_parallax = BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Shuffle parallax",
            variable=self.shuffle_parallax,
            onvalue=True,
            offvalue=False,
        ).grid(column=1, row=6, sticky=W, pady=5)

        self.shuffle_music = BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Shuffle music",
            variable=self.shuffle_music,
            onvalue=True,
            offvalue=False,
        ).grid(column=2, row=4, sticky=W, pady=5)

        # Progression settings #
        progression_frame = ttk.LabelFrame(root, text="Progression")
        progression_frame.grid(column=0, row=4, sticky=(N,W,E))

        self.use_chain_logic = BooleanVar(value=False)
        ttk.Checkbutton(
            progression_frame,
            text="Enable chain logic",
            variable=self.use_chain_logic,
            onvalue=True,
            offvalue=False,
        ).grid(column=0, row=5, sticky=W, padx=5, pady=5)

        self.no_logicvar = BooleanVar(value=False)
        ttk.Checkbutton(
            progression_frame,
            text="No logic",
            variable=self.no_logicvar,
            onvalue=True,
            offvalue=False,
        ).grid(column=1, row=5, sticky=W, padx=5, pady=5)

        ttk.Label(
            progression_frame, text="Progression item placement location pool"
        ).grid(column=0, row=6, sticky=E, pady=5, padx=5)
        module_options = [e.value for e in ItemPlacementRestriction]
        self.module_optionsvar = StringVar(
            value=ItemPlacementRestriction.FREE
        )
        module_settings_list = ttk.Combobox(
            progression_frame,
            textvariable=self.module_optionsvar,
            values=module_options,
            width=32,
        )
        module_settings_list.grid(column=1, row=6, sticky=W, columnspan=3)
        module_settings_list.state(["readonly"])

        self.limit_one_module_per_room = BooleanVar(value=True)
        ttk.Checkbutton(
            progression_frame,
            text="Limit 1 module per room",
            variable=self.limit_one_module_per_room,
            onvalue=True,
            offvalue=False,
        ).grid(column=1, row=7, sticky=W)

        self.module_door_label = ttk.Label(progression_frame, text="Module door")
        module_door_options = [e.value for e in ModuleDoorOptions]
        self.module_door_optionsvar = StringVar(value=ModuleDoorOptions.MIX)
        self.module_door_list = ttk.Combobox(
            progression_frame,
            textvariable=self.module_door_optionsvar,
            values=module_door_options,
        )
        self.module_door_list.state(["readonly"])
        self.module_door_label.grid(column=0, row=9, sticky=E, padx=5, pady=5)
        self.module_door_list.grid(column=1, row=9, sticky=W)

        self.module_count_label = ttk.Label(progression_frame, text="Module count")
        module_count_options = [e.value for e in ModuleCount]
        self.module_count_optionsvar = StringVar(value=ModuleCount.ALL)
        self.module_count_list = ttk.Combobox(
            progression_frame,
            textvariable=self.module_count_optionsvar,
            values=module_count_options,
        )
        self.module_count_list.state(["readonly"])

        self.module_count_label.grid(column=0, row=10, sticky=E, padx=5, pady=5)
        self.module_count_list.grid(column=1, row=10, sticky=W)


        ttk.Label(progression_frame, text="Key count").grid(column=0, row=11, sticky=NE, padx=5, pady=5)
        self.key_countvar = StringVar(value="16")
        self.key_count_spinbox = ttk.Spinbox(
            progression_frame,
            from_=0,
            to=16,
            textvariable=self.key_countvar,
            width=5,
            command=self.on_key_count_spinbox_changed,
            increment=1,
        )
        self.key_count_spinbox.grid(column=1, row=11, sticky=W)

        self.even_item_distribution = BooleanVar(value=False)
        ttk.Checkbutton(
            progression_frame,
            text="Equal item distribution across regions",
            variable=self.even_item_distribution,
            onvalue=True,
            offvalue=False,
        ).grid(column=1, row=12, sticky=W, pady=5)

        # Enemy settings #

        self.enemy_data = [
            {"name": e, "weight": 1.0, "enabled": True, "protected": False}
            for e in BASE_LIST_OF_ENEMIES
        ]
        for e in self.enemy_data:
            # Sensible defaults
            if e["name"] in ["Birdman", "slime", "spider", "Dirkommander"]:
                e["protected"] = True
            if e["name"] in ["Dirkommander"]:
                e["enabled"] = False

        self.enemy_choices = [
            e["name"] if e["enabled"] else ("(DISABLED) " + e["name"])
            for e in self.enemy_data
        ]
        self.enemy_choicesvar = StringVar(value=self.enemy_choices)

        enemy_pool_frame = ttk.LabelFrame(root, height=90, text="Enemies")
        enemy_pool_frame.grid(column=1, row=2, sticky=NSEW, rowspan=2)

        ttk.Label(
            enemy_pool_frame, text="Enemy pool", justify=CENTER, font=("TkHeadingFont")
        ).grid(column=0, row=0, sticky=NE)
        self.enemy_list = Listbox(
            enemy_pool_frame, listvariable=self.enemy_choicesvar, width=27
        )
        self.enemy_list.configure(exportselection=False)
        self.enemy_list.grid(column=1, row=0, sticky=W, rowspan=2)
        self.enemy_list.bind("<<ListboxSelect>>", self.onenemyselect)

        s = ttk.Scrollbar(
            enemy_pool_frame, orient=VERTICAL, command=self.enemy_list.yview
        )
        self.enemy_list.configure(yscrollcommand=s.set)
        s.grid(column=1, row=0, sticky=(N, S, E), rowspan=2)

        # Weight spinbox
        weight_frame = ttk.Frame(enemy_pool_frame)
        weight_frame.grid(column=2, row=0)
        ttk.Label(weight_frame, text="Weight").grid(column=0, row=0, sticky=NW)
        self.current_weightvar = StringVar()
        self.spinbox = ttk.Spinbox(
            weight_frame,
            from_=0.0,
            to=100.0,
            textvariable=self.current_weightvar,
            width=5,
            command=self.onspinboxchanged,
            increment=0.1,
        )
        self.spinbox.grid(column=1, row=0, sticky=NW, padx=5)
        self.spinbox.bind("<Return>", self.onspinboxreturn)

        # Pool edit buttons
        buttons_frame = ttk.Frame(enemy_pool_frame)
        buttons_frame.grid(column=0, row=6, columnspan=2)
        ttk.Button(buttons_frame, text="Enable", command=self.enable_enemy).grid(
            column=0,
            row=0,
        )
        ttk.Button(buttons_frame, text="Disable", command=self.disable_enemy).grid(
            column=1, row=0, padx=5
        )
        ttk.Button(
            buttons_frame, text="Toggle rando protection", command=self.protect_enemy
        ).grid(column=2, row=0, padx=5)

        # Protect pool
        protect_pool_frame = ttk.Frame(enemy_pool_frame)
        protect_pool_frame.grid(column=2, row=1, sticky=NW)
        ttk.Label(protect_pool_frame, text="Protect pool").grid(
            column=0, row=0, sticky=NW
        )

        self.enemy_protect_pool = [e["name"] for e in self.enemy_data if e["protected"]]
        self.enemy_protect_poolvar = StringVar(value=self.enemy_protect_pool)
        self.protect_list = Listbox(
            protect_pool_frame, listvariable=self.enemy_protect_poolvar
        )
        self.protect_list.grid(column=1, row=0, sticky=W, rowspan=2)

        for child in enemy_pool_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

        # PRESETS #
        preset_frame = ttk.LabelFrame(root, text="Presets")
        preset_frame.grid(column=1, row=4, sticky=(N, W, E), padx=5, pady=5)


        # Preset picker
        ttk.Label(preset_frame, text="Preset").grid(column=0, row=1, sticky=NW)
        preset_options = [e.value for e in PresetType]
        self.preset_optionsvar = StringVar(value=PresetType.NONE)
        self.preset_list = ttk.Combobox(
            preset_frame, textvariable=self.preset_optionsvar, values=preset_options
        )
        self.preset_list.grid(column=1, row=1, sticky=NW)
        self.preset_list.state(["readonly"])
        self.preset_description_label = ttk.Label(preset_frame, text="", wraplength=400)
        self.preset_description_label.grid(column=1, row=3, sticky=NW, columnspan=3)
        self.preset_optionsvar.trace("w", self._on_preset_selection)

        for child in preset_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

        # Save slot picker
        self.save_num_label = ttk.Label(preset_frame, text="Save slot")
        self.save_num_label.grid(column=0, row=2, sticky=NW, padx=5, pady=5)
        self.save_num_label.grid_remove()
        save_numbers = [1, 2, 3, 4]
        self.save_numbervar = StringVar(value=DEFAULT_SAVE_EDIT_NUMBER + 1)
        self.save_number_picker = ttk.Combobox(
            preset_frame, textvariable=self.save_numbervar, values=save_numbers
        )
        self.save_number_picker.grid(column=1, row=2, sticky=NW, padx=5, pady=5)
        self.save_number_picker.state(["readonly"])
        self.save_number_picker.grid_remove()

        # Bottom buttons #
        bottom_frame = ttk.Frame(root)
        bottom_frame.grid(column=0, row=9, sticky=NSEW, columnspan=3)

        # ttk.Button(bottom_frame, text="Push to HLD", command=self.do_push).grid(column=2,row=0)
        ttk.Button(bottom_frame, text="Check tracker", command=self.show_check_tracker).grid(
            column=3, row=0
        )
        ttk.Button(bottom_frame, text="Item tracker", command=self.show_tracker).grid(
            column=2, row=0
        )
        ttk.Button(
            bottom_frame, text="Check solution", command=self.show_solution
        ).grid(column=1, row=0)
        ttk.Button(
            bottom_frame, text="Revert game to normal", command=self.do_revert
        ).grid(column=0, row=0)
        # ttk.Button(bottom_frame, text="Close", command=root.destroy).grid(column=4, row=0)
        ttk.Button(
            bottom_frame, text="Generate", padding=10, command=self.randomize
        ).grid(column=4, row=0, sticky=NE)
        bottom_frame.grid_columnconfigure(4, weight=1)

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


class ItemTracker:
    class RepeatingTimer:
        def __init__(self, interval, function, *args, **kwargs):
            self.interval = interval
            self.function = function
            self.args = args
            self.kwargs = kwargs
            self._stop_event = threading.Event()
            self._timer = None

        def _run(self):
            if not self._stop_event.is_set():
                self.function(*self.args, **self.kwargs)
                self.start()  # schedule next call

        def start(self):
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()

        def stop(self):
            self._stop_event.set()
            if self._timer:
                self._timer.cancel()

    class ItemImage(ttk.Label):
        count = 0
        imgs = []
        def __init__(
            self,
            master,
            width=40,
            height=40,
            initial_state=False,
            path_prefix="mod_",
            range_size=5
        ):
            super().__init__(master)

            # Load and resize images to fixed size
            self.imgs = []
            for i in range(range_size):
                self.imgs.append(
                    ImageTk.PhotoImage(
                        Image.open(os.path.join("assets", "%s%d.png" % (path_prefix, i))).resize((40, 40), Image.LANCZOS)
                    )
                )

            # Load images
            self.img_on = self.imgs[0]

            self.state = initial_state
            self.update_image()

        def set_manual_image(self, path):
            img = ImageTk.PhotoImage(Image.open(path).resize((40, 40), Image.LANCZOS))
            self.img_on = img
            self.update_image()

        def update_image(self):
            self.config(image=self.img_on)

        def set_count(self, count: int):
            self.count = count
            if self.count >= len(self.imgs):
                self.count = len(self.imgs) - 1
            self.config(image=self.imgs[count])

    class ToggleImage(ttk.Label):
        counter = 0

        def __init__(
            self,
            master,
            img_on_path,
            img_off_path,
            width=40,
            height=40,
            initial_state=False,
            show_text = False,
            is_module = False
        ):
            super().__init__(master)

            if not is_module:
                # Load and resize images to fixed size
                img_on = Image.open(img_on_path).resize((width, height), Image.LANCZOS)
                img_off = Image.open(img_off_path).resize((width, height), Image.LANCZOS)

                # Load images
                self.img_on = ImageTk.PhotoImage(img_on)
                self.img_off = ImageTk.PhotoImage(img_off)
                self.show_text = show_text

                self.state = initial_state
                self.update_image()


                # Bind click toggle
                self.bind("<Button-1>", self.toggle)
                self.set_text("0")

        def set_text(self, _text: str):
            if not self.show_text: return
            self.config(text=_text, compound='center', font=("TkHeadingFont", 24), foreground="white")

        def set_off(self):
            self.state = False
            self.update_image()

        def set_on(self):
            self.state = True
            self.update_image()

        def set_counter(self, num: int):
            self.counter = num
            self.set_text(str(self.counter))

        def increment_counter(self):
            self.counter += 1
            self.set_text(str(self.counter))

        def toggle(self, event=None):
            self.state = not self.state
            self.update_image()

        def update_image(self):
            if self.state:
                self.config(image=self.img_on, text=self.counter)
            else:
                self.config(image=self.img_off, text=self.counter)
            if self.show_text:
                self.config(compound='center')


    def poll_save(self, save_path, save_edit_number, entrance_data, mod_map):
        

        print("Polling save...")

        metadata = SaveMetadata(None, save_path)
        savedata_map = savedata_load(metadata, [0, save_edit_number])

        self.track_keys(savedata_map)

        self.toggle_item("laser", self.has_laser(savedata_map))

        for s in self.skills.keys():
            self.toggle_item(s, self.has_skill(savedata_map, str(self.skills[s])))

        self.toggle_item("pistol", self.has_pistol(savedata_map))

        def toggle_if_have(item: str, arg):
            val = False
            if item.startswith("pylon"):
                val = self.has_pylon(savedata_map, arg)

            if val:
                self.toggle_item(item, True)
            else:
                self.toggle_item(item, False)

        toggle_if_have("pylon_north", "north")
        toggle_if_have("pylon_east", "east")
        toggle_if_have("pylon_west", "west")
        toggle_if_have("pylon_south", "south")

        self.track_modules(savedata_map, mod_map)
        self.track_bits(savedata_map)
        self.track_grenades(savedata_map)
        self.track_heal_ups(savedata_map)
        self.track_outfit(savedata_map)

        if entrance_data != {}:
            # Track visited entrances
            mapping: dict = {}
            empty_mapping = {}
            for row in entrance_data:
                from_entrance = row['from'].lower().split('/')[0]
                to_entrance = row['to_random']['to'].lower().split('/')[0]

                og_to = row['to'].split("/")[0]
                # text += f"{row['from']:<10} -> {row['to_random']['to']:<5} (OG: {row['to']})\n"
                mapping[to_entrance] = from_entrance

                # mapping[from_entrance] = to_entrance

                name_mapping = HLDBasics.room_name_str_mapping()
                human_from =  HLDBasics.room_names[name_mapping[from_entrance]][1]
                human_to = HLDBasics.room_names[name_mapping[to_entrance]][1]
                og_to = HLDBasics.room_names[name_mapping[og_to.lower()]][1]

                empty_mapping[to_entrance] = {"random": None, "og": og_to, 
                                              "human_from": human_from,
                                              "human_to": human_to
                                              }


            # Get visited rooms
            visited = self.get_visited_rooms(savedata_map)

            for v in visited:
                if not HLDBasics.room_names.get(v): continue
                name: str = HLDBasics.room_names[v][0]
                if mapping.get(name) != None:
                    empty_mapping[     name       ]["random"] = mapping[name]
                    
            dir_mapping = {
                "North": "North\n-----\n",
                "East": "East\n-----\n",
                "West": "West\n-----\n",
                "South": "South\n-----\n",
            }
            for k in empty_mapping.keys():
                if empty_mapping[k]["random"] != None:
                    # text = empty_mapping[k]["human_from"] + " -> " + empty_mapping[k]["human_to"] + (" (%s entrance)" % empty_mapping[k]["og"]) + "\n"
                    text = ("%s entrance" % empty_mapping[k]["og"]) + ' -> ' + empty_mapping[k]["human_to"] + "\n"
                    dir_mapping[self.get_dir_from_lvl_name(empty_mapping[k]["random"])] += text
                    

            final_text = "ENTRANCE TRACKER\n------------------\n"
            for k in dir_mapping.keys():
                final_text += dir_mapping[k] + "\n"
            self.entrance_textvar.set(final_text)

    @staticmethod
    def get_visited_rooms(savedata_map) -> list[int]:
        rooms = savedata_map["rooms"].value.split("+")
        result = []
        for r in rooms:
            if r == "" or r == None: 
                continue
            result.append(int(r))
        return result

    @staticmethod
    def has_laser(savedata_map):
        return "21" in savedata_map["sc"].value or "23" in savedata_map["sc"].value

    @staticmethod
    def has_key(savedata_map):
        return savedata_map["drifterkey"].value > 0

    @staticmethod
    def has_dash(savedata_map):
        return "4" in savedata_map["skill"].value

    @staticmethod 
    def has_skill(savedata_map, skill):
        return skill in savedata_map["skill"].value

    @staticmethod
    def has_pistol(savedata_map):
        return "1" in savedata_map["sc"].value.split("+")

    @staticmethod
    def has_pylon(savedata_map, dir):
        val = None
        if dir == "east":
            val = 0
        elif dir == "north":
            val = 1
        elif dir == "west":
            val = 2
        elif dir == "south":
            val = 3
        return str(val) in savedata_map["wellMap"].value

    @staticmethod
    def has_modules(savedata_map, dir):
        return savedata_map["mapMod"].value.count(">") >= 16

    def toggle_item(self, name: str, state: bool = True):
        obj = None
        if name == "laser":
            obj = self.laser
        elif name == "key":
            obj = self.key
        elif name == "dash":
            obj = self.skills_widgets["dash"]
        elif name == "jab":
            obj = self.skills_widgets["jab"]
        elif name == "shield":
            obj = self.skills_widgets["shield"]
        elif name == "slash":
            obj = self.skills_widgets["slash"]
        elif name == "phantom":
            obj = self.skills_widgets["phantom"]
        elif name == "deflect":
            obj = self.skills_widgets["deflect"]
        elif name == "pistol":
            obj = self.pistol
        elif name == "pylon_north":
            obj = self.wells["well_north"]
        elif name == "pylon_east":
            obj = self.wells["well_east"]
        elif name == "pylon_west":
            obj = self.wells["well_west"]
        elif name == "pylon_south":
            obj = self.wells["well_south"]
        elif name == "module_north":
            obj = self.modules[Direction.NORTH]
        elif name == "module_west":
            obj = self.modules[Direction.WEST]
        elif name == "module_east":
            obj = self.modules[Direction.EAST]
        elif name == "module_south":
            obj = self.modules[Direction.SOUTH]
        elif name == "all_modules":
            # obj = self.modules
            # for o in obj.values():
            #     o.state = state
            #     o.update_image()
            return

        obj.state = state
        obj.update_image()
        return

    def track_keys(self, savedata_map):
        key_count = int(savedata_map['drifterkey'].value)

        if key_count > 0:
            self.toggle_item("key")
            self.key_text.config(
text=key_count, font=("TkHeadingFont", 14, "bold")
            )

    def track_grenades(self, savedata_map):
        g_count = int(savedata_map["specialUp"].value)
        self.grenade.set_count(g_count)

    def track_heal_ups(self, savedata_map):
        h_count = int(savedata_map["healthUp"].value)
        self.heal_up.set_count(h_count)

    def track_outfit(self, savedata_map):
        comp = int(savedata_map["compShell"].value)
        self.comp.set_count(comp)

        is_alt = savedata_map["CH"].value != 0.0
        cape = int(savedata_map["cape"].value)
        if cape == 0 and is_alt:
            self.cloak.set_manual_image(os.path.join("assets", "cl_0_alt.png"))
        else:
            self.cloak.set_count(cape)

        sword = int(savedata_map["sword"].value)
        self.sword.set_count(sword)

    @staticmethod
    def get_dir_from_lvl_name(name: str):
        code = name.split("_")[1]
        match code[0]:
            case "n":
                return Direction.NORTH
            case "w":
                return Direction.WEST
            case "e":
                return Direction.EAST
            case _:
                return Direction.SOUTH

    def track_bits(self, savedata_map):
        bit_count = savedata_map["gear"].value
        big_bit_count = bit_count / 4
        small_bit_count = bit_count % 4
        if big_bit_count == 0 and small_bit_count == 0:
            self.bit.set_off()
            self.bit_text.grid_forget()
            return
        else:
            self.bit.set_on()
            small_bit_text = ['', '⠁' ,'⠉', '⠋'][int(small_bit_count)]
            self.bit_text.config(text="%d %s" % (big_bit_count, small_bit_text), compound='center', font=("TkHeadingFont", 14, "bold"))
            self.bit_text.grid()

    def track_modules(self, savedata_map, mod_map):
        tokens = savedata_map["mapMod"].value.split("&>")
        module_locations = []
        for token in tokens:
            if token != None and token != "":
                module_locations.append(int(token.split("=")[0]))


        mapping = {
            "North": 0,
            "West": 0,
            "East": 0,
            "South": 0,
        }
        for module in module_locations:
            dir = self.get_dir_from_lvl_name(   HLDBasics.room_names[module][0]  )
            mapping[dir] += 1
        for k in mapping.keys():
            self.modules[k].set_count(min(mapping[k], 4))
        return

    def __init__(
        self,
        parent,
        save_path: str,
        track_dash_shop: bool = False,
        track_pistol: bool = False,
        save_edit_number: int = 3,
        entrance_track: bool = False,
        entrance_data: dict = {},
        mod_map: dict = {},
        graph_data: dict = {}
    ):
        self.window = Toplevel(parent)
        self.window.title("Item Tracker")
        # self.window.attributes('-topmost', True)

        # .ico icons don't work on other platforms, skip for now
        if platform.system() == "Windows":
            self.window.iconbitmap("icon.ico")

        row = ttk.Frame(self.window, padding=(10, 10, 10, 20))
        row.grid(row=1, sticky=N)
        self.window.columnconfigure(0, weight=0)
        self.window.columnconfigure(1, weight=1)

        path_on = os.path.join("assets", "module_icon_on.png")
        path_off = os.path.join("assets", "module_icon_off.png")
        laser_on = os.path.join("assets", "laser.png")
        laser_off = os.path.join("assets", "laser_off.png")
        key_on = os.path.join("assets", "key.png")
        key_off = os.path.join("assets", "key_off.png")

        pistol_on = os.path.join("assets", "pistol_on.png")
        pistol_off = os.path.join("assets", "pistol_off.png")

        dash_on = os.path.join("assets", "dash_on.png")
        dash_off = os.path.join("assets", "dash_off.png")

        img_paths = [
            (path_on, path_off),
            (path_on, path_off),
            (path_on, path_off),
            (path_on, path_off),
        ]

        i = 0
        directions = ["North", "East", "West", "South"]
        for direction in directions:
            widget = ttk.Label(row, text=direction)
            widget.grid(row=0, column=i, padx=5, pady=5)
            i += 1

        self.modules = {}
        for col, (on_path, off_path) in enumerate(img_paths):
            self.modules[directions[col]] = self.ItemImage(row)
            self.modules[directions[col]].grid(row=1, column=col, padx=5)

        self.laser = self.ToggleImage(row, laser_on, laser_off)
        self.laser.grid(row=3, column=2, padx=5, pady=5, sticky=N)

        # Key
        self.key_frame = ttk.Frame(row)
        self.key_frame.grid(row=3, column=1, padx=5, pady=5, sticky=N)

        self.key = self.ToggleImage(self.key_frame, key_on, key_off)
        self.key.grid(sticky=N)
        self.key_text = ttk.Label(self.key_frame)
        self.key_text.grid(row=1, padx=5, sticky=N)

        

        # Skills
        self.skills = {
            "slash": 1,
            "deflect": 2,
            "phantom": 3,
            "dash": 4,
            "shield": 5,
            "jab": 6,
        }
        self.skills_widgets = {}
        skill_col_count = 0
        skill_row_count = 4
        for s in self.skills:
            self.skills_widgets[s] = self.ToggleImage(row, os.path.join("assets", "%s_on.png" % s), os.path.join("assets", "%s_off.png" % s))
            self.skills_widgets[s].grid(row=skill_row_count, column=skill_col_count, padx=5)
            skill_col_count += 1
            if skill_col_count > 2:
                skill_col_count = 0
                skill_row_count+=1


        # Pistol
        self.pistol = self.ToggleImage(row, pistol_on, pistol_off)
        self.pistol.grid(row=3, column=3, padx=5, pady=5, sticky=N)


        # Bits

        self.bit_frame = ttk.Frame(row)
        self.bit_frame.grid(row=3, column=0, pady=5, sticky=N)

        self.bit = self.ToggleImage(
            self.bit_frame,
            os.path.join("assets", "bit_on.png"),
            os.path.join("assets", "bit_off.png"),
        )
        self.bit.grid(row=0, column=0, sticky=N)
        self.bit_text = ttk.Label(self.bit_frame, text="bit count")
        self.bit_text.grid(row=1, column=0, sticky=N)

        # Grenades
        self.grenade = self.ItemImage(
            row, path_prefix="g_",
            range_size=3
        )
        self.grenade.grid(row=4, column=3)

        # Heal ups
        self.heal_up = self.ItemImage(
            row, path_prefix="heal_",
            range_size=3
        )
        self.heal_up.grid(row=5, column=3)

        # Outfit
        self.cloak = self.ItemImage(row, path_prefix="cl_", range_size=11)
        self.cloak.grid(row=6, column=2)
        self.sword = self.ItemImage(row, path_prefix="sw_", range_size=11)
        self.sword.grid(row=6, column=1)
        self.comp = self.ItemImage(row, path_prefix="comp_", range_size=11)
        self.comp.grid(row=6, column=0)

        # Wells
        i = 0
        self.wells = {}
        for direction in ["north", "east", "west", "south"]:
            self.wells[f"well_{direction}"] = self.ToggleImage(
                row,
                os.path.join("assets", f"well_{direction}.png"),
                os.path.join("assets", "well_off.png"),
                height=75,
            )
            self.wells[f"well_{direction}"].grid(row=2, column=i, padx=5, pady=5)
            i += 1




        # Entrance data
        self.entrance_textvar = StringVar(value="")
        ttk.Label(self.window, textvariable=self.entrance_textvar, font=("TkDefaultFont", 12)).grid(row=1, column=1, pady=5, padx=5, sticky=NW)

        self.window.rowconfigure(1, weight=0)
        self.window.rowconfigure(2, weight=0)

        self.save_edit_number = save_edit_number
        ttk.Label(self.window, text="Tracking save " + str(self.save_edit_number + 1)).grid(
            row=0, column=0, pady=5, padx=5, sticky=N
        )

        

        MainRandomizerUI.center_subwindow(parent, self.window)
        # self.window.transient(parent)
        # self.window.grab_set()

        self.poll_save(save_path, self.save_edit_number, entrance_data, mod_map)
        self.poll_job = self.RepeatingTimer(
            15.0, lambda: self.poll_save(save_path, self.save_edit_number, entrance_data, mod_map)
        )
        self.poll_job.start()

        def _on_close():
            self.poll_job.stop()
            self.window.destroy()

        self.window.protocol("WM_DELETE_WINDOW", _on_close)

root = Tk()

# .ico icons don't work on other platforms, skip for now
if platform.system() == "Windows":
    root.iconbitmap("icon.ico")

try:
    PATH_TO_HLD = HLDBasics.find_path()
    MainRandomizerUI(root, PATH_TO_HLD)
except ValueError as e:
    GamePathSetup(root)

root.mainloop()
