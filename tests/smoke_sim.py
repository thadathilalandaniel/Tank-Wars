"""
tests/smoke_sim.py

Headless smoke simulation test for DSA Defenders.
Runs the game headless (SDL_VIDEODRIVER=dummy, SDL_AUDIODRIVER=dummy) for several
thousand frames, simulating:
- Wave starts and progression
- Automatic firing, projectile flight, and enemy kills
- Upgrades (Attack, Speed, Shield, Hearts, Blast)
- Dynamic targeting mode switching (Queue -> Heap -> Greedy)
- Tower movement and dragging
- Algorithm Lab toggle
- Verification that lists (dead enemies, projectiles, particles) do not grow unbounded.
"""

import os
import sys

# Set dummy drivers before importing pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dsa_defenders"))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import pygame
from game.game_manager import GameManager
from config import TARGET_MODE_QUEUE, TARGET_MODE_HEAP, TARGET_MODE_GREEDY


def run_simulation(total_frames: int = 3500):
    print(f"[SMOKE SIM] Initializing headless simulation for {total_frames} frames...")
    pygame.init()
    pygame.font.init()

    game = GameManager(headless=True)
    game.start_game()

    # Give test budget to exercise all upgrade paths
    game.economy.add_coins(600)

    modes = [TARGET_MODE_QUEUE, TARGET_MODE_HEAP, TARGET_MODE_GREEDY]
    dt = 1.0 / 60.0

    print("[SMOKE SIM] Simulation running...")
    for frame in range(1, total_frames + 1):
        # 1. Update Game
        game.update(dt)
        game.draw()

        # 2. Cycle targeting modes every 300 frames
        if frame % 300 == 0:
            new_mode = modes[(frame // 300) % len(modes)]
            game.set_targeting_mode(new_mode)

        # 3. Simulate Tower movement
        if frame % 100 < 50:
            game.tower.move(1.0, 0.5, dt)
        else:
            game.tower.move(-1.0, -0.5, dt)

        # 4. Exercise Upgrades periodically
        if frame == 200:
            game.buy_upgrade_attack()
            game.buy_upgrade_speed()
            game.buy_recharge_shield()
        elif frame == 500:
            game.buy_upgrade_heart()
            game.trigger_emergency_blast()
        elif frame == 1200:
            game.buy_upgrade_attack()
            game.buy_recharge_shield()

        # 5. Toggle Algorithm Lab on and off
        if frame == 400:
            game.toggle_algo_lab()
            game.draw()
        elif frame == 450:
            game.toggle_algo_lab()

        # 6. Auto-advance if wave clears
        if game.state == game.STATE_WAVE_COMPLETE:
            print(f"[SMOKE SIM] Wave {game.wave_manager.current_wave} cleared at frame {frame}! Advancing...")
            game.advance_next_wave()

        # 7. Check for memory leak safety: ensure dead enemies/projectiles are pruned
        if frame % 500 == 0:
            active_enemies = len(game.enemies)
            active_projectiles = len(game.combat.projectiles)
            active_particles = len(game.effects.particles)
            print(f"  Frame {frame:4d} | Wave: {game.wave_manager.current_wave} | Mode: {game.targeting.mode:14s} | "
                  f"Enemies: {active_enemies:2d} | Projectiles: {active_projectiles:2d} | Particles: {active_particles:2d} | Coins: {game.economy.coins}")

            # Verify lists are within reasonable bounds
            assert active_projectiles < 80, f"Potential projectile leak! Count: {active_projectiles}"
            assert active_particles < 250, f"Potential particle leak! Count: {active_particles}"

    print(f"[SMOKE SIM] Completed {total_frames} frames successfully with 0 exceptions!")
    print(f"Total kills: {game.combat.total_enemies_killed}, Total coins earned: {game.economy.total_earned}")
    pygame.quit()
    return True


if __name__ == "__main__":
    success = run_simulation()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
