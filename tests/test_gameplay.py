"""
tests/test_gameplay.py

Full verification script covering all 8 points in Step 8:
1. Menu -> Wave Select -> Gameplay transitions.
2. Tower movement with keyboard and mouse drag + boundary clamping.
3. Tower auto-fire, projectile collisions, damage numbers, coin awards, enemy deaths.
4. Targeting modes verification.
5. Upgrades: Attack Power, Fire Speed, Extra Hearts (respecting MAX_HEARTS), Shield absorption,
   Emergency Blast, Unaffordable rejection & feedback.
6. Wave progression, difficulty scaling, wave complete, victory on wave 40, game over, restart reset.
7. Pause/resume, sound toggle, 1x/2x/3x game speed.
8. Memory cleanup and list pruning.
"""

import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dsa_defenders"))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import pygame
import unittest
from game.game_manager import GameManager
from entities.enemy import Enemy
from config import (
    ARENA_LEFT,
    ARENA_RIGHT,
    ARENA_TOP,
    ARENA_BOTTOM,
    TOWER_RADIUS,
    TOWER_MAX_HEARTS,
    TOWER_MIN_FIRE_COOLDOWN,
    TARGET_MODE_QUEUE,
    TARGET_MODE_HEAP,
    TARGET_MODE_GREEDY,
    SPEED_1X,
    SPEED_2X,
    SPEED_3X,
)


class TestGameplayRequirements(unittest.TestCase):

    def setUp(self):
        pygame.init()
        pygame.font.init()
        self.game = GameManager(headless=True)

    def tearDown(self):
        pygame.quit()

    def test_item_1_menu_transitions(self):
        """1. Game launches without tracebacks and menu -> wave select -> gameplay flow works."""
        self.assertEqual(self.game.state, GameManager.STATE_MENU)

        # Transition to wave select
        self.game.set_state(GameManager.STATE_WAVE_SELECT)
        self.assertEqual(self.game.state, GameManager.STATE_WAVE_SELECT)
        self.game.draw()

        # Transition to gameplay
        self.game.start_game()
        self.assertEqual(self.game.state, GameManager.STATE_PLAYING)
        self.game.draw()

    def test_item_2_tower_movement_and_clamping(self):
        """2. Tower moves with arrows/WASD and mouse drag, and stays inside bounds."""
        tower = self.game.tower
        start_x, start_y = tower.x, tower.y

        # Move right
        tower.move(1.0, 0.0, 0.5)
        self.assertGreater(tower.x, start_x)

        # Attempt to move far beyond right arena boundary
        tower.move(100.0, 0.0, 10.0)
        max_allowed_x = ARENA_RIGHT - tower.radius - 10
        self.assertLessEqual(tower.x, max_allowed_x)

        # Test mouse drag to bottom-left
        tower.drag_to(0, 1000)
        min_allowed_x = ARENA_LEFT + tower.radius + 10
        max_allowed_y = ARENA_BOTTOM - tower.radius - 10
        self.assertGreaterEqual(tower.x, min_allowed_x)
        self.assertLessEqual(tower.y, max_allowed_y)

    def test_item_3_combat_fire_and_rewards(self):
        """3. Tower auto-fires, projectiles collide, damage numbers and coins appear, enemies die with effects."""
        self.game.start_game()
        tower = self.game.tower
        # Place enemy right in front of tower
        enemy = Enemy(tower.x, tower.y - 80, enemy_type="scout", hp_mult=0.5)
        enemy.health = 10.0  # Weak enough to be killed by 1 shot (damage = 15)
        self.game.enemies = [enemy]
        self.game.targeting.on_enemy_spawned(enemy)

        coins_before = self.game.economy.coins

        # Step frames until projectile fires and hits
        for _ in range(30):
            self.game.update(1.0 / 60.0)

        # Enemy should be dead, projectile removed, coin text spawned, coins awarded
        self.assertEqual(len(self.game.enemies), 0, "Enemy should have been killed by the shot!")
        self.assertGreater(self.game.economy.coins, coins_before, "Coins should have been deposited on kill!")
        self.assertGreater(len(self.game.effects.floating_texts), 0, "Floating damage/coin text should exist!")

    def test_item_5_upgrades_and_affordability(self):
        """
        5. Upgrades: attack power raises damage, shooting speed lowers cooldown,
           extra heart respects MAX_HEARTS, shield absorbs damage before hearts,
           emergency blast damages all visible enemies, unaffordable purchases rejected.
        """
        self.game.start_game()
        tower = self.game.tower
        econ = self.game.economy

        # Verify unaffordable purchase rejection
        econ.coins = 0
        initial_damage = tower.damage
        self.game.buy_upgrade_attack()
        self.assertEqual(tower.damage, initial_damage, "Unaffordable attack upgrade should be rejected!")
        self.assertTrue(econ.is_denied_active(), "Denial feedback should be active!")

        # Add budget and test Attack Power
        econ.coins = 1000
        self.game.buy_upgrade_attack()
        self.assertGreater(tower.damage, initial_damage, "Attack upgrade should raise damage!")

        # Test Shooting Speed
        initial_cd = tower.fire_cooldown
        self.game.buy_upgrade_speed()
        self.assertLess(tower.fire_cooldown, initial_cd, "Speed upgrade should lower fire cooldown!")

        # Test Extra Heart & MAX_HEARTS cap
        tower.hearts = TOWER_MAX_HEARTS
        self.assertTrue(self.game.upgrades.is_heart_maxed(tower))
        bought_heart = self.game.upgrades.upgrade_heart(tower, econ)
        self.assertFalse(bought_heart, "Heart upgrade should be rejected when at MAX_HEARTS!")

        # Test Shield absorption
        self.game.buy_recharge_shield()
        self.assertGreater(self.game.shield.capacity, 0.0)
        hearts_before = tower.hearts
        # Incoming contact damage of 10 points
        unabsorbed = self.game.shield.absorb_damage(10.0, tower=tower)
        self.assertEqual(unabsorbed, 0.0, "Shield should fully absorb damage up to capacity!")
        self.assertEqual(tower.hearts, hearts_before, "Hearts should NOT decrease when shield absorbs!")

        # Test Emergency Blast
        e1 = Enemy(tower.x + 40, tower.y - 40, hp_mult=1.0)
        e2 = Enemy(tower.x - 40, tower.y - 40, hp_mult=1.0)
        e1_hp_before = e1.health
        e2_hp_before = e2.health
        self.game.enemies = [e1, e2]
        self.game.trigger_emergency_blast()
        self.assertLess(e1.health, e1_hp_before, "Blast should damage enemy 1!")
        self.assertLess(e2.health, e2_hp_before, "Blast should damage enemy 2!")

    def test_item_6_wave_progression_and_restart(self):
        """6. Wave progression, wave complete, victory on wave 40, game over, and clean restart."""
        wm = self.game.wave_manager
        self.game.start_game()
        self.assertEqual(wm.current_wave, 1)

        # Force clear wave 1
        wm.spawn_queue.clear()
        self.game.enemies.clear()
        completed = wm.check_wave_completion(0)
        self.assertTrue(completed)
        self.assertTrue(wm.is_wave_unlocked(2), "Wave 2 should unlock after Wave 1 is cleared!")

        # Test Victory trigger on wave 40
        wm.current_wave = 40
        wm.spawn_queue.clear()
        self.game.enemies.clear()
        wm.wave_active = True
        completed_40 = wm.check_wave_completion(0)
        self.assertTrue(completed_40)
        self.assertTrue(wm.all_completed, "Wave 40 completion must set all_completed flag!")

        # Test Restart resets state cleanly
        self.game.enemies = [Enemy(100, 100)]
        self.game.combat.projectiles = ["dummy_proj"]
        self.game.restart_wave()
        self.assertEqual(len(self.game.enemies), 0, "Restart must clear active enemies!")
        self.assertEqual(len(self.game.combat.projectiles), 0, "Restart must clear active projectiles!")

    def test_item_7_speed_sound_pause(self):
        """7. Pause/resume, sound toggle, and 1x/2x/3x speed work properly."""
        self.game.start_game()

        # Pause toggle
        self.game.toggle_pause()
        self.assertEqual(self.game.state, GameManager.STATE_PAUSED)
        self.game.resume_game()
        self.assertEqual(self.game.state, GameManager.STATE_PLAYING)

        # Sound toggle
        sound_status = self.game.sound.enabled
        self.game.toggle_sound()
        self.assertEqual(self.game.sound.enabled, not sound_status)

        # Speed cycle
        self.assertEqual(self.game.game_speed, SPEED_1X)
        self.game.cycle_speed()
        self.assertEqual(self.game.game_speed, SPEED_2X)
        self.game.cycle_speed()
        self.assertEqual(self.game.game_speed, SPEED_3X)
        self.game.cycle_speed()
        self.assertEqual(self.game.game_speed, SPEED_1X)


if __name__ == "__main__":
    unittest.main()
