from unittest.mock import Mock

from evennia.utils.create import create_object
from evennia.utils.test_resources import EvenniaTest


class TestArenaPvPProgression(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.room = create_object(
            "typeclasses.pvp_rooms.BrokenShoreRingRoom",
            key="Arena Room",
        )
        self.addCleanup(self.room.delete)
        self.attacker = create_object(
            "typeclasses.characters.Character",
            key="Attacker",
            location=self.room,
            home=self.room,
        )
        self.defender = create_object(
            "typeclasses.characters.Character",
            key="Defender",
            location=self.room,
            home=self.room,
        )
        self.addCleanup(self.attacker.delete)
        self.addCleanup(self.defender.delete)
        self.attacker.hp = 100
        self.attacker.hp_max = 100
        self.attacker.max_hp = 100
        self.defender.hp = 100
        self.defender.hp_max = 100
        self.defender.max_hp = 100
        self.attacker.msg = Mock()
        self.defender.msg = Mock()

    def test_damage_based_xp_allocation(self):
        self.defender.at_damage(30, attacker=self.attacker)
        self.attacker.at_damage(10, attacker=self.defender)
        self.defender.at_damage(self.defender.hp, attacker=self.attacker)

        self.assertEqual(self.attacker.db.pvp_xp, 36)
        self.assertEqual(self.defender.db.pvp_xp, 4)
        self.assertEqual(self.attacker.db.pvp_wins, 1)
        self.assertEqual(self.defender.db.pvp_losses, 1)

    def test_no_reward_when_no_damage_recorded(self):
        self.assertEqual(int(getattr(self.attacker.db, "pvp_xp", 0) or 0), 0)
        self.assertEqual(int(getattr(self.defender.db, "pvp_xp", 0) or 0), 0)

    def test_repeated_opponent_decay(self):
        for _ in range(3):
            self.defender.hp = self.defender.hp_max
            self.attacker.hp = self.attacker.hp_max
            self.defender.at_damage(20, attacker=self.attacker)
            self.attacker.at_damage(20, attacker=self.defender)
            self.defender.at_damage(self.defender.hp, attacker=self.attacker)

        self.assertEqual(self.attacker.db.pvp_xp, 57)
        self.assertEqual(self.defender.db.pvp_xp, 13)

    def test_rank_up_from_pvp_xp(self):
        self.attacker.db.pvp_xp = 95
        self.attacker.db.pvp_rank = 1

        self.defender.at_damage(self.defender.hp, attacker=self.attacker)

        self.assertEqual(self.attacker.db.pvp_rank, 2)
        self.assertGreaterEqual(self.attacker.db.pvp_xp, 100)

    def test_non_player_targets_do_not_award_pvp_xp(self):
        dummy = create_object(
            "typeclasses.training_dummy.SaltWornSparringEffigy",
            key="The Salt-Worn Sparring Effigy",
            location=self.room,
            home=self.room,
        )
        self.addCleanup(dummy.delete)

        dummy.at_damage(dummy.hp, attacker=self.attacker)

        self.assertEqual(int(getattr(self.attacker.db, "pvp_xp", 0) or 0), 0)
