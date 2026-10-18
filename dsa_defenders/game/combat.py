"""
dsa_defenders/game/combat.py

This module orchestrates combat interactions:
- Automatic projectile firing towards targeted enemies
- Projectile flight physics and collision resolution
- Damage application, health depletion, and floating damage numbers
- Coin rewards upon enemy elimination
- Enemy contact damage against tower shield and hearts

Modules that interact with this:
- entities/tower.py & entities/projectile.py
- entities/enemy.py & entities/effects.py
- game/collision.py (circle-circle collision)
- systems/economy.py & systems/shield.py & systems/sound.py
- dsa/targeting.py (notifies dispatcher when enemies are destroyed)
"""

from entities.projectile import Projectile
from game.collision import circle_circle_collision


class CombatManager:
    """Manages weapon firing, collision handling, and damage resolution."""

    def __init__(self):
        self.projectiles = []
        self.total_enemies_killed = 0
        self.total_damage_dealt = 0.0

    def update(self, dt: float, tower, target_enemy, enemies: list,
               effects, economy, shield, sound_manager, targeting_dispatcher) -> None:
        """
        Execute one combat frame:
          1. Auto-fire tower at active target.
          2. Move active projectiles.
          3. Resolve projectile-enemy collisions.
          4. Resolve enemy-tower contact collisions.
        """
        # -------------------------------------------------------------
        # 1. TOWER AUTO-FIRE
        # -------------------------------------------------------------
        if target_enemy is not None and tower.can_fire() and tower.is_alive():
            # Spawn projectile slightly in front of tower along turret direction
            proj = Projectile(tower.x, tower.y, target_enemy, damage=tower.damage)
            self.projectiles.append(proj)
            tower.trigger_shot()
            if sound_manager:
                sound_manager.play("shoot")

        # -------------------------------------------------------------
        # 2. UPDATE PROJECTILES
        # -------------------------------------------------------------
        for proj in self.projectiles:
            proj.update(dt)

        # -------------------------------------------------------------
        # 3. PROJECTILE VS ENEMY COLLISIONS
        # -------------------------------------------------------------
        for proj in self.projectiles:
            if not proj.is_alive():
                continue

            for enemy in enemies:
                if not enemy.is_alive():
                    continue

                if circle_circle_collision(proj.x, proj.y, proj.radius,
                                           enemy.x, enemy.y, enemy.radius):
                    # Direct hit!
                    proj.destroy()
                    actual_dmg, killed = enemy.take_damage(proj.damage)
                    self.total_damage_dealt += actual_dmg

                    if sound_manager:
                        sound_manager.play("hit")

                    if effects:
                        effects.add_floating_damage(f"{int(actual_dmg)}", enemy.x, enemy.y)

                    if killed:
                        self._handle_enemy_kill(enemy, effects, economy, sound_manager, targeting_dispatcher)
                    break

        # Remove dead projectiles and dead enemies
        self.projectiles = [p for p in self.projectiles if p.is_alive()]
        enemies[:] = [e for e in enemies if e.is_alive()]

        # -------------------------------------------------------------
        # 4. ENEMY VS TOWER CONTACT COLLISIONS
        # -------------------------------------------------------------
        for enemy in list(enemies):
            if not enemy.is_alive():
                continue

            # Check if enemy reached the tower
            if circle_circle_collision(enemy.x, enemy.y, enemy.radius,
                                       tower.x, tower.y, tower.radius):
                # Apply damage to shield first!
                unabsorbed = shield.absorb_damage(enemy.damage, tower=tower,
                                                  effects=effects, sound_manager=sound_manager)

                # Penetrating damage strikes hearts
                if unabsorbed > 0 and tower.is_alive():
                    hearts_lost = int(unabsorbed)
                    tower.hearts = max(0, tower.hearts - hearts_lost)
                    tower.trigger_damage_flash()
                    if effects:
                        effects.add_screen_flash(color=(255, 40, 40), max_alpha=120, duration=0.25)
                    if sound_manager:
                        sound_manager.play("hurt")

                # Enemy explodes on impact with the tower
                enemy.health = 0.0
                if effects:
                    effects.add_explosion(enemy.x, enemy.y, enemy.color, count=14)

                targeting_dispatcher.on_enemy_removed(enemy)
                if enemy in enemies:
                    enemies.remove(enemy)

    def _handle_enemy_kill(self, enemy, effects, economy, sound_manager, targeting_dispatcher) -> None:
        """Distribute rewards and spawn effects when an enemy is eliminated."""
        self.total_enemies_killed += 1
        economy.add_coins(enemy.coin_reward)

        if sound_manager:
            sound_manager.play("coin")

        if effects:
            effects.add_floating_coin(enemy.coin_reward, enemy.x, enemy.y)
            effects.add_explosion(enemy.x, enemy.y, enemy.color, count=16)

        targeting_dispatcher.on_enemy_removed(enemy)

    def clear(self) -> None:
        """Reset combat state."""
        self.projectiles.clear()
        self.total_enemies_killed = 0
        self.total_damage_dealt = 0.0
