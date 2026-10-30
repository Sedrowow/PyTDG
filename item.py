#!/usr/bin/env python3
"""
Master Item Registry, Inventory Management, and Crafting Workshop module.
"""

import time
from typing import Dict, List, Any, Optional
from utils import Colors, GameContext, p_line, read_key, clear_full_screen
from status import StatusManager

class ItemManager:
    def __init__(self, ctx: GameContext, status_mgr: StatusManager):
        self.ctx = ctx
        self.status_mgr = status_mgr

    def item_manager_menu(self):
        clear_full_screen()
        sel = 0
        last_sec = -1
        needs_redraw = True
        item_type_options = ["heal_fixed", "heal_pct", "exp_fixed", "exp_pct", "collectible", "timer", "no_effect"]

        while True:
            items = self.ctx.data["items"]
            display_items = items + [{"id": -1, "name": "[+ Create New Master Item...]", "is_create_slot": True}]
            if sel >= len(display_items):
                sel = max(0, len(display_items) - 1)

            now_sec = time.time()
            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- MASTER ITEM REGISTRY ---{Colors.RESET}")
                p_line(f"{Colors.CYAN}Configure base items, consumable effects, collectibles, timers, or plain consumables.{Colors.RESET}")
                p_line()

                for idx, item in enumerate(display_items):
                    cursor = "► " if idx == sel else "  "
                    if item.get("is_create_slot"):
                        line = f"{cursor}{Colors.GREEN}{item['name']}{Colors.RESET}"
                    else:
                        color_code = Colors.parse_color(item.get("color", "WHITE"))
                        t_str = item.get("type", "heal_fixed")
                        v_str = item.get("value", 30.0)
                        line = f"{cursor}{color_code}{item['name']:<22}{Colors.RESET} Type: [{t_str:<11}] Val: {v_str}"

                    if idx == sel:
                        p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                    else:
                        p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select Item  [ENTER] Edit / Create  [C] Create New  [0/ESC] Back")
                last_sec = int(now_sec)
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            key_upper = key.upper() if isinstance(key, str) else ""

            if key == "UP":
                sel = (sel - 1) % len(display_items)
            elif key == "DOWN":
                sel = (sel + 1) % len(display_items)
            elif key_upper == "C":
                fields = [
                    {"key": "name", "label": "Item Name", "type": "text", "val": "Fortune Cookie"},
                    {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": "YELLOW"},
                    {"key": "description", "label": "Description", "type": "text", "val": "A simple consumable item that does nothing."},
                    {"key": "type", "label": "Effect/Item Type", "type": "select", "val": "no_effect", "options": item_type_options},
                    {"key": "value", "label": "Value / Timer (Min)", "type": "number", "val": 0.0},
                    {"key": "SAVE", "label": "SAVE MASTER ITEM", "type": "button"},
                    {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                ]
                res = self.ctx.run_menu_form("Create Master Item", fields, self.status_mgr.display_status_header)
                if res:
                    new_id = max([i["id"] for i in items], default=0) + 1
                    self.ctx.data["items"].append({
                        "id": new_id, "name": str(res["name"]), "color": str(res["color"]),
                        "description": str(res["description"]), "type": str(res["type"]),
                        "value": float(res["value"])
                    })
                    self.ctx.save_data()
                clear_full_screen()

            elif key == "ENTER":
                selected = display_items[sel]
                if selected.get("is_create_slot"):
                    fields = [
                        {"key": "name", "label": "Item Name", "type": "text", "val": "Fortune Cookie"},
                        {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": "YELLOW"},
                        {"key": "description", "label": "Description", "type": "text", "val": "A simple consumable item."},
                        {"key": "type", "label": "Effect/Item Type", "type": "select", "val": "no_effect", "options": item_type_options},
                        {"key": "value", "label": "Value / Timer (Min)", "type": "number", "val": 0.0},
                        {"key": "SAVE", "label": "SAVE MASTER ITEM", "type": "button"},
                        {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                    ]
                    res = self.ctx.run_menu_form("Create Master Item", fields, self.status_mgr.display_status_header)
                    if res:
                        new_id = max([i["id"] for i in items], default=0) + 1
                        self.ctx.data["items"].append({
                            "id": new_id, "name": str(res["name"]), "color": str(res["color"]),
                            "description": str(res["description"]), "type": str(res["type"]),
                            "value": float(res["value"])
                        })
                        self.ctx.save_data()
                else:
                    item = selected
                    opts = ["1. Edit Master Item Details", "2. Delete Item", "0. Cancel"]
                    choice = self.ctx.run_action_menu(f"Master Item: {item['name']}", opts, self.status_mgr.display_status_header)
                    if choice == 0:
                        fields = [
                            {"key": "name", "label": "Item Name", "type": "text", "val": item["name"]},
                            {"key": "color", "label": "Color (Name/#Hex)", "type": "text", "val": item.get("color", "WHITE")},
                            {"key": "description", "label": "Description", "type": "text", "val": item.get("description", "")},
                            {"key": "type", "label": "Effect/Item Type", "type": "select", "val": item.get("type", "heal_fixed"), "options": item_type_options},
                            {"key": "value", "label": "Value / Timer (Min)", "type": "number", "val": item.get("value", 30.0)},
                            {"key": "SAVE", "label": "SAVE MASTER ITEM", "type": "button"},
                            {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                        ]
                        res = self.ctx.run_menu_form(f"Edit Master Item: {item['name']}", fields, self.status_mgr.display_status_header)
                        if res:
                            old_name = item["name"]
                            item["name"] = str(res["name"])
                            item["color"] = str(res["color"])
                            item["description"] = str(res["description"])
                            item["type"] = str(res["type"])
                            item["value"] = float(res["value"])

                            if old_name != item["name"]:
                                for s in self.ctx.data["shop"]:
                                    if s["name"] == old_name: s["name"] = item["name"]
                                for c in self.ctx.data["crafting"]:
                                    if c.get("result_item") == old_name: c["result_item"] = item["name"]
                                    if c["name"] == old_name: c["name"] = item["name"]

                            self.ctx.save_data()
                    elif choice == 1:
                        self.ctx.data["items"] = [x for x in self.ctx.data["items"] if x["id"] != item["id"]]
                        self.ctx.save_data()
                clear_full_screen()

            elif key in ("0", "ESC") or key_upper in ("Q", "E"):
                break
        clear_full_screen()

    def inventory_menu(self):
        clear_full_screen()
        selected_idx = 0
        last_sec = -1
        needs_redraw = True

        while True:
            prof = self.ctx.get_profile()
            inv = prof["inventory"]
            available = [k for k, v in inv.items() if v > 0]

            now_sec = time.time()
            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- CHARACTER INVENTORY ---{Colors.RESET}")
                p_line()

                if not available:
                    p_line(f"{Colors.GREY}Inventory is empty. Purchase items in the shop!{Colors.RESET}")
                else:
                    if selected_idx >= len(available):
                        selected_idx = max(0, len(available) - 1)

                    for idx, name in enumerate(available):
                        cursor = "► " if idx == selected_idx else "  "
                        qty = inv[name]
                        item_info = next((i for i in self.ctx.data["items"] if i["name"] == name), None)
                        if not item_info:
                            item_info = next((s for s in self.ctx.data["shop"] if s["name"] == name), None)
                        if not item_info:
                            item_info = next((c for c in self.ctx.data["crafting"] if c["name"] == name), None)

                        color_code = Colors.parse_color(item_info.get("color", "WHITE")) if item_info else Colors.WHITE
                        desc = item_info.get("description", "") if item_info else ""
                        itype = item_info.get("type", "heal_fixed") if item_info else "item"
                        
                        line = f"{cursor}{color_code}{name:<20}{Colors.RESET} (x{qty}) [{itype.upper()}] - {desc}"
                        if idx == selected_idx:
                            p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                        else:
                            p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select  [ENTER] Use / View  [0/ESC] Back")
                last_sec = int(now_sec)
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            if key == "UP":
                selected_idx = (selected_idx - 1) % len(available) if available else 0
            elif key == "DOWN":
                selected_idx = (selected_idx + 1) % len(available) if available else 0
            elif key == "ENTER" and available:
                item_name = available[selected_idx]
                item_info = next((i for i in self.ctx.data["items"] if i["name"] == item_name), None)
                if not item_info:
                    item_info = next((s for s in self.ctx.data["shop"] if s["name"] == item_name), None)
                if not item_info:
                    item_info = next((c for c in self.ctx.data["crafting"] if c["name"] == item_name), None)

                item_type = item_info.get("type", "heal_fixed") if item_info else "heal_fixed"
                val = float(item_info.get("value", item_info.get("val", 30.0))) if item_info else 30.0

                if item_type == "collectible":
                    print(f"\n{Colors.GOLD}{Colors.BOLD}🏆 '{item_name}' is a collectible trophy! (Cannot be consumed){Colors.RESET}")
                    time.sleep(1.2)
                    continue

                elif item_type == "no_effect":
                    inv[item_name] -= 1
                    if inv[item_name] <= 0:
                        del inv[item_name]
                    self.ctx.save_data()
                    print(f"\n{Colors.YELLOW}{Colors.BOLD}😋 Consumed '{item_name}'. Tasted great, but nothing happened!{Colors.RESET}")
                    time.sleep(1.2)

                elif item_type == "timer":
                    duration_min = int(val) if val > 0 else 15
                    prof["timers"].append({
                        "name": f"Timer: {item_name}",
                        "start_time": time.time(),
                        "duration_sec": duration_min * 60,
                        "color": item_info.get("color", "CYAN") if item_info else "CYAN",
                        "type": "item_timer"
                    })
                    inv[item_name] -= 1
                    if inv[item_name] <= 0:
                        del inv[item_name]
                    self.ctx.save_data()
                    print(f"\n{Colors.CYAN}{Colors.BOLD}⏱️ Activated '{item_name}' timer for {duration_min} minutes!{Colors.RESET}")
                    time.sleep(1.2)

                else:
                    inv[item_name] -= 1
                    if inv[item_name] <= 0:
                        del inv[item_name]

                    old_hp = prof["hp"]
                    if item_type in ("heal_fixed", "heal"):
                        target_hp = min(prof["max_hp"], old_hp + val)
                        self.status_mgr.animate_hp_change(old_hp, target_hp)
                    elif item_type == "heal_pct":
                        target_hp = min(prof["max_hp"], old_hp + (prof["max_hp"] * (val / 100.0)))
                        self.status_mgr.animate_hp_change(old_hp, target_hp)
                    elif item_type in ("exp_fixed", "exp"):
                        self.status_mgr.add_exp_animated(int(val), skill_name=None, skill_exp_gain=0)
                    elif item_type == "exp_pct":
                        req = self.ctx.exp_for_level(prof["level"])
                        exp_gain = int(req * (val / 100.0))
                        self.status_mgr.add_exp_animated(exp_gain, skill_name=None, skill_exp_gain=0)

                    self.ctx.save_data()

            elif key in ("0", "ESC"):
                break
        clear_full_screen()

    def recipe_form_editor(self, existing_recipe: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        reg_items = self.ctx.get_registered_item_names()
        if not reg_items:
            reg_items = ["Health Potion", "EXP Bottle", "Fortune Cookie"]

        out_item = existing_recipe.get("result_item", reg_items[0]) if existing_recipe else reg_items[0]
        out_qty = existing_recipe.get("result_qty", 1) if existing_recipe else 1
        ingredients = dict(existing_recipe.get("ingredients", {})) if existing_recipe else {}

        sel = 0
        last_sec = -1
        needs_redraw = True

        while True:
            ing_keys = list(ingredients.keys())
            form_items = [
                {"type": "out_item", "label": "Result Item Output", "val": out_item},
                {"type": "out_qty", "label": "Output Quantity", "val": out_qty},
                {"type": "header", "label": "--- REQUIRED INGREDIENTS ---"}
            ]

            for ik in ing_keys:
                form_items.append({"type": "ing_entry", "item": ik, "qty": ingredients[ik]})

            form_items.extend([
                {"type": "add_ing", "label": "[+ Add / Modify Ingredient...]"},
                {"type": "save", "label": "*** SAVE RECIPE ***"},
                {"type": "cancel", "label": "*** CANCEL ***"}
            ])

            if sel >= len(form_items):
                sel = max(0, len(form_items) - 1)

            now_sec = time.time()
            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                title_str = "Edit Crafting Recipe" if existing_recipe else "Create Crafting Recipe"
                p_line(f"{Colors.BOLD}--- {title_str.upper()} ---{Colors.RESET}")
                p_line()

                for idx, fi in enumerate(form_items):
                    cursor = "► " if idx == sel else "  "
                    t = fi["type"]
                    if t == "header":
                        p_line(f"  {fi['label']}")
                        continue
                    elif t == "out_item":
                        line = f"{cursor}{fi['label']:<25}: [ < {fi['val']} > ]"
                    elif t == "out_qty":
                        line = f"{cursor}{fi['label']:<25}: [{fi['val']}]"
                    elif t == "ing_entry":
                        line = f"{cursor}• {fi['item']:<23}: x{fi['qty']}"
                    elif t == "add_ing":
                        line = f"{cursor}{Colors.CYAN}{fi['label']}{Colors.RESET}"
                    elif t == "save":
                        line = f"{cursor}{Colors.GREEN}{fi['label']}{Colors.RESET}"
                    elif t == "cancel":
                        line = f"{cursor}{Colors.RED}{fi['label']}{Colors.RESET}"

                    if idx == sel:
                        p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                    else:
                        p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Navigate  [←/→] Cycle Item / Adjust Qty  [ENTER] Select/Confirm  [ESC] Cancel")
                last_sec = int(now_sec)
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            cur_fi = form_items[sel]
            fi_type = cur_fi["type"]

            if fi_type == "header":
                sel = (sel + 1) % len(form_items)
                continue

            if key == "UP":
                sel = (sel - 1) % len(form_items)
                if form_items[sel]["type"] == "header":
                    sel = (sel - 1) % len(form_items)
            elif key == "DOWN":
                sel = (sel + 1) % len(form_items)
                if form_items[sel]["type"] == "header":
                    sel = (sel + 1) % len(form_items)
            elif key == "LEFT":
                if fi_type == "out_item":
                    curr_i = reg_items.index(out_item) if out_item in reg_items else 0
                    out_item = reg_items[(curr_i - 1) % len(reg_items)]
                elif fi_type == "out_qty":
                    out_qty = max(1, out_qty - 1)
                elif fi_type == "ing_entry":
                    k = cur_fi["item"]
                    ingredients[k] = max(1, ingredients[k] - 1)
            elif key == "RIGHT":
                if fi_type == "out_item":
                    curr_i = reg_items.index(out_item) if out_item in reg_items else 0
                    out_item = reg_items[(curr_i + 1) % len(reg_items)]
                elif fi_type == "out_qty":
                    out_qty += 1
                elif fi_type == "ing_entry":
                    k = cur_fi["item"]
                    ingredients[k] += 1
            elif key == "ENTER":
                if fi_type == "out_item":
                    curr_i = reg_items.index(out_item) if out_item in reg_items else 0
                    out_item = reg_items[(curr_i + 1) % len(reg_items)]
                elif fi_type == "out_qty":
                    new_val = self.ctx.prompt_input(f"Enter Output Quantity [{out_qty}]: ")
                    if new_val and new_val.isdigit():
                        out_qty = max(1, int(new_val))
                elif fi_type == "ing_entry":
                    k = cur_fi["item"]
                    opts = ["1. Change Quantity", "2. Remove Ingredient", "0. Cancel"]
                    ch = self.ctx.run_action_menu(f"Ingredient: {k}", opts, self.status_mgr.display_status_header)
                    if ch == 0:
                        nq = self.ctx.prompt_input(f"Enter Quantity for '{k}' [{ingredients[k]}]: ")
                        if nq and nq.isdigit(): ingredients[k] = max(1, int(nq))
                    elif ch == 1:
                        del ingredients[k]
                elif fi_type == "add_ing":
                    ing_opts = reg_items
                    sel_item_i = self.ctx.run_action_menu("Select Ingredient to Add", [f"• {x}" for x in ing_opts] + ["0. Cancel"], self.status_mgr.display_status_header)
                    if sel_item_i is not None and sel_item_i < len(ing_opts):
                        chosen_item = ing_opts[sel_item_i]
                        q_str = self.ctx.prompt_input(f"Enter Required Qty for '{chosen_item}': ")
                        if q_str and q_str.isdigit():
                            ingredients[chosen_item] = max(1, int(q_str))
                elif fi_type == "save":
                    if not ingredients:
                        print(f"\n{Colors.RED}Recipe must require at least one ingredient!{Colors.RESET}")
                        time.sleep(1.0)
                    else:
                        item_info = next((i for i in self.ctx.data["items"] if i["name"] == out_item), None)
                        color = item_info.get("color", "GOLD") if item_info else "GOLD"
                        return {
                            "name": out_item, "result_item": out_item, "result_qty": out_qty,
                            "ingredients": ingredients, "color": color, "description": f"Crafts {out_qty}x {out_item}"
                        }
                elif fi_type == "cancel":
                    return None
            elif key == "ESC":
                return None

    def crafting_menu(self):
        clear_full_screen()
        selected_idx = 0
        last_sec = -1
        needs_redraw = True

        while True:
            crafting = self.ctx.data["crafting"]
            prof = self.ctx.get_profile()
            if selected_idx >= len(crafting):
                selected_idx = max(0, len(crafting) - 1)

            now_sec = time.time()
            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- CRAFTING WORKSHOP ---{Colors.RESET}")
                p_line()

                if not crafting:
                    p_line(f"{Colors.GREY}No recipes found. Press 'E' to enter Edit Mode and add recipes.{Colors.RESET}")
                else:
                    for idx, r in enumerate(crafting):
                        cursor = "► " if idx == selected_idx else "  "
                        color_code = Colors.parse_color(r.get("color", "WHITE"))
                        ing_str = ", ".join([f"{k} x{v}" for k, v in r.get("ingredients", {}).items()])
                        out_qty = r.get("result_qty", 1)
                        res_item = r.get("result_item", r["name"])
                        line = f"{cursor}{color_code}[{r['id']}] {res_item}{Colors.RESET} (x{out_qty}) -> Requires: {ing_str}"
                        if idx == selected_idx:
                            p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                        else:
                            p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select  [ENTER] Craft  [E] Edit Mode  [0/ESC] Back")
                last_sec = int(now_sec)
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            key_upper = key.upper() if isinstance(key, str) else ""

            if key == "UP":
                selected_idx = (selected_idx - 1) % len(crafting) if crafting else 0
            elif key == "DOWN":
                selected_idx = (selected_idx + 1) % len(crafting) if crafting else 0
            elif key == "ENTER" and crafting:
                recipe = crafting[selected_idx]
                inv = prof["inventory"]
                ings = recipe.get("ingredients", {})
                if all(inv.get(k, 0) >= v for k, v in ings.items()):
                    for k, v in ings.items():
                        inv[k] -= v
                        if inv[k] <= 0:
                            del inv[k]
                    res = recipe.get("result_item", recipe["name"])
                    out_qty = recipe.get("result_qty", 1)
                    inv[res] = inv.get(res, 0) + out_qty
                    self.ctx.save_data()
                    print(f"\n{Colors.GREEN}{Colors.BOLD}Successfully crafted +{out_qty}x '{res}'!{Colors.RESET}")
                    time.sleep(1.0)
                else:
                    print(f"\n{Colors.RED}Missing required ingredients to craft this item!{Colors.RESET}")
                    time.sleep(1.0)
            elif key_upper == "E":
                self.crafting_edit_mode()
                clear_full_screen()
            elif key in ("0", "ESC") or key_upper == "Q":
                break
        clear_full_screen()

    def crafting_edit_mode(self):
        clear_full_screen()
        sel = 0
        last_sec = -1
        needs_redraw = True

        while True:
            crafting = self.ctx.data["crafting"]
            header_items = [{"id": -2, "name": "[ Manage Master Item Registry ]", "is_registry_slot": True}]
            footer_items = [{"id": -1, "name": "[+ Create New Recipe...]", "is_create_slot": True}]
            items = header_items + crafting + footer_items

            if sel >= len(items):
                sel = max(0, len(items) - 1)

            now_sec = time.time()
            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- CRAFTING EDIT MODE ---{Colors.RESET}")
                p_line(f"{Colors.CYAN}Select a recipe with Arrow Keys and press ENTER to edit details or ingredients.{Colors.RESET}")
                p_line()

                for idx, item in enumerate(items):
                    cursor = "► " if idx == sel else "  "
                    if item.get("is_registry_slot"):
                        line = f"{cursor}{Colors.PURPLE}{item['name']}{Colors.RESET}"
                    elif item.get("is_create_slot"):
                        line = f"{cursor}{Colors.GREEN}{item['name']}{Colors.RESET}"
                    else:
                        color_code = Colors.parse_color(item.get("color", "WHITE"))
                        ing_str = ", ".join([f"{k} x{v}" for k, v in item.get("ingredients", {}).items()])
                        out_qty = item.get("result_qty", 1)
                        res_item = item.get("result_item", item["name"])
                        line = f"{cursor}{color_code}{res_item:<20}{Colors.RESET} (x{out_qty}) -> Requires: {ing_str}"

                    if idx == sel:
                        p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                    else:
                        p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select Recipe  [ENTER] Manage / Action  [C] Create Recipe  [0/ESC] Exit Edit Mode")

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
            elif key_upper == "C":
                res = self.recipe_form_editor()
                if res:
                    new_id = max([r["id"] for r in crafting], default=0) + 1
                    res["id"] = new_id
                    self.ctx.data["crafting"].append(res)
                    self.ctx.save_data()
                clear_full_screen()

            elif key == "ENTER":
                selected_item = items[sel]
                if selected_item.get("is_registry_slot"):
                    self.item_manager_menu()
                elif selected_item.get("is_create_slot"):
                    res = self.recipe_form_editor()
                    if res:
                        new_id = max([r["id"] for r in crafting], default=0) + 1
                        res["id"] = new_id
                        self.ctx.data["crafting"].append(res)
                        self.ctx.save_data()
                else:
                    recipe = selected_item
                    opts = ["1. Edit Recipe Details & Ingredients", "2. Delete Recipe", "0. Cancel"]
                    choice = self.ctx.run_action_menu(f"Recipe Actions: {recipe.get('result_item', recipe['name'])}", opts, self.status_mgr.display_status_header)
                    if choice == 0:
                        updated = self.recipe_form_editor(existing_recipe=recipe)
                        if updated:
                            recipe.update(updated)
                            self.ctx.save_data()
                    elif choice == 1:
                        self.ctx.data["crafting"] = [r for r in self.ctx.data["crafting"] if r["id"] != recipe["id"]]
                        self.ctx.save_data()
                clear_full_screen()

            elif key in ("0", "ESC") or key_upper in ("Q", "E"):
                break
        clear_full_screen()