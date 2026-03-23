from evennia.utils.create import create_object
from evennia.utils.test_resources import EvenniaTest


class TestBrokenShoreRingRoom(EvenniaTest):
    def test_broken_shore_ring_room_enables_nonlethal_pvp(self):
        from typeclasses.pvp_rooms import BrokenShoreRingRoom

        room = create_object(BrokenShoreRingRoom, key="Broken Shore Test Room")

        self.assertTrue(room.allow_combat)
        self.assertTrue(room.allow_pvp)
        self.assertFalse(room.allow_death)
        self.assertEqual(
            room.get_display_footer(self.char1),
            "|yNon-lethal PvP combat is allowed here!|n",
        )

        room.delete()
