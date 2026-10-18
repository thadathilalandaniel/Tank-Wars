"""
dsa_defenders/entities/effects.py

This module contains visual effect data structures:
- Floating numbers (damage text, coin popups)
- Particles (explosion sparks, smoke, coin stars, shield shards)
- Expanding shockwave rings (Emergency Blast, Shield shatter)
- Screen flashes (damage taken, blast)

Modules that interact with this:
- game/combat.py (spawns damage text, death sparks)
- systems/blast.py (spawns shockwaves and flashes)
- systems/shield.py (spawns shield break effects)
- systems/upgrades.py (spawns purchase sparkles)
- ui/game_screen.py (renders all active effects)
"""

import math
import random
from config import (
    COLOR_DAMAGE_TEXT,
    COLOR_COIN_TEXT,
    COLOR_BLAST_RING,
    COLOR_SHIELD_BORDER,
)


class FloatingText:
    """Floating numerical or text label that rises and fades out."""

    def __init__(self, text: str, x: float, y: float, color=COLOR_DAMAGE_TEXT,
                 duration: float = 0.85, vy: float = -45.0, font_size: int = 20):
        self.text = str(text)
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.duration = float(duration)
        self.lifetime = float(duration)
        self.vy = float(vy)
        self.vx = random.uniform(-10.0, 10.0)
        self.font_size = font_size

    def update(self, dt: float) -> bool:
        """Update position and lifetime. Returns False when expired."""
        self.lifetime -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        return self.lifetime > 0.0

    def alpha_fraction(self) -> float:
        """Returns 1.0 (opaque) down to 0.0 (transparent)."""
        return max(0.0, min(1.0, self.lifetime / self.duration))


class Particle:
    """A single energetic particle for explosions, sparks, and sparkles."""

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color: tuple, size: float = 4.0, duration: float = 0.5):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.initial_size = float(size)
        self.size = float(size)
        self.duration = float(duration)
        self.lifetime = float(duration)

    def update(self, dt: float) -> bool:
        """Update physics. Returns False when dead."""
        self.lifetime -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Drag/friction
        self.vx *= (1.0 - 1.5 * dt)
        self.vy *= (1.0 - 1.5 * dt)
        # Shrink with age
        fraction = max(0.0, self.lifetime / self.duration)
        self.size = self.initial_size * fraction
        return self.lifetime > 0.0 and self.size > 0.5


class ShockwaveRing:
    """Expanding circular shockwave for blast powers and shield events."""

    def __init__(self, cx: float, cy: float, max_radius: float, speed: float = 480.0,
                 color=COLOR_BLAST_RING, line_width: int = 4):
        self.cx = float(cx)
        self.cy = float(cy)
        self.current_radius = 5.0
        self.max_radius = float(max_radius)
        self.speed = float(speed)
        self.color = color
        self.line_width = line_width
        self.alive = True

    def update(self, dt: float) -> bool:
        """Advance expansion. Returns False when maximum radius reached."""
        self.current_radius += self.speed * dt
        if self.current_radius >= self.max_radius:
            self.alive = False
        return self.alive

    def alpha_fraction(self) -> float:
        """Fades out towards edge of blast."""
        return max(0.0, 1.0 - (self.current_radius / self.max_radius))


class ScreenFlash:
    """Screen-wide color tint overlay for impact feedback."""

    def __init__(self, color=(255, 50, 50), max_alpha: int = 120, duration: float = 0.22):
        self.color = color
        self.max_alpha = max_alpha
        self.duration = duration
        self.lifetime = duration

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        return self.lifetime > 0.0

    def current_alpha(self) -> int:
        frac = max(0.0, min(1.0, self.lifetime / self.duration))
        return int(self.max_alpha * frac)


class EffectsManager:
    """Consolidates and manages all active visual particles and popups."""

    def __init__(self):
        self.floating_texts = []
        self.particles = []
        self.shockwaves = []
        self.screen_flashes = []

    def add_floating_damage(self, text: str, x: float, y: float, crit: bool = False) -> None:
        color = (255, 82, 82) if crit else COLOR_DAMAGE_TEXT
        size = 22 if crit else 18
        self.floating_texts.append(FloatingText(text, x, y - 10, color=color, font_size=size))

    def add_floating_coin(self, amount: int, x: float, y: float) -> None:
        self.floating_texts.append(FloatingText(f"+{amount}", x, y - 10, color=COLOR_COIN_TEXT, font_size=19))

    def add_explosion(self, x: float, y: float, base_color: tuple, count: int = 14) -> None:
        """Spawn circular burst of sparks."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50.0, 220.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(3.0, 6.0)
            dur = random.uniform(0.35, 0.65)
            self.particles.append(Particle(x, y, vx, vy, base_color, size=size, duration=dur))

    def add_sparkle(self, x: float, y: float, count: int = 8, color=(255, 235, 59)) -> None:
        """Spawn light sparkles (for upgrades and coins)."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30.0, 120.0)
            self.particles.append(Particle(x, y, math.cos(angle) * speed, math.sin(angle) * speed,
                                           color, size=3.5, duration=0.4))

    def add_shockwave(self, cx: float, cy: float, max_radius: float = 300.0,
                      color=COLOR_BLAST_RING, line_width: int = 5) -> None:
        self.shockwaves.append(ShockwaveRing(cx, cy, max_radius, color=color, line_width=line_width))

    def add_screen_flash(self, color=(255, 50, 50), max_alpha: int = 100, duration: float = 0.2) -> None:
        self.screen_flashes.append(ScreenFlash(color, max_alpha, duration))

    def update(self, dt: float) -> None:
        """Update all active effects, pruning finished ones."""
        self.floating_texts = [t for t in self.floating_texts if t.update(dt)]
        self.particles = [p for p in self.particles if p.update(dt)]
        self.shockwaves = [s for s in self.shockwaves if s.update(dt)]
        self.screen_flashes = [f for f in self.screen_flashes if f.update(dt)]

    def clear(self) -> None:
        """Reset all effects."""
        self.floating_texts.clear()
        self.particles.clear()
        self.shockwaves.clear()
        self.screen_flashes.clear()
