"""
dsa_defenders/ui/menus.py

This module contains menu screens and state overlays:
- Main Menu
- Wave Select Grid (40 waves with unlock progression)
- Pause Overlay
- Wave Complete Screen
- Victory Screen (Wave 40 completion)
- Game Over Screen

Modules that interact with this:
- game/game_manager.py (switches states and invokes menu draws/events)
- ui/buttons.py (uses Button widgets)
- game/wave_manager.py (checks unlocked waves)
"""

import math
import pygame
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    TOTAL_WAVES,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED,
    COLOR_COIN_GOLD,
    get_font,
)
from ui.buttons import Button


class MenuManager:
    """Orchestrates all non-gameplay menu interfaces and modals."""

    def __init__(self, callbacks: dict):
        self.callbacks = callbacks
        self._init_main_menu()
        self._init_wave_select()
        self._init_pause_menu()
        self._init_wave_complete()
        self._init_game_over()
        self._init_victory()

    def _init_main_menu(self) -> None:
        cx = SCREEN_WIDTH // 2
        self.main_play_btn = Button(cx - 150, 310, 300, 60, text="PLAY GAME", font_size=24,
                                    bg_color=(46, 125, 50), hover_color=(67, 160, 71),
                                    callback=self.callbacks.get("play"))
        self.main_wave_btn = Button(cx - 150, 395, 300, 56, text="SELECT WAVE (1-40)", font_size=20,
                                    bg_color=(25, 118, 210), hover_color=(30, 136, 229),
                                    callback=self.callbacks.get("wave_select"))

    def _init_wave_select(self) -> None:
        self.wave_buttons = []
        start_x = (SCREEN_WIDTH - (8 * 72 + 7 * 14)) // 2  # 8 columns
        start_y = 150                                      # 5 rows
        for i in range(1, TOTAL_WAVES + 1):
            col = (i - 1) % 8
            row = (i - 1) // 8
            bx = start_x + col * (72 + 14)
            by = start_y + row * (54 + 14)

            # Special styling for boss waves (10, 20, 30, 40)
            is_boss = (i % 10 == 0)
            txt = f"W{i}*" if is_boss else f"W{i}"
            bg = (123, 31, 162) if is_boss else (33, 150, 243)
            hover = (156, 39, 176) if is_boss else (66, 165, 245)

            btn = Button(bx, by, 72, 54, text=txt, font_size=14, bg_color=bg, hover_color=hover,
                         callback=lambda w=i: self.callbacks.get("select_wave", lambda _: None)(w))
            self.wave_buttons.append(btn)

        self.wave_back_btn = Button(SCREEN_WIDTH // 2 - 100, 560, 200, 44, text="BACK TO MENU", font_size=16,
                                    bg_color=(55, 71, 79), hover_color=(69, 90, 100),
                                    callback=self.callbacks.get("menu"))

    def _init_pause_menu(self) -> None:
        cx = SCREEN_WIDTH // 2
        self.pause_resume_btn = Button(cx - 110, 260, 220, 46, text="RESUME [P]", font_size=18,
                                       bg_color=(46, 125, 50), hover_color=(67, 160, 71),
                                       callback=self.callbacks.get("resume"))
        self.pause_restart_btn = Button(cx - 110, 320, 220, 46, text="RESTART WAVE [R]", font_size=16,
                                        bg_color=(239, 108, 0), hover_color=(245, 124, 0),
                                        callback=self.callbacks.get("restart"))
        self.pause_menu_btn = Button(cx - 110, 380, 220, 46, text="MAIN MENU", font_size=16,
                                     bg_color=(55, 71, 79), hover_color=(69, 90, 100),
                                     callback=self.callbacks.get("menu"))

    def _init_wave_complete(self) -> None:
        cx = SCREEN_WIDTH // 2
        self.wc_next_btn = Button(cx - 120, 340, 240, 50, text="NEXT WAVE", font_size=18,
                                  bg_color=(46, 125, 50), hover_color=(67, 160, 71),
                                  callback=self.callbacks.get("next_wave"))
        self.wc_replay_btn = Button(cx - 120, 405, 240, 44, text="REPLAY WAVE", font_size=16,
                                    bg_color=(25, 118, 210), hover_color=(30, 136, 229),
                                    callback=self.callbacks.get("restart"))
        self.wc_menu_btn = Button(cx - 120, 460, 240, 44, text="MAIN MENU", font_size=16,
                                  bg_color=(55, 71, 79), hover_color=(69, 90, 100),
                                  callback=self.callbacks.get("menu"))

    def _init_game_over(self) -> None:
        cx = SCREEN_WIDTH // 2
        self.go_retry_btn = Button(cx - 120, 370, 240, 50, text="TRY AGAIN [R]", font_size=18,
                                   bg_color=(211, 47, 47), hover_color=(229, 57, 53),
                                   callback=self.callbacks.get("restart"))
        self.go_waves_btn = Button(cx - 120, 435, 240, 44, text="WAVE SELECT", font_size=16,
                                   bg_color=(25, 118, 210), hover_color=(30, 136, 229),
                                   callback=self.callbacks.get("wave_select"))
        self.go_menu_btn = Button(cx - 120, 490, 240, 44, text="MAIN MENU", font_size=16,
                                  bg_color=(55, 71, 79), hover_color=(69, 90, 100),
                                  callback=self.callbacks.get("menu"))

    def _init_victory(self) -> None:
        cx = SCREEN_WIDTH // 2
        self.vic_play_again_btn = Button(cx - 130, 420, 260, 52, text="PLAY AGAIN", font_size=18,
                                         bg_color=(46, 125, 50), hover_color=(67, 160, 71),
                                         callback=self.callbacks.get("play"))
        self.vic_menu_btn = Button(cx - 130, 485, 260, 46, text="MAIN MENU", font_size=16,
                                   bg_color=(55, 71, 79), hover_color=(69, 90, 100),
                                   callback=self.callbacks.get("menu"))

    # --- Draw Screens ---
    def draw_main_menu(self, surface: pygame.Surface, font_cache: dict) -> None:
        # Tiny Towers style Cartoon Logo: "TANK" and "WARS" stacked with thick black outline and blue gradient
        font_logo = get_font(font_cache, 68, bold=True)
        lines = ["TANK", "WARS"]
        cx = SCREEN_WIDTH // 2
        start_y = 100
        line_height = 68

        for idx, line_text in enumerate(lines):
            line_y = start_y + idx * line_height
            
            # 1. Base text surface for gradient mask
            text_mask = font_logo.render(line_text, True, (255, 255, 255))
            tw, th = text_mask.get_size()

            # 2. Vertical color gradient (Pure white at top -> Vibrant sky/ice blue at bottom)
            grad_surf = pygame.Surface((tw, th), pygame.SRCALPHA)
            top_col = (255, 255, 255)
            bot_col = (130, 215, 255)
            for y_step in range(th):
                frac = y_step / max(1, th - 1)
                col = (
                    int(top_col[0] + (bot_col[0] - top_col[0]) * frac),
                    int(top_col[1] + (bot_col[1] - top_col[1]) * frac),
                    int(top_col[2] + (bot_col[2] - top_col[2]) * frac),
                    255
                )
                pygame.draw.line(grad_surf, col, (0, y_step), (tw, y_step))
            grad_surf.blit(text_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # 3. Soft drop shadow
            black_mask = font_logo.render(line_text, True, (15, 30, 50))
            shadow_rect = black_mask.get_rect(center=(cx + 4, line_y + 8))
            surface.blit(black_mask, shadow_rect)

            # 4. Thick cartoon black border / outline (8-directional stamp)
            outline_stroke = 5
            for ox in range(-outline_stroke, outline_stroke + 1):
                for oy in range(-outline_stroke, outline_stroke + 1):
                    if ox * ox + oy * oy <= outline_stroke * outline_stroke:
                        border_rect = black_mask.get_rect(center=(cx + ox, line_y + oy))
                        surface.blit(black_mask, border_rect)

            # 5. Front gradient text
            front_rect = grad_surf.get_rect(center=(cx, line_y))
            surface.blit(grad_surf, front_rect)

        self.main_play_btn.draw(surface, font_cache)
        self.main_wave_btn.draw(surface, font_cache)

    def draw_wave_select(self, surface: pygame.Surface, font_cache: dict, wave_manager) -> None:
        f_title = font_cache.get(30, pygame.font.SysFont("arial", 30, bold=True))
        f_hint = font_cache.get(14, pygame.font.SysFont("arial", 14))

        title_surf = f_title.render("SELECT DEFENSE WAVE", True, (255, 215, 0))
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 65)))

        hint_surf = f_hint.render("Clear each wave to unlock the next. Waves marked with * are Boss Battles!", True, (180, 210, 240))
        surface.blit(hint_surf, hint_surf.get_rect(center=(SCREEN_WIDTH // 2, 105)))

        for i, btn in enumerate(self.wave_buttons, start=1):
            btn.is_enabled = wave_manager.is_wave_unlocked(i)
            btn.is_selected = (wave_manager.current_wave == i)
            btn.draw(surface, font_cache)

        self.wave_back_btn.draw(surface, font_cache)

    def draw_pause(self, surface: pygame.Surface, font_cache: dict) -> None:
        modal_rect = pygame.Rect(SCREEN_WIDTH // 2 - 160, 180, 320, 280)
        pygame.draw.rect(surface, (20, 32, 50), modal_rect, border_radius=14)
        pygame.draw.rect(surface, (0, 229, 255), modal_rect, width=2, border_radius=14)

        f_title = font_cache.get(26, pygame.font.SysFont("arial", 26, bold=True))
        t_surf = f_title.render("GAME PAUSED", True, (255, 215, 0))
        surface.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2, 220)))

        self.pause_resume_btn.draw(surface, font_cache)
        self.pause_restart_btn.draw(surface, font_cache)
        self.pause_menu_btn.draw(surface, font_cache)

    def draw_wave_complete(self, surface: pygame.Surface, font_cache: dict, wave_num: int, reward: int) -> None:
        modal_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, 160, 360, 370)
        pygame.draw.rect(surface, (20, 35, 55), modal_rect, border_radius=14)
        pygame.draw.rect(surface, (76, 175, 80), modal_rect, width=2, border_radius=14)

        f_title = font_cache.get(28, pygame.font.SysFont("arial", 28, bold=True))
        f_sub = font_cache.get(16, pygame.font.SysFont("arial", 16))

        t_surf = f_title.render(f"WAVE {wave_num} CLEARED!", True, (76, 175, 80))
        surface.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2, 210)))

        sub_surf = f_sub.render(f"Sector successfully defended!", True, COLOR_TEXT_WHITE)
        surface.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 250)))

        # Coin reward badge
        reward_surf = f_sub.render(f"Wave Reward: +{reward} Coins", True, COLOR_COIN_GOLD)
        surface.blit(reward_surf, reward_surf.get_rect(center=(SCREEN_WIDTH // 2, 285)))

        self.wc_next_btn.draw(surface, font_cache)
        self.wc_replay_btn.draw(surface, font_cache)
        self.wc_menu_btn.draw(surface, font_cache)

    def draw_game_over(self, surface: pygame.Surface, font_cache: dict, wave_num: int, enemies_killed: int) -> None:
        modal_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, 160, 360, 400)
        pygame.draw.rect(surface, (30, 20, 25), modal_rect, border_radius=14)
        pygame.draw.rect(surface, (211, 47, 47), modal_rect, width=2, border_radius=14)

        f_title = font_cache.get(28, pygame.font.SysFont("arial", 28, bold=True))
        f_sub = font_cache.get(16, pygame.font.SysFont("arial", 16))

        t_surf = f_title.render("DEFENSE COMPROMISED", True, (244, 67, 54))
        surface.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2, 210)))

        s1 = f_sub.render(f"Overrun on Wave {wave_num} of {TOTAL_WAVES}", True, COLOR_TEXT_WHITE)
        s2 = f_sub.render(f"Enemies Eliminated: {enemies_killed}", True, (200, 215, 235))
        surface.blit(s1, s1.get_rect(center=(SCREEN_WIDTH // 2, 260)))
        surface.blit(s2, s2.get_rect(center=(SCREEN_WIDTH // 2, 295)))

        self.go_retry_btn.draw(surface, font_cache)
        self.go_waves_btn.draw(surface, font_cache)
        self.go_menu_btn.draw(surface, font_cache)

    def draw_victory(self, surface: pygame.Surface, font_cache: dict, total_kills: int, total_coins: int) -> None:
        modal_rect = pygame.Rect(SCREEN_WIDTH // 2 - 210, 150, 420, 410)
        pygame.draw.rect(surface, (20, 35, 60), modal_rect, border_radius=16)
        pygame.draw.rect(surface, (255, 215, 0), modal_rect, width=3, border_radius=16)

        f_title = font_cache.get(30, pygame.font.SysFont("arial", 30, bold=True))
        f_sub = font_cache.get(16, pygame.font.SysFont("arial", 16))

        t_surf = f_title.render("SYSTEM VICTORIOUS!", True, (255, 215, 0))
        surface.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2, 205)))

        sub_surf = f_sub.render("All 40 Defense Waves Successfully Mastered!", True, (130, 220, 255))
        surface.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 250)))

        k_surf = f_sub.render(f"Total Robotic Hostiles Defeated: {total_kills}", True, COLOR_TEXT_WHITE)
        c_surf = f_sub.render(f"Total Defense Budget Earned: {total_coins} Coins", True, COLOR_COIN_GOLD)
        surface.blit(k_surf, k_surf.get_rect(center=(SCREEN_WIDTH // 2, 300)))
        surface.blit(c_surf, c_surf.get_rect(center=(SCREEN_WIDTH // 2, 335)))

        self.vic_play_again_btn.draw(surface, font_cache)
        self.vic_menu_btn.draw(surface, font_cache)
