from unittest.mock import Mock

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

    def test_ghost_cannot_enter_broken_shore_ring(self):
        from typeclasses.pvp_rooms import BrokenShoreRingRoom

        courtyard = create_object("typeclasses.rooms.Room", key="Courtyard")
        room = create_object(BrokenShoreRingRoom, key="Broken Shore Test Room")
        ghost = create_object(
            "evennia.contrib.tutorials.tutorial_world.mob.Mob",
            key="Ghostly apparition",
            location=courtyard,
            home=courtyard,
        )
        ghost.msg = Mock()

        moved = ghost.move_to(room)

        self.assertFalse(moved)
        self.assertEqual(ghost.location, courtyard)
        ghost.msg.assert_called_with("The ghost cannot cross into the ring.")

        ghost.delete()
        courtyard.delete()
        room.delete()

    def test_player_can_enter_broken_shore_ring(self):
        from typeclasses.pvp_rooms import BrokenShoreRingRoom

        courtyard = create_object("typeclasses.rooms.Room", key="Courtyard")
        room = create_object(BrokenShoreRingRoom, key="Broken Shore Test Room")

        moved = self.char1.move_to(room)

        self.assertTrue(moved)
        self.assertEqual(self.char1.location, room)

        courtyard.delete()
        room.delete()
