#!/usr/bin/env python3
"""
Settings & Profile Management Module.
"""

import time
from datetime import datetime, timedelta
from utils import Colors, GameContext, p_line, read_key, clear_full_screen, DEFAULT_PROFILE, DEFAULT_DATA
from status import StatusManager

class SettingsManager:
    def __init__(self, ctx: GameContext, status_mgr: StatusManager):
        self.ctx = ctx
        self.status_mgr = status_mgr

    def generate_sample_data(self):
        prof = self.ctx.get_profile()
        now_dt = datetime.now()

        prof["tasks"] = [
            {
                "id": 1, "title": "Morning Workout", "category": "Fitness", "skill": "Fitness",
                "difficulty": 50, "urgency": 40, "fear": 10, "interval_val": 1, "interval_unit": "days",
                "due_datetime": (now_dt + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
                "max_repeats": 5, "current_repeats": 0, "streak": 2, "reward_type": "HP",
                "money_reward": 10.0, "reward_item": "Health Potion", "penalty_type": "HP Loss", "penalty_val": 15.0
            },
            {
                "id": 2, "title": "Python Micro-Practice", "category": "Study", "skill": "Coding",
                "difficulty": 85, "urgency": 70, "fear": 50, "interval_val": 30, "interval_unit": "minutes",
                "due_datetime": (now_dt + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M"),
                "max_repeats": 3, "current_repeats": 0, "streak": 0, "reward_type": "Item",
                "money_reward": 25.0, "reward_item": "EXP Bottle", "penalty_type": "Penalty Timer", "penalty_val": 30.0
            }
        ]

        self.ctx.data["items"] = DEFAULT_DATA["items"].copy()

        self.ctx.data["shop"] = [
            {
                "id": 1, "name": "Health Potion", "color": "RED", "price": 20.0,
                "description": "Restores 30 HP instantly.", "type": "heal_fixed", "value": 30.0
            },
            {
                "id": 2, "name": "Plinko Peg Drop", "color": "CYAN", "price": 10.0,
                "description": "Drop a chip through the peg grid into outcome buckets!", "type": "plinko",
                "symbols": self.ctx.get_default_5x5_symbols()
            },
            {
                "id": 3, "name": "1x5 Wheel of Fortune", "color": "GOLD", "price": 15.0,
                "description": "Spin the 1x5 symbol strip to hit the center pointer!", "type": "wheel",
                "symbols": self.ctx.get_default_5x5_symbols()
            }
        ]

        self.ctx.data["crafting"] = [
            {
                "id": 1, "name": "Super EXP Elixir", "color": "PURPLE",
                "description": "Boosts main EXP by 25%.", "ingredients": {"Health Potion": 2},
                "result_item": "Super EXP Elixir", "result_qty": 1, "type": "exp_pct", "value": 25.0
            }
        ]
        self.ctx.save_data()

    def check_initial_sample_prompt(self):
        prof = self.ctx.get_profile()
        if len(prof["tasks"]) == 0 and len(self.ctx.data["shop"]) == 0:
            clear_full_screen()
            print(f"{Colors.BOLD}{Colors.YELLOW}Welcome to LifeRPG!{Colors.RESET}")
            print("Your task list and shop are currently empty.\n")
            ans = self.ctx.prompt_input("Would you like to generate sample starter tasks & shop items? (Y/n): ")
            if not ans or ans.lower().startswith("y"):
                self.generate_sample_data()
                print(f"{Colors.GREEN}Sample tasks, shop games, and items created!{Colors.RESET}")
                time.sleep(1.2)

    def settings_menu(self):
        opts = [
            "1. Edit Active Character Stats",
            "2. Switch Active Profile",
            "3. Create New Profile",
            "4. Delete Profile",
            "5. Generate Sample Tasks & Shop Items",
            "0. Back to Main Menu"
        ]
        sel = 0
        last_sec = -1
        needs_redraw = True

        while True:
            now_sec = datetime.now().second
            if needs_redraw or now_sec != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- SETTINGS & PROFILE MANAGER ---{Colors.RESET}")
                p_line()
                for idx, opt in enumerate(opts):
                    cursor = "► " if idx == sel else "  "
                    line = f"{cursor}{opt}"
                    if idx == sel:
                        p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                    else:
                        p_line(line)
                last_sec = now_sec
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            if key == "UP": sel = (sel - 1) % len(opts)
            elif key == "DOWN": sel = (sel + 1) % len(opts)
            elif key in ("1", "2", "3", "4", "5", "0"):
                sel = ["1", "2", "3", "4", "5", "0"].index(key)
                key = "ENTER"

            if key == "ENTER":
                if sel == 0:
                    prof = self.ctx.get_profile()
                    fields = [
                        {"key": "name", "label": "Character Name", "type": "text", "val": prof["name"]},
                        {"key": "level", "label": "Main Level", "type": "number", "val": prof["level"]},
                        {"key": "exp", "label": "Main EXP", "type": "number", "val": prof["exp"]},
                        {"key": "money", "label": "Wallet Money ($)", "type": "number", "val": prof["money"]},
                        {"key": "max_hp", "label": "Max HP", "type": "number", "val": prof["max_hp"]},
                        {"key": "hp_scale_mode", "label": "HP Scale Mode", "type": "select", "val": prof["hp_scale_mode"], "options": ["percentage", "static"]},
                        {"key": "hp_scale_value", "label": "HP Scale Value", "type": "number", "val": prof["hp_scale_value"]},
                        {"key": "SAVE", "label": "SAVE STATS", "type": "button"},
                        {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                    ]
                    res = self.ctx.run_menu_form("Character Stats", fields, self.status_mgr.display_status_header)
                    if res:
                        old_m = prof["money"]
                        new_m = float(res["money"])
                        prof["name"] = str(res["name"])
                        prof["level"] = int(res["level"])
                        prof["exp"] = int(res["exp"])
                        prof["max_hp"] = float(res["max_hp"])
                        prof["hp"] = min(prof["hp"], prof["max_hp"])
                        prof["hp_scale_mode"] = str(res["hp_scale_mode"])
                        prof["hp_scale_value"] = float(res["hp_scale_value"])
                        self.status_mgr.animate_money_change(old_m, new_m)

                elif sel == 1:
                    p_keys = list(self.ctx.data["profiles"].keys())
                    p_names = [self.ctx.data["profiles"][k]["name"] for k in p_keys]
                    print("\nAvailable Profiles: " + ", ".join(f"[{k}: {n}]" for k, n in zip(p_keys, p_names)))
                    target = self.ctx.prompt_input("Enter Profile ID to activate: ")
                    if target in self.ctx.data["profiles"]:
                        self.ctx.data["active_profile_id"] = target
                        self.ctx.save_data()

                elif sel == 2:
                    new_id = f"p_{int(time.time())}"
                    p_name = self.ctx.prompt_input("Enter New Profile Name: ") or "Hero"
                    new_prof = DEFAULT_PROFILE.copy()
                    new_prof["name"] = p_name
                    new_prof["tasks"] = []
                    new_prof["inventory"] = {}
                    self.ctx.data["profiles"][new_id] = new_prof
                    self.ctx.data["active_profile_id"] = new_id
                    self.ctx.save_data()

                elif sel == 3:
                    if len(self.ctx.data["profiles"]) <= 1:
                        print(f"\n{Colors.RED}Cannot delete the only existing profile!{Colors.RESET}")
                        time.sleep(1.2)
                    else:
                        target = self.ctx.prompt_input("Enter Profile ID to Delete: ")
                        if target in self.ctx.data["profiles"]:
                            conf = self.ctx.prompt_input(f"Confirm deletion of profile '{self.ctx.data['profiles'][target]['name']}'? (y/N): ")
                            if conf.lower().startswith("y"):
                                del self.ctx.data["profiles"][target]
                                if self.ctx.data["active_profile_id"] == target:
                                    self.ctx.data["active_profile_id"] = list(self.ctx.data["profiles"].keys())[0]
                                self.ctx.save_data()

                elif sel == 4:
                    self.generate_sample_data()
                    print(f"\n{Colors.GREEN}Sample tasks, shop games, and items generated!{Colors.RESET}")
                    time.sleep(1.2)

                elif sel == 5:
                    break
                clear_full_screen()

            elif key == "ESC":
                break
        clear_full_screen()