from evennia.contrib.tutorials.evadventure.npcs import EvAdventureMob

from typeclasses.training import grant_training_effigy_xp


class SaltWornSparringEffigy(EvAdventureMob):
    hit_dice = 3
    coins = 0

    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = (
            "A salt-worn effigy of rope, driftwood, and cracked armor plates stands "
            "waiting for blows. It has no voice, no anger, and no purpose beyond "
            "enduring practice inside the ring."
        )

    def at_looted(self, looter):
        return None

    def _stop_handler(self, obj):
        combathandler = getattr(getattr(obj, "ndb", None), "combathandler", None)
        if combathandler and getattr(combathandler, "id", None):
            combathandler.stop_combat()

    def at_damage(self, damage, attacker=None):
        super().at_damage(damage, attacker=attacker)
        if self.hp > 0 or not attacker or not getattr(attacker, "is_pc", False):
            return

        grant_training_effigy_xp(attacker)
        self.hp = self.hp_max
        self._stop_handler(attacker)
        self._stop_handler(self)
