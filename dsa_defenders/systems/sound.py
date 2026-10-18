"""
dsa_defenders/systems/sound.py

This module implements a procedural synthesizer for retro game audio tones.
It generates PCM waveform buffers using pure Python math and struct packaging
without requiring external audio files, numpy, or third-party assets.
If pygame.mixer cannot be initialized (e.g. in headless environments), it
degrades gracefully with zero errors.

Modules that interact with this:
- game/game_manager.py (toggles audio mute)
- game/combat.py (plays shoot, hit, kill tones)
- systems/upgrades.py (plays upgrade chimes)
- systems/blast.py (plays blast explosion sound)
"""

import math
import struct
import pygame


class SoundManager:
    """Manages audio playback and procedural sound generation."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.available = False
        self._sounds = {}

        self._init_mixer()
        if self.available:
            self._generate_all_tones()

    def _init_mixer(self) -> None:
        """Initialize the mixer safely."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.available = True
        except Exception:
            self.available = False

    def _synthesize_tone(self, freq_start: float, freq_end: float, duration: float,
                         volume: float = 0.25, waveform: str = "sine") -> pygame.mixer.Sound | None:
        """Generate a procedural sound using pure Python struct packing."""
        if not self.available:
            return None

        sample_rate = 22050
        n_samples = max(1, int(sample_rate * duration))
        buf = bytearray()

        for i in range(n_samples):
            t = float(i) / sample_rate
            progress = float(i) / n_samples
            current_freq = freq_start + (freq_end - freq_start) * progress

            # Envelope: fast attack, linear decay
            envelope = 1.0 - progress

            if waveform == "square":
                phase = (t * current_freq) % 1.0
                sample_val = 1.0 if phase < 0.5 else -1.0
            else:  # sine
                sample_val = math.sin(2.0 * math.pi * current_freq * t)

            int_val = int(32767 * volume * envelope * sample_val)
            int_val = max(-32768, min(32767, int_val))
            buf += struct.pack('<h', int_val)

        try:
            return pygame.mixer.Sound(buffer=bytes(buf))
        except Exception:
            return None

    def _generate_all_tones(self) -> None:
        """Synthesize all game sound effects."""
        # Laser shoot (pitch descending)
        self._sounds["shoot"] = self._synthesize_tone(650.0, 220.0, 0.08, volume=0.18)
        # Enemy hit (short blip)
        self._sounds["hit"] = self._synthesize_tone(300.0, 150.0, 0.05, volume=0.22, waveform="square")
        # Coin pickup (bright high ping)
        self._sounds["coin"] = self._synthesize_tone(880.0, 1320.0, 0.10, volume=0.20)
        # Upgrade purchased (pleasant upward chord tone)
        self._sounds["upgrade"] = self._synthesize_tone(440.0, 880.0, 0.22, volume=0.25)
        # Emergency Blast (deep rumble)
        self._sounds["blast"] = self._synthesize_tone(180.0, 45.0, 0.45, volume=0.35, waveform="square")
        # Shield impact (metallic ping)
        self._sounds["shield_hit"] = self._synthesize_tone(900.0, 450.0, 0.09, volume=0.22)
        # Shield broken (descending harsh crunch)
        self._sounds["shield_break"] = self._synthesize_tone(400.0, 90.0, 0.25, volume=0.30, waveform="square")
        # Tower hurt (low thud)
        self._sounds["hurt"] = self._synthesize_tone(160.0, 80.0, 0.20, volume=0.32, waveform="square")
        # Wave complete fanfare
        self._sounds["wave_clear"] = self._synthesize_tone(523.0, 1046.0, 0.35, volume=0.28)
        # Game over (sad slide)
        self._sounds["game_over"] = self._synthesize_tone(320.0, 80.0, 0.55, volume=0.30)
        # Denied / Not enough coins
        self._sounds["denied"] = self._synthesize_tone(140.0, 120.0, 0.12, volume=0.20, waveform="square")

    def play(self, sound_name: str) -> None:
        """Play a synthesized sound effect if audio is enabled."""
        if not self.enabled or not self.available:
            return
        sound = self._sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def toggle(self) -> bool:
        """Toggle mute on/off. Returns new enabled status."""
        self.enabled = not self.enabled
        return self.enabled
