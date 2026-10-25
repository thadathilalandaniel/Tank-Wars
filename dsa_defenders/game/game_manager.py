"""
dsa_defenders/game/game_manager.py

Master GameManager orchestrating the application lifecycle:
- High-level State Machine (Menu, Wave Select, Playing, Paused, Wave Complete, Game Over, Victory)
- 60 FPS real-time game loop with delta-time calculation
- Game speed scaling (1x, 2x, 3x) that scales delta time without distorting frame rate
- Input routing (keyboard, mouse drag, buttons, shortcuts)
- Subsystem synchronization (Combat, Waves, Targeting/DSA, Upgrades, Economy, Sound, UI)
"""

import sys
import pygame
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    WINDOW_TITLE,
    SPEED_1X,
    SPEED_2X,
    SPEED_3X,
    TARGET_MODE_QUEUE,
    TARGET_MODE_HEAP,
    TARGET_MODE_GREEDY,
    INITIAL_COINS,
)
from entities.tower import Tower
from entities.effects import EffectsManager
from dsa.targeting import TargetingDispatcher
from game.wave_manager import WaveManager
from game.combat import CombatManager
from systems.economy import EconomySystem
from systems.upgrades import UpgradeSystem
from systems.shield import ShieldSystem
from systems.blast import BlastSystem
from systems.sound import SoundManager
from ui.hud import HUD
from ui.menus import MenuManager
from ui.game_screen import GameScreenRenderer
from ui.algorithm_lab import AlgorithmLabPanel


class GameManager:
    """Central controller managing game states, loops, and subsystem integration."""

    STATE_MENU = "MENU"
    STATE_WAVE_SELECT = "WAVE_SELECT"
    STATE_PLAYING = "PLAYING"
    STATE_PAUSED = "PAUSED"
    STATE_WAVE_COMPLETE = "WAVE_COMPLETE"
    STATE_GAME_OVER = "GAME_OVER"
    STATE_VICTORY = "VICTORY"

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.running = True
        self.state = self.STATE_MENU
        self.game_speed = SPEED_1X

        # Display & Clock
        if not self.headless:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption(WINDOW_TITLE)
        else:
            self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Font Cache to avoid recreating fonts per frame
        self.font_cache = {}

        # -------------------------------------------------------------
        # SUBSYSTEM INITIALIZATION
        # -------------------------------------------------------------
        self.sound = SoundManager(enabled=True)
        self.economy = EconomySystem(initial_coins=INITIAL_COINS)
        self.tower = Tower()
        self.effects = EffectsManager()
        self.targeting = TargetingDispatcher(initial_mode=TARGET_MODE_QUEUE)
        self.wave_manager = WaveManager()
        self.combat = CombatManager()
        self.upgrades = UpgradeSystem()
        self.shield = ShieldSystem()
        self.blast = BlastSystem()

        # Active Entities
        self.enemies = []

        # -------------------------------------------------------------
        # UI & MENUS INITIALIZATION
        # -------------------------------------------------------------
        menu_callbacks = {
            "play": self.start_game,
            "wave_select": lambda: self.set_state(self.STATE_WAVE_SELECT),
            "select_wave": self.select_and_start_wave,
            "lab": self.toggle_algo_lab,
            "resume": self.resume_game,
            "restart": self.restart_wave,
            "next_wave": self.advance_next_wave,
            "menu": lambda: self.set_state(self.STATE_MENU),
            "quit": self.quit_game,
        }
        self.menus = MenuManager(menu_callbacks)

        hud_callbacks = {
            "on_home": lambda: self.set_state(self.STATE_MENU),
            "on_pause": self.toggle_pause,
            "on_sound": self.toggle_sound,
            "on_speed": self.cycle_speed,
            "on_mode_change": self.set_targeting_mode,
            "on_lab_toggle": self.toggle_algo_lab,
        }
        self.hud = HUD(**hud_callbacks)

        renderer_callbacks = {
            "upgrade_attack": self.buy_upgrade_attack,
            "upgrade_speed": self.buy_upgrade_speed,
            "recharge_shield": self.buy_recharge_shield,
            "upgrade_heart": self.buy_upgrade_heart,
            "activate_blast": self.trigger_emergency_blast,
        }
        self.renderer = GameScreenRenderer(renderer_callbacks)

        self.lab_panel = AlgorithmLabPanel(on_close=None)

    def set_state(self, new_state: str) -> None:
        """Switch game states cleanly."""
        self.state = new_state

    # -------------------------------------------------------------
    # ACTION CALLBACKS
    # -------------------------------------------------------------
    def start_game(self) -> None:
        """Start playing from the current selected wave."""
        self.full_reset_for_wave(self.wave_manager.current_wave)
        self.wave_manager.start_wave()
        self.state = self.STATE_PLAYING

    def select_and_start_wave(self, wave_num: int) -> None:
        """Select a specific wave and begin gameplay."""
        if self.wave_manager.set_wave(wave_num):
            self.start_game()

    def advance_next_wave(self) -> None:
        """Progress to the next unlocked wave."""
        if self.wave_manager.advance_next_wave():
            self.start_game()
        else:
            self.set_state(self.STATE_VICTORY)

    def restart_wave(self) -> None:
        """Restart current wave with clean reset."""
        self.start_game()

    def full_reset_for_wave(self, wave_num: int) -> None:
        """Completely reset all combat state and leftover entities."""
        self.enemies.clear()
        self.combat.clear()
        self.effects.clear()
        self.targeting.clear()
        self.tower.reset()
        self.shield.reset()
        self.blast.reset()
        self.wave_manager.reset_to_wave(wave_num)

    def toggle_pause(self) -> None:
        """Toggle pause state."""
        if self.state == self.STATE_PLAYING:
            self.state = self.STATE_PAUSED
        elif self.state == self.STATE_PAUSED:
            self.state = self.STATE_PLAYING

    def resume_game(self) -> None:
        self.state = self.STATE_PLAYING

    def toggle_sound(self) -> None:
        self.sound.toggle()

    def cycle_speed(self) -> None:
        """Cycle game speed between 1x, 2x, and 3x."""
        if self.game_speed == SPEED_1X:
            self.game_speed = SPEED_2X
        elif self.game_speed == SPEED_2X:
            self.game_speed = SPEED_3X
        else:
            self.game_speed = SPEED_1X

    def set_targeting_mode(self, mode: str) -> None:
        self.targeting.set_mode(mode)

    def toggle_algo_lab(self) -> None:
        self.lab_panel.toggle()

    def quit_game(self) -> None:
        self.running = False

    # -------------------------------------------------------------
    # UPGRADE & ABILITY ACTIONS
    # -------------------------------------------------------------
    def buy_upgrade_attack(self) -> None:
        if not self.upgrades.upgrade_attack(self.tower, self.economy, self.effects, self.sound):
            self.renderer.trigger_card_shake("attack")

    def buy_upgrade_speed(self) -> None:
        if not self.upgrades.upgrade_speed(self.tower, self.economy, self.effects, self.sound):
            self.renderer.trigger_card_shake("speed")

    def buy_recharge_shield(self) -> None:
        if not self.shield.recharge(self.economy, self.effects, self.sound, self.tower):
            self.renderer.trigger_card_shake("shield")

    def buy_upgrade_heart(self) -> None:
        if not self.upgrades.upgrade_heart(self.tower, self.economy, self.effects, self.sound):
            self.renderer.trigger_card_shake("heart")

    def trigger_emergency_blast(self) -> None:
        if not self.blast.activate(self.tower, self.enemies, self.effects, self.sound,
                                   targeting_dispatcher=self.targeting, economy=self.economy):
            self.renderer.trigger_card_shake("blast")

    # -------------------------------------------------------------
    # EVENT HANDLING
    # -------------------------------------------------------------
    def handle_events(self) -> None:
        """Process keyboard, mouse, and system events."""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # If Algorithm Lab panel is open, it gets first priority
            if self.lab_panel.is_open:
                if self.lab_panel.handle_event(event):
                    continue

            # Keyboard Shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.toggle_pause()
                elif event.key == pygame.K_m:
                    self.toggle_sound()
                elif event.key == pygame.K_l:
                    self.toggle_algo_lab()
                elif event.key == pygame.K_SPACE:
                    self.trigger_emergency_blast()
                elif event.key == pygame.K_1:
                    self.set_targeting_mode(TARGET_MODE_QUEUE)
                elif event.key == pygame.K_2:
                    self.set_targeting_mode(TARGET_MODE_HEAP)
                elif event.key == pygame.K_3:
                    self.set_targeting_mode(TARGET_MODE_GREEDY)
                elif event.key == pygame.K_r:
                    if self.state in (self.STATE_PLAYING, self.STATE_PAUSED, self.STATE_GAME_OVER, self.STATE_WAVE_COMPLETE):
                        self.restart_wave()

            # State-specific event handling
            if self.state == self.STATE_PLAYING:
                # Top HUD clicks
                if self.hud.handle_event(event):
                    continue

                # Mouse Dragging on Tower
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if clicked on tower
                    dx = mouse_pos[0] - self.tower.x
                    dy = mouse_pos[1] - self.tower.y
                    if (dx * dx + dy * dy) <= ((self.tower.radius + 12) ** 2):
                        self.tower.is_dragging = True
                    # Check bottom upgrade cards
                    elif self.renderer.handle_card_click(mouse_pos):
                        pass

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.tower.is_dragging = False

                elif event.type == pygame.MOUSEMOTION and self.tower.is_dragging:
                    self.tower.drag_to(mouse_pos[0], mouse_pos[1])

            elif self.state == self.STATE_MENU:
                self.menus.main_play_btn.handle_event(event)
                self.menus.main_wave_btn.handle_event(event)

            elif self.state == self.STATE_WAVE_SELECT:
                for btn in self.menus.wave_buttons:
                    btn.handle_event(event)
                self.menus.wave_back_btn.handle_event(event)

            elif self.state == self.STATE_PAUSED:
                for btn in (self.menus.pause_resume_btn, self.menus.pause_restart_btn, self.menus.pause_menu_btn):
                    btn.handle_event(event)

            elif self.state == self.STATE_WAVE_COMPLETE:
                for btn in (self.menus.wc_next_btn, self.menus.wc_replay_btn, self.menus.wc_menu_btn):
                    btn.handle_event(event)

            elif self.state == self.STATE_GAME_OVER:
                for btn in (self.menus.go_retry_btn, self.menus.go_waves_btn, self.menus.go_menu_btn):
                    btn.handle_event(event)

            elif self.state == self.STATE_VICTORY:
                for btn in (self.menus.vic_play_again_btn, self.menus.vic_menu_btn):
                    btn.handle_event(event)

    # -------------------------------------------------------------
    # UPDATE CYCLE
    # -------------------------------------------------------------
    def update(self, dt: float) -> None:
        """Update game physics, timers, and state transitions."""
        mouse_pos = pygame.mouse.get_pos()
        self.hud.update(mouse_pos)
        self.lab_panel.update(mouse_pos)

        if self.state == self.STATE_PLAYING:
            # Scale delta time by game speed
            effective_dt = dt * self.game_speed

            # 1. Keyboard Tower Movement (WASD & Arrows)
            keys = pygame.key.get_pressed()
            kx = 0.0
            ky = 0.0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                kx -= 1.0
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                kx += 1.0
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                ky -= 1.0
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                ky += 1.0

            if not self.tower.is_dragging:
                self.tower.move(kx, ky, effective_dt)

            # 2. Wave Manager Spawning
            new_enemy = self.wave_manager.update(effective_dt)
            if new_enemy is not None:
                self.enemies.append(new_enemy)
                self.targeting.on_enemy_spawned(new_enemy)

            # 3. Move Living Enemies
            for enemy in self.enemies:
                if enemy.is_alive():
                    enemy.move_towards(self.tower.x, self.tower.y, effective_dt)

            # 4. Target Acquisition via Active DSA Algorithm
            target_enemy = self.targeting.select_target(
                self.tower.x, self.tower.y, self.tower.range, self.enemies
            )

            # 5. Update Tower Turret Orientation
            self.tower.update(effective_dt, target_enemy)

            # 6. Execute Combat & Projectile Collisions
            self.combat.update(
                effective_dt,
                self.tower,
                target_enemy,
                self.enemies,
                self.effects,
                self.economy,
                self.shield,
                self.sound,
                self.targeting,
            )

            # 7. Update Systems & Visual Effects
            self.blast.update(effective_dt)
            self.shield.update(effective_dt)
            self.economy.update(effective_dt)
            self.effects.update(effective_dt)
            self.renderer.update_cards(dt, mouse_pos)

            # 8. Check Wave Completion
            if self.wave_manager.check_wave_completion(len(self.enemies)):
                reward = self.wave_manager.get_wave_clear_reward()
                self.economy.add_coins(reward)
                self.sound.play("wave_clear")
                if self.wave_manager.all_completed:
                    self.set_state(self.STATE_VICTORY)
                else:
                    self.set_state(self.STATE_WAVE_COMPLETE)

            # 9. Check Tower Defeat
            if not self.tower.is_alive():
                self.sound.play("game_over")
                self.set_state(self.STATE_GAME_OVER)

        elif self.state == self.STATE_MENU:
            self.menus.main_play_btn.update_hover(mouse_pos)
            self.menus.main_wave_btn.update_hover(mouse_pos)

        elif self.state == self.STATE_WAVE_SELECT:
            for btn in self.menus.wave_buttons:
                btn.update_hover(mouse_pos)
            self.menus.wave_back_btn.update_hover(mouse_pos)

        elif self.state == self.STATE_PAUSED:
            for btn in (self.menus.pause_resume_btn, self.menus.pause_restart_btn, self.menus.pause_menu_btn):
                btn.update_hover(mouse_pos)

        elif self.state == self.STATE_WAVE_COMPLETE:
            for btn in (self.menus.wc_next_btn, self.menus.wc_replay_btn, self.menus.wc_menu_btn):
                btn.update_hover(mouse_pos)

        elif self.state == self.STATE_GAME_OVER:
            for btn in (self.menus.go_retry_btn, self.menus.go_waves_btn, self.menus.go_menu_btn):
                btn.update_hover(mouse_pos)

        elif self.state == self.STATE_VICTORY:
            for btn in (self.menus.vic_play_again_btn, self.menus.vic_menu_btn):
                btn.update_hover(mouse_pos)

    # -------------------------------------------------------------
    # DRAW CYCLE
    # -------------------------------------------------------------
    def draw(self) -> None:
        """Render active state scene to display surface."""
        target_enemy = self.targeting.last_selected_target

        if self.state in (self.STATE_PLAYING, self.STATE_PAUSED, self.STATE_WAVE_COMPLETE, self.STATE_GAME_OVER):
            # Render arena and entities
            self.renderer.draw(
                self.screen,
                self.font_cache,
                self.tower,
                self.enemies,
                self.combat.projectiles,
                self.effects,
                self.wave_manager.portal_locations,
                target_enemy,
                self.economy,
                self.upgrades,
                self.shield,
                self.blast,
            )

            # Render top HUD
            self.hud.draw(
                self.screen,
                self.font_cache,
                self.wave_manager.current_wave,
                self.wave_manager.total_waves,
                self.tower.hearts,
                self.tower.max_hearts,
                self.shield.capacity,
                self.shield.max_capacity,
                self.economy.coins,
                self.targeting.mode,
                self.sound.enabled,
                self.game_speed,
            )

            # Draw modal overlays
            if self.state == self.STATE_PAUSED:
                self.menus.draw_pause(self.screen, self.font_cache)
            elif self.state == self.STATE_WAVE_COMPLETE:
                reward = self.wave_manager.get_wave_clear_reward()
                self.menus.draw_wave_complete(self.screen, self.font_cache, self.wave_manager.current_wave, reward)
            elif self.state == self.STATE_GAME_OVER:
                self.menus.draw_game_over(self.screen, self.font_cache, self.wave_manager.current_wave, self.combat.total_enemies_killed)

        elif self.state == self.STATE_MENU:
            self.screen.blit(self.renderer.cached_bg, (0, 0))
            self.menus.draw_main_menu(self.screen, self.font_cache)

        elif self.state == self.STATE_WAVE_SELECT:
            self.screen.blit(self.renderer.cached_bg, (0, 0))
            self.menus.draw_wave_select(self.screen, self.font_cache, self.wave_manager)

        elif self.state == self.STATE_VICTORY:
            self.screen.blit(self.renderer.cached_bg, (0, 0))
            self.menus.draw_victory(self.screen, self.font_cache, self.combat.total_enemies_killed, self.economy.total_earned)

        # Draw Algorithm Lab panel on top if opened
        if self.lab_panel.is_open:
            self.lab_panel.draw(self.screen, self.font_cache, self.targeting, self.tower, self.enemies)

        if not self.headless:
            pygame.display.flip()

    # -------------------------------------------------------------
    # MAIN LOOP EXECUTION
    # -------------------------------------------------------------
    def run(self) -> None:
        """Run the main game loop at target FPS."""
        while self.running:
            raw_dt = self.clock.tick(FPS) / 1000.0
            # Cap dt to avoid massive physics jumps on window drag
            dt = min(0.08, raw_dt)

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
