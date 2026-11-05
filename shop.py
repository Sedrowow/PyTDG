#!/usr/bin/env python3
"""
Item Shop System Module.
Manages purchasing master registry items and configuring shop entries.
"""

import time
from typing import Dict, List, Any, Optional
from utils import Colors, GameContext, p_line, read_key, clear_full_screen
from status import StatusManager
from item import ItemManager

CASINO_TYPES = ("slotmachine", "slotmachine_5x3", "wheel", "chests", "coindrop")

class ShopManager:
    def __init__(self, ctx: GameContext, status_mgr: StatusManager, item_mgr: ItemManager):
        self.ctx = ctx
        self.status_mgr = status_mgr
        self.item_mgr = item_mgr

    def get_shop_items(self) -> List[Dict[str, Any]]:
        return [i for i in self.ctx.data["shop"] if i.get("type") not in CASINO_TYPES]

    def shop_menu(self):
        clear_full_screen()
        selected_idx = 0
        last_sec = -1
        needs_redraw = True

        while True:
            shop_items = self.get_shop_items()
            prof = self.ctx.get_profile()
            if selected_idx >= len(shop_items):
                selected_idx = max(0, len(shop_items) - 1)

            now_sec = time.time()
            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- ITEM SHOP ---{Colors.RESET}")
                p_line(f"Wallet: {Colors.YELLOW}${prof['money']:.2f}{Colors.RESET}")
                p_line()

                if not shop_items:
                    p_line(f"{Colors.GREY}Item shop is empty. Press 'E' to enter Edit Mode and add items.{Colors.RESET}")
                else:
                    for idx, item in enumerate(shop_items):
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
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select Item  [ENTER] Purchase  [E] Edit Mode  [0/ESC] Back")
                last_sec = int(now_sec)
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            key_upper = key.upper() if isinstance(key, str) else ""

            if key == "UP":
                selected_idx = (selected_idx - 1) % len(shop_items) if shop_items else 0
            elif key == "DOWN":
                selected_idx = (selected_idx + 1) % len(shop_items) if shop_items else 0
            elif key == "ENTER" and shop_items:
                item = shop_items[selected_idx]
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
            shop_items = self.get_shop_items()
            header_items = [{"id": -2, "name": "[ Manage Master Item Registry ]", "is_registry_slot": True}]
            footer_items = [{"id": -1, "name": "[+ Add Existing Item to Shop...]", "is_add_item_slot": True}]
            items = header_items + shop_items + footer_items

            if sel >= len(items):
                sel = max(0, len(items) - 1)

            now_sec = time.time()
            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- ITEM SHOP EDIT MODE ---{Colors.RESET}")
                p_line(f"{Colors.CYAN}Select an item with Arrow Keys and press ENTER to edit price or description.{Colors.RESET}")
                p_line()

                for idx, item in enumerate(items):
                    cursor = "► " if idx == sel else "  "
                    if item.get("is_registry_slot"):
                        line = f"{cursor}{Colors.PURPLE}{item['name']}{Colors.RESET}"
                    elif item.get("is_add_item_slot"):
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
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select Item  [ENTER] Manage  [0/ESC] Exit Edit Mode")
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
                                new_id = max([i["id"] for i in self.ctx.data["shop"]], default=0) + 1
                                self.ctx.data["shop"].append({
                                    "id": new_id, "name": chosen_m["name"], "color": chosen_m.get("color", "WHITE"),
                                    "price": float(res["price"]), "description": str(res["description"]),
                                    "type": chosen_m.get("type", "heal_fixed"), "value": float(chosen_m.get("value", 0.0))
                                })
                                self.ctx.save_data()
                else:
                    item = selected_item
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