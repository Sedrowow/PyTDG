#!/usr/bin/env python3
"""
Main entry point for Terminal LifeRPG application.
"""

import sys
import time
from datetime import datetime
from utils import Colors, GameContext, p_line, read_key, clear_full_screen
from status import StatusManager
from tasks import TaskManager
from item import ItemManager
from shopcasino import ShopCasinoManager
from settings import SettingsManager

class LifeRPGApp:
    def __init__(self):
        self.ctx = GameContext()
        self.status_mgr = StatusManager(self.ctx)
        self.task_mgr = TaskManager(self.ctx, self.status_mgr)
        self.item_mgr = ItemManager(self.ctx, self.status_mgr)
        self.shop_mgr = ShopCasinoManager(self.ctx, self.status_mgr, self.item_mgr)
        self.settings_mgr = SettingsManager(self.ctx, self.status_mgr)

    def run(self):
        clear_full_screen()
        self.settings_mgr.check_initial_sample_prompt()

        menu_options = [
            "1. Tasks List",
            "2. Inventory & Consumables",
            "3. Shop & Casino",
            "4. Crafting Workshop",
            "5. Active Timers Manager (Hotkey 'T')",
            "6. Settings & Profile Manager",
            "7. Quick Adjust HP (Hotkey 'L')",
            "0. Exit Game"
        ]
        selected_idx = 0
        last_sec = -1
        needs_redraw = True

        with self.ctx.cbreak_term:
            while True:
                now_sec = datetime.now().second
                if needs_redraw or now_sec != last_sec:
                    self.status_mgr.display_status_header()
                    p_line(f"{Colors.BOLD}MAIN MENU:{Colors.RESET}")
                    for idx, opt in enumerate(menu_options):
                        cursor = "► " if idx == selected_idx else "  "
                        line = f"{cursor}{opt}"
                        if idx == selected_idx:
                            p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                        else:
                            p_line(line)

                    p_line()
                    p_line("-" * 70)
                    p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Navigate  [ENTER] Select  [1-7, T, L, 0/Q] Hotkeys")
                    
                    last_sec = now_sec
                    needs_redraw = False

                key = read_key(timeout=0.03)
                if not key:
                    continue

                needs_redraw = True
                key_upper = key.upper() if isinstance(key, str) else ""

                if key == "UP":
                    selected_idx = (selected_idx - 1) % len(menu_options)
                elif key == "DOWN":
                    selected_idx = (selected_idx + 1) % len(menu_options)
                elif key == "ENTER":
                    if selected_idx == 0: self.task_mgr.task_menu()
                    elif selected_idx == 1: self.item_mgr.inventory_menu()
                    elif selected_idx == 2: self.shop_mgr.shop_menu()
                    elif selected_idx == 3: self.item_mgr.crafting_menu()
                    elif selected_idx == 4: self.status_mgr.timer_manager_menu()
                    elif selected_idx == 5: self.settings_mgr.settings_menu()
                    elif selected_idx == 6: self.status_mgr.quick_adjust_hp()
                    elif selected_idx == 7:
                        self.ctx.save_data()
                        clear_full_screen()
                        print(f"{Colors.GREEN}Progress saved. Goodbye!{Colors.RESET}")
                        sys.exit(0)
                elif key_upper in ("1", "2", "3", "4", "5", "6", "7", "T", "L", "0", "Q"):
                    if key_upper == "1": self.task_mgr.task_menu()
                    elif key_upper == "2": self.item_mgr.inventory_menu()
                    elif key_upper == "3": self.shop_mgr.shop_menu()
                    elif key_upper == "4": self.item_mgr.crafting_menu()
                    elif key_upper in ("5", "T"): self.status_mgr.timer_manager_menu()
                    elif key_upper == "6": self.settings_mgr.settings_menu()
                    elif key_upper in ("7", "L"): self.status_mgr.quick_adjust_hp()
                    elif key_upper in ("0", "Q"):
                        self.ctx.save_data()
                        clear_full_screen()
                        print(f"{Colors.GREEN}Progress saved. Goodbye!{Colors.RESET}")
                        sys.exit(0)

if __name__ == "__main__":
    app = LifeRPGApp()
    app.run()