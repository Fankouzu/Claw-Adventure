from unittest.mock import Mock, patch

from evennia.utils.create import create_object
from evennia.utils.test_resources import EvenniaTest
from typeclasses.training import _today_key


class TestTrainingEffigyRewards(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.room = create_object(
            "typeclasses.pvp_rooms.BrokenShoreRingRoom",
            key="Training Arena",
        )
        self.addCleanup(self.room.delete)
        self.attacker = create_object(
            "typeclasses.characters.Character",
            key="Attacker",
            location=self.room,
            home=self.room,
        )
        self.addCleanup(self.attacker.delete)
        self.attacker.msg = Mock()

    def _create_dummy(self):
        return create_object(
            "typeclasses.training_dummy.SaltWornSparringEffigy",
            key="The Salt-Worn Sparring Effigy",
            location=self.room,
            home=self.room,
        )

    def test_level_one_defeat_grants_25_xp(self):
        dummy = self._create_dummy()
        self.addCleanup(dummy.delete)

        dummy.at_damage(dummy.hp, attacker=self.attacker)

        self.assertEqual(self.attacker.xp, 25)
        self.attacker.msg.assert_called_with(
            "You learn a little from striking the Salt-Worn Sparring Effigy."
        )

    def test_level_six_defeat_grants_no_xp(self):
        dummy = self._create_dummy()
        self.addCleanup(dummy.delete)
        self.attacker.level = 6

        dummy.at_damage(dummy.hp, attacker=self.attacker)

        self.assertEqual(self.attacker.xp, 0)
        self.attacker.msg.assert_called_with(
            "Your skills have outgrown what this effigy can teach."
        )

    def test_daily_cap_limits_award(self):
        dummy = self._create_dummy()
        self.addCleanup(dummy.delete)
        self.attacker.db.training_effigy_daily_xp = 240
        self.attacker.db.training_effigy_lifetime_xp = 0
        self.attacker.db.training_effigy_last_reset = _today_key()

        dummy.at_damage(dummy.hp, attacker=self.attacker)

        self.assertEqual(self.attacker.xp, 10)
        self.assertEqual(self.attacker.db.training_effigy_daily_xp, 250)

    def test_lifetime_cap_limits_award(self):
        dummy = self._create_dummy()
        self.addCleanup(dummy.delete)
        self.attacker.db.training_effigy_daily_xp = 0
        self.attacker.db.training_effigy_lifetime_xp = 1490

        dummy.at_damage(dummy.hp, attacker=self.attacker)

        self.assertEqual(self.attacker.xp, 10)
        self.assertEqual(self.attacker.db.training_effigy_lifetime_xp, 1500)

    def test_defeat_can_level_up_character(self):
        dummy = self._create_dummy()
        self.addCleanup(dummy.delete)
        self.attacker.xp = 990

        dummy.at_damage(dummy.hp, attacker=self.attacker)

        self.assertEqual(self.attacker.level, 2)
        self.assertEqual(self.attacker.xp, 1015)

    def test_dummy_defeat_does_not_log_standard_combat_achievement(self):
        dummy = self._create_dummy()
        self.addCleanup(dummy.delete)

        with patch(
            "world.achievements.integration.record_combat_victory_for_defeat"
        ) as record_victory:
            dummy.at_damage(dummy.hp, attacker=self.attacker)

        record_victory.assert_not_called()

    def test_dummy_defeat_uses_english_daily_cap_message(self):
        dummy = self._create_dummy()
        self.addCleanup(dummy.delete)
        self.attacker.db.training_effigy_daily_xp = 250
        self.attacker.db.training_effigy_lifetime_xp = 0
        self.attacker.db.training_effigy_last_reset = _today_key()

        dummy.at_damage(dummy.hp, attacker=self.attacker)

        self.attacker.msg.assert_called_with(
            "You cannot learn any more from the effigy today."
        )

    def test_dummy_cannot_be_looted_for_coins(self):
        dummy = self._create_dummy()
        self.addCleanup(dummy.delete)
        self.attacker.coins = 7

        dummy.at_looted(self.attacker)

        self.assertEqual(self.attacker.coins, 7)

    def test_dummy_recovers_after_defeat(self):
        dummy = self._create_dummy()
        self.addCleanup(dummy.delete)

        dummy.at_damage(dummy.hp, attacker=self.attacker)

        self.assertEqual(dummy.hp, dummy.hp_max)
        self.assertEqual(dummy.location, self.room)
