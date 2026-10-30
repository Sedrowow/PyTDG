#!/usr/bin/env python3
"""
Core utility module providing terminal I/O, persistence, menu forms,
and shared configuration structures across LifeRPG modules.
"""

import os
import sys
import json
import math
import time
import select
import random
import importlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

DATA_FILE = "liferpg_data.json"

if os.name == 'nt':
    os.system('')

termios = None
tty = None
try:
    termios = importlib.import_module('termios')
    tty = importlib.import_module('tty')
except ImportError:
    pass

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GREY = "\033[90m"
    GOLD = "\033[38;2;255;215;0m"
    PURPLE = "\033[38;2;160;32;240m"
    ORANGE = "\033[38;2;255;140;0m"
    HIGHLIGHT = "\033[7m"

    @staticmethod
    def parse_color(color_str: str) -> str:
        if not color_str:
            return Colors.WHITE
        c_upper = color_str.upper().strip()
        named = {
            "RED": Colors.RED, "GREEN": Colors.GREEN, "YELLOW": Colors.YELLOW,
            "BLUE": Colors.BLUE, "MAGENTA": Colors.MAGENTA, "CYAN": Colors.CYAN,
            "WHITE": Colors.WHITE, "GREY": Colors.GREY, "GOLD": Colors.GOLD,
            "PURPLE": Colors.PURPLE, "ORANGE": Colors.ORANGE
        }
        if c_upper in named:
            return named[c_upper]
        if c_upper.startswith("#") and len(c_upper) == 7:
            try:
                r = int(c_upper[1:3], 16)
                g = int(c_upper[3:5], 16)
                b = int(c_upper[5:7], 16)
                return f"\033[38;2;{r};{g};{b}m"
            except ValueError:
                pass
        return Colors.WHITE

class CbreakTerminal:
    def __init__(self):
        self.is_posix = os.name != 'nt' and termios is not None
        self.old_settings = None
        self.active = False

    def enter(self):
        if self.is_posix and sys.stdin.isatty() and not self.active:
            self.old_settings = termios.tcgetattr(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            self.active = True

    def restore(self):
        if self.is_posix and self.old_settings and self.active:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, self.old_settings)
            self.active = False

    def flush_input(self):
        if self.is_posix and self.active:
            termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)

    def __enter__(self):
        self.enter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.restore()

def move_cursor_home():
    print("\033[H", end="", flush=True)

def clear_full_screen():
    print("\033[2J\033[H", end="", flush=True)

def p_line(text: str = ""):
    print(f"{text}\033[K")

def render_bar(current: float, maximum: float, length: int = 20, color: str = Colors.GREEN, show_values: bool = True) -> str:
    if maximum <= 0:
        maximum = 1.0
    pct = max(0.0, min(1.0, current / maximum))
    total_quarters = int(round(pct * length * 4))
    full_blocks = total_quarters // 4
    remainder = total_quarters % 4

    quarter_chars = {1: "▎", 2: "▌", 3: "▊"}
    part_char = quarter_chars.get(remainder, "")
    empty_blocks = max(0, length - full_blocks - (1 if remainder > 0 else 0))

    bar_str = "█" * full_blocks + part_char + "░" * empty_blocks
    val_str = f" {current:.0f}/{maximum:.0f}" if show_values else f" {int(pct * 100)}%"
    return f"{color}[{bar_str}]{Colors.RESET}{val_str}"

def read_key(timeout: float = 0.03) -> Optional[str]:
    if os.name == 'nt':
        import msvcrt
        start_time = time.time()
        while time.time() - start_time < timeout:
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch in (b'\x00', b'\xe0'):
                    if msvcrt.kbhit():
                        ch2 = msvcrt.getch()
                        if ch2 == b'H': return "UP"
                        if ch2 == b'P': return "DOWN"
                        if ch2 == b'K': return "LEFT"
                        if ch2 == b'M': return "RIGHT"
                elif ch in (b'\r', b'\n'):
                    return "ENTER"
                elif ch == b'\x1b':
                    return "ESC"
                elif ch in (b'\x08', b'\x7f'):
                    return "BACKSPACE"
                else:
                    try:
                        return ch.decode('utf-8')
                    except UnicodeDecodeError:
                        return ""
            time.sleep(0.005)
        return None
    else:
        rlist, _, _ = select.select([0], [], [], timeout)
        if rlist:
            try:
                data = os.read(0, 1024)
            except OSError:
                return None

            if not data:
                return None

            if b'\x1b[A' in data or b'\x1bOA' in data: return "UP"
            if b'\x1b[B' in data or b'\x1bOB' in data: return "DOWN"
            if b'\x1b[C' in data or b'\x1bOC' in data: return "RIGHT"
            if b'\x1b[D' in data or b'\x1bOD' in data: return "LEFT"
            if data == b'\x1b': return "ESC"
            if data in (b'\r', b'\n'): return "ENTER"
            if data in (b'\x08', b'\x7f'): return "BACKSPACE"
            if data in (b'\x03', b'\x04'): return "Q"

            try:
                return data.decode('utf-8', errors='ignore')
            except Exception:
                return ""
        return None

DEFAULT_5x5_ARTS = {
    "SEVEN": ["77777", "   7 ", "  7  ", " 7   ", "7    "],
    "STAR":  ["  *  ", " *** ", "*****", " *** ", " * * "],
    "GEM":   ["  ^  ", " / \\ ", "\\   /", " \\ / ", "  V  "],
    "COIN":  [" .-. ", "| $ |", "|   |", " '-' ", "  .  "],
    "SKULL": [" .-. ", "(o o)", " |=| ", " '=' ", "  V  "]
}

DEFAULT_PROFILE = {
    "name": "Hero",
    "level": 1,
    "exp": 0,
    "hp": 100,
    "max_hp": 100,
    "money": 50.0,
    "hp_scale_mode": "percentage",
    "hp_scale_value": 10.0,
    "skills": {"Fitness": {"level": 1, "exp": 0}, "General": {"level": 1, "exp": 0}},
    "tasks": [],
    "inventory": {},
    "timers": []
}

DEFAULT_DATA = {
    "active_profile_id": "default",
    "profiles": {"default": DEFAULT_PROFILE},
    "categories": ["Fitness", "Study", "Productivity", "General"],
    "items": [
        {"id": 1, "name": "Health Potion", "color": "RED", "description": "Restores 30 HP instantly.", "type": "heal_fixed", "value": 30.0},
        {"id": 2, "name": "EXP Bottle", "color": "GREEN", "description": "Grants 50 Main EXP instantly.", "type": "exp_fixed", "value": 50.0},
        {"id": 3, "name": "Fortune Cookie", "color": "YELLOW", "description": "A tasty treat that does nothing.", "type": "no_effect", "value": 0.0},
        {"id": 4, "name": "Focus Hourglass", "color": "CYAN", "description": "Triggers a 30-minute focus timer upon use.", "type": "timer", "value": 30.0}
    ],
    "shop": [],
    "crafting": []
}

class GameContext:
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self.cbreak_term = CbreakTerminal()
        self.data = self.load_data()
        self.normalize_all_data()

    def prompt_input(self, prompt_text: str) -> str:
        self.cbreak_term.restore()
        print(f"\033[K{prompt_text}", end='', flush=True)
        val = sys.stdin.readline().strip()
        self.cbreak_term.enter()
        self.cbreak_term.flush_input()
        return val

    def get_profile(self) -> Dict[str, Any]:
        p_id = self.data.get("active_profile_id", "default")
        if p_id not in self.data["profiles"]:
            p_id = list(self.data["profiles"].keys())[0]
            self.data["active_profile_id"] = p_id
        return self.data["profiles"][p_id]

    def load_data(self) -> Dict[str, Any]:
        if not os.path.exists(self.data_file):
            self.save_data(DEFAULT_DATA)
            return DEFAULT_DATA
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_DATA

    def save_data(self, data: Optional[Dict[str, Any]] = None):
        if data is None:
            data = self.data
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def normalize_all_data(self):
        self.data.setdefault("active_profile_id", "default")
        self.data.setdefault("profiles", {"default": DEFAULT_PROFILE.copy()})
        self.data.setdefault("categories", ["Fitness", "Study", "Productivity", "General"])
        self.data.setdefault("items", DEFAULT_DATA["items"].copy())
        self.data.setdefault("shop", [])
        self.data.setdefault("crafting", [])

        now_dt = datetime.now()
        for p_id, prof in self.data["profiles"].items():
            prof.setdefault("name", f"Player_{p_id}")
            prof.setdefault("level", 1)
            prof.setdefault("exp", 0)
            prof.setdefault("hp", 100)
            prof.setdefault("max_hp", 100)
            prof.setdefault("money", 50.0)
            prof.setdefault("hp_scale_mode", "percentage")
            prof.setdefault("hp_scale_value", 10.0)
            prof.setdefault("skills", {"Fitness": {"level": 1, "exp": 0}, "General": {"level": 1, "exp": 0}})
            prof.setdefault("tasks", [])
            prof.setdefault("inventory", {})
            prof.setdefault("timers", [])

            for t in prof["tasks"]:
                t.setdefault("category", "General")
                t.setdefault("difficulty", 50)
                t.setdefault("urgency", 30)
                t.setdefault("fear", 10)
                t.setdefault("interval_val", 1)
                t.setdefault("interval_unit", "days")
                t.setdefault("max_repeats", 1)
                t.setdefault("current_repeats", 0)
                t.setdefault("streak", 0)
                t.setdefault("money_reward", 10.0)
                t.setdefault("reward_type", "XP")
                t.setdefault("reward_item", "Health Potion")
                t.setdefault("penalty_type", "HP Loss")
                t.setdefault("penalty_val", 15.0)

                if "due_datetime" not in t:
                    default_due = now_dt + timedelta(days=1)
                    t["due_datetime"] = default_due.strftime("%Y-%m-%d %H:%M")

        for item in self.data["shop"]:
            if item.get("type") in ("wheel", "chests", "slotmachine"):
                item.setdefault("symbols", self.get_default_5x5_symbols())

    def get_default_5x5_symbols(self) -> List[Dict[str, Any]]:
        return [
            {"id": "777", "name": "777", "color": "GOLD", "weight": 10, "tier": "Jackpot", "reward_type": "Money Gain", "val": 100.0, "target_skill": "None", "skill_val": 0.0, "item_name": "Health Potion", "art": DEFAULT_5x5_ARTS["SEVEN"]},
            {"id": "STAR", "name": "STAR", "color": "YELLOW", "weight": 25, "tier": "Rare", "reward_type": "EXP Gain", "val": 50.0, "target_skill": "None", "skill_val": 0.0, "item_name": "Health Potion", "art": DEFAULT_5x5_ARTS["STAR"]},
            {"id": "GEM", "name": "GEM", "color": "PURPLE", "weight": 20, "tier": "Rare", "reward_type": "Item Win", "val": 1.0, "target_skill": "None", "skill_val": 0.0, "item_name": "Health Potion", "art": DEFAULT_5x5_ARTS["GEM"]},
            {"id": "COIN", "name": "COIN", "color": "CYAN", "weight": 30, "tier": "Normal", "reward_type": "Money Gain", "val": 25.0, "target_skill": "None", "skill_val": 0.0, "item_name": "Health Potion", "art": DEFAULT_5x5_ARTS["COIN"]},
            {"id": "SKULL", "name": "SKULL", "color": "RED", "weight": 15, "tier": "Normal", "reward_type": "HP Loss", "val": 20.0, "target_skill": "None", "skill_val": 0.0, "item_name": "Health Potion", "art": DEFAULT_5x5_ARTS["SKULL"]}
        ]

    def get_registered_item_names(self) -> List[str]:
        names = [i["name"] for i in self.data["items"]]
        for s in self.data["shop"]:
            if s.get("type") not in ("slotmachine", "chests", "wheel") and s["name"] not in names:
                names.append(s["name"])
        for c in self.data["crafting"]:
            if c["name"] not in names:
                names.append(c["name"])
        return sorted(list(set(names)))

    @staticmethod
    def exp_for_level(level: int) -> int:
        return int(100 * math.pow(level, 1.2))

    @staticmethod
    def calculate_task_rewards(difficulty: int, urgency: int, fear: int) -> Tuple[int, int, float]:
        d, u, f = max(0, min(100, difficulty)), max(0, min(100, urgency)), max(0, min(100, fear))
        score = (0.50 * d) + (0.30 * u) + (0.20 * f)
        factor = math.pow(score / 100.0, 1.3)
        return int(20 + factor * 830), int(15 + factor * 1185), round(1.0 + factor * 64.0, 2)

    @staticmethod
    def compute_next_due(base_dt: datetime, val: int, unit: str) -> datetime:
        unit = unit.lower()
        if "min" in unit:
            return base_dt + timedelta(minutes=val)
        elif "hour" in unit:
            return base_dt + timedelta(hours=val)
        else:
            return base_dt + timedelta(days=val)

    def run_action_menu(self, title: str, options: List[str], render_header_cb) -> Optional[int]:
        sel = 0
        last_sec = -1
        needs_redraw = True
        while True:
            now_sec = datetime.now().second
            if needs_redraw or now_sec != last_sec:
                render_header_cb()
                p_line(f"{Colors.BOLD}--- {title.upper()} ---{Colors.RESET}")
                p_line()
                for idx, opt in enumerate(options):
                    cursor = "► " if idx == sel else "  "
                    line = f"{cursor}{opt}"
                    if idx == sel:
                        p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                    else:
                        p_line(line)
                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select  [ENTER] Confirm  [ESC/0] Cancel")
                last_sec = now_sec
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            if key == "UP":
                sel = (sel - 1) % len(options)
            elif key == "DOWN":
                sel = (sel + 1) % len(options)
            elif key == "ENTER":
                return sel
            elif key in ("ESC", "0"):
                return None

    def run_menu_form(self, title: str, fields: List[Dict[str, Any]], render_header_cb) -> Optional[Dict[str, Any]]:
        clear_full_screen()
        sel = 0
        last_sec = -1
        needs_redraw = True

        while True:
            now_sec = datetime.now().second
            if needs_redraw or now_sec != last_sec:
                render_header_cb()
                p_line(f"{Colors.BOLD}--- {title.upper()} ---{Colors.RESET}")
                p_line()

                for idx, f in enumerate(fields):
                    cursor = "► " if idx == sel else "  "
                    val_display = ""
                    if f["type"] in ("text", "number"):
                        val_display = f"[{f['val']}]"
                    elif f["type"] == "select":
                        val_display = f"[ < {f['val']} > ]"
                    elif f["type"] == "slider":
                        bar_len = 10
                        filled = int(bar_len * (f['val'] / 100.0))
                        val_display = f"[{'█' * filled}{'░' * (bar_len - filled)}] {f['val']}%"
                    elif f["type"] == "button":
                        val_display = f"*** {f['label']} ***"

                    label_str = f"{f['label']}:" if f["type"] != "button" else ""
                    line = f"{cursor}{label_str:<26} {val_display}"
                    if idx == sel:
                        p_line(f"{Colors.HIGHLIGHT}{line}{Colors.RESET}")
                    else:
                        p_line(line)

                p_line()
                p_line("-" * 70)
                p_line(f"{Colors.BOLD}CONTROLS:{Colors.RESET} [↑/↓] Select  [←/→] Adjust  [ENTER] Change/Confirm  [ESC] Cancel")
                last_sec = now_sec
                needs_redraw = False

            key = read_key(timeout=0.03)
            if not key:
                continue

            needs_redraw = True
            f = fields[sel]

            if key == "UP":
                sel = (sel - 1) % len(fields)
            elif key == "DOWN":
                sel = (sel + 1) % len(fields)
            elif key == "LEFT":
                if f["type"] == "slider": f["val"] = max(0, f["val"] - 5)
                elif f["type"] == "select":
                    opts = f["options"]
                    curr_i = opts.index(f["val"]) if f["val"] in opts else 0
                    f["val"] = opts[(curr_i - 1) % len(opts)]
            elif key == "RIGHT":
                if f["type"] == "slider": f["val"] = min(100, f["val"] + 5)
                elif f["type"] == "select":
                    opts = f["options"]
                    curr_i = opts.index(f["val"]) if f["val"] in opts else 0
                    f["val"] = opts[(curr_i + 1) % len(opts)]
            elif key == "ENTER":
                if f["type"] == "button":
                    if f["key"] == "SAVE":
                        return {field["key"]: field["val"] for field in fields if "key" in field and "val" in field}
                    elif f["key"] == "CANCEL":
                        return None
                elif f["type"] == "select":
                    opts = f["options"]
                    curr_i = opts.index(f["val"]) if f["val"] in opts else 0
                    f["val"] = opts[(curr_i + 1) % len(opts)]
                elif f["type"] in ("text", "number"):
                    new_val = self.prompt_input(f"Enter {f['label']} [{f['val']}]: ")
                    if new_val:
                        if f["type"] == "number":
                            try: f["val"] = float(new_val) if "." in new_val else int(new_val)
                            except ValueError: pass
                        else: f["val"] = new_val
            elif key == "ESC":
                return None