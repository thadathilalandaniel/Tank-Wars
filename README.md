# 🎮 Tank Wars

**A Python-based tower defense game powered by Data Structures and Algorithms.**

Tank Wars is a 2D tower defense game built using Python and Pygame. Defend your base against waves of increasingly dangerous enemies, upgrade your tank, manage resources, and experiment with different enemy-targeting algorithms.

The game combines arcade-style combat with practical implementations of fundamental Data Structures and Algorithms (Defense), making it both entertaining and educational.

## ✨ Features

### 🎯 Dynamic Combat
- Move the tank using the keyboard or mouse.
- Automatically target and shoot enemies within attack range.
- Track enemy health using health bars and damage indicators.
- Earn coins by defeating enemies.
- Encounter different enemy types with different strengths and movement speeds.

### 🌊 Wave-Based Progression
- Choose between 40 waves.
- Face progressively more challenging enemies.
- Experience increasing enemy health, quantity, damage, and movement speed.
- Earn rewards and prepare for subsequent waves.
- Enjoy wave completion, victory, and game-over screens.

### 🛡️ Tank Upgrades and Powers
- **Shield:** Absorb incoming damage before losing hearts.
- **Attack Power:** Increase the damage dealt by projectiles.
- **Shooting Speed:** Reduce the delay between shots.
- **Extra Hearts:** Spend coins to restore health, subject to the maximum health limit.
- **Emergency Blast:** Damage multiple enemies simultaneously.
- **Coin Economy:** Earn and spend coins strategically to survive difficult waves.

### 🧠 Data Structures and Algorithms

Tank Wars integrates Defense directly into its combat system.

| Concept | Application |
|---|---|
| Queue (FIFO) | Target enemies according to their arrival order. |
| Binary Max-Heap Priority Queue | Prioritize enemies based on their threat scores. |
| Greedy Algorithm | Select the nearest eligible enemy. |
| Lists | Manage active enemies and projectiles. |
| Searching | Find suitable targets during combat. |

Switching targeting modes changes how the tank selects enemies. The game also includes an Algorithm Lab to help players understand the selected algorithm and its time complexity.

### 🎮 Controls

| Action | Control |
|---|---|
| Move tank | Arrow keys or WASD |
| Mouse movement | Click and drag the tank |
| Select targeting mode | On-screen targeting buttons |
| Purchase upgrades | On-screen upgrade buttons |
| Pause / Resume | Dedicated pause button |
| Restart | Restart button |

*Controls may vary slightly depending on the current implementation.*

## 🛠️ Technology Stack

- **Language:** Python
- **Game Framework:** Pygame
- **Defense:** Queue, Binary Max-Heap, Greedy Target Selection
- **Graphics:** Pygame shapes, text, and animations
- **Testing:** Python testing tools

## 📁 Project Structure

```text
Tank-Wars/
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── defense/
│   ├── queue_ds.py
│   ├── priority_queue.py
│   ├── greedy_targeting.py
│   └── targeting.py
├── game/
│   ├── game_manager.py
│   ├── wave_manager.py
│   ├── combat.py
│   └── collision.py
├── entities/
│   ├── tower.py
│   ├── enemy.py
│   ├── projectile.py
│   └── effects.py
├── systems/
│   ├── upgrades.py
│   ├── shield.py
│   ├── economy.py
│   └── blast.py
├── ui/
│   ├── game_screen.py
│   ├── hud.py
│   ├── menus.py
│   ├── buttons.py
│   └── algorithm_lab.py
└── tests/
```

*The structure above describes the intended organization. Keep the README synchronized with the actual files in the repository.*

## 🚀 Installation and Setup

### Prerequisites

- Python 3.10 or later recommended.
- Git.
- Pygame and the dependencies listed in `requirements.txt`.

### 1. Clone the repository

```bash
git clone https://github.com/thadathilalandaniel/Tank-Wars.git
cd Tank-Wars
```

### 2. Create a virtual environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the game

```bash
python main.py
```

## 📚 Learning Objectives

Tank Wars demonstrates how Defense concepts can be applied to a practical application.

- Understand FIFO behaviour through Queue-based targeting.
- Learn how a binary max-heap maintains priorities.
- Compare priority-based targeting with greedy nearest-target selection.
- Understand algorithmic time complexity.
- Explore object-oriented programming through game entities and systems.
- Apply collision detection, game loops, resource management, and event handling.

## 🔬 Future Improvements

Potential extensions include:

- Additional enemy types and boss battles.
- More targeting algorithms.
- New tank abilities and upgrade paths.
- Persistent high scores and player statistics.
- Improved sound effects and visual animations.
- Additional levels and challenge modes.

## 👨‍💻 Author

**Alan Daniel**

GitHub: [@thadathilalandaniel](https://github.com/thadathilalandaniel)

## 📄 License

Add a license if you intend to distribute or reuse the project publicly. Until a license is added, the repository remains subject to the default copyright rules.

---

**Tank Wars — Defend your base. Master your strategy. Explore the algorithms.**
