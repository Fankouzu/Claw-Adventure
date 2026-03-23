from evennia.utils.create import create_object
from evennia.utils.test_resources import EvenniaCommandTest

from commands.progress_commands import CmdProgress


class TestProgressCommands(EvenniaCommandTest):
    def setUp(self):
        super().setUp()
        self.char1.key = "Attacker"
        self.char1.db_key = "Attacker"
        self.char1.save()
        self.other = create_object(
            "typeclasses.characters.Character",
            key="Defender",
            location=self.room1,
            home=self.room1,
        )
        self.addCleanup(self.other.delete)
        self.char1.db.pvp_rank = 2
        self.char1.db.pvp_xp = 135
        self.char1.db.pvp_wins = 3
        self.char1.db.pvp_losses = 1
        self.char1.db.pvp_damage_dealt_lifetime = 87
        self.other.db.pvp_rank = 1
        self.other.db.pvp_xp = 40
        self.other.db.pvp_wins = 0
        self.other.db.pvp_losses = 1
        self.other.db.pvp_damage_dealt_lifetime = 12

    def test_progress_shows_self(self):
        self.call(
            CmdProgress(),
            "",
            "PvP Progress\nRank: 2\nXP: 135\nXP to next rank: 65\nWins: 3\nLosses: 1\nLifetime PvP damage dealt: 87",
            caller=self.char1,
        )

    def test_progress_shows_other_character(self):
        self.call(
            CmdProgress(),
            "Defender",
            "PvP Progress for Defender\nRank: 1\nXP: 40\nXP to next rank: 60\nWins: 0\nLosses: 1\nLifetime PvP damage dealt: 12",
            caller=self.char1,
        )

    def test_rank_alias_works(self):
        self.call(
            CmdProgress(),
            "",
            "PvP Progress\nRank: 2\nXP: 135\nXP to next rank: 65\nWins: 3\nLosses: 1\nLifetime PvP damage dealt: 87",
            caller=self.char1,
            cmdstring="rank",
        )
