"""
defense_defenders/ui/buttons.py

This module contains UI interactive components:
1. Button: A versatile, styled button widget with hover states and sound feedback.
2. UpgradeCard: The bottom tray upgrade card matching the Tiny Towers visual reference.

Modules that interact with this:
- ui/hud.py (uses Button for speed/pause/audio toggles)
- ui/menus.py (uses Button for navigation and wave selection)
- ui/game_screen.py (renders the bottom upgrade cards)
"""

import math
import pygame
from config import (
    COLOR_CARD_BG,
    COLOR_CARD_BG_HOVER,
    COLOR_CARD_BG_DISABLED,
    COLOR_CARD_OUTLINE,
    COLOR_CARD_AFFORDABLE_BADGE,
    COLOR_CARD_UNAFFORDABLE_BADGE,
    COLOR_COIN_GOLD,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED,
    get_font,
)


class Button:
    """A reusable, modern styled button with hover and click response."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str = "",
                 font_size: int = 18, bg_color=(45, 70, 105), hover_color=(60, 95, 140),
                 text_color=COLOR_TEXT_WHITE, border_color=(20, 35, 55), border_radius: int = 8,
                 callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.callback = callback

        self.is_hovered = False
        self.is_enabled = True
        self.is_selected = False

    def handle_event(self, event) -> bool:
        """Handle mouse events. Returns True if clicked."""
        if not self.is_enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def update_hover(self, mouse_pos) -> None:
        """Update hover state outside event loop."""
        self.is_hovered = self.is_enabled and self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface, font_cache: dict) -> None:
        """Render button with rounded corners and centered text."""
        font = get_font(font_cache, self.font_size, bold=True)

        if not self.is_enabled:
            color = (35, 45, 60)
        elif self.is_selected:
            color = (0, 180, 216)
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.bg_color

        # Button background
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        # Button border
        border_col = (255, 255, 255) if self.is_selected else self.border_color
        pygame.draw.rect(surface, border_col, self.rect, width=2, border_radius=self.border_radius)

        # Label
        if self.text:
            text_col = COLOR_TEXT_MUTED if not self.is_enabled else self.text_color
            surf = font.render(self.text, True, text_col)
            text_rect = surf.get_rect(center=self.rect.center)
            surface.blit(surf, text_rect)


class UpgradeCard:
    """
    Bottom-row Upgrade Card styled after the Tiny Towers visual reference:
    - Rounded rectangular container
    - Large icon symbol (Attack, Speed, Shield, Heart, Blast)
    - Level indicator
    - Bottom pill badge with coin icon and cost
    - Shake and red feedback on insufficient funds
    """

    def __init__(self, x: int, y: int, width: int, height: int, card_id: str,
                 title: str, icon_type: str, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.card_id = card_id
        self.title = title
        self.icon_type = icon_type
        self.callback = callback

        self.is_hovered = False
        self.shake_timer = 0.0

    def trigger_shake(self) -> None:
        """Trigger brief horizontal shake on failed purchase."""
        self.shake_timer = 0.30

    def update(self, dt: float, mouse_pos) -> None:
        """Update hover and shake animation."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.shake_timer > 0:
            self.shake_timer = max(0.0, self.shake_timer - dt)

    def handle_click(self, mouse_pos) -> bool:
        """Check click on the card."""
        if self.rect.collidepoint(mouse_pos):
            if self.callback:
                self.callback()
            return True
        return False

    def draw(self, surface: pygame.Surface, font_cache: dict, level: int, cost: int,
             can_afford: bool, is_maxed: bool = False, cooldown_fraction: float = 1.0) -> None:
        """Render upgrade card with Tiny Towers styling."""
        # Calculate horizontal shake offset
        offset_x = 0
        if self.shake_timer > 0:
            offset_x = int(math.sin(self.shake_timer * 40.0) * 6.0)

        draw_rect = self.rect.copy()
        draw_rect.x += offset_x

        # Background color
        if is_maxed:
            bg_col = COLOR_CARD_BG_DISABLED
        elif self.is_hovered:
            bg_col = COLOR_CARD_BG_HOVER
        else:
            bg_col = COLOR_CARD_BG

        # Draw card body with rounded corners
        pygame.draw.rect(surface, bg_col, draw_rect, border_radius=12)

        # Draw border (red if shaking from denial, bright if hovered, dark otherwise)
        if self.shake_timer > 0:
            border_col = (255, 60, 60)
            border_w = 3
        elif self.is_hovered and not is_maxed:
            border_col = (120, 180, 240)
            border_w = 2
        else:
            border_col = COLOR_CARD_OUTLINE
            border_w = 2
        pygame.draw.rect(surface, border_col, draw_rect, width=border_w, border_radius=12)

        # Fonts (Tiny Towers rounded bold style)
        title_font = get_font(font_cache, 14, bold=True)
        lvl_font = get_font(font_cache, 12, bold=False)
        cost_font = get_font(font_cache, 14, bold=True)

        # -------------------------------------------------------------
        # DRAW CARD ICON (Pygame Primitives)
        # -------------------------------------------------------------
        icon_cx = draw_rect.centerx
        icon_cy = draw_rect.y + 36
        self._draw_icon(surface, icon_cx, icon_cy, is_maxed, cooldown_fraction)

        # -------------------------------------------------------------
        # TITLE & LEVEL
        # -------------------------------------------------------------
        title_surf = title_font.render(self.title, True, COLOR_TEXT_WHITE)
        surface.blit(title_surf, title_surf.get_rect(center=(draw_rect.centerx, draw_rect.y + 66)))

        if not is_maxed:
            lvl_text = f"Lv {level}" if self.icon_type != "blast" else f"Pwr {level}"
            lvl_surf = lvl_font.render(lvl_text, True, COLOR_TEXT_MUTED)
            surface.blit(lvl_surf, lvl_surf.get_rect(center=(draw_rect.centerx, draw_rect.y + 80)))

        # -------------------------------------------------------------
        # BOTTOM COST PILL
        # -------------------------------------------------------------
        pill_rect = pygame.Rect(draw_rect.x + 14, draw_rect.bottom - 26, draw_rect.width - 28, 20)
        if is_maxed:
            pygame.draw.rect(surface, (45, 55, 70), pill_rect, border_radius=10)
            max_surf = cost_font.render("MAX", True, (160, 170, 185))
            surface.blit(max_surf, max_surf.get_rect(center=pill_rect.center))
        else:
            badge_col = COLOR_CARD_AFFORDABLE_BADGE if can_afford else COLOR_CARD_UNAFFORDABLE_BADGE
            pygame.draw.rect(surface, badge_col, pill_rect, border_radius=10)

            # Draw small gold coin circle in pill
            coin_cx = pill_rect.x + 14
            coin_cy = pill_rect.centery
            pygame.draw.circle(surface, COLOR_COIN_GOLD, (coin_cx, coin_cy), 5)
            pygame.draw.circle(surface, (180, 135, 0), (coin_cx, coin_cy), 5, width=1)

            # Draw cost text
            cost_surf = cost_font.render(str(cost), True, COLOR_TEXT_WHITE)
            surface.blit(cost_surf, cost_surf.get_rect(midleft=(coin_cx + 9, pill_rect.centery)))

    def _draw_icon(self, surface: pygame.Surface, cx: int, cy: int, is_maxed: bool,
                   cooldown_frac: float) -> None:
        """Render distinct colorful icons using pure Pygame primitives."""
        if self.icon_type == "attack":
            # Upward Attack Arrow
            pts = [(cx, cy - 14), (cx - 12, cy + 2), (cx - 5, cy + 2),
                   (cx - 5, cy + 12), (cx + 5, cy + 12), (cx + 5, cy + 2), (cx + 12, cy + 2)]
            col = (76, 175, 80) if not is_maxed else (100, 120, 100)
            pygame.draw.polygon(surface, col, pts)
            pygame.draw.polygon(surface, (25, 60, 30), pts, width=2)

        elif self.icon_type == "speed":
            # Turret Head with fast muzzle lines
            pygame.draw.circle(surface, (255, 235, 59), (cx, cy + 2), 11)
            pygame.draw.circle(surface, (30, 30, 40), (cx, cy + 2), 11, width=2)
            pygame.draw.rect(surface, (30, 30, 40), (cx - 3, cy - 14, 6, 10), border_radius=2)
            # Speed wind lines
            pygame.draw.line(surface, (255, 255, 255), (cx - 14, cy - 2), (cx - 14, cy + 6), 2)
            pygame.draw.line(surface, (255, 255, 255), (cx + 14, cy - 2), (cx + 14, cy + 6), 2)

        elif self.icon_type == "shield":
            # Glowing Shield Crest
            shield_pts = [(cx, cy + 14), (cx + 13, cy + 2), (cx + 13, cy - 10),
                          (cx - 13, cy - 10), (cx - 13, cy + 2)]
            pygame.draw.polygon(surface, (0, 229, 255), shield_pts)
            pygame.draw.polygon(surface, (10, 50, 80), shield_pts, width=2)
            # Inner cross
            pygame.draw.line(surface, (255, 255, 255), (cx, cy - 6), (cx, cy + 8), 2)
            pygame.draw.line(surface, (255, 255, 255), (cx - 6, cy + 1), (cx + 6, cy + 1), 2)

        elif self.icon_type == "heart":
            # Red Heart icon
            r = 6
            pygame.draw.circle(surface, (244, 67, 54), (cx - 6, cy - 3), r)
            pygame.draw.circle(surface, (244, 67, 54), (cx + 6, cy - 3), r)
            heart_pts = [(cx - 12, cy - 2), (cx + 12, cy - 2), (cx, cy + 12)]
            pygame.draw.polygon(surface, (244, 67, 54), heart_pts)
            # Outline
            pygame.draw.circle(surface, (150, 20, 20), (cx - 6, cy - 3), r, width=1)
            pygame.draw.circle(surface, (150, 20, 20), (cx + 6, cy - 3), r, width=1)
            pygame.draw.lines(surface, (150, 20, 20), False, [(cx - 12, cy - 2), (cx, cy + 12), (cx + 12, cy - 2)], 2)

        elif self.icon_type == "blast":
            # Emergency Blast / Energy Nova
            col = (255, 171, 0) if cooldown_frac >= 1.0 else (120, 100, 70)
            pygame.draw.circle(surface, col, (cx, cy), 12)
            pygame.draw.circle(surface, (50, 30, 10), (cx, cy), 12, width=2)
            # Radiating spikes
            for i in range(8):
                ang = i * (math.pi / 4)
                x1 = cx + math.cos(ang) * 9
                y1 = cy + math.sin(ang) * 9
                x2 = cx + math.cos(ang) * 16
                y2 = cy + math.sin(ang) * 16
                pygame.draw.line(surface, col, (x1, y1), (x2, y2), 2)
