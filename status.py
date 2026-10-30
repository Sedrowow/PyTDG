#!/usr/bin/env python3
"""
Character Status, Health, EXP, Wallet Animations, and Custom Timer HUD Manager.
"""

import time
import math
from datetime import datetime
from typing import Optional
from utils import Colors, GameContext, move_cursor_home, p_line, render_bar, read_key, clear_full_screen

class StatusManager:
    def __init__(self, ctx: GameContext):
        self.ctx = ctx

    def display_status_header(self, override_hp: Optional[float] = None, override_exp: Optional[float] = None, override_skill_exp: Optional[tuple] = None, override_money: Optional[float] = None):
        prof = self.ctx.get_profile()
        skills = prof["skills"]
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        current_hp = override_hp if override_hp is not None else prof["hp"]
        current_exp = override_exp if override_exp is not None else prof["exp"]
        current_money = override_money if override_money is not None else prof["money"]
        req_exp = self.ctx.exp_for_level(prof["level"])

        active_timers = []
        now_time = time.time()
        timers_list = list(prof.get("timers", []))
        for tm in timers_list:
            elapsed = now_time - tm.get("start_time", now_time)
            total_sec = tm.get("duration_sec", 1)
            remaining = total_sec - elapsed
            if remaining > 0:
                active_timers.append((tm, remaining, total_sec))
            else:
                if tm in prof.get("timers", []):
                    prof["timers"].remove(tm)

        move_cursor_home()
        p_line(f"{Colors.GREY}📅 METRIC TIME: {now_str} | PROFILE: [{prof['name']}]{Colors.RESET}")
        p_line("=" * 70)
        p_line(f"{Colors.BOLD}{Colors.WHITE} CHARACTER STATUS: {prof['name']}{Colors.RESET}")
        p_line("=" * 70)
        p_line(f" Level:    {Colors.YELLOW}{prof['level']}{Colors.RESET}")
        p_line(f" Health:   {render_bar(current_hp, prof['max_hp'], 22, Colors.RED)}")
        p_line(f" Main EXP: {render_bar(current_exp, req_exp, 22, Colors.GREEN)}")
        p_line(f" Wallet:   {Colors.YELLOW}${current_money:.2f}{Colors.RESET}")

        if active_timers:
            p_line(f" Active Timers:")
            for tm, remaining, total_sec in active_timers:
                mins = int(remaining // 60)
                secs = int(remaining % 60)
                tm_color_str = tm.get("color", "CYAN")
                color = Colors.RED if tm.get("type") == "penalty" else Colors.parse_color(tm_color_str)
                bar = render_bar(remaining, total_sec, 16, color, show_values=False)
                p_line(f"  • {color}{tm['name']:<18}{Colors.RESET} ({mins:02d}:{secs:02d}) {bar}")

        p_line("-" * 70)
        p_line(f"{Colors.BOLD} Skills:{Colors.RESET}")

        for s_name, s_info in skills.items():
            s_req = self.ctx.exp_for_level(s_info["level"])
            s_exp = s_info["exp"]
            if override_skill_exp and override_skill_exp[0] == s_name:
                s_exp = override_skill_exp[1]
            p_line(f"  • {s_name:<15} Lv.{s_info['level']:<2} {render_bar(s_exp, s_req, 14, Colors.BLUE)}")
        p_line("=" * 70)

    def animate_hp_change(self, old_hp: float, new_hp: float):
        gap = abs(new_hp - old_hp)
        if gap < 0.1:
            self.ctx.get_profile()["hp"] = new_hp
            self.ctx.save_data()
            return

        frames = max(20, min(50, int(math.sqrt(gap) * 5)))
        for i in range(frames + 1):
            t = i / frames
            ease_t = 3 * (t ** 2) - 2 * (t ** 3)
            current = old_hp + (new_hp - old_hp) * ease_t
            self.display_status_header(override_hp=current)
            time.sleep(0.015)

        self.ctx.get_profile()["hp"] = new_hp
        self.ctx.save_data()
        self.display_status_header()

    def animate_money_change(self, old_money: float, new_money: float):
        gap = abs(new_money - old_money)
        if gap < 0.01:
            self.ctx.get_profile()["money"] = new_money
            self.ctx.save_data()
            return

        frames = max(20, min(50, int(math.sqrt(gap) * 5)))
        for i in range(frames + 1):
            t = i / frames
            ease_t = 3 * (t ** 2) - 2 * (t ** 3)
            current = old_money + (new_money - old_money) * ease_t
            self.display_status_header(override_money=current)
            time.sleep(0.015)

        self.ctx.get_profile()["money"] = new_money
        self.ctx.save_data()
        self.display_status_header()

    def add_exp_animated(self, main_exp_gain: int, skill_name: Optional[str] = None, skill_exp_gain: int = 0):
        prof = self.ctx.get_profile()
        target_exp = prof["exp"] + main_exp_gain
        start_exp = prof["exp"]
        req_exp = self.ctx.exp_for_level(prof["level"])

        frames = max(20, min(50, int(math.sqrt(max(1, main_exp_gain))) * 4))
        if main_exp_gain > 0:
            for i in range(frames + 1):
                t = i / frames
                ease_t = 3 * (t ** 2) - 2 * (t ** 3)
                current_exp = start_exp + (target_exp - start_exp) * ease_t

                if current_exp >= req_exp:
                    prof["exp"] = 0
                    target_exp -= req_exp
                    start_exp = 0
                    prof["level"] += 1

                    for _ in range(3):
                        clear_full_screen()
                        print(f"\n{Colors.HIGHLIGHT}{Colors.BOLD} 🎉 LEVEL UP! REACHED LEVEL {prof['level']}! 🎉 {Colors.RESET}\n", flush=True)
                        time.sleep(0.15)
                        clear_full_screen()
                        time.sleep(0.1)

                    old_max_hp = prof["max_hp"]
                    increase = math.ceil(old_max_hp * (prof["hp_scale_value"] / 100.0)) if prof["hp_scale_mode"] == "percentage" else int(prof["hp_scale_value"])
                    prof["max_hp"] += increase
                    prof["hp"] += increase
                    req_exp = self.ctx.exp_for_level(prof["level"])

                self.display_status_header(override_exp=current_exp)
                time.sleep(0.015)

        prof["exp"] = target_exp

        if skill_name and skill_name != "None" and skill_exp_gain > 0:
            skills = prof["skills"]
            if skill_name not in skills:
                skills[skill_name] = {"level": 1, "exp": 0}

            sk = skills[skill_name]
            target_sk_exp = sk["exp"] + skill_exp_gain
            start_sk_exp = sk["exp"]
            sk_req = self.ctx.exp_for_level(sk["level"])

            sk_frames = max(20, min(50, int(math.sqrt(skill_exp_gain) * 4)))
            for i in range(sk_frames + 1):
                t = i / sk_frames
                ease_t = 3 * (t ** 2) - 2 * (t ** 3)
                current_sk_exp = start_sk_exp + (target_sk_exp - start_sk_exp) * ease_t

                if current_sk_exp >= sk_req:
                    sk["exp"] = 0
                    target_sk_exp -= sk_req
                    start_sk_exp = 0
                    sk["level"] += 1
                    sk_req = self.ctx.exp_for_level(sk["level"])

                self.display_status_header(override_skill_exp=(skill_name, current_sk_exp))
                time.sleep(0.015)

            sk["exp"] = target_sk_exp

        self.ctx.save_data()
        self.display_status_header()

    def quick_adjust_hp(self):
        prof = self.ctx.get_profile()
        fields = [
            {"key": "mode", "label": "Adjustment Mode", "type": "select", "val": "Damage (-)", "options": ["Damage (-)", "Heal (+)", "Set Exact (=)"]},
            {"key": "amount", "label": "HP Amount / Target", "type": "number", "val": 20.0},
            {"key": "SAVE", "label": "APPLY HP CHANGE", "type": "button"},
            {"key": "CANCEL", "label": "CANCEL", "type": "button"}
        ]
        res = self.ctx.run_menu_form("Quick Adjust HP", fields, self.display_status_header)
        if res:
            mode = str(res.get("mode", "Damage (-)"))
            amount = float(res.get("amount", 20.0))
            old_hp = prof["hp"]
            if mode == "Damage (-)":
                target_hp = max(0.0, old_hp - amount)
            elif mode == "Heal (+)":
                target_hp = min(prof["max_hp"], old_hp + amount)
            else:
                target_hp = max(0.0, min(prof["max_hp"], amount))
            self.animate_hp_change(old_hp, target_hp)
        clear_full_screen()

    def timer_manager_menu(self):
        clear_full_screen()
        opts = ["1. Start New Custom Timer", "2. Stop Running Timer", "0. Back to Main Menu"]
        sel = 0
        last_sec = -1
        needs_redraw = True

        while True:
            now_sec = datetime.now().second
            if needs_redraw or now_sec != last_sec:
                self.display_status_header()
                p_line(f"{Colors.BOLD}--- TIMERS & CLOCK MANAGER ---{Colors.RESET}")
                p_line()
                for idx, opt in enumerate(opts):
                    cursor = "► " if idx == sel else "  "
                    line = f"{cursor}{opt}"
                    if idx == sel:
                        p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                    else:
                        p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select  [ENTER] Confirm  [0/ESC] Back")
                last_sec = now_sec
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            key_upper = key.upper() if isinstance(key, str) else ""

            if key == "UP":
                sel = (sel - 1) % len(opts)
            elif key == "DOWN":
                sel = (sel + 1) % len(opts)
            elif key in ("1", "2", "0"):
                sel = ["1", "2", "0"].index(key)
                key = "ENTER"

            if key == "ENTER":
                if sel == 0:
                    fields = [
                        {"key": "name", "label": "Timer Name", "type": "text", "val": "Focus Session"},
                        {"key": "minutes", "label": "Duration (Minutes)", "type": "number", "val": 25},
                        {"key": "color", "label": "Timer Color", "type": "select", "val": "CYAN", "options": ["CYAN", "GOLD", "PURPLE", "GREEN", "BLUE", "MAGENTA", "ORANGE"]},
                        {"key": "type", "label": "Timer Type", "type": "select", "val": "Focus", "options": ["Focus", "Custom", "Penalty"]},
                        {"key": "SAVE", "label": "START TIMER", "type": "button"},
                        {"key": "CANCEL", "label": "CANCEL", "type": "button"}
                    ]
                    res = self.ctx.run_menu_form("Start Custom Timer", fields, self.display_status_header)
                    if res:
                        prof = self.ctx.get_profile()
                        dur_min = float(res.get("minutes", 25))
                        prof["timers"].append({
                            "name": str(res["name"]),
                            "start_time": time.time(),
                            "duration_sec": max(10, dur_min * 60),
                            "color": str(res["color"]),
                            "type": str(res["type"]).lower()
                        })
                        self.ctx.save_data()
                        print(f"\n{Colors.GREEN}Started timer '{res['name']}' ({res['color']}) for {dur_min} minutes!{Colors.RESET}")
                        time.sleep(1.0)

                elif sel == 1:
                    prof = self.ctx.get_profile()
                    timers = prof.get("timers", [])
                    if not timers:
                        print(f"\n{Colors.RED}No active timers currently running!{Colors.RESET}")
                        time.sleep(1.2)
                    else:
                        t_options = [f"• {t['name']} ({int((t['duration_sec'] - (time.time() - t['start_time']))//60)}m left)" for t in timers] + ["0. Cancel"]
                        choice = self.ctx.run_action_menu("Select Timer to Stop", t_options, self.display_status_header)
                        if choice is not None and choice < len(timers):
                            stopped = timers.pop(choice)
                            self.ctx.save_data()
                            print(f"\n{Colors.YELLOW}Stopped active timer '{stopped['name']}'!{Colors.RESET}")
                            time.sleep(1.0)

                elif sel == 2:
                    break
                clear_full_screen()

            elif key in ("0", "ESC") or key_upper == "Q":
                break
        clear_full_screen()