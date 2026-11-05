#!/usr/bin/env python3
"""
Casino Module with 5x3 Multi-Win Grid Slots, CS:GO Ticker Loot Wheel, Mystery Chests, and Plinko Coin Drop.
"""

import time
import random
from typing import Dict, List, Any, Optional
from utils import Colors, GameContext, p_line, read_key, clear_full_screen, DEFAULT_5x5_ARTS
from status import StatusManager

CASINO_TYPES = ("slotmachine", "slotmachine_5x3", "wheel", "chests", "coindrop")

RARE_BANNER = [
    "  ____     _     ____  _____   _   _ _____ _   _ _ ",
    " |  _ \\   / \\   |  _ \\| ____| | | | |_   _| \\ | | |",
    " | |_) | / _ \\  | |_) |  _|   | | | | | | |  \\| | |",
    " |  _ < / ___ \\ |  _ <| |___  | |_| | | | | |\\  |_|",
    " |_| \\_/_/   \\_\\|_| \\_\\_____|  \\___/  |_| |_| \\_(_)"
]

JACKPOT_BANNER = [
    "  _   _ _____  ____ _  _______   ___ _____ _ ",
    " | | / \\|_   _|/ ___| |/ /  _  \\ / _ \\_   _| |",
    " | |/ _ \\ | | | |   | ' /| |_) |/ /_\\ \\| | | |",
    " | / ___ \\| | | |___| . \\|  __/|  _  || | |_|",
    " |/_/   \\_\\_|  \\____|_|\\_\\_|   |_| |_||_| (_)"
]

class CasinoManager:
    def __init__(self, ctx: GameContext, status_mgr: StatusManager):
        self.ctx = ctx
        self.status_mgr = status_mgr

    def get_casino_items(self) -> List[Dict[str, Any]]:
        return [i for i in self.ctx.data["shop"] if i.get("type") in CASINO_TYPES]

    def show_victory_banner(self, tier: str):
        banner = JACKPOT_BANNER if tier == "Jackpot" else RARE_BANNER
        colors = [Colors.GOLD, Colors.YELLOW, Colors.CYAN, Colors.MAGENTA, Colors.GREEN]

        for step in range(6):
            c_code = colors[step % len(colors)]
            self.status_mgr.display_status_header()
            p_line()
            for line in banner:
                p_line(f"   {c_code}{Colors.BOLD}{line}{Colors.RESET}")
            p_line()
            time.sleep(0.1)

    def casino_menu(self):
        clear_full_screen()
        selected_idx = 0
        last_sec = -1
        needs_redraw = True

        while True:
            casino_games = self.get_casino_items()
            prof = self.ctx.get_profile()
            if selected_idx >= len(casino_games):
                selected_idx = max(0, len(casino_games) - 1)

            now_sec = time.time()
            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- CASINO FLOOR ---{Colors.RESET}")
                p_line(f"Wallet: {Colors.YELLOW}${prof['money']:.2f}{Colors.RESET}")
                p_line()

                if not casino_games:
                    p_line(f"{Colors.GREY}Casino floor is empty. Press 'E' to enter Edit Mode and add games.{Colors.RESET}")
                else:
                    for idx, item in enumerate(casino_games):
                        cursor = "► " if idx == selected_idx else "  "
                        color_code = Colors.parse_color(item.get("color", "GOLD"))
                        item_str = f"[{item['id']}] {item['name']:<22} ${item['price']:<8.2f} - {item.get('description', '')}"
                        line = f"{cursor}{color_code}{item_str}{Colors.RESET}"
                        if idx == selected_idx:
                            p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                        else:
                            p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select Game  [ENTER] Play Game  [E] Edit Mode  [0/ESC] Back")
                last_sec = int(now_sec)
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            key_upper = key.upper() if isinstance(key, str) else ""

            if key == "UP":
                selected_idx = (selected_idx - 1) % len(casino_games) if casino_games else 0
            elif key == "DOWN":
                selected_idx = (selected_idx + 1) % len(casino_games) if casino_games else 0
            elif key == "ENTER" and casino_games:
                item = casino_games[selected_idx]
                gtype = item.get("type")
                if gtype == "slotmachine":
                    self.run_slot_machine(item)
                    clear_full_screen()
                elif gtype == "slotmachine_5x3":
                    self.run_slot_machine_5x3(item)
                    clear_full_screen()
                elif gtype == "chests":
                    self.run_mystery_chests(item)
                    clear_full_screen()
                elif gtype == "wheel":
                    self.run_spinning_wheel(item)
                    clear_full_screen()
                elif gtype == "coindrop":
                    self.run_coin_drop(item)
                    clear_full_screen()
            elif key_upper == "E":
                self.casino_edit_mode()
                clear_full_screen()
            elif key in ("0", "ESC") or key_upper == "Q":
                break
        clear_full_screen()

    def casino_edit_mode(self):
        clear_full_screen()
        sel = 0
        last_sec = -1
        needs_redraw = True

        while True:
            casino_games = self.get_casino_items()
            footer_items = [
                {"id": -3, "name": "[+ Create 3-Reel Slot Machine...]", "is_create_slot_machine": True},
                {"id": -4, "name": "[+ Create 5x3 Multi-Win Slot Machine...]", "is_create_slot_5x3": True},
                {"id": -5, "name": "[+ Create Mystery Chests...]", "is_create_chests": True},
                {"id": -6, "name": "[+ Create CS:GO Loot Wheel (1x5)...]", "is_create_wheel": True},
                {"id": -7, "name": "[+ Create Plinko Coin Drop...]", "is_create_coindrop": True}
            ]
            items = casino_games + footer_items

            if sel >= len(items):
                sel = max(0, len(items) - 1)

            now_sec = time.time()
            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- CASINO EDIT MODE ---{Colors.RESET}")
                p_line(f"{Colors.CYAN}Select a casino game with Arrow Keys and press ENTER to edit details or odds.{Colors.RESET}")
                p_line()

                for idx, item in enumerate(items):
                    cursor = "► " if idx == sel else "  "
                    if item.get("name", "").startswith("[+ Create"):
                        line = f"{cursor}{Colors.GREEN}{item['name']}{Colors.RESET}"
                    else:
                        color_code = Colors.parse_color(item.get("color", "GOLD"))
                        type_tag = f"[{item.get('type', 'game').upper()}]"
                        line = f"{cursor}{color_code}{item['name']:<22}{Colors.RESET} ${item.get('price', 0.0):<6.2f} {type_tag}"

                    if idx == sel:
                        p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                    else:
                        p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select Game  [ENTER] Manage / Action  [0/ESC] Exit Edit Mode")
                last_sec = int(now_sec)
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            key_upper = key.upper() if isinstance(key, str) else ""

            if key == "UP":
                sel = (sel - 1) % len(items)
            elif key == "DOWN":
                sel = (sel + 1) % len(items)
            elif key == "ENTER":
                selected_item = items[sel]
                if selected_item.get("is_create_slot_machine"):
                    fields = [
                        {"key": "name", "label": "Slot Machine Name", "type": "text", "val": "3-Reel Classic Slot"},
                        {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": "GOLD"},
                        {"key": "price", "label": "Spin Cost ($)", "type": "number", "val": 10.0},
                        {"key": "description", "label": "Description", "type": "text", "val": "Spin 3 reels for rewards!"},
                        {"key": "SAVE", "label": "SAVE SLOT MACHINE", "type": "button"},
                        {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                    ]
                    res = self.ctx.run_menu_form("Create 3-Reel Slot Machine", fields, self.status_mgr.display_status_header)
                    if res:
                        new_id = max([i["id"] for i in self.ctx.data["shop"]], default=0) + 1
                        self.ctx.data["shop"].append({
                            "id": new_id, "name": str(res["name"]), "color": str(res["color"]),
                            "price": float(res["price"]), "description": str(res["description"]),
                            "type": "slotmachine", "cost": float(res["price"]), "symbols": self.ctx.get_default_5x5_symbols()
                        })
                        self.ctx.save_data()
                elif selected_item.get("is_create_slot_5x3"):
                    fields = [
                        {"key": "name", "label": "Mega Slot Name", "type": "text", "val": "5x3 Multi-Win Slots"},
                        {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": "PURPLE"},
                        {"key": "price", "label": "Spin Cost ($)", "type": "number", "val": 20.0},
                        {"key": "description", "label": "Description", "type": "text", "val": "5-Reel 3-Row slot grid with row & column multi-wins!"},
                        {"key": "SAVE", "label": "SAVE 5x3 SLOT", "type": "button"},
                        {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                    ]
                    res = self.ctx.run_menu_form("Create 5x3 Multi-Win Slot", fields, self.status_mgr.display_status_header)
                    if res:
                        new_id = max([i["id"] for i in self.ctx.data["shop"]], default=0) + 1
                        self.ctx.data["shop"].append({
                            "id": new_id, "name": str(res["name"]), "color": str(res["color"]),
                            "price": float(res["price"]), "description": str(res["description"]),
                            "type": "slotmachine_5x3", "cost": float(res["price"]), "symbols": self.ctx.get_default_5x5_symbols()
                        })
                        self.ctx.save_data()
                elif selected_item.get("is_create_chests"):
                    fields = [
                        {"key": "name", "label": "Mystery Chests Name", "type": "text", "val": "Lucky Mystery Chests"},
                        {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": "CYAN"},
                        {"key": "price", "label": "Play Cost ($)", "type": "number", "val": 10.0},
                        {"key": "description", "label": "Description", "type": "text", "val": "Pick 1 of 3 chests to reveal instant wins or traps!"},
                        {"key": "SAVE", "label": "SAVE MYSTERY CHESTS", "type": "button"},
                        {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                    ]
                    res = self.ctx.run_menu_form("Create Mystery Chests", fields, self.status_mgr.display_status_header)
                    if res:
                        new_id = max([i["id"] for i in self.ctx.data["shop"]], default=0) + 1
                        self.ctx.data["shop"].append({
                            "id": new_id, "name": str(res["name"]), "color": str(res["color"]),
                            "price": float(res["price"]), "description": str(res["description"]),
                            "type": "chests", "symbols": self.ctx.get_default_5x5_symbols()
                        })
                        self.ctx.save_data()
                elif selected_item.get("is_create_wheel"):
                    fields = [
                        {"key": "name", "label": "Loot Wheel Name", "type": "text", "val": "CS:GO Loot Wheel"},
                        {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": "GOLD"},
                        {"key": "price", "label": "Spin Cost ($)", "type": "number", "val": 15.0},
                        {"key": "description", "label": "Description", "type": "text", "val": "Right-to-left CS:GO style ticker stream reel!"},
                        {"key": "SAVE", "label": "SAVE LOOT WHEEL", "type": "button"},
                        {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                    ]
                    res = self.ctx.run_menu_form("Create CS:GO Loot Wheel", fields, self.status_mgr.display_status_header)
                    if res:
                        new_id = max([i["id"] for i in self.ctx.data["shop"]], default=0) + 1
                        self.ctx.data["shop"].append({
                            "id": new_id, "name": str(res["name"]), "color": str(res["color"]),
                            "price": float(res["price"]), "description": str(res["description"]),
                            "type": "wheel", "symbols": self.ctx.get_default_5x5_symbols()
                        })
                        self.ctx.save_data()
                elif selected_item.get("is_create_coindrop"):
                    fields = [
                        {"key": "name", "label": "Coin Drop Name", "type": "text", "val": "Plinko Coin Drop"},
                        {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": "YELLOW"},
                        {"key": "price", "label": "Play Cost ($)", "type": "number", "val": 12.0},
                        {"key": "description", "label": "Description", "type": "text", "val": "Drop an animated coin into clear basket buckets!"},
                        {"key": "SAVE", "label": "SAVE COIN DROP", "type": "button"},
                        {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                    ]
                    res = self.ctx.run_menu_form("Create Coin Drop", fields, self.status_mgr.display_status_header)
                    if res:
                        new_id = max([i["id"] for i in self.ctx.data["shop"]], default=0) + 1
                        self.ctx.data["shop"].append({
                            "id": new_id, "name": str(res["name"]), "color": str(res["color"]),
                            "price": float(res["price"]), "description": str(res["description"]),
                            "type": "coindrop", "symbols": self.ctx.get_default_5x5_symbols()
                        })
                        self.ctx.save_data()
                else:
                    item = selected_item
                    opts = ["1. Edit Game Details", "2. Manage Symbols, Odds & Pixel Art", "3. Delete Game", "0. Cancel"]
                    choice = self.ctx.run_action_menu(f"Casino Game: {item['name']}", opts, self.status_mgr.display_status_header)
                    if choice == 0:
                        fields = [
                            {"key": "name", "label": "Game Name", "type": "text", "val": item["name"]},
                            {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": item.get("color", "GOLD")},
                            {"key": "price", "label": "Cost ($)", "type": "number", "val": item.get("price", 10.0)},
                            {"key": "description", "label": "Description", "type": "text", "val": item.get("description", "")},
                            {"key": "SAVE", "label": "SAVE GAME", "type": "button"},
                            {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                        ]
                        res = self.ctx.run_menu_form(f"Edit Game: {item['name']}", fields, self.status_mgr.display_status_header)
                        if res:
                            item["name"] = str(res["name"])
                            item["color"] = str(res["color"])
                            item["price"] = float(res["price"])
                            item["description"] = str(res["description"])
                            item["cost"] = float(res["price"])
                            self.ctx.save_data()
                    elif choice == 1:
                        self.manage_5x5_symbols_and_odds(item)
                    elif choice == 2:
                        self.ctx.data["shop"] = [x for x in self.ctx.data["shop"] if x["id"] != item["id"]]
                        self.ctx.save_data()
                clear_full_screen()

            elif key in ("0", "ESC") or key_upper in ("Q", "E"):
                break
        clear_full_screen()

    # --- CASINO: MYSTERY CHESTS GAME ---
    def run_mystery_chests(self, item: Dict[str, Any]):
        prof = self.ctx.get_profile()
        cost = float(item.get("price", 10.0))
        symbols = item.get("symbols") or self.ctx.get_default_5x5_symbols()

        if prof["money"] < cost:
            print(f"\n{Colors.RED}Not enough money to play! (Cost: ${cost:.2f}){Colors.RESET}")
            time.sleep(1.2)
            return

        chest_opts = ["1. Mystery Chest #1", "2. Mystery Chest #2", "3. Mystery Chest #3", "0. Cancel"]
        chosen_i = self.ctx.run_action_menu("Pick 1 of 3 Mystery Chests", chest_opts, self.status_mgr.display_status_header)
        if chosen_i is None or chosen_i == 3:
            return

        old_money = prof["money"]
        self.status_mgr.animate_money_change(old_money, old_money - cost)

        chest_outcomes = [self.pick_weighted_symbol(symbols) for _ in range(3)]

        for step in range(8):
            self.status_mgr.display_status_header()
            p_line(f"{Colors.BOLD}{Colors.PURPLE}--- MYSTERY CHESTS: {item['name'].upper()} ---{Colors.RESET}")
            p_line()

            cards_line = ""
            for i in range(3):
                pointer = " ▼ " if i == chosen_i else "   "
                cards_line += f"  {Colors.YELLOW}{pointer}{Colors.RESET}  "
            p_line(cards_line)

            for line_idx in range(5):
                row_str = " | ".join([
                    f"{Colors.parse_color(sym.get('color', 'WHITE'))}{sym.get('art', DEFAULT_5x5_ARTS['COIN'])[line_idx]}{Colors.RESET}" if step >= 4 else f"{Colors.GREY}[ ? ? ? ]{Colors.RESET}"
                    for sym in chest_outcomes
                ])
                p_line(f"   | {row_str} |")

            p_line()
            time.sleep(0.08)

        winning_sym = chest_outcomes[chosen_i]
        p_line("-" * 70)
        p_line(f"{Colors.BOLD}YOU REVEALED CHEST #{chosen_i + 1}: {winning_sym['name'].upper()}!{Colors.RESET}")
        self.apply_symbol_outcome(winning_sym, multiplier=1.0)
        self.ctx.prompt_input("\nPress Enter to continue...")

    # --- CASINO: CS:GO STYLE LOOT WHEEL (RIGHT TO LEFT) ---
    def run_spinning_wheel(self, item: Dict[str, Any]):
        prof = self.ctx.get_profile()
        cost = float(item.get("price", 15.0))
        symbols = item.get("symbols") or self.ctx.get_default_5x5_symbols()

        if prof["money"] < cost:
            print(f"\n{Colors.RED}Not enough money to spin! (Cost: ${cost:.2f}){Colors.RESET}")
            time.sleep(1.2)
            return

        old_money = prof["money"]
        self.status_mgr.animate_money_change(old_money, old_money - cost)

        winning_sym = self.pick_weighted_symbol(symbols)
        
        total_stream_len = 35
        win_pos = 28
        stream = [self.pick_weighted_symbol(symbols) for _ in range(total_stream_len)]
        stream[win_pos] = winning_sym

        end_offset = win_pos - 2

        for step in range(end_offset + 1):
            reel = stream[step : step + 5]

            self.status_mgr.display_status_header()
            p_line(f"{Colors.BOLD}{Colors.GOLD}--- CS:GO LOOT WHEEL (RIGHT TO LEFT): {item['name'].upper()} ---{Colors.RESET}")
            p_line()
            p_line("                         ▼ WIN POINTER (CENTER) ▼")

            for line_idx in range(5):
                row_str = " | ".join([
                    f"{Colors.parse_color(s.get('color', 'WHITE'))}{s.get('art', DEFAULT_5x5_ARTS['STAR'])[line_idx]}{Colors.RESET}"
                    for s in reel
                ])
                p_line(f"   | {row_str} |")

            p_line("                         ▲ WIN POINTER (CENTER) ▲")
            p_line()

            progress = step / float(end_offset)
            delay = 0.03 + (progress ** 2.5) * 0.35
            time.sleep(delay)

        p_line("-" * 70)
        p_line(f"{Colors.GREEN}{Colors.BOLD}CENTER POINTER LANDED ON: {winning_sym['name'].upper()}!{Colors.RESET}")
        self.apply_symbol_outcome(winning_sym, multiplier=1.0)
        self.ctx.prompt_input("\nPress Enter to continue...")

    # --- CASINO: 5x3 MULTI-WIN SLOT MACHINE ---
    def run_slot_machine_5x3(self, item: Dict[str, Any]):
        prof = self.ctx.get_profile()
        cost = float(item.get("cost", item.get("price", 20.0)))
        symbols = item.get("symbols") or self.ctx.get_default_5x5_symbols()

        if prof["money"] < cost:
            print(f"\n{Colors.RED}Not enough money to play! (Cost: ${cost:.2f}){Colors.RESET}")
            time.sleep(1.2)
            return

        old_money = prof["money"]
        self.status_mgr.animate_money_change(old_money, old_money - cost)

        num_cols = 5
        num_rows = 3
        final_grid = [
            [self.pick_weighted_symbol(symbols) for _ in range(num_rows)]
            for _ in range(num_cols)
        ]

        total_steps = 16

        for step in range(total_steps):
            curr_grid = []
            for col in range(num_cols):
                stop_step = 4 + (col * 2)
                if step >= stop_step:
                    curr_grid.append(final_grid[col])
                else:
                    curr_grid.append([self.pick_weighted_symbol(symbols) for _ in range(num_rows)])

            self.status_mgr.display_status_header()
            p_line(f"{Colors.BOLD}{Colors.GOLD}--- 5x3 MULTI-WIN SLOT MACHINE: {item['name'].upper()} ---{Colors.RESET}")
            p_line()

            for row in range(num_rows):
                for line_idx in range(5):
                    col_strs = []
                    for col in range(num_cols):
                        sym = curr_grid[col][row]
                        c_code = Colors.parse_color(sym.get("color", "WHITE"))
                        art_line = sym.get("art", DEFAULT_5x5_ARTS["COIN"])[line_idx]
                        col_strs.append(f"{c_code}{art_line}{Colors.RESET}")
                    p_line("   | " + " | ".join(col_strs) + " |")
                p_line()

            time.sleep(0.05 + (step * 0.006))

        # Evaluate Multi-Wins Across All Rows & Columns
        wins = []

        # Check 3 Horizontal Rows
        for r_idx in range(3):
            row_syms = [final_grid[c][r_idx] for c in range(5)]
            row_ids = [s["id"] for s in row_syms]
            counts = {sid: row_ids.count(sid) for sid in set(row_ids)}
            max_c = max(counts.values())
            best_id = max(counts, key=counts.get)
            if max_c >= 3:
                matched_sym = next(s for s in row_syms if s["id"] == best_id)
                mult = 5.0 if max_c == 5 else (3.0 if max_c == 4 else 1.5)
                wins.append((f"Row #{r_idx + 1} ({max_c}-in-a-Row)", matched_sym, mult))

        # Check 5 Vertical Columns
        for c_idx in range(5):
            col_syms = [final_grid[c_idx][r] for r in range(3)]
            col_ids = [s["id"] for s in col_syms]
            if col_ids[0] == col_ids[1] == col_ids[2]:
                matched_sym = col_syms[0]
                wins.append((f"Column #{c_idx + 1} Full Column Match", matched_sym, 1.5))

        p_line("-" * 70)
        p_line(f"{Colors.BOLD}5x3 SLOT RESULTS:{Colors.RESET}")

        if not wins:
            p_line(f"{Colors.GREY}No matching row or column combinations. Better luck next spin!{Colors.RESET}")
        else:
            p_line(f"{Colors.GREEN}{Colors.BOLD}🎉 MULTI-WIN MATCHES DETECTED ({len(wins)} Line Wins)!{Colors.RESET}")
            for win_label, win_sym, mult in wins:
                p_line(f"   • {Colors.CYAN}{win_label}{Colors.RESET} -> {win_sym['name']} (x{mult:.1f})")
                self.apply_symbol_outcome(win_sym, multiplier=mult)

        self.ctx.save_data()
        self.ctx.prompt_input("\nPress Enter to continue...")

    # --- CASINO: COIN DROP / PLINKO GAME (WITH CLEAR BASKETS & PAUSE) ---
    def run_coin_drop(self, item: Dict[str, Any]):
        prof = self.ctx.get_profile()
        cost = float(item.get("price", 12.0))
        symbols = item.get("symbols") or self.ctx.get_default_5x5_symbols()

        if prof["money"] < cost:
            print(f"\n{Colors.RED}Not enough money to play! (Cost: ${cost:.2f}){Colors.RESET}")
            time.sleep(1.2)
            return

        num_slots = 5
        slot_symbols = (symbols * 2)[:num_slots]

        old_money = prof["money"]
        self.status_mgr.animate_money_change(old_money, old_money - cost)

        num_peg_rows = 6
        landing_slot = random.randint(0, num_slots - 1)

        # Animate bouncing down pegs
        for r in range(num_peg_rows):
            self.status_mgr.display_status_header()
            p_line(f"{Colors.BOLD}{Colors.GOLD}--- PLINKO COIN DROP: {item['name'].upper()} ---{Colors.RESET}")
            p_line()

            curr_slot_pos = min(num_slots - 1, max(0, landing_slot + random.choice([-1, 0, 1]))) if r < num_peg_rows - 1 else landing_slot

            for row in range(num_peg_rows):
                peg_line = "   "
                for s_i in range(num_slots):
                    if row == r and s_i == curr_slot_pos:
                        peg_line += f"  {Colors.YELLOW}{Colors.BOLD}🟡{Colors.RESET}  "
                    else:
                        peg_line += f"  {Colors.GREY}•{Colors.RESET}  "
                p_line(peg_line)

            # Draw Basket Buckets
            p_line("   " + " \\___/ " * num_slots)
            basket_labels = "   " + "".join([
                f"|{Colors.parse_color(s.get('color', 'WHITE'))}{s['name'][:5]:^5}{Colors.RESET}|"
                for s in slot_symbols
            ])
            p_line(basket_labels)
            p_line()

            time.sleep(0.18)

        # LANDING IN BASKET: Render Coin Resting inside the Basket Bucket
        self.status_mgr.display_status_header()
        p_line(f"{Colors.BOLD}{Colors.GOLD}--- PLINKO COIN DROP: {item['name'].upper()} ---{Colors.RESET}")
        p_line()

        for row in range(num_peg_rows):
            p_line("   " + f"  {Colors.GREY}•{Colors.RESET}  " * num_slots)

        p_line("   " + " \\___/ " * num_slots)

        basket_contents = "   "
        for s_i in range(num_slots):
            if s_i == landing_slot:
                basket_contents += f"|{Colors.YELLOW}{Colors.BOLD}  🟡 {Colors.RESET}|"
            else:
                c_code = Colors.parse_color(slot_symbols[s_i].get("color", "WHITE"))
                basket_contents += f"|{c_code}{slot_symbols[s_i]['name'][:5]:^5}{Colors.RESET}|"

        p_line(basket_contents)
        p_line()
        p_line(f"               {Colors.YELLOW}► COIN RESTING IN BASKET #{landing_slot + 1} ◄{Colors.RESET}")

        # Pause so player clearly sees where the coin rested
        time.sleep(1.2)

        winning_sym = slot_symbols[landing_slot]
        p_line("-" * 70)
        p_line(f"{Colors.GREEN}{Colors.BOLD}COIN LANDED IN BASKET #{landing_slot + 1}: {winning_sym['name'].upper()}!{Colors.RESET}")
        self.apply_symbol_outcome(winning_sym, multiplier=1.0)
        self.ctx.prompt_input("\nPress Enter to continue...")

    def pick_weighted_symbol(self, symbols: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not symbols:
            return self.ctx.get_default_5x5_symbols()[0]
        weights = [max(1, int(s.get("weight", 10))) for s in symbols]
        return random.choices(symbols, weights=weights, k=1)[0]

    def run_slot_machine(self, item: Dict[str, Any]):
        prof = self.ctx.get_profile()
        cost = float(item.get("cost", item.get("price", 10.0)))
        symbols = item.get("symbols") or self.ctx.get_default_5x5_symbols()

        if prof["money"] < cost:
            print(f"\n{Colors.RED}Not enough money to play! (Cost: ${cost:.2f}){Colors.RESET}")
            time.sleep(1.2)
            return

        old_money = prof["money"]
        self.status_mgr.animate_money_change(old_money, old_money - cost)

        num_wheels = 3
        final_symbols = [self.pick_weighted_symbol(symbols) for _ in range(num_wheels)]
        total_steps = 10 + (num_wheels * 2)

        for step in range(total_steps):
            current_symbols = [
                final_symbols[i] if step >= 6 + (i * 2) else self.pick_weighted_symbol(symbols)
                for i in range(num_wheels)
            ]
            self.status_mgr.display_status_header()
            p_line(f"{Colors.BOLD}{Colors.GOLD}--- 3-REEL SLOT MACHINE: {item['name'].upper()} ---{Colors.RESET}")
            p_line()

            for line_idx in range(5):
                row_str = " | ".join([
                    f"{Colors.parse_color(sym.get('color', 'WHITE'))}{sym.get('art', DEFAULT_5x5_ARTS['COIN'])[line_idx]}{Colors.RESET}"
                    for sym in current_symbols
                ])
                p_line(f"   | {row_str} |")

            p_line()
            time.sleep(0.06 + (step * 0.005))

        self.status_mgr.display_status_header()
        p_line(f"{Colors.BOLD}{Colors.GOLD}--- 3-REEL SLOT MACHINE: {item['name'].upper()} ---{Colors.RESET}")
        p_line()
        for line_idx in range(5):
            row_str = " | ".join([
                f"{Colors.parse_color(sym.get('color', 'WHITE'))}{sym.get('art', DEFAULT_5x5_ARTS['COIN'])[line_idx]}{Colors.RESET}"
                for sym in final_symbols
            ])
            p_line(f"   | {row_str} |")
        p_line()

        s1, s2, s3 = final_symbols
        p_line("-" * 70)
        p_line(f"{Colors.BOLD}SLOT MACHINE RESULTS:{Colors.RESET}")

        if s1["id"] == s2["id"] == s3["id"]:
            p_line(f"{Colors.GREEN}{Colors.BOLD}🎉 TRIPLE MATCH: 3x {s1['name']}!{Colors.RESET}")
            self.apply_symbol_outcome(s1, multiplier=3.0)
        elif s1["id"] == s2["id"] or s2["id"] == s3["id"] or s1["id"] == s3["id"]:
            matched_sym = s1 if s1["id"] == s2["id"] or s1["id"] == s3["id"] else s2
            p_line(f"{Colors.CYAN}{Colors.BOLD}✨ DOUBLE MATCH: 2x {matched_sym['name']}!{Colors.RESET}")
            self.apply_symbol_outcome(matched_sym, multiplier=1.5)
        else:
            p_line(f"{Colors.GREY}No matching combination. Better luck next time!{Colors.RESET}")

        self.ctx.save_data()
        self.ctx.prompt_input("\nPress Enter to continue...")

    def apply_symbol_outcome(self, sym: Dict[str, Any], multiplier: float = 1.0):
        prof = self.ctx.get_profile()
        tier = str(sym.get("tier", "Normal"))

        if tier in ("Rare", "Jackpot"):
            self.show_victory_banner(tier)

        rtype = sym.get("reward_type", "Money Gain")
        val = float(sym.get("val", 10.0)) * multiplier

        target_skill = str(sym.get("target_skill", "None"))
        skill_val = float(sym.get("skill_val", 0.0)) * multiplier

        if rtype == "Money Gain":
            old_m = prof["money"]
            p_line(f"   • Won: +{Colors.GREEN}${val:.2f}{Colors.RESET}")
            self.status_mgr.animate_money_change(old_m, old_m + val)
        elif rtype == "Money Loss":
            old_m = prof["money"]
            p_line(f"   • Lost: -{Colors.RED}${val:.2f}{Colors.RESET}")
            self.status_mgr.animate_money_change(old_m, max(0.0, old_m - val))
        elif rtype == "HP Heal":
            old_hp = prof["hp"]
            target_hp = min(prof["max_hp"], old_hp + val)
            p_line(f"   • Healed: +{Colors.GREEN}{val:.0f} HP{Colors.RESET}")
            self.status_mgr.animate_hp_change(old_hp, target_hp)
        elif rtype == "HP Loss":
            old_hp = prof["hp"]
            target_hp = max(0.0, old_hp - val)
            p_line(f"   • Suffered: -{Colors.RED}{val:.0f} HP Damage{Colors.RESET}")
            self.status_mgr.animate_hp_change(old_hp, target_hp)
        elif rtype == "EXP Gain":
            p_line(f"   • Gained: +{Colors.GREEN}{int(val)} Main EXP{Colors.RESET}")
            if target_skill != "None" and skill_val > 0:
                p_line(f"   • Skill EXP ({target_skill}): +{Colors.BLUE}{int(skill_val)}{Colors.RESET}")
                self.status_mgr.add_exp_animated(int(val), target_skill, int(skill_val))
            else:
                self.status_mgr.add_exp_animated(int(val), skill_name=None, skill_exp_gain=0)
        elif rtype == "Skill EXP Gain":
            if target_skill != "None" and val > 0:
                p_line(f"   • Gained Skill EXP ({target_skill}): +{Colors.BLUE}{int(val)}{Colors.RESET}")
                self.status_mgr.add_exp_animated(0, target_skill, int(val))
        elif rtype == "EXP Loss":
            prof["exp"] = max(0, prof["exp"] - int(val))
            p_line(f"   • Lost: -{Colors.RED}{int(val)} Main EXP{Colors.RESET}")
            self.ctx.save_data()
            self.status_mgr.display_status_header()
        elif rtype == "Item Win":
            item_n = sym.get("item_name", "Health Potion")
            prof["inventory"][item_n] = prof["inventory"].get(item_n, 0) + int(multiplier)
            p_line(f"   • Won Item: +{Colors.CYAN}{int(multiplier)}x {item_n}{Colors.RESET}")
            self.ctx.save_data()

    def edit_ascii_art_5x5(self, sym: Dict[str, Any]):
        clear_full_screen()
        art_lines = sym.get("art", DEFAULT_5x5_ARTS["STAR"])
        if len(art_lines) != 5:
            art_lines = DEFAULT_5x5_ARTS["STAR"]
        
        grid = [list(f"{line:<5}"[:5]) for line in art_lines]
        cur_r, cur_c = 0, 0
        palette = ['#', '*', '=', '@', 'O', 'X', '7', '$', '.', ' ']

        last_sec = -1
        needs_redraw = True

        while True:
            now_sec = time.time()
            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                c_code = Colors.parse_color(sym.get("color", "WHITE"))
                p_line(f"{Colors.BOLD}--- 5x5 ASCII PIXEL EDITOR: {c_code}{sym['name'].upper()}{Colors.RESET}{Colors.BOLD} ---{Colors.RESET}")
                p_line(f"Active Pixel Position: Row {cur_r + 1}/5, Column {cur_c + 1}/5")
                p_line()

                p_line("   ┌─────┐")
                for r in range(5):
                    row_str = ""
                    for c in range(5):
                        ch = grid[r][c]
                        if r == cur_r and c == cur_c:
                            row_str += f"{Colors.HIGHLIGHT}{ch}{Colors.RESET}"
                        else:
                            row_str += f"{c_code}{ch}{Colors.RESET}"
                    p_line(f" {r+1} │{row_str}│")
                p_line("   └─────┘")
                p_line("    12345")
                p_line()

                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓/←/→] Navigate Grid  [SPACE] Cycle Char  [Any Key] Draw Char  [ENTER] Save  [ESC] Cancel")

                last_sec = int(now_sec)
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True

            if key == "UP": cur_r = (cur_r - 1) % 5
            elif key == "DOWN": cur_r = (cur_r + 1) % 5
            elif key == "LEFT": cur_c = (cur_c - 1) % 5
            elif key == "RIGHT": cur_c = (cur_c + 1) % 5
            elif key == " ":
                curr_ch = grid[cur_r][cur_c]
                next_i = (palette.index(curr_ch) + 1) % len(palette) if curr_ch in palette else 0
                grid[cur_r][cur_c] = palette[next_i]
            elif key in ("BACKSPACE", "DELETE"):
                grid[cur_r][cur_c] = " "
            elif key == "ENTER":
                sym["art"] = ["".join(row) for row in grid]
                self.ctx.save_data()
                print(f"\n{Colors.GREEN}Successfully saved 5x5 ASCII Art for '{sym['name']}'!{Colors.RESET}")
                time.sleep(1.0)
                break
            elif key == "ESC":
                break
            elif isinstance(key, str) and len(key) == 1 and ord(key) >= 32:
                grid[cur_r][cur_c] = key

        clear_full_screen()

    def manage_5x5_symbols_and_odds(self, casino_item: Dict[str, Any]):
        casino_item.setdefault("symbols", self.ctx.get_default_5x5_symbols())
        symbols = casino_item["symbols"]
        sel = 0
        last_sec = -1
        needs_redraw = True

        while True:
            prof = self.ctx.get_profile()
            skill_options = ["None"] + list(prof["skills"].keys())
            item_options = self.ctx.get_registered_item_names() or ["Health Potion"]

            total_weight = sum([int(s.get("weight", 10)) for s in symbols])
            now_sec = time.time()

            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- SYMBOL & ODDS CONFIGURATOR: {casino_item['name'].upper()} ---{Colors.RESET}")
                p_line(f"Total Combined Weight Pool: {total_weight}")
                p_line()

                for idx, sym in enumerate(symbols):
                    cursor = "► " if idx == sel else "  "
                    c_code = Colors.parse_color(sym.get("color", "WHITE"))
                    w = int(sym.get("weight", 10))
                    prob_pct = (w / total_weight * 100.0) if total_weight > 0 else 0.0
                    tier = str(sym.get("tier", "Normal"))
                    tier_tag = f" [{tier.upper()}]" if tier != "Normal" else ""

                    rtype = sym.get("reward_type", "Money Gain")
                    sk_target = sym.get("target_skill", "None")
                    sk_info = f" | Skill EXP: {sk_target} (+{sym.get('skill_val', 0)})" if sk_target != "None" else ""
                    r_info = f"{rtype} ({sym.get('val', 0)}){sk_info}" if rtype != "Item Win" else f"Item: {sym.get('item_name', 'Potion')}"

                    line = f"{cursor}{c_code}[{sym['name']:<6}]{Colors.RESET}{Colors.GOLD}{tier_tag}{Colors.RESET} Wt: {w:<3} ({prob_pct:>5.1f}%) | Effect: {r_info}"
                    if idx == sel:
                        p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                    else:
                        p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select  [ENTER] Edit Odds/Effect  [P] Edit 5x5 Art  [A] Add  [D] Delete  [0/ESC] Back")
                last_sec = int(now_sec)
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            key_upper = key.upper() if isinstance(key, str) else ""

            if key == "UP": sel = (sel - 1) % len(symbols) if symbols else 0
            elif key == "DOWN": sel = (sel + 1) % len(symbols) if symbols else 0
            elif key_upper == "P" and symbols:
                self.edit_ascii_art_5x5(symbols[sel])
                clear_full_screen()
            elif key_upper == "A":
                fields = [
                    {"key": "name", "label": "Symbol Name/Text", "type": "text", "val": "COIN"},
                    {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": "CYAN"},
                    {"key": "tier", "label": "Symbol Tier", "type": "select", "val": "Normal", "options": ["Normal", "Rare", "Jackpot"]},
                    {"key": "weight", "label": "Odds Weight (Chance)", "type": "number", "val": 10},
                    {"key": "reward_type", "label": "Effect Type", "type": "select", "val": "Money Gain", "options": ["Money Gain", "Money Loss", "HP Heal", "HP Loss", "EXP Gain", "Skill EXP Gain", "EXP Loss", "Item Win"]},
                    {"key": "val", "label": "Value / Amount", "type": "number", "val": 25.0},
                    {"key": "target_skill", "label": "Target Skill EXP", "type": "select", "val": "None", "options": skill_options},
                    {"key": "skill_val", "label": "Skill EXP Amount", "type": "number", "val": 0.0},
                    {"key": "item_name", "label": "Item Reward (If Item Win)", "type": "select", "val": item_options[0], "options": item_options},
                    {"key": "SAVE", "label": "SAVE SYMBOL", "type": "button"},
                    {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                ]
                res = self.ctx.run_menu_form("Create Symbol", fields, self.status_mgr.display_status_header)
                if res:
                    new_sym = {
                        "id": str(res["name"]).upper(),
                        "name": str(res["name"]),
                        "color": str(res["color"]),
                        "tier": str(res.get("tier", "Normal")),
                        "weight": int(res["weight"]),
                        "reward_type": str(res["reward_type"]),
                        "val": float(res["val"]),
                        "target_skill": str(res.get("target_skill", "None")),
                        "skill_val": float(res.get("skill_val", 0.0)),
                        "item_name": str(res["item_name"]),
                        "art": DEFAULT_5x5_ARTS.get(str(res["name"]).upper(), DEFAULT_5x5_ARTS["COIN"])
                    }
                    symbols.append(new_sym)
                    self.ctx.save_data()

            elif key == "ENTER" and symbols:
                sym = symbols[sel]
                init_sk = sym.get("target_skill", "None")
                if init_sk not in skill_options: skill_options.append(init_sk)

                init_item = sym.get("item_name", item_options[0])
                if init_item not in item_options: item_options.append(init_item)

                fields = [
                    {"key": "name", "label": "Symbol Name/Text", "type": "text", "val": sym["name"]},
                    {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": sym.get("color", "WHITE")},
                    {"key": "tier", "label": "Symbol Tier", "type": "select", "val": sym.get("tier", "Normal"), "options": ["Normal", "Rare", "Jackpot"]},
                    {"key": "weight", "label": "Odds Weight (Chance)", "type": "number", "val": sym.get("weight", 10)},
                    {"key": "reward_type", "label": "Effect Type", "type": "select", "val": sym.get("reward_type", "Money Gain"), "options": ["Money Gain", "Money Loss", "HP Heal", "HP Loss", "EXP Gain", "Skill EXP Gain", "EXP Loss", "Item Win"]},
                    {"key": "val", "label": "Value / Amount", "type": "number", "val": sym.get("val", 10.0)},
                    {"key": "target_skill", "label": "Target Skill EXP", "type": "select", "val": init_sk, "options": skill_options},
                    {"key": "skill_val", "label": "Skill EXP Amount", "type": "number", "val": sym.get("skill_val", 0.0)},
                    {"key": "item_name", "label": "Item Reward (If Item Win)", "type": "select", "val": init_item, "options": item_options},
                    {"key": "SAVE", "label": "SAVE SYMBOL", "type": "button"},
                    {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                ]
                res = self.ctx.run_menu_form(f"Edit Symbol: {sym['name']}", fields, self.status_mgr.display_status_header)
                if res:
                    sym["name"] = str(res["name"])
                    sym["color"] = str(res["color"])
                    sym["tier"] = str(res.get("tier", "Normal"))
                    sym["weight"] = int(res["weight"])
                    sym["reward_type"] = str(res["reward_type"])
                    sym["val"] = float(res["val"])
                    sym["target_skill"] = str(res.get("target_skill", "None"))
                    sym["skill_val"] = float(res.get("skill_val", 0.0))
                    sym["item_name"] = str(res["item_name"])
                    self.ctx.save_data()

            elif key_upper == "D" and len(symbols) > 1:
                del symbols[sel]
                sel = max(0, sel - 1)
                self.ctx.save_data()

            elif key in ("0", "ESC"):
                break
        clear_full_screen()