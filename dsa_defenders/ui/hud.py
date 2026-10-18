"""
dsa_defenders/ui/hud.py

This module renders the Heads-Up Display (HUD) overlay:
- Top wave indicator ("WAVE 7 / 40")
- Lives (heart icons) and energy shield meter
- Coin balance with gold coin badge
- Speed multiplier button (1x / 2x / 3x)
- Audio toggle and Pause buttons
- Targeting algorithm mode selector pills (Queue / Heap / Greedy)
- Algorithm Lab quick-launch button

Modules that interact with this:
- game/game_manager.py (queries button clicks and state)
- ui/buttons.py (instantiates top buttons)
- ui/game_screen.py (orchestrates complete screen rendering)
"""

import math
import pygame
from config import (
    SCREEN_WIDTH,
    COLOR_HUD_BG,
    COLOR_HUD_BORDER,
    COLOR_COIN_GOLD,
    COLOR_HEART_RED,
    COLOR_HEART_OUTLINE,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED,
    SPEED_1X,
    SPEED_2X,
    SPEED_3X,
    TARGET_MODE_QUEUE,
    TARGET_MODE_HEAP,
    TARGET_MODE_GREEDY,
    get_font,
)
from ui.buttons import Button


class HUD:
    """Manages HUD rendering, life counters, coins, and top control widgets."""

    def __init__(self, on_home=None, on_pause=None, on_sound=None, on_speed=None,
                 on_mode_change=None, on_lab_toggle=None):
        self.on_home = on_home
        self.on_pause = on_pause
        self.on_sound = on_sound
        self.on_speed = on_speed
        self.on_mode_change = on_mode_change
        self.on_lab_toggle = on_lab_toggle

        # Top Control Buttons
        self.btn_home = Button(SCREEN_WIDTH - 210, 16, 42, 36, text="Home", font_size=12,
                               bg_color=(35, 55, 85), hover_color=(50, 80, 120), callback=on_home)
        self.btn_sound = Button(SCREEN_WIDTH - 160, 16, 42, 36, text="Snd", font_size=12,
                                bg_color=(35, 55, 85), hover_color=(50, 80, 120), callback=on_sound)
        self.btn_pause = Button(SCREEN_WIDTH - 110, 16, 42, 36, text="II", font_size=14,
                                bg_color=(35, 55, 85), hover_color=(50, 80, 120), callback=on_pause)
        self.btn_speed = Button(SCREEN_WIDTH - 60, 16, 46, 36, text="1x", font_size=14,
                                bg_color=(35, 55, 85), hover_color=(50, 80, 120), callback=on_speed)

        # Targeting Mode Selector Buttons (Left side of top bar)
        self.btn_mode_q = Button(20, 16, 85, 36, text="1: Queue", font_size=12,
                                 callback=lambda: on_mode_change and on_mode_change(TARGET_MODE_QUEUE))
        self.btn_mode_heap = Button(112, 16, 85, 36, text="2: Heap", font_size=12,
                                    callback=lambda: on_mode_change and on_mode_change(TARGET_MODE_HEAP))
        self.btn_mode_greedy = Button(204, 16, 85, 36, text="3: Greedy", font_size=12,
                                      callback=lambda: on_mode_change and on_mode_change(TARGET_MODE_GREEDY))
        self.btn_lab = Button(296, 16, 95, 36, text="[L] Algo Lab", font_size=12,
                              bg_color=(80, 45, 120), hover_color=(110, 60, 165), callback=on_lab_toggle)

    def handle_event(self, event) -> bool:
        """Handle clicks on HUD buttons. Returns True if consumed."""
        for btn in (self.btn_home, self.btn_sound, self.btn_pause, self.btn_speed,
                    self.btn_mode_q, self.btn_mode_heap, self.btn_mode_greedy, self.btn_lab):
            if btn.handle_event(event):
                return True
        return False

    def update(self, mouse_pos) -> None:
        """Update hover states."""
        for btn in (self.btn_home, self.btn_sound, self.btn_pause, self.btn_speed,
                    self.btn_mode_q, self.btn_mode_heap, self.btn_mode_greedy, self.btn_lab):
            btn.update_hover(mouse_pos)

    def draw(self, surface: pygame.Surface, font_cache: dict, wave_num: int, total_waves: int,
             hearts: int, max_hearts: int, shield: float, max_shield: float, coins: int,
             current_mode: str, sound_enabled: bool, game_speed: float) -> None:
        """Render complete HUD."""
        # Top banner background bar
        top_bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 68)
        pygame.draw.rect(surface, COLOR_HUD_BG, top_bar_rect)
        pygame.draw.line(surface, COLOR_HUD_BORDER, (0, 68), (SCREEN_WIDTH, 68), 2)

        # -------------------------------------------------------------
        # 1. WAVE INDICATOR (Center Pill)
        # -------------------------------------------------------------
        wave_pill_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 14, 200, 40)
        pygame.draw.rect(surface, (20, 32, 54), wave_pill_rect, border_radius=20)
        pygame.draw.rect(surface, (70, 110, 170), wave_pill_rect, width=2, border_radius=20)

        wave_font = get_font(font_cache, 18, bold=True)
        wave_text = f"WAVE {wave_num} / {total_waves}"
        wave_surf = wave_font.render(wave_text, True, COLOR_TEXT_WHITE)
        surface.blit(wave_surf, wave_surf.get_rect(center=wave_pill_rect.center))

        # -------------------------------------------------------------
        # 2. TARGETING MODE BUTTONS (Highlighted active state)
        # -------------------------------------------------------------
        self.btn_mode_q.is_selected = (current_mode == TARGET_MODE_QUEUE)
        self.btn_mode_heap.is_selected = (current_mode == TARGET_MODE_HEAP)
        self.btn_mode_greedy.is_selected = (current_mode == TARGET_MODE_GREEDY)

        self.btn_mode_q.draw(surface, font_cache)
        self.btn_mode_heap.draw(surface, font_cache)
        self.btn_mode_greedy.draw(surface, font_cache)
        self.btn_lab.draw(surface, font_cache)

        # -------------------------------------------------------------
        # 3. CONTROL BUTTONS (Home, Sound, Pause, Speed)
        # -------------------------------------------------------------
        self.btn_sound.text = "Snd:On" if sound_enabled else "Mute"
        self.btn_speed.text = f"{int(game_speed)}x" if game_speed.is_integer() else f"{game_speed}x"

        self.btn_home.draw(surface, font_cache)
        self.btn_sound.draw(surface, font_cache)
        self.btn_pause.draw(surface, font_cache)
        self.btn_speed.draw(surface, font_cache)

        # -------------------------------------------------------------
        # 4. COIN COUNTER PILL (Right-Center)
        # -------------------------------------------------------------
        coin_pill_rect = pygame.Rect(SCREEN_WIDTH // 2 + 120, 18, 120, 32)
        pygame.draw.rect(surface, (15, 24, 40), coin_pill_rect, border_radius=16)
        pygame.draw.rect(surface, (200, 160, 0), coin_pill_rect, width=2, border_radius=16)

        # Coin icon
        pygame.draw.circle(surface, COLOR_COIN_GOLD, (coin_pill_rect.x + 18, coin_pill_rect.centery), 9)
        pygame.draw.circle(surface, (180, 130, 0), (coin_pill_rect.x + 18, coin_pill_rect.centery), 9, width=1)

        coin_font = get_font(font_cache, 16, bold=True)
        coin_surf = coin_font.render(str(coins), True, COLOR_TEXT_WHITE)
        surface.blit(coin_surf, coin_surf.get_rect(midleft=(coin_pill_rect.x + 35, coin_pill_rect.centery)))

        # -------------------------------------------------------------
        # 5. HEARTS & SHIELD STATUS (Placed clearly below top bar, on the left)
        # -------------------------------------------------------------
        panel_w = max_hearts * 22 + 16
        panel_h = 28 if shield <= 0 else 40
        status_panel_rect = pygame.Rect(20, 76, panel_w, panel_h)
        pygame.draw.rect(surface, (18, 30, 50, 210), status_panel_rect, border_radius=8)
        pygame.draw.rect(surface, (35, 58, 96), status_panel_rect, width=1, border_radius=8)

        hud_health_start_x = status_panel_rect.x + 16
        hud_health_y = status_panel_rect.y + 14

        # Draw row of hearts left-to-right
        for i in range(max_hearts):
            hx = hud_health_start_x + (i * 22)
            hy = hud_health_y
            is_filled = (i < hearts)
            self._draw_heart(surface, hx, hy, is_filled)

        # Draw Shield bar if active
        if shield > 0:
            shield_bar_rect = pygame.Rect(hud_health_start_x - 6, status_panel_rect.y + 26, (max_hearts * 22), 7)
            pygame.draw.rect(surface, (10, 30, 50), shield_bar_rect, border_radius=3)
            fill_w = int(shield_bar_rect.width * min(1.0, shield / max_shield))
            if fill_w > 0:
                pygame.draw.rect(surface, (0, 229, 255), (shield_bar_rect.x, shield_bar_rect.y, fill_w, 7), border_radius=3)
            pygame.draw.rect(surface, (0, 180, 216), shield_bar_rect, width=1, border_radius=3)

    def _draw_heart(self, surface: pygame.Surface, cx: int, cy: int, filled: bool) -> None:
        """Render small heart icon."""
        r = 4
        col = COLOR_HEART_RED if filled else (40, 45, 60)
        outline = COLOR_HEART_OUTLINE if filled else (25, 30, 40)

        pygame.draw.circle(surface, col, (cx - 4, cy - 2), r)
        pygame.draw.circle(surface, col, (cx + 4, cy - 2), r)
        heart_pts = [(cx - 8, cy - 1), (cx + 8, cy - 1), (cx, cy + 8)]
        pygame.draw.polygon(surface, col, heart_pts)
        pygame.draw.circle(surface, outline, (cx - 4, cy - 2), r, width=1)
        pygame.draw.circle(surface, outline, (cx + 4, cy - 2), r, width=1)
        pygame.draw.lines(surface, outline, False, [(cx - 8, cy - 1), (cx, cy + 8), (cx + 8, cy - 1)], 1)
