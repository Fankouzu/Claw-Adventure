"""
EvAdventure mobs with achievement hooks.

Set prototype typeclass to ``typeclasses.mobs.ClawEvAdventureMob`` for combat
credit when HP hits 0. Loot-based credit shares the same ndb dedup flag.
"""

from evennia.contrib.tutorials.evadventure.npcs import EvAdventureMob

from world.achievements.integration import send_achievement_unlock_messages


class ClawEvAdventureMob(EvAdventureMob):
    """
    Records combat achievements when HP drops to 0 (before loot).

    Use for content where players may not run the loot command.
    """

    def at_damage(self, damage, attacker=None):
        super().at_damage(damage, attacker=attacker)
        if self.hp > 0 or not attacker:
            return
        from world.achievements.integration import (
            record_combat_victory_for_defeat,
        )

        unlocked = record_combat_victory_for_defeat(attacker, self)
        send_achievement_unlock_messages(attacker, unlocked)
