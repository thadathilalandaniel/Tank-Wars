"""
dsa_defenders/systems/economy.py

This module manages the player's currency (coins) and purchase transactions.
All systems and UI widgets MUST use the centralized can_afford() and spend()
methods to guarantee single-source-of-truth consistency.

Modules that interact with this:
- game/combat.py (deposits bounty coins on enemy kill)
- systems/upgrades.py (checks affordability and spends coins)
- systems/shield.py (recharges shield with coins)
- systems/blast.py (purchases emergency blast charges/upgrades)
- ui/hud.py & ui/buttons.py (displays balance and triggers shake feedback)
"""

from config import INITIAL_COINS


class EconomySystem:
    """Centralized currency ledger and affordability controller."""

    def __init__(self, initial_coins: int = INITIAL_COINS):
        self.coins = initial_coins
        self.total_earned = initial_coins
        self.denied_feedback_timer = 0.0

    def can_afford(self, cost: int) -> bool:
        """Check if current coin reserve meets or exceeds the required cost."""
        return self.coins >= cost

    def spend(self, cost: int) -> bool:
        """
        Deduct coins if sufficient balance exists.
        Returns True on success, False on failure.
        """
        if self.can_afford(cost):
            self.coins -= cost
            return True
        
        # Trigger visual/audio denial feedback
        self.denied_feedback_timer = 0.35
        return False

    def add_coins(self, amount: int) -> None:
        """Deposit earned currency."""
        if amount > 0:
            self.coins += amount
            self.total_earned += amount

    def trigger_denied(self) -> None:
        """Manually trigger insufficient funds feedback."""
        self.denied_feedback_timer = 0.35

    def update(self, dt: float) -> None:
        """Update feedback timers."""
        if self.denied_feedback_timer > 0:
            self.denied_feedback_timer = max(0.0, self.denied_feedback_timer - dt)

    def is_denied_active(self) -> bool:
        """Check if shake/red border feedback should be actively rendered."""
        return self.denied_feedback_timer > 0.0

    def reset(self, initial_coins: int = INITIAL_COINS) -> None:
        """Reset economy to starting balance."""
        self.coins = initial_coins
        self.total_earned = initial_coins
        self.denied_feedback_timer = 0.0
