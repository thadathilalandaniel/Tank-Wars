# 🛡️ DSA Defenders: Data Structure & Algorithm Tower Defense

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pygame 2.x](https://img.shields.io/badge/Pygame-2.x-green.svg)](https://www.pygame.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An educational, arcade-style tower defense game developed for college computer science coursework, practical demonstrations, and **Viva Voce examinations**. 

Inspired by the vibrant, polished visual aesthetic of *Tiny Towers* and modern mobile arcade games, **DSA Defenders** bridges theoretical computer science concepts with real-time video game mechanics: the tower's targeting decisions are driven directly by manual, from-scratch implementations of a **FIFO Queue**, a **Binary Max-Heap**, and a **Greedy Nearest-Neighbor Heuristic**.

---

## 🌟 Key Features

- **Tiny Towers Inspired Aesthetic**: Bright blue geometric tile background, stacked magenta turret with smooth directional tracking, and cute robotic enemies (Scouts, Runners, Goliath Tanks, Apex Bosses) with walking foot-cycles and health bars.
- **Manual, Pure-Python DSA Implementations**:
  - **FIFO Queue** (`dsa/queue_ds.py`): Manual head-pointer array with amortized $O(1)$ dequeues (zero `collections.deque`).
  - **Binary Max-Heap** (`dsa/priority_queue.py`): Manual array-based heap with $O(\log n)$ sift-up/sift-down and $O(n)$ Floyd's bottom-up construction (zero `heapq`).
  - **Greedy Algorithm** (`dsa/greedy_targeting.py`): Monotonic squared Euclidean distance comparisons ($O(n)$ without expensive $\sqrt{x}$ calculations).
- **Interactive Algorithm Lab [Key: `L`]**: A real-time inspection dashboard displaying live memory state, queue order, heap threat breakdowns, complexity tables, and high-yield viva study flashcards.
- **40-Wave Campaign**: Full 40-wave progression with dynamic difficulty scaling (health, speed, count, interval) and boss encounters every 10th wave.
- **Power & Upgrade Systems**:
  - Multi-level **Attack Power** and **Shooting Speed** upgrades.
  - **Energy Shield Bubble** that absorbs contact damage before player hearts deplete.
  - **Extra Hearts** (capped at `MAX_HEARTS`).
  - **Emergency Blast**: Screen-wide EMP detonation with expanding shockwaves and screen flash.
- **Synthesized Audio Engine**: Zero external audio files required! Generates procedural 16-bit PCM sound effects (lasers, hits, coins, chimes, shockwaves, alerts) via standard library `struct` and `math`.
- **Zero External Image Assets**: 100% drawn with procedural Pygame primitives (circles, rounded rects, polygons, anti-aliased rings, dynamic text).

---

## 🏗️ Project Architecture & Folder Structure

```
dsa_defenders/
├── main.py                  # Entry point: initializes Pygame and launches GameManager
├── config.py                # Global constants: arena bounds, colors, balance, keybindings
├── requirements.txt         # Dependencies (pygame>=2.5.0)
├── README.md                # Documentation and Viva Voce guide
├── dsa/                     # PURE PYTHON DSA (Strictly NO Pygame imports)
│   ├── __init__.py
│   ├── queue_ds.py          # Manual FIFO Queue (head pointer, O(1) amortized)
│   ├── priority_queue.py    # Manual Binary Max-Heap (zero heapq)
│   ├── greedy_targeting.py  # Greedy Nearest-Enemy (squared Euclidean distance)
│   └── targeting.py         # Algorithmic dispatcher & live inspection analyzer
├── entities/                # Active game objects & state models
│   ├── __init__.py
│   ├── tower.py             # Defense tower position, clamping, turret angle, stats
│   ├── enemy.py             # Robotic enemy archetypes, health, animation phases
│   ├── projectile.py        # Homing energy bolts with mid-flight target loss fallback
│   └── effects.py           # Particles, floating damage numbers, shockwaves, flashes
├── systems/                 # Core mechanics & gameplay logic
│   ├── __init__.py
│   ├── economy.py           # Coins ledger, centralized can_afford()/spend()
│   ├── upgrades.py          # Attack power, fire rate, and extra heart scaling
│   ├── shield.py            # Shield capacity, absorb logic, and shatter events
│   ├── blast.py             # Screen-wide Emergency Blast ability & cooldown
│   └── sound.py             # Procedural PCM audio synthesizer (no numpy/audio files)
├── game/                    # Game loop, wave orchestration, and combat
│   ├── __init__.py
│   ├── game_manager.py      # State machine, input routing, update/draw orchestration
│   ├── wave_manager.py      # 40-wave scheduler, difficulty curves, boss encounters
│   ├── combat.py            # Auto-firing, collisions, damage resolution, rewards
│   └── collision.py         # Circle-circle spatial checks & distance math
└── ui/                      # Visual presentation & user interfaces
    ├── __init__.py
    ├── game_screen.py       # Pre-rendered background, entities, effects, upgrade cards
    ├── hud.py               # Top wave banner, coins, hearts, shield bar, toggles
    ├── menus.py             # Main Menu, Wave Select (40 grid), Pause, Game Over, Victory
    ├── buttons.py           # Reusable Button and Tiny Towers UpgradeCard widget
    └── algorithm_lab.py     # Live DSA Inspection & Viva Voce modal panel
```

---

## 🔄 Module Interaction & Data-Flow Pipeline

```
                                +-------------------+
                                |      main.py      |
                                +---------+---------+
                                          |
                                          v
                                +-------------------+
                                |    GameManager    | <------- User Input (Keyboard / Mouse)
                                +---------+---------+
                                          |
         +--------------------------------+--------------------------------+
         |                                |                                |
         v                                v                                v
+------------------+            +------------------+            +------------------+
|   WaveManager    |            |   Targeting &    |            |      Combat      |
| Spawns & scales  |            |  DSA Dispatcher  |            |   Auto-firing,   |
| 40 waves/bosses  |            | (Queue/Heap/Grd) |            |   Projectiles    |
+--------+---------+            +--------+---------+            +--------+---------+
         |                               |                               |
         v                               v                               v
+------------------+            +------------------+            +------------------+
|  Active Enemies  | ---------> |  select_target() | ---------> |    Collision     |
|  (Scout, Runner, |            | Picks vanguard,  |            |  Circle-circle   |
|   Tank, Boss)    |            | threat, or dist  |            |  damage checks   |
+------------------+            +------------------+            +--------+---------+
                                                                         |
         +---------------------------------------------------------------+
         |
         v
+------------------+            +------------------+            +------------------+
|     Economy      |            | Upgrades/Shield/ |            |   UI, HUD, and   |
| Awards coins on  | ---------> | Blast Systems    | ---------> |  Algorithm Lab   |
| kills & waves    |            | Modifies tower   |            | Live frame draw  |
+------------------+            +------------------+            +------------------+
```

---

## 📊 DSA Implementation Summary

| Data Structure / Algorithm | File | Core Operations | Time Complexity | Space Complexity | Combat Role & Effect |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FIFO Queue** | [`dsa/queue_ds.py`](file:///dsa_defenders/dsa/queue_ds.py) | `enqueue`, `dequeue`, `peek`, `remove` | Enqueue: $O(1)$<br>Dequeue: $O(1)$ amortized<br>Peek: $O(1)$<br>Remove: $O(n)$ | $O(n)$ | **First-Come, First-Served**: Targets the earliest-spawned enemy currently in range, defending against the vanguard line. |
| **Binary Max-Heap** | [`dsa/priority_queue.py`](file:///dsa_defenders/dsa/priority_queue.py) | `insert`, `extract_max`, `peek_max`, `build_heap` | Insert: $O(\log n)$<br>Extract: $O(\log n)$<br>Build: $O(n)$<br>Peek: $O(1)$ | $O(n)$ | **Threat Prioritization**: Evaluates composite threat score $(3\times\text{Dmg} + 1.5\times\text{Spd} + \frac{1000}{\text{Dist}+1} + \text{Bonus})$. Targets the most lethal enemy first. |
| **Greedy Heuristic** | [`dsa/greedy_targeting.py`](file:///dsa_defenders/dsa/greedy_targeting.py) | `find_nearest_enemy` | Search: $O(n)$ | $O(1)$ | **Local Optimum**: Computes squared Euclidean distance ($dx^2 + dy^2$) to target the closest hostile. Tower movement directly shifts the local optimum in real time. |

---

## 🎮 Controls & Shortcuts

| Action | Controls |
| :--- | :--- |
| **Move Tower** | **`W` / `A` / `S` / `D`** or **Arrow Keys** |
| **Drag Tower** | **Left Click & Drag** on the Central Tower |
| **Queue Mode (FIFO)** | Press **`1`** or click HUD `[1: Queue]` button |
| **Priority Queue (Heap)** | Press **`2`** or click HUD `[2: Heap]` button |
| **Greedy Mode (Nearest)** | Press **`3`** or click HUD `[3: Greedy]` button |
| **Emergency Blast** | Press **`SPACE`** or click the *Emergency Blast* card |
| **Algorithm Lab** | Press **`L`** or click HUD `[L: Algo Lab]` button |
| **Pause / Resume** | Press **`P`** or click HUD `[II]` button |
| **Sound Toggle (Mute)** | Press **`M`** or click HUD `[Snd]` button |
| **Game Speed (1x / 2x / 3x)** | Click HUD `[1x]` button (scales game delta time) |
| **Restart Wave / Retry** | Press **`R`** (on Playing, Paused, or Game Over screens) |

---

## 🎓 Viva Voce Guide & Examination FAQ

### Q1: Why use an array-based Binary Max-Heap instead of a Sorted Linked List?
> **Answer:** In a sorted list, retrieving the maximum is $O(1)$, but inserting a newly spawned or updated enemy requires shifting elements or linear traversal, which takes $O(n)$ time. In a Binary Max-Heap, both `insert` and `extract_max` operate in $O(\log n)$ time. Furthermore, rebuilds with updated enemy distances run in $O(n)$ total time using Floyd's bottom-up `build_heap` algorithm. Heap nodes in an array also have superior CPU cache locality and require zero pointer overhead.

### Q2: Why is the Greedy Nearest-Enemy heuristic not always globally optimal?
> **Answer:** A greedy algorithm chooses the immediate local optimum (the enemy with the smallest distance). For example, a low-damage Scout might be 50 pixels away, while an Apex Boss with $5\times$ damage is 55 pixels away. Greedy will focus on the Scout while the Boss marches forward and destroys the tower. This illustrates the fundamental DSA lesson: local optimality does not guarantee global system safety.

### Q3: Why does our distance comparison use squared Euclidean distance ($dx^2 + dy^2$)?
> **Answer:** The square root function $f(x) = \sqrt{x}$ is strictly monotonically increasing for all non-negative numbers $x \ge 0$. Therefore:
> $$a^2 < b^2 \iff a < b$$
> Computing `math.sqrt()` consumes heavy CPU floating-point instructions. By comparing squared values, we produce the exact same ordering without running a single square root on every frame.

### Q4: Why does our Queue use an integer head pointer instead of `list.pop(0)`?
> **Answer:** In Python, standard lists are implemented as dynamic arrays. Calling `list.pop(0)` takes $O(n)$ time because every subsequent element must shift left in memory. With an integer `head` pointer, dequeuing simply reads from `head` and increments the pointer in $O(1)$ time, accompanied by periodic amortized compaction when dead slots exceed half the array.

---

## 🚀 Installation & Running

### Prerequisites
- Python 3.10 or higher.
- Pygame 2.5.0 or higher.

### Quick Start
```bash
# 1. Clone or navigate to the project directory
cd tiny_towers_remake

# 2. (Optional) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate       # On macOS/Linux
# venv\Scripts\activate        # On Windows

# 3. Install requirements
pip install -r requirements.txt

# 4. Launch DSA Defenders!
python main.py
```
*(You can also run directly inside `dsa_defenders/`: `cd dsa_defenders && python main.py`)*

### Running Automated Test Suites
```bash
# Run DSA unit tests (FIFO Queue, Max-Heap vs sorted(), Greedy, zero heapq imports)
python tests/test_dsa.py

# Run gameplay requirements verification
python tests/test_gameplay.py

# Run headless 3500-frame smoke simulation
python tests/smoke_sim.py
```
