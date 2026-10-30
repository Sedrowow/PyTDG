#!/usr/bin/env python3
"""
Task Management, Flexible Repeat Intervals, and Dynamic Due Date System.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from utils import Colors, GameContext, p_line, read_key, clear_full_screen
from status import StatusManager

class TaskManager:
    def __init__(self, ctx: GameContext, status_mgr: StatusManager):
        self.ctx = ctx
        self.status_mgr = status_mgr

    def task_form_editor(self, existing_task: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        categories = list(self.ctx.data["categories"]) + ["+ New Category..."]
        prof = self.ctx.get_profile()
        skills = list(prof["skills"].keys()) + ["+ New Skill..."]

        init_cat = existing_task.get("category", "General") if existing_task else categories[0]
        if init_cat not in categories: categories.insert(0, init_cat)

        init_skill = existing_task.get("skill", "Fitness") if existing_task else skills[0]
        if init_skill not in skills: skills.insert(0, init_skill)

        init_reward_type = existing_task.get("reward_type", "XP") if existing_task else "XP"
        now_dt = datetime.now()
        default_due_str = (now_dt + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

        fields = [
            {"key": "title", "label": "Task Title", "type": "text", "val": existing_task["title"] if existing_task else "New Task"},
            {"key": "category", "label": "Category", "type": "select", "val": init_cat, "options": categories},
            {"key": "skill", "label": "Associated Skill", "type": "select", "val": init_skill, "options": skills},
            {"key": "difficulty", "label": "Difficulty (50% Wt)", "type": "slider", "val": existing_task["difficulty"] if existing_task else 50},
            {"key": "urgency", "label": "Urgency (30% Wt)", "type": "slider", "val": existing_task["urgency"] if existing_task else 30},
            {"key": "fear", "label": "Fear Factor (20% Wt)", "type": "slider", "val": existing_task["fear"] if existing_task else 10},
            {"key": "interval_val", "label": "Interval Length", "type": "number", "val": existing_task.get("interval_val", 1) if existing_task else 1},
            {"key": "interval_unit", "label": "Interval Unit", "type": "select", "val": existing_task.get("interval_unit", "days") if existing_task else "days", "options": ["minutes", "hours", "days"]},
            {"key": "due_datetime", "label": "Due Date & Time (YYYY-MM-DD HH:MM)", "type": "text", "val": existing_task.get("due_datetime", default_due_str) if existing_task else default_due_str},
            {"key": "max_repeats", "label": "Max Repeats Target", "type": "number", "val": existing_task.get("max_repeats", 1) if existing_task else 1},
            {"key": "reward_type", "label": "Main Reward Type", "type": "select", "val": init_reward_type, "options": ["XP", "HP", "Item", "None"]},
            {"key": "money_reward", "label": "Money Reward ($)", "type": "number", "val": existing_task.get("money_reward", 10.0) if existing_task else 10.0},
            {"key": "reward_item", "label": "Item Name (If Item)", "type": "text", "val": existing_task.get("reward_item", "Health Potion") if existing_task else "Health Potion"},
            {"key": "penalty_type", "label": "Penalty Type", "type": "select", "val": existing_task.get("penalty_type", "HP Loss") if existing_task else "HP Loss", "options": ["HP Loss", "XP Loss", "Penalty Timer"]},
            {"key": "penalty_val", "label": "Penalty Val / Min", "type": "number", "val": existing_task.get("penalty_val", 15.0) if existing_task else 15.0},
            {"key": "SAVE", "label": "SAVE TASK", "type": "button"},
            {"key": "CANCEL", "label": "CANCEL", "type": "button"}
        ]

        res = self.ctx.run_menu_form("Task Configurator", fields, self.status_mgr.display_status_header)
        if not res:
            return None

        cat = res["category"]
        if cat == "+ New Category...":
            cat = self.ctx.prompt_input("Enter New Category Name: ") or "General"
            if cat not in self.ctx.data["categories"]: self.ctx.data["categories"].append(cat)

        sk = res["skill"]
        if sk == "+ New Skill...":
            sk = self.ctx.prompt_input("Enter New Skill Name: ") or "General"
            if sk not in prof["skills"]: prof["skills"][sk] = {"level": 1, "exp": 0}

        return {
            "title": str(res["title"]),
            "category": cat,
            "skill": sk,
            "difficulty": int(res["difficulty"]),
            "urgency": int(res["urgency"]),
            "fear": int(res["fear"]),
            "interval_val": int(res["interval_val"]),
            "interval_unit": str(res["interval_unit"]),
            "due_datetime": str(res["due_datetime"]),
            "max_repeats": int(res["max_repeats"]),
            "reward_type": str(res["reward_type"]),
            "money_reward": float(res["money_reward"]),
            "reward_item": str(res["reward_item"]),
            "penalty_type": str(res["penalty_type"]),
            "penalty_val": float(res["penalty_val"])
        }

    def task_menu(self):
        clear_full_screen()
        selected_idx = 0
        current_category = "ALL"
        sort_modes = ["Default", "Status", "Difficulty", "Penalty", "Alphabetical"]
        sort_idx = 0

        last_rendered_second = -1
        needs_redraw = True

        while True:
            prof = self.ctx.get_profile()
            all_tasks = prof["tasks"]
            categories = ["ALL"] + sorted(list(set(self.ctx.data["categories"])))
            if current_category not in categories: current_category = "ALL"

            if current_category == "ALL":
                filtered_tasks = list(all_tasks)
            else:
                filtered_tasks = [t for t in all_tasks if t.get("category", "General") == current_category]

            active_sort = sort_modes[sort_idx]
            if active_sort == "Status":
                filtered_tasks.sort(key=lambda x: (x.get("current_repeats", 0) >= x.get("max_repeats", 1), x["id"]))
            elif active_sort == "Difficulty":
                filtered_tasks.sort(key=lambda x: x.get("difficulty", 0), reverse=True)
            elif active_sort == "Penalty":
                filtered_tasks.sort(key=lambda x: x.get("penalty_val", 0), reverse=True)
            elif active_sort == "Alphabetical":
                filtered_tasks.sort(key=lambda x: x["title"].lower())

            if selected_idx >= len(filtered_tasks):
                selected_idx = max(0, len(filtered_tasks) - 1)

            now_sec = datetime.now().second
            now_dt = datetime.now()

            if needs_redraw or now_sec != last_rendered_second:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- TASK LIST ---{Colors.RESET}")
                p_line(f"{Colors.CYAN}Category Filter: [{current_category}]{Colors.RESET} | {Colors.MAGENTA}Sort Mode: [{active_sort}]{Colors.RESET}")
                p_line()

                if not filtered_tasks:
                    p_line(f"{Colors.GREY}No tasks found. Press 'E' to Manage Tasks or 'C' to cycle Category.{Colors.RESET}")
                else:
                    for idx, t in enumerate(filtered_tasks):
                        cursor = "► " if idx == selected_idx else "  "
                        is_finished = t.get("current_repeats", 0) >= t.get("max_repeats", 1)

                        due_str = t.get("due_datetime", "2026-10-31 00:00")
                        is_overdue = False
                        try:
                            due_dt = datetime.strptime(due_str, "%Y-%m-%d %H:%M")
                            if now_dt > due_dt and not is_finished:
                                is_overdue = True
                        except ValueError:
                            pass

                        if is_finished:
                            status = f"{Colors.GREEN}[DONE]{Colors.RESET}"
                        elif is_overdue:
                            status = f"{Colors.RED}[OVERDUE]{Colors.RESET}"
                        else:
                            status = f"{Colors.YELLOW}[PENDING]{Colors.RESET}"

                        repeats_str = f"Rep: {t.get('current_repeats', 0)}/{t.get('max_repeats', 1)}"
                        streak_str = f"Streak: 🔥{t.get('streak', 0)}" if t.get("max_repeats", 1) >= 2 else ""

                        base_m_exp, sk_exp, _ = self.ctx.calculate_task_rewards(t.get("difficulty", 50), t.get("urgency", 30), t.get("fear", 10))
                        mult = 1.0 + (t.get("streak", 0) * 0.15) if t.get("max_repeats", 1) >= 2 else 1.0

                        main_reward_str = ""
                        r_type = t.get("reward_type", "XP")
                        if r_type == "XP": main_reward_str = f"+{int(base_m_exp * mult)} EXP"
                        elif r_type == "HP": main_reward_str = f"+{int(20 * mult)} HP"
                        elif r_type == "Item": main_reward_str = f"Item: {t.get('reward_item', 'Potion')}"

                        m_val = float(t.get("money_reward", 10.0)) * mult
                        money_str = f"+${m_val:.2f}" if m_val > 0 else ""

                        reward_parts = [p for p in [main_reward_str, money_str] if p]
                        reward_str = " & ".join(reward_parts) if reward_parts else "None"

                        int_info = f"Every {t.get('interval_val',1)} {t.get('interval_unit','days')}"
                        line = f"{cursor}{status} {t['title']:<16} | Due: {due_str} ({int_info}) | {repeats_str} {streak_str:<8} | Reward: {reward_str}"
                        if idx == selected_idx:
                            p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                        else:
                            p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select  [ENTER] Complete  [F] Fail  [C] Category  [S] Sort  [E] Edit Mode  [0/ESC] Back")
                
                last_rendered_second = now_sec
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            key_upper = key.upper() if isinstance(key, str) else ""

            if key == "UP":
                selected_idx = (selected_idx - 1) % len(filtered_tasks) if filtered_tasks else 0
            elif key == "DOWN":
                selected_idx = (selected_idx + 1) % len(filtered_tasks) if filtered_tasks else 0
            elif key_upper == "C":
                cat_idx = (categories.index(current_category) + 1) % len(categories)
                current_category = categories[cat_idx]
                selected_idx = 0
            elif key_upper == "S":
                sort_idx = (sort_idx + 1) % len(sort_modes)
                selected_idx = 0
            elif key == "ENTER" and filtered_tasks:
                t = filtered_tasks[selected_idx]
                if t.get("current_repeats", 0) < t.get("max_repeats", 1):
                    t["current_repeats"] += 1
                    t["streak"] = t.get("streak", 0) + 1

                    try:
                        curr_due = datetime.strptime(t["due_datetime"], "%Y-%m-%d %H:%M")
                        base_dt = max(now_dt, curr_due)
                    except ValueError:
                        base_dt = now_dt

                    next_due = self.ctx.compute_next_due(base_dt, int(t.get("interval_val", 1)), str(t.get("interval_unit", "days")))
                    t["due_datetime"] = next_due.strftime("%Y-%m-%d %H:%M")

                    base_m_exp, sk_exp, _ = self.ctx.calculate_task_rewards(t.get("difficulty", 50), t.get("urgency", 30), t.get("fear", 10))
                    mult = 1.0 + (t["streak"] * 0.15) if t.get("max_repeats", 1) >= 2 else 1.0

                    m_val = float(t.get("money_reward", 0.0)) * mult
                    if m_val > 0:
                        old_m = prof["money"]
                        self.status_mgr.animate_money_change(old_m, old_m + m_val)

                    r_type = t.get("reward_type", "XP")
                    if r_type == "XP":
                        self.status_mgr.add_exp_animated(int(base_m_exp * mult), t["skill"], sk_exp)
                    elif r_type == "HP":
                        old_hp = prof["hp"]
                        target_hp = min(prof["max_hp"], old_hp + (20 * mult))
                        self.status_mgr.animate_hp_change(old_hp, target_hp)
                    elif r_type == "Item":
                        item_n = t.get("reward_item", "Health Potion")
                        prof["inventory"][item_n] = prof["inventory"].get(item_n, 0) + 1
                        self.ctx.save_data()

            elif key_upper == "F" and filtered_tasks:
                t = filtered_tasks[selected_idx]
                t["streak"] = 0
                p_type = t.get("penalty_type", "HP Loss")
                p_val = t.get("penalty_val", 15.0)

                if p_type == "HP Loss":
                    old_hp = prof["hp"]
                    target_hp = max(0, old_hp - p_val)
                    print(f"\n{Colors.RED}{Colors.BOLD}❌ FAILED TASK: '{t['title']}'! Streak reset. Suffered -{p_val:.1f} HP Penalty!{Colors.RESET}")
                    time.sleep(1.2)
                    self.status_mgr.animate_hp_change(old_hp, target_hp)
                elif p_type == "XP Loss":
                    prof["exp"] = max(0, prof["exp"] - int(p_val))
                    self.ctx.save_data()
                    print(f"\n{Colors.RED}{Colors.BOLD}❌ FAILED TASK: '{t['title']}'! Streak reset. Lost {int(p_val)} Main EXP!{Colors.RESET}")
                    time.sleep(1.2)
                elif p_type == "Penalty Timer":
                    duration_min = int(p_val) if p_val > 0 else 15
                    prof["timers"].append({
                        "name": f"Penalty: {t['title']}",
                        "start_time": time.time(),
                        "duration_sec": duration_min * 60,
                        "color": "RED",
                        "type": "penalty"
                    })
                    self.ctx.save_data()
                    print(f"\n{Colors.RED}{Colors.BOLD}❌ FAILED TASK: '{t['title']}'! Penalty Timer activated for {duration_min} minutes!{Colors.RESET}")
                    time.sleep(1.2)

            elif key_upper == "E":
                self.task_management_menu()
                clear_full_screen()
            elif key in ("0", "ESC") or key_upper == "Q":
                break
        clear_full_screen()

    def task_management_menu(self):
        clear_full_screen()
        sel = 0
        last_sec = -1
        needs_redraw = True

        while True:
            prof = self.ctx.get_profile()
            tasks = prof["tasks"]
            items = tasks + [{"id": -1, "title": "[+ Create New Task...]", "is_create_slot": True}]
            if sel >= len(items):
                sel = max(0, len(items) - 1)

            now_sec = time.time()
            if needs_redraw or int(now_sec) != last_sec:
                self.status_mgr.display_status_header()
                p_line(f"{Colors.BOLD}--- TASK EDIT MODE ---{Colors.RESET}")
                p_line(f"{Colors.CYAN}Select a task with Arrow Keys and press ENTER to edit or delete.{Colors.RESET}")
                p_line()

                for idx, item in enumerate(items):
                    cursor = "► " if idx == sel else "  "
                    if item.get("is_create_slot"):
                        line = f"{cursor}{Colors.GREEN}{item['title']}{Colors.RESET}"
                    else:
                        line = f"{cursor}{item['title']:<25} | Cat: [{item.get('category','General'):<8}] | Diff: {item.get('difficulty',50)}%"
                    
                    if idx == sel:
                        p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                    else:
                        p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select Task  [ENTER] Manage Task  [C] Create Task  [0/ESC] Exit Edit Mode")
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
                task_data = self.task_form_editor()
                if task_data:
                    new_id = max([t["id"] for t in tasks], default=0) + 1
                    task_data.update({"id": new_id, "current_repeats": 0, "streak": 0})
                    tasks.append(task_data)
                    self.ctx.save_data()
                clear_full_screen()

            elif key == "ENTER":
                selected_item = items[sel]
                if selected_item.get("is_create_slot"):
                    task_data = self.task_form_editor()
                    if task_data:
                        new_id = max([t["id"] for t in tasks], default=0) + 1
                        task_data.update({"id": new_id, "current_repeats": 0, "streak": 0})
                        tasks.append(task_data)
                        self.ctx.save_data()
                else:
                    t = selected_item
                    action_opts = ["1. Edit Task Details", "2. Reset Task Progress", "3. Delete Task", "0. Cancel"]
                    choice = self.ctx.run_action_menu(f"Task Actions: {t['title']}", action_opts, self.status_mgr.display_status_header)
                    if choice == 0:
                        updated = self.task_form_editor(existing_task=t)
                        if updated:
                            t.update(updated)
                            self.ctx.save_data()
                    elif choice == 1:
                        t["current_repeats"] = 0
                        t["streak"] = 0
                        self.ctx.save_data()
                    elif choice == 2:
                        prof["tasks"] = [x for x in prof["tasks"] if x["id"] != t["id"]]
                        self.ctx.save_data()
                clear_full_screen()

            elif key in ("0", "ESC") or key_upper in ("Q", "E"):
                break
        clear_full_screen()