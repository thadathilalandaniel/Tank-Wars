"""
defense_defenders/game/wave_manager.py

This module manages the 40-wave progression system, difficulty scaling curves,
enemy spawn queues, wave-select unlock progression, and boss encounters.

Modules that interact with this:
- entities/enemy.py (instantiates scaled enemies)
- game/game_manager.py (advances waves, queries progress)
- ui/menus.py (wave selection grid and completion screens)
"""

import random
from config import (
    TOTAL_WAVES,
    SPAWN_INTERVAL_INITIAL,
    SPAWN_INTERVAL_MIN,
    ENEMY_TYPE_SCOUT,
    ENEMY_TYPE_RUNNER,
    ENEMY_TYPE_TANK,
    ENEMY_TYPE_BOSS,
    ARENA_TOP,
    SCREEN_WIDTH,
    UNLOCK_ALL_WAVES,
    START_WAVE_OVERRIDE,
)
from entities.enemy import Enemy


class WaveManager:
    """Orchestrates wave progression, enemy composition, and spawn scheduling."""

    def __init__(self):
        self.total_waves = TOTAL_WAVES
        self.current_wave = START_WAVE_OVERRIDE
        self.highest_unlocked_wave = TOTAL_WAVES if UNLOCK_ALL_WAVES else 1

        # Spawn queue and timers
        self.spawn_queue = []
        self.spawn_interval = SPAWN_INTERVAL_INITIAL
        self.spawn_timer = 0.0

        # State tracking
        self.wave_active = False
        self.wave_cleared = False
        self.all_completed = False
        self.total_enemies_in_wave = 0
        self.enemies_spawned_count = 0

        # Spawn portal locations (top edge of arena)
        self.portal_locations = [
            (SCREEN_WIDTH // 2 - 240, ARENA_TOP + 40),
            (SCREEN_WIDTH // 2 - 80, ARENA_TOP + 40),
            (SCREEN_WIDTH // 2 + 80, ARENA_TOP + 40),
            (SCREEN_WIDTH // 2 + 240, ARENA_TOP + 40),
        ]

    def is_wave_unlocked(self, wave_num: int) -> bool:
        """Check if a specific wave is accessible."""
        if UNLOCK_ALL_WAVES:
            return True
        return 1 <= wave_num <= self.highest_unlocked_wave

    def set_wave(self, wave_num: int) -> bool:
        """Select a wave to play if unlocked."""
        if self.is_wave_unlocked(wave_num):
            self.current_wave = wave_num
            return True
        return False

    def start_wave(self) -> None:
        """Construct the enemy spawn queue for the current wave and begin spawning."""
        w = self.current_wave
        self.wave_active = True
        self.wave_cleared = False
        self.all_completed = False
        self.spawn_timer = 0.5  # Brief pause before first enemy emerges

        # Difficulty scaling formulas
        self.spawn_interval = max(
            SPAWN_INTERVAL_MIN,
            SPAWN_INTERVAL_INITIAL - (w - 1) * 0.028
        )
        hp_mult = 1.0 + (w - 1) * 0.12
        spd_mult = 1.0 + min(0.55, (w - 1) * 0.015)

        # Total enemies to spawn
        count = 5 + int(w * 1.6)
        if w % 10 == 0:
            count += 4  # Extra guards on boss waves

        self.total_enemies_in_wave = count
        self.enemies_spawned_count = 0
        self.spawn_queue.clear()

        # Build archetype composition
        for i in range(count):
            portal_x, portal_y = random.choice(self.portal_locations)
            # Add slight jitter to spawn coords
            sx = portal_x + random.uniform(-20, 20)
            sy = portal_y + random.uniform(-10, 10)

            # Boss every 10th wave (spawned midway through the wave)
            if (w % 10 == 0) and (i == count // 2):
                enemy_type = ENEMY_TYPE_BOSS
            elif w <= 3:
                enemy_type = ENEMY_TYPE_SCOUT
            elif w <= 9:
                enemy_type = random.choices(
                    [ENEMY_TYPE_SCOUT, ENEMY_TYPE_RUNNER],
                    weights=[65, 35]
                )[0]
            elif w <= 19:
                enemy_type = random.choices(
                    [ENEMY_TYPE_SCOUT, ENEMY_TYPE_RUNNER, ENEMY_TYPE_TANK],
                    weights=[45, 35, 20]
                )[0]
            else:
                # Late waves: high tank and runner frequency
                enemy_type = random.choices(
                    [ENEMY_TYPE_SCOUT, ENEMY_TYPE_RUNNER, ENEMY_TYPE_TANK],
                    weights=[30, 40, 30]
                )[0]

            enemy = Enemy(sx, sy, enemy_type=enemy_type, hp_mult=hp_mult, spd_mult=spd_mult)
            self.spawn_queue.append(enemy)

    def update(self, dt: float) -> Enemy | None:
        """
        Advance wave spawn timer. Returns newly spawned Enemy or None.
        """
        if not self.wave_active or not self.spawn_queue:
            return None

        self.spawn_timer -= dt
        if self.spawn_timer <= 0.0:
            self.spawn_timer = self.spawn_interval
            enemy = self.spawn_queue.pop(0)
            self.enemies_spawned_count += 1
            return enemy

        return None

    def check_wave_completion(self, alive_enemies_count: int) -> bool:
        """
        Check if all enemies in the current wave have been defeated.
        """
        if self.wave_active and len(self.spawn_queue) == 0 and alive_enemies_count == 0:
            self.wave_active = False
            self.wave_cleared = True

            # Unlock next wave
            if self.current_wave >= self.highest_unlocked_wave and self.current_wave < self.total_waves:
                self.highest_unlocked_wave = self.current_wave + 1

            if self.current_wave >= self.total_waves:
                self.all_completed = True

            return True
        return False

    def advance_next_wave(self) -> bool:
        """Progress to the next wave if available."""
        if self.current_wave < self.total_waves:
            self.current_wave += 1
            return True
        return False

    def get_wave_clear_reward(self) -> int:
        """Calculate coin bonus awarded upon completing the wave."""
        return 20 + self.current_wave * 5

    def reset_to_wave(self, wave_num: int = 1) -> None:
        """Reset wave manager to a specific wave."""
        self.current_wave = wave_num
        self.spawn_queue.clear()
        self.wave_active = False
        self.wave_cleared = False
        self.all_completed = False
        self.enemies_spawned_count = 0
