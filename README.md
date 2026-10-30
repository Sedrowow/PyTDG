# 🎮 PyTDG — Terminal LifeRPG

**PyTDG** (Terminal LifeRPG) is a gamified productivity application and task management system for your terminal. Turn your daily tasks, habits, and goals into an immersive RPG complete with character leveling, skill progression, gold earnings, item crafting, active focus timers, and interactive casino mini-games.

Built entirely with standard Python libraries—no external dependencies required.

---

## ✨ Features

- 🎯 **Gamified Task & Habit System**
  - Custom task creation with **Difficulty**, **Urgency**, and **Fear Factor** sliders.
  - Flexible intervals (minutes, hours, days) with automatic due-date rollover.
  - Streak multipliers (+15% boost per consecutive completion).
  - Penalties for failed tasks: HP damage, EXP loss, or forced Focus/Penalty Timers.
  - Category filtering and multiple sorting modes (Status, Difficulty, Penalty, Alphabetical).

- 📊 **Dynamic Terminal HUD & Animated Progress**
  - Real-time ASCII status header with HP, Main EXP, Wallet balance, active focus timers, and individual skill bars.
  - Smooth eased animations for HP changes, money gains/losses, EXP gain, and screen-flashing Level Up notifications.

- 🛍️ **Shop, Casino & Custom Symbol Editor**
  - **European Roulette**: Bet on Red/Black, Even/Odd, or single numbers (35:1 payout) with animated wheel spins.
  - **3-Reel Classic Slots**: Weighted symbols with 2x double match and 3x triple match payout multipliers.
  - **5x5 Wheel of Fortune**: Customizable spinning wheel with custom item/money/EXP rewards.
  - **In-Terminal 5x5 ASCII Pixel Art Editor**: Design custom pixel art symbols for casino games directly within the terminal UI.

- 🧪 **Crafting Workshop & Master Item Registry**
  - Complete master item registry for custom potions, EXP boosters, focus timers, and collectible trophies.
  - Multi-ingredient recipe crafting system to synthesize high-tier items from raw task rewards.

- ⏱️ **Focus & Clock Manager**
  - Built-in Pomodoro/Focus session timers with live visual progress bars rendered right on the main status HUD.

- 👤 **Multi-Profile & Custom Scaling**
  - Create and switch between multiple character profiles.
  - Customizable stat scaling (percentage or fixed HP increase per level).
  - Local JSON auto-saving (`liferpg_data.json`).

---

## 🛠️ Architecture & Project Structure

```text
PyTDG/
├── main.py          # Application entry point & main menu loop
├── status.py        # StatusManager: HUD rendering, bar animations, timers, HP/EXP logic
├── tasks.py         # TaskManager: Task creation, editing, completion, penalties, sorting
├── shopcasino.py    # ShopCasinoManager: Shop, Roulette, Slots, 5x5 Wheel, Pixel Art Editor
├── item.py          # ItemManager: Master Item Registry, Inventory, Crafting Workshop
├── settings.py      # SettingsManager: Profile creation/switching, stat editor, sample data
└── utils.py         # Core utilities: CbreakTerminal, key-reading, ANSI colors, math calculations
```

---

## 🚀 Quickstart & Installation

### Prerequisites
- **Python 3.8+**
- A terminal with standard ANSI color support (Linux, macOS Terminal/iTerm, Windows Terminal/PowerShell).

### Running PyTDG
1. Clone or download the repository:
   ```bash
   git clone https://github.com/your-username/PyTDG.git
   cd PyTDG
   ```
2. Run the application:
   ```bash
   python3 main.py
   ```
   *(On first run, PyTDG will offer to load starter tasks, items, and mini-games).*

---

## 📐 Task Reward Mechanics

Task rewards are dynamically calculated based on three attributes rated from 0 to 100:

- **Difficulty ($D$)**: $50\%$ weight
- **Urgency ($U$)**: $30\%$ weight
- **Fear Factor ($F$)**: $20\%$ weight

The composite Task Score is determined by:
$$ \text{Score} = 0.50 \cdot D + 0.30 \cdot U + 0.20 \cdot F $$

From the composite score, the scaling factor is derived:
$$ \text{Factor} = \left( \frac{\text{Score}}{100} \right)^{1.3} $$

### Base Reward Formulas
- **Main EXP**: $20 + \lfloor 830 \cdot \text{Factor} \rfloor$
- **Associated Skill EXP**: $15 + \lfloor 1185 \cdot \text{Factor} \rfloor$
- **Streak Bonus Multiplier**: $\text{Mult} = 1.0 + (0.15 \cdot \text{Streak})$ *(for repeatable tasks)*

---

## 🕹️ Controls Reference

PyTDG features responsive terminal controls with hotkeys for fast navigation:

| Key / Control | Action |
| :--- | :--- |
| `↑` / `↓` | Navigate menu items, lists, or form fields |
| `←` / `→` | Adjust sliders, select options, shift form controls |
| `ENTER` | Confirm selection, execute action, or complete task |
| `ESC` / `0` / `Q` | Go back to previous menu or exit |
| `1` – `7` | Main menu direct hotkeys |
| `T` | Active Timers & Clock Manager |
| `L` | Quick Adjust HP (Damage / Heal) |
| `E` | Enter Edit Mode (Tasks, Shop, Crafting) |
| `C` | Cycle Category filter / Create item |
| `S` | Cycle Sort order (Tasks) |
| `F` | Mark selected task as Failed |
| `SPACE` / Any Key | Draw/Cycle pixel in 5x5 ASCII Pixel Editor |

---

## 📦 Data Storage

All character progression, inventory items, task configurations, crafting recipes, and casino symbol weights are saved automatically to `liferpg_data.json` in the application directory. You can backup or transfer this file to keep your save state intact across machines.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
