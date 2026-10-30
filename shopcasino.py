#!/usr/bin/env python3
"""
Shop System & Casino Games (European Roulette, 3-Reel Slots, 5x5 Spinning Wheel, ASCII Pixel Art Configurator).
"""

import time
import random
from typing import Dict, List, Any, Optional
from utils import Colors, GameContext, p_line, read_key, clear_full_screen, DEFAULT_5x5_ARTS
from status import StatusManager
from item import ItemManager

class ShopCasinoManager:
    def __init__(self, ctx: GameContext, status_mgr: StatusManager, item_mgr: ItemManager):
        self.ctx = ctx
        self.status_mgr = status_mgr
        self.item_mgr = item_mgr

    def shop_menu(self):
        clear_full_screen()
        selected_idx = 0
        last_sec = -1
        needs_redraw = True

        while True:
            shop = self.ctx.data["shop"]
            prof = self.ctx.get_profile()
            if selected_idx >= len(shop):
                selected_idx = max(0, len(shop) - 1)

            now_sec = time.time()
            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- SHOP & CASINO ---{Colors.RESET}")
                p_line(f"Wallet: {Colors.YELLOW}${prof['money']:.2f}{Colors.RESET}")
                p_line()
                
                if not shop:
                    p_line(f"{Colors.GREY}Shop is empty. Press 'E' to enter Edit Mode and add items/games.{Colors.RESET}")
                else:
                    for idx, item in enumerate(shop):
                        cursor = "► " if idx == selected_idx else "  "
                        color_code = Colors.parse_color(item.get("color", "WHITE"))
                        item_str = f"[{item['id']}] {item['name']:<22} ${item['price']:<8.2f} - {item.get('description', '')}"
                        line = f"{cursor}{color_code}{item_str}{Colors.RESET}"
                        if idx == selected_idx:
                            p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                        else:
                            p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select Item/Game  [ENTER] Purchase/Play  [E] Edit Mode  [0/ESC] Back")
                last_sec = int(now_sec)
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            key_upper = key.upper() if isinstance(key, str) else ""

            if key == "UP":
                selected_idx = (selected_idx - 1) % len(shop) if shop else 0
            elif key == "DOWN":
                selected_idx = (selected_idx + 1) % len(shop) if shop else 0
            elif key == "ENTER" and shop:
                item = shop[selected_idx]
                gtype = item.get("type")
                if gtype == "slotmachine":
                    self.run_slot_machine(item)
                    clear_full_screen()
                elif gtype == "roulette":
                    self.run_roulette(item)
                    clear_full_screen()
                elif gtype == "wheel":
                    self.run_spinning_wheel(item)
                    clear_full_screen()
                else:
                    if prof["money"] >= item["price"]:
                        old_m = prof["money"]
                        new_m = old_m - item["price"]
                        inv = prof["inventory"]
                        inv[item["name"]] = inv.get(item["name"], 0) + 1
                        self.status_mgr.animate_money_change(old_m, new_m)
                    else:
                        print(f"\n{Colors.RED}Not enough money!{Colors.RESET}")
                        time.sleep(1.0)
            elif key_upper == "E":
                self.shop_edit_mode()
                clear_full_screen()
            elif key in ("0", "ESC") or key_upper == "Q":
                break
        clear_full_screen()

    def shop_edit_mode(self):
        clear_full_screen()
        sel = 0
        last_sec = -1
        needs_redraw = True

        while True:
            shop = self.ctx.data["shop"]
            header_items = [{"id": -2, "name": "[ Manage Master Item Registry ]", "is_registry_slot": True}]
            footer_items = [
                {"id": -1, "name": "[+ Add Existing Item to Shop...]", "is_add_item_slot": True},
                {"id": -3, "name": "[+ Create Slot Machine...]", "is_create_slot_machine": True},
                {"id": -4, "name": "[+ Create Roulette Table...]", "is_create_roulette": True},
                {"id": -5, "name": "[+ Create Spinning Wheel (5x5)...]", "is_create_wheel": True}
            ]
            items = header_items + shop + footer_items

            if sel >= len(items):
                sel = max(0, len(items) - 1)

            now_sec = time.time()
            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- SHOP & CASINO EDIT MODE ---{Colors.RESET}")
                p_line(f"{Colors.CYAN}Select an item/game with Arrow Keys and press ENTER to edit details or symbol odds.{Colors.RESET}")
                p_line()

                for idx, item in enumerate(items):
                    cursor = "► " if idx == sel else "  "
                    if item.get("is_registry_slot"):
                        line = f"{cursor}{Colors.PURPLE}{item['name']}{Colors.RESET}"
                    elif item.get("is_add_item_slot") or item.get("is_create_slot_machine") or item.get("is_create_roulette") or item.get("is_create_wheel"):
                        line = f"{cursor}{Colors.GREEN}{item['name']}{Colors.RESET}"
                    else:
                        color_code = Colors.parse_color(item.get("color", "WHITE"))
                        type_tag = f"[{item.get('type', 'item').upper()}]"
                        line = f"{cursor}{color_code}{item['name']:<22}{Colors.RESET} ${item.get('price', 0.0):<6.2f} {type_tag}"

                    if idx == sel:
                        p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                    else:
                        p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select Item  [ENTER] Manage / Action  [0/ESC] Exit Edit Mode")
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
                if selected_item.get("is_registry_slot"):
                    self.item_mgr.item_manager_menu()
                elif selected_item.get("is_add_item_slot"):
                    master_items = self.ctx.data["items"]
                    if not master_items:
                        print(f"\n{Colors.RED}No items in Master Item Registry! Create items there first.{Colors.RESET}")
                        time.sleep(1.2)
                    else:
                        m_names = [i["name"] for i in master_items]
                        m_choice = self.ctx.run_action_menu("Select Master Item to Add to Shop", [f"• {x}" for x in m_names] + ["0. Cancel"], self.status_mgr.display_status_header)
                        if m_choice is not None and m_choice < len(master_items):
                            chosen_m = master_items[m_choice]
                            fields = [
                                {"key": "price", "label": "Shop Price ($)", "type": "number", "val": 20.0},
                                {"key": "description", "label": "Shop Description", "type": "text", "val": chosen_m.get("description", "")},
                                {"key": "SAVE", "label": "ADD TO SHOP", "type": "button"},
                                {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                            ]
                            res = self.ctx.run_menu_form(f"Add '{chosen_m['name']}' to Shop", fields, self.status_mgr.display_status_header)
                            if res:
                                new_id = max([i["id"] for i in shop], default=0) + 1
                                self.ctx.data["shop"].append({
                                    "id": new_id, "name": chosen_m["name"], "color": chosen_m.get("color", "WHITE"),
                                    "price": float(res["price"]), "description": str(res["description"]),
                                    "type": chosen_m.get("type", "heal_fixed"), "value": float(chosen_m.get("value", 0.0))
                                })
                                self.ctx.save_data()
                elif selected_item.get("is_create_slot_machine"):
                    fields = [
                        {"key": "name", "label": "Slot Machine Name", "type": "text", "val": "3-Reel Classic Slot"},
                        {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": "GOLD"},
                        {"key": "price", "label": "Spin Cost ($)", "type": "number", "val": 10.0},
                        {"key": "description", "label": "Description", "type": "text", "val": "Spin 3 wheels for rewards!"},
                        {"key": "SAVE", "label": "SAVE SLOT MACHINE", "type": "button"},
                        {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                    ]
                    res = self.ctx.run_menu_form("Create Slot Machine", fields, self.status_mgr.display_status_header)
                    if res:
                        new_id = max([i["id"] for i in shop], default=0) + 1
                        self.ctx.data["shop"].append({
                            "id": new_id, "name": str(res["name"]), "color": str(res["color"]),
                            "price": float(res["price"]), "description": str(res["description"]),
                            "type": "slotmachine", "cost": float(res["price"]), "symbols": self.ctx.get_default_5x5_symbols()
                        })
                        self.ctx.save_data()
                elif selected_item.get("is_create_roulette"):
                    fields = [
                        {"key": "name", "label": "Roulette Table Name", "type": "text", "val": "European Roulette"},
                        {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": "GREEN"},
                        {"key": "price", "label": "Entry / Base Bet ($)", "type": "number", "val": 10.0},
                        {"key": "description", "label": "Description", "type": "text", "val": "Bet on Red, Black, Even, Odd, or Numbers!"},
                        {"key": "SAVE", "label": "SAVE ROULETTE TABLE", "type": "button"},
                        {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                    ]
                    res = self.ctx.run_menu_form("Create Roulette Table", fields, self.status_mgr.display_status_header)
                    if res:
                        new_id = max([i["id"] for i in shop], default=0) + 1
                        self.ctx.data["shop"].append({
                            "id": new_id, "name": str(res["name"]), "color": str(res["color"]),
                            "price": float(res["price"]), "description": str(res["description"]), "type": "roulette"
                        })
                        self.ctx.save_data()
                elif selected_item.get("is_create_wheel"):
                    fields = [
                        {"key": "name", "label": "Spinning Wheel Name", "type": "text", "val": "5x5 Wheel of Fortune"},
                        {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": "GOLD"},
                        {"key": "price", "label": "Spin Cost ($)", "type": "number", "val": 15.0},
                        {"key": "description", "label": "Description", "type": "text", "val": "Spin the 5x5 symbol wheel for rewards!"},
                        {"key": "SAVE", "label": "SAVE SPINNING WHEEL", "type": "button"},
                        {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                    ]
                    res = self.ctx.run_menu_form("Create 5x5 Spinning Wheel", fields, self.status_mgr.display_status_header)
                    if res:
                        new_id = max([i["id"] for i in shop], default=0) + 1
                        self.ctx.data["shop"].append({
                            "id": new_id, "name": str(res["name"]), "color": str(res["color"]),
                            "price": float(res["price"]), "description": str(res["description"]),
                            "type": "wheel", "symbols": self.ctx.get_default_5x5_symbols()
                        })
                        self.ctx.save_data()
                else:
                    item = selected_item
                    stype = item.get("type")
                    if stype in ("slotmachine", "wheel"):
                        opts = ["1. Edit Game Details", "2. Manage 5x5 Symbols, Odds & Pixel Art", "3. Delete Game", "0. Cancel"]
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
                    elif stype == "roulette":
                        opts = ["1. Edit Roulette Details", "2. Delete Table", "0. Cancel"]
                        choice = self.ctx.run_action_menu(f"Roulette Table: {item['name']}", opts, self.status_mgr.display_status_header)
                        if choice == 0:
                            fields = [
                                {"key": "name", "label": "Table Name", "type": "text", "val": item["name"]},
                                {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": item.get("color", "GREEN")},
                                {"key": "price", "label": "Base Bet ($)", "type": "number", "val": item.get("price", 10.0)},
                                {"key": "description", "label": "Description", "type": "text", "val": item.get("description", "")},
                                {"key": "SAVE", "label": "SAVE TABLE", "type": "button"},
                                {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                            ]
                            res = self.ctx.run_menu_form(f"Edit Table: {item['name']}", fields, self.status_mgr.display_status_header)
                            if res:
                                item["name"] = str(res["name"])
                                item["color"] = str(res["color"])
                                item["price"] = float(res["price"])
                                item["description"] = str(res["description"])
                                self.ctx.save_data()
                        elif choice == 1:
                            self.ctx.data["shop"] = [x for x in self.ctx.data["shop"] if x["id"] != item["id"]]
                            self.ctx.save_data()
                    else:
                        opts = ["1. Edit Shop Price & Description", "2. Remove from Shop", "0. Cancel"]
                        choice = self.ctx.run_action_menu(f"Shop Item: {item['name']}", opts, self.status_mgr.display_status_header)
                        if choice == 0:
                            fields = [
                                {"key": "price", "label": "Shop Price ($)", "type": "number", "val": item.get("price", 10.0)},
                                {"key": "description", "label": "Shop Description", "type": "text", "val": item.get("description", "")},
                                {"key": "SAVE", "label": "SAVE SHOP ITEM", "type": "button"},
                                {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                            ]
                            res = self.ctx.run_menu_form(f"Edit Shop Entry: {item['name']}", fields, self.status_mgr.display_status_header)
                            if res:
                                item["price"] = float(res["price"])
                                item["description"] = str(res["description"])
                                self.ctx.save_data()
                        elif choice == 1:
                            self.ctx.data["shop"] = [x for x in self.ctx.data["shop"] if x["id"] != item["id"]]
                            self.ctx.save_data()
                clear_full_screen()

            elif key in ("0", "ESC") or key_upper in ("Q", "E"):
                break
        clear_full_screen()

    def run_roulette(self, item: Dict[str, Any]):
        prof = self.ctx.get_profile()
        bet_options = ["1. Red (1:1)", "2. Black (1:1)", "3. Even (1:1)", "4. Odd (1:1)", "5. Single Number 0-36 (35:1)", "0. Cancel"]
        choice = self.ctx.run_action_menu("European Roulette - Place Your Bet", bet_options, self.status_mgr.display_status_header)
        if choice is None or choice == 5:
            return

        bet_type = ["red", "black", "even", "odd", "number"][choice]
        target_num = -1
        if bet_type == "number":
            num_str = self.ctx.prompt_input("Enter Target Number (0-36): ")
            try:
                target_num = int(num_str)
                if not (0 <= target_num <= 36):
                    print(f"{Colors.RED}Invalid number!{Colors.RESET}")
                    time.sleep(1.0)
                    return
            except ValueError:
                return

        bet_str = self.ctx.prompt_input("Enter Bet Amount ($): ")
        try:
            bet_amt = float(bet_str)
            if bet_amt <= 0 or bet_amt > prof["money"]:
                print(f"{Colors.RED}Invalid bet amount!{Colors.RESET}")
                time.sleep(1.0)
                return
        except ValueError:
            return

        old_money = prof["money"]
        self.status_mgr.animate_money_change(old_money, old_money - bet_amt)

        red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        winning_num = random.randint(0, 36)

        steps = 25
        for s in range(steps):
            display_num = random.randint(0, 36) if s < steps - 1 else winning_num
            col = Colors.GREEN if display_num == 0 else (Colors.RED if display_num in red_numbers else Colors.WHITE)
            self.status_mgr.display_status_header()
            p_line(f"{Colors.BOLD}{Colors.GOLD}--- EUROPEAN ROULETTE WHEEL ---{Colors.RESET}")
            p_line()
            p_line(f"           [  {col}{Colors.BOLD}{display_num:^2}{Colors.RESET}  ]           ")
            p_line()
            time.sleep(0.04 + (s * 0.008))

        is_red = winning_num in red_numbers
        is_black = winning_num != 0 and not is_red
        is_even = winning_num != 0 and winning_num % 2 == 0
        is_odd = winning_num % 2 != 0

        won = False
        payout = 0.0

        if bet_type == "red" and is_red: won = True; payout = bet_amt * 2.0
        elif bet_type == "black" and is_black: won = True; payout = bet_amt * 2.0
        elif bet_type == "even" and is_even: won = True; payout = bet_amt * 2.0
        elif bet_type == "odd" and is_odd: won = True; payout = bet_amt * 2.0
        elif bet_type == "number" and winning_num == target_num: won = True; payout = bet_amt * 36.0

        num_color_str = "GREEN" if winning_num == 0 else ("RED" if is_red else "BLACK")
        p_line("-" * 70)
        p_line(f"Winning Ball Landed On: {Colors.parse_color(num_color_str)}{Colors.BOLD}{winning_num} ({num_color_str}){Colors.RESET}")

        if won:
            p_line(f"{Colors.GREEN}{Colors.BOLD}🎉 YOU WON! Payout: +${payout:.2f}{Colors.RESET}")
            self.status_mgr.animate_money_change(prof["money"], prof["money"] + payout)
        else:
            p_line(f"{Colors.RED}House Wins. Better luck next spin!{Colors.RESET}")

        self.ctx.prompt_input("\nPress Enter to continue...")

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

        weights = [max(1, int(s.get("weight", 10))) for s in symbols]
        winning_sym = random.choices(symbols, weights=weights, k=1)[0]

        total_steps = 18
        for step in range(total_steps):
            cur_sym = winning_sym if step == total_steps - 1 else random.choice(symbols)
            self.status_mgr.display_status_header()
            p_line(f"{Colors.BOLD}{Colors.GOLD}--- 5x5 WHEEL OF FORTUNE: {item['name'].upper()} ---{Colors.RESET}")
            p_line()

            art_lines = cur_sym.get("art", DEFAULT_5x5_ARTS["STAR"])
            c_code = Colors.parse_color(cur_sym.get("color", "WHITE"))
            
            p_line("        ▼ POINTER ▼        ")
            p_line("      ┌───────────┐      ")
            for r in range(5):
                line_str = "".join([f"{ch} " for ch in art_lines[r]])
                p_line(f"      │ {c_code}{line_str}{Colors.RESET}│      ")
            p_line("      └───────────┘      ")
            p_line(f"       [{c_code}{cur_sym['name']:^9}{Colors.RESET}]")
            p_line()

            time.sleep(0.05 + (step * 0.01))

        p_line("-" * 70)
        p_line(f"{Colors.GREEN}{Colors.BOLD}WHEEL LANDED ON: {winning_sym['name'].upper()}!{Colors.RESET}")
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
            total_weight = sum([int(s.get("weight", 10)) for s in symbols])
            now_sec = time.time()

            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- 5x5 SYMBOL & ODDS CONFIGURATOR: {casino_item['name'].upper()} ---{Colors.RESET}")
                p_line(f"Total Combined Weight Pool: {total_weight}")
                p_line()

                for idx, sym in enumerate(symbols):
                    cursor = "► " if idx == sel else "  "
                    c_code = Colors.parse_color(sym.get("color", "WHITE"))
                    w = int(sym.get("weight", 10))
                    prob_pct = (w / total_weight * 100.0) if total_weight > 0 else 0.0
                    
                    rtype = sym.get("reward_type", "Money Gain")
                    sk_target = sym.get("target_skill", "None")
                    sk_info = f" | Skill EXP: {sk_target} (+{sym.get('skill_val', 0)})" if sk_target != "None" else ""
                    r_info = f"{rtype} ({sym.get('val', 0)}){sk_info}" if rtype != "Item Win" else f"Item: {sym.get('item_name', 'Potion')}"

                    line = f"{cursor}{c_code}[{sym['name']:<6}]{Colors.RESET} Wt: {w:<3} ({prob_pct:>5.1f}%) | Effect: {r_info}"
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
                    {"key": "weight", "label": "Odds Weight (Chance)", "type": "number", "val": 10},
                    {"key": "reward_type", "label": "Effect Type", "type": "select", "val": "Money Gain", "options": ["Money Gain", "Money Loss", "HP Heal", "HP Loss", "EXP Gain", "Skill EXP Gain", "EXP Loss", "Item Win"]},
                    {"key": "val", "label": "Value / Amount", "type": "number", "val": 25.0},
                    {"key": "target_skill", "label": "Target Skill EXP", "type": "select", "val": "None", "options": skill_options},
                    {"key": "skill_val", "label": "Skill EXP Amount", "type": "number", "val": 0.0},
                    {"key": "item_name", "label": "Item Name (If Item Win)", "type": "text", "val": "Health Potion"},
                    {"key": "SAVE", "label": "SAVE SYMBOL", "type": "button"},
                    {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                ]
                res = self.ctx.run_menu_form("Create 5x5 Symbol", fields, self.status_mgr.display_status_header)
                if res:
                    new_sym = {
                        "id": str(res["name"]).upper(),
                        "name": str(res["name"]),
                        "color": str(res["color"]),
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

                fields = [
                    {"key": "name", "label": "Symbol Name/Text", "type": "text", "val": sym["name"]},
                    {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": sym.get("color", "WHITE")},
                    {"key": "weight", "label": "Odds Weight (Chance)", "type": "number", "val": sym.get("weight", 10)},
                    {"key": "reward_type", "label": "Effect Type", "type": "select", "val": sym.get("reward_type", "Money Gain"), "options": ["Money Gain", "Money Loss", "HP Heal", "HP Loss", "EXP Gain", "Skill EXP Gain", "EXP Loss", "Item Win"]},
                    {"key": "val", "label": "Value / Amount", "type": "number", "val": sym.get("val", 10.0)},
                    {"key": "target_skill", "label": "Target Skill EXP", "type": "select", "val": init_sk, "options": skill_options},
                    {"key": "skill_val", "label": "Skill EXP Amount", "type": "number", "val": sym.get("skill_val", 0.0)},
                    {"key": "item_name", "label": "Item Name (If Item Win)", "type": "text", "val": sym.get("item_name", "Health Potion")},
                    {"key": "SAVE", "label": "SAVE SYMBOL", "type": "button"},
                    {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                ]
                res = self.ctx.run_menu_form(f"Edit Symbol: {sym['name']}", fields, self.status_mgr.display_status_header)
                if res:
                    sym["name"] = str(res["name"])
                    sym["color"] = str(res["color"])
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