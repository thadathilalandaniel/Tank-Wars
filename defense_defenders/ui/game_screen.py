"""
defense_defenders/ui/game_screen.py

This module renders all in-game gameplay elements:
- Pre-cached geometric blue background (layered tiles/polygons)
- Spawn portals with glowing rings at top edge
- Tower range ring (semi-transparent anti-aliased circular surface)
- Central Tower with rotating turret and health/shield bubble
- Cute robotic enemies (Scout, Runner, Tank, Boss) with walking animations and health bars
- Target acquisition line and reticle
- Projectiles and energy glow
- Visual particles, floating numbers, shockwave rings, and screen flashes
- Bottom tray of upgrade cards

Modules that interact with this:
- game/game_manager.py (invokes render)
- entities/* (reads positions and animation phases)
- systems/* (reads upgrade levels and shield capacity)
- ui/buttons.py (renders UpgradeCards)
"""

import math
import pygame
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG_SKY,
    COLOR_BG_DEEP,
    COLOR_BG_TILE,
    COLOR_BG_TILE_ALT,
    COLOR_ARENA_BORDER,
    ARENA_LEFT,
    ARENA_RIGHT,
    ARENA_TOP,
    ARENA_BOTTOM,
    COLOR_TOWER_BASE,
    COLOR_TOWER_BASE_SHADOW,
    COLOR_TOWER_OUTLINE,
    COLOR_TOWER_TURRET,
    COLOR_TOWER_TURRET_TRIM,
    COLOR_TOWER_BARREL,
    COLOR_SHIELD_BORDER,
    COLOR_SHIELD_BUBBLE,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_DARK,
    ENEMY_TYPE_SCOUT,
    ENEMY_TYPE_RUNNER,
    ENEMY_TYPE_TANK,
    ENEMY_TYPE_BOSS,
)
from ui.buttons import UpgradeCard


class GameScreenRenderer:
    """Handles rendering of arena background, entities, effects, and upgrade cards."""

    def __init__(self, callbacks: dict):
        self.cached_bg = None
        self._build_cached_background()

        # Upgrade Cards along the bottom tray
        # Width ~195, height ~110, nicely spaced
        card_w = 195
        card_h = 110
        gap = 18
        start_x = (SCREEN_WIDTH - (5 * card_w + 4 * gap)) // 2
        card_y = SCREEN_HEIGHT - card_h - 14

        self.cards = [
            UpgradeCard(start_x + 0 * (card_w + gap), card_y, card_w, card_h,
                        "attack", "Attack Power", "attack", callbacks.get("upgrade_attack")),
            UpgradeCard(start_x + 1 * (card_w + gap), card_y, card_w, card_h,
                        "speed", "Shooting Speed", "speed", callbacks.get("upgrade_speed")),
            UpgradeCard(start_x + 2 * (card_w + gap), card_y, card_w, card_h,
                        "shield", "Recharge Shield", "shield", callbacks.get("recharge_shield")),
            UpgradeCard(start_x + 3 * (card_w + gap), card_y, card_w, card_h,
                        "heart", "Extra Heart", "heart", callbacks.get("upgrade_heart")),
            UpgradeCard(start_x + 4 * (card_w + gap), card_y, card_w, card_h,
                        "blast", "Emergency Blast", "blast", callbacks.get("activate_blast")),
        ]

    def _build_cached_background(self) -> None:
        """Render geometric layered blue background once to a cached surface."""
        self.cached_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.cached_bg.fill(COLOR_BG_SKY)

        # Draw diagonal geometric rounded tile pattern (like the screenshot!)
        tile_size = 56
        for y in range(0, SCREEN_HEIGHT, tile_size):
            for x in range(0, SCREEN_WIDTH, tile_size):
                if (x // tile_size + y // tile_size) % 2 == 0:
                    tile_rect = pygame.Rect(x + 4, y + 4, tile_size - 8, tile_size - 8)
                    pygame.draw.rect(self.cached_bg, COLOR_BG_TILE, tile_rect, border_radius=10)
                else:
                    tile_rect = pygame.Rect(x + 8, y + 8, tile_size - 16, tile_size - 16)
                    pygame.draw.rect(self.cached_bg, COLOR_BG_TILE_ALT, tile_rect, border_radius=8)

        # Bottom tray backing bar
        tray_rect = pygame.Rect(0, SCREEN_HEIGHT - 138, SCREEN_WIDTH, 138)
        pygame.draw.rect(self.cached_bg, (32, 50, 78), tray_rect)
        pygame.draw.line(self.cached_bg, (18, 30, 50), (0, SCREEN_HEIGHT - 138),
                         (SCREEN_WIDTH, SCREEN_HEIGHT - 138), 3)

        # Arena framing line
        arena_rect = pygame.Rect(ARENA_LEFT, ARENA_TOP, ARENA_RIGHT - ARENA_LEFT, ARENA_BOTTOM - ARENA_TOP)
        pygame.draw.rect(self.cached_bg, COLOR_ARENA_BORDER, arena_rect, width=3, border_radius=18)

    def update_cards(self, dt: float, mouse_pos) -> None:
        """Update upgrade cards hover and shake physics."""
        for card in self.cards:
            card.update(dt, mouse_pos)

    def handle_card_click(self, mouse_pos) -> bool:
        """Check if an upgrade card was clicked."""
        for card in self.cards:
            if card.handle_click(mouse_pos):
                return True
        return False

    def trigger_card_shake(self, card_id: str) -> None:
        """Shake a specific card upon failed purchase."""
        for card in self.cards:
            if card.card_id == card_id:
                card.trigger_shake()
                break

    # -------------------------------------------------------------
    # MAIN DRAW ROUTINE
    # -------------------------------------------------------------
    def draw(self, surface: pygame.Surface, font_cache: dict, tower, enemies: list,
             projectiles: list, effects, portals: list, target_enemy, economy,
             upgrade_sys, shield_sys, blast_sys) -> None:
        """Render the complete game screen."""
        # 1. Blit cached background
        surface.blit(self.cached_bg, (0, 0))

        # 2. Draw Spawn Portals (top edge)
        self._draw_portals(surface, portals)

        # 3. Draw Attack Range Ring
        self._draw_range_ring(surface, tower)

        # 4. Draw Targeting Line & Reticle
        if target_enemy is not None and getattr(target_enemy, "is_alive", lambda: False)():
            self._draw_target_marker(surface, tower, target_enemy)

        # 5. Draw Enemies
        for enemy in enemies:
            if enemy.is_alive():
                self._draw_cute_enemy(surface, enemy, font_cache)

        # 6. Draw Projectiles
        self._draw_projectiles(surface, projectiles)

        # 7. Draw Central Tower
        self._draw_tower(surface, tower, shield_sys)

        # 8. Draw Visual Particles & Shockwaves
        self._draw_effects(surface, effects, font_cache)

        # 9. Draw Bottom Upgrade Cards
        self._draw_cards(surface, font_cache, tower, economy, upgrade_sys, shield_sys, blast_sys)

        # 10. Screen Flash Overlay
        self._draw_screen_flashes(surface, effects)

    # -------------------------------------------------------------
    # DRAW SUBROUTINES
    # -------------------------------------------------------------
    def _draw_portals(self, surface: pygame.Surface, portals: list) -> None:
        """Render cyan/green glowing oval portals at the top."""
        time_ms = pygame.time.get_ticks()
        pulse = 0.5 + 0.5 * math.sin(time_ms * 0.005)

        for px, py in portals:
            pw = int(58 + pulse * 6)
            ph = int(22 + pulse * 4)
            portal_rect = pygame.Rect(px - pw // 2, py - ph // 2, pw, ph)

            # Portal translucent aura
            aura_surf = pygame.Surface((pw + 10, ph + 10), pygame.SRCALPHA)
            pygame.draw.ellipse(aura_surf, (0, 230, 180, 55), (5, 5, pw, ph))
            surface.blit(aura_surf, (px - pw // 2 - 5, py - ph // 2 - 5))

            # Main portal ring
            pygame.draw.ellipse(surface, (100, 200, 170), portal_rect)
            pygame.draw.ellipse(surface, (20, 60, 50), portal_rect, width=2)

            # Inner vortex slit
            inner_rect = pygame.Rect(px - pw // 4, py - ph // 4, pw // 2, ph // 2)
            pygame.draw.ellipse(surface, (30, 80, 65), inner_rect)

    def _draw_range_ring(self, surface: pygame.Surface, tower) -> None:
        """Render semi-transparent attack radius circle around tower."""
        r = int(tower.range)
        diam = r * 2
        ring_surf = pygame.Surface((diam, diam), pygame.SRCALPHA)

        # Translucent fill
        pygame.draw.circle(ring_surf, (255, 255, 255, 30), (r, r), r)
        # Smooth ring outline
        pygame.draw.circle(ring_surf, (220, 245, 255, 140), (r, r), r, width=2)

        surface.blit(ring_surf, (int(tower.x - r), int(tower.y - r)))

    def _draw_target_marker(self, surface: pygame.Surface, tower, target) -> None:
        """Draw targeting ray and reticle box on active target."""
        # Subtle targeting tracer line
        pygame.draw.line(surface, (255, 255, 255, 120), (int(tower.x), int(tower.y)),
                         (int(target.x), int(target.y)), 1)

        # Bracket reticle on targeted enemy
        tx, ty = int(target.x), int(target.y)
        tr = int(target.radius + 6)
        bracket_col = (255, 215, 0)
        line_len = 7

        # Top-left corner
        pygame.draw.line(surface, bracket_col, (tx - tr, ty - tr), (tx - tr + line_len, ty - tr), 2)
        pygame.draw.line(surface, bracket_col, (tx - tr, ty - tr), (tx - tr, ty - tr + line_len), 2)
        # Top-right corner
        pygame.draw.line(surface, bracket_col, (tx + tr, ty - tr), (tx + tr - line_len, ty - tr), 2)
        pygame.draw.line(surface, bracket_col, (tx + tr, ty - tr), (tx + tr, ty - tr + line_len), 2)
        # Bottom-left corner
        pygame.draw.line(surface, bracket_col, (tx - tr, ty + tr), (tx - tr + line_len, ty + tr), 2)
        pygame.draw.line(surface, bracket_col, (tx - tr, ty + tr), (tx - tr, ty - tr + line_len), 2)
        # Bottom-right corner
        pygame.draw.line(surface, bracket_col, (tx + tr, ty + tr), (tx + tr - line_len, ty + tr), 2)
        pygame.draw.line(surface, bracket_col, (tx + tr, ty + tr), (tx + tr, ty - tr + line_len), 2)

    def _draw_cute_enemy(self, surface: pygame.Surface, enemy, font_cache: dict) -> None:
        """
        Draw cute robotic enemies matching Tiny Towers aesthetic:
        - Rounded body with thick dark outline
        - Eye stalks with blinking/looking pupils
        - Cute little antennas with bobbing tips
        - Stubby feet walking with animation cycle
        - Health bar with green/red ratio above
        """
        ex, ey = int(enemy.x), int(enemy.y)
        r = int(enemy.radius)
        phase = enemy.anim_phase

        # Walk bobbing
        bob_y = int(math.sin(phase * 4.0) * 2.0)
        ey += bob_y

        # Feet (two little stubby circles that alternate forward/backward)
        foot_offset = int(math.sin(phase * 5.0) * 3.5)
        foot_r = max(3, r // 4)
        foot_col = (40, 40, 50)
        pygame.draw.circle(surface, foot_col, (ex - r // 2, ey + r - 2 + foot_offset), foot_r)
        pygame.draw.circle(surface, foot_col, (ex + r // 2, ey + r - 2 - foot_offset), foot_r)

        # Body (rounded shape with outline)
        body_col = (255, 255, 255) if enemy.hit_flash_timer > 0 else enemy.color
        body_rect = pygame.Rect(ex - r, ey - r + 3, r * 2, r * 2 - 3)
        pygame.draw.rect(surface, body_col, body_rect, border_radius=max(6, r // 2))
        pygame.draw.rect(surface, (20, 20, 30), body_rect, width=2, border_radius=max(6, r // 2))

        # Antenna stalk & tip
        ant_x = ex
        ant_y = ey - r + 2
        pygame.draw.line(surface, (30, 30, 40), (ant_x, ant_y), (ant_x, ant_y - 8), 2)
        pygame.draw.circle(surface, (255, 215, 0), (ant_x, ant_y - 9), 3)

        # Eyes on Stalks (two cute white circles with black pupils)
        eye_spacing = max(5, r // 2)
        eye_y = ey - r // 3
        for eye_x in (ex - eye_spacing, ex + eye_spacing):
            # Eye outer ring
            pygame.draw.circle(surface, (255, 255, 255), (eye_x, eye_y), max(3, r // 3))
            pygame.draw.circle(surface, (30, 30, 40), (eye_x, eye_y), max(3, r // 3), width=1)
            # Pupil looking downward toward base
            pygame.draw.circle(surface, (20, 20, 30), (eye_x, eye_y + 1), max(1, r // 6))

        # Mouth / Screen visor
        mouth_rect = pygame.Rect(ex - r // 3, ey + r // 4, max(4, (r * 2) // 3), 4)
        pygame.draw.rect(surface, (20, 40, 30), mouth_rect, border_radius=2)

        # Boss Crown / Indicator
        if enemy.enemy_type == ENEMY_TYPE_BOSS:
            crown_pts = [(ex - 14, ey - r - 4), (ex - 8, ey - r - 12), (ex, ey - r - 6),
                         (ex + 8, ey - r - 12), (ex + 14, ey - r - 4), (ex, ey - r - 2)]
            pygame.draw.polygon(surface, (255, 215, 0), crown_pts)
            pygame.draw.polygon(surface, (180, 130, 0), crown_pts, width=1)

        # Health Bar
        bar_w = max(28, r * 2 + 8)
        bar_h = 5
        bar_x = ex - bar_w // 2
        bar_y = ey - r - 16
        pygame.draw.rect(surface, (40, 20, 20), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        fill_w = int(bar_w * enemy.health_fraction())
        if fill_w > 0:
            hp_col = (76, 175, 80) if enemy.health_fraction() > 0.35 else (239, 83, 80)
            pygame.draw.rect(surface, hp_col, (bar_x, bar_y, fill_w, bar_h), border_radius=3)
        pygame.draw.rect(surface, (20, 20, 30), (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=3)

    def _draw_projectiles(self, surface: pygame.Surface, projectiles: list) -> None:
        """Render energy shots with golden glow."""
        for proj in projectiles:
            px, py = int(proj.x), int(proj.y)
            r = int(proj.radius)
            # Outer glow
            pygame.draw.circle(surface, (255, 235, 59), (px, py), r)
            pygame.draw.circle(surface, (230, 81, 0), (px, py), r, width=1)
            # Center bright white core
            pygame.draw.circle(surface, (255, 255, 255), (px, py), max(1, r - 2))

    def _draw_tower(self, surface: pygame.Surface, tower, shield_sys) -> None:
        """
        Render colorful central tower:
        - Magenta rounded base with thick black border
        - White circular turret head with pink accents
        - Cannon barrel pointing toward current target angle
        - Shield bubble when active
        """
        tx, ty = int(tower.x), int(tower.y)
        r = int(tower.radius)

        # Damage flash white tint
        base_col = (255, 255, 255) if tower.damage_flash_timer > 0 else COLOR_TOWER_BASE

        # Base rounded rect
        base_rect = pygame.Rect(tx - r, ty - r, r * 2, r * 2)
        # Drop shadow
        pygame.draw.rect(surface, COLOR_TOWER_BASE_SHADOW, (base_rect.x, base_rect.y + 4, base_rect.width, base_rect.height), border_radius=10)
        # Base body
        pygame.draw.rect(surface, base_col, base_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_TOWER_OUTLINE, base_rect, width=3, border_radius=10)

        # Turret Head (circular)
        turret_r = int(r * 0.72)
        pygame.draw.circle(surface, COLOR_TOWER_TURRET, (tx, ty), turret_r)
        pygame.draw.circle(surface, COLOR_TOWER_TURRET_TRIM, (tx, ty), turret_r - 3, width=2)
        pygame.draw.circle(surface, COLOR_TOWER_OUTLINE, (tx, ty), turret_r, width=2)

        # Turret Barrel (pointing along turret_angle)
        ang = tower.turret_angle
        bx1 = tx + math.cos(ang) * 4
        by1 = ty + math.sin(ang) * 4
        bx2 = tx + math.cos(ang) * (r + 10)
        by2 = ty + math.sin(ang) * (r + 10)
        pygame.draw.line(surface, COLOR_TOWER_BARREL, (int(bx1), int(by1)), (int(bx2), int(by2)), 7)
        pygame.draw.circle(surface, (255, 64, 129), (int(bx2), int(by2)), 3)

        # Turret side bumpers (headphone style from Tiny Towers screenshot)
        side_ang1 = ang + math.pi / 2
        side_ang2 = ang - math.pi / 2
        for s_ang in (side_ang1, side_ang2):
            sx = tx + math.cos(s_ang) * turret_r
            sy = ty + math.sin(s_ang) * turret_r
            pygame.draw.circle(surface, (255, 64, 129), (int(sx), int(sy)), 5)
            pygame.draw.circle(surface, COLOR_TOWER_OUTLINE, (int(sx), int(sy)), 5, width=1)

        # Shield Bubble (glowing cyan aura around tower)
        if shield_sys.is_active():
            pulse = math.sin(shield_sys.pulse_timer) * 3.0
            bubble_r = int(r + 18 + pulse)
            shield_surf = pygame.Surface((bubble_r * 2 + 10, bubble_r * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, COLOR_SHIELD_BUBBLE, (bubble_r + 5, bubble_r + 5), bubble_r)
            pygame.draw.circle(shield_surf, COLOR_SHIELD_BORDER, (bubble_r + 5, bubble_r + 5), bubble_r, width=2)
            surface.blit(shield_surf, (tx - bubble_r - 5, ty - bubble_r - 5))

    def _draw_effects(self, surface: pygame.Surface, effects, font_cache: dict) -> None:
        """Render all active visual effects."""
        # Shockwaves
        for s in effects.shockwaves:
            r = int(s.current_radius)
            if r > 0:
                alpha = int(255 * s.alpha_fraction())
                ring_surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
                col = (s.color[0], s.color[1], s.color[2], alpha)
                pygame.draw.circle(ring_surf, col, (r + 5, r + 5), r, width=s.line_width)
                surface.blit(ring_surf, (int(s.cx - r - 5), int(s.cy - r - 5)))

        # Particles (explosions & sparkles)
        for p in effects.particles:
            px, py = int(p.x), int(p.y)
            pr = max(1, int(p.size))
            pygame.draw.circle(surface, p.color, (px, py), pr)

        # Floating numbers (damage & coins)
        for t in effects.floating_texts:
            f = font_cache.get(t.font_size, pygame.font.SysFont("arial", t.font_size, bold=True))
            # Text shadow for clarity
            shadow_surf = f.render(t.text, True, (20, 20, 30))
            text_surf = f.render(t.text, True, t.color)
            surface.blit(shadow_surf, (int(t.x + 1), int(t.y + 1)))
            surface.blit(text_surf, (int(t.x), int(t.y)))

    def _draw_cards(self, surface: pygame.Surface, font_cache: dict, tower, economy,
                    upgrade_sys, shield_sys, blast_sys) -> None:
        """Render upgrade cards with live affordability and status."""
        # 1. Attack Power
        cost_atk = upgrade_sys.get_attack_cost()
        self.cards[0].draw(surface, font_cache, upgrade_sys.attack_level, cost_atk,
                           economy.can_afford(cost_atk), is_maxed=False)

        # 2. Shooting Speed
        cost_spd = upgrade_sys.get_speed_cost()
        is_spd_max = upgrade_sys.is_speed_maxed(tower)
        self.cards[1].draw(surface, font_cache, upgrade_sys.speed_level, cost_spd,
                           economy.can_afford(cost_spd), is_maxed=is_spd_max)

        # 3. Shield
        cost_shield = shield_sys.get_recharge_cost()
        is_shield_full = not shield_sys.can_recharge()
        self.cards[2].draw(surface, font_cache, shield_sys.level, cost_shield,
                           economy.can_afford(cost_shield), is_maxed=is_shield_full)

        # 4. Extra Heart
        cost_heart = upgrade_sys.get_heart_cost()
        is_heart_max = upgrade_sys.is_heart_maxed(tower)
        self.cards[3].draw(surface, font_cache, upgrade_sys.heart_level, cost_heart,
                           economy.can_afford(cost_heart), is_maxed=is_heart_max)

        # 5. Emergency Blast
        cost_blast = blast_sys.get_upgrade_cost()
        self.cards[4].draw(surface, font_cache, blast_sys.level, cost_blast,
                           economy.can_afford(cost_blast), is_maxed=False,
                           cooldown_fraction=blast_sys.ready_fraction())

    def _draw_screen_flashes(self, surface: pygame.Surface, effects) -> None:
        """Render fullscreen screen tint flash."""
        for flash in effects.screen_flashes:
            alpha = flash.current_alpha()
            if alpha > 0:
                tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                tint.fill((flash.color[0], flash.color[1], flash.color[2], alpha))
                surface.blit(tint, (0, 0))
