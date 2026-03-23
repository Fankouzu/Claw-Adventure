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
        from typeclasses.exits import Exit
        from typeclasses.pvp_rooms import BrokenShoreRingRoom

        courtyard = create_object("typeclasses.rooms.Room", key="Courtyard")
        room = create_object(BrokenShoreRingRoom, key="Broken Shore Test Room")
        ring_exit = create_object(
            Exit, key="ring", location=courtyard, destination=room
        )
        ghost = create_object(
            "evennia.contrib.tutorials.tutorial_world.mob.Mob",
            key="Ghostly apparition",
            location=courtyard,
            home=courtyard,
        )
        ghost.msg = Mock()

        ring_exit.at_traverse(ghost, room)

        self.assertEqual(ghost.location, courtyard)
        ghost.msg.assert_called_with("The ghost cannot cross into the ring.")

        ghost.delete()
        ring_exit.delete()
        courtyard.delete()
        room.delete()

    def test_player_can_enter_broken_shore_ring(self):
        from typeclasses.exits import Exit
        from typeclasses.pvp_rooms import BrokenShoreRingRoom

        courtyard = create_object("typeclasses.rooms.Room", key="Courtyard")
        room = create_object(BrokenShoreRingRoom, key="Broken Shore Test Room")
        ring_exit = create_object(
            Exit, key="ring", location=courtyard, destination=room
        )

        ring_exit.at_traverse(self.char1, room)

        self.assertEqual(self.char1.location, room)

        ring_exit.delete()
        courtyard.delete()
        room.delete()
