from django.test import SimpleTestCase

from world.codeworld import definitions as defs


class BrokenShoreRingDefinitionsTest(SimpleTestCase):
    def test_broken_shore_ring_room_exists(self):
        self.assertTrue(
            any(
                room["key"] == "Claw / The Broken Shore Ring"
                for room in defs.CODED_ROOMS
            )
        )

    def test_broken_shore_ring_exit_exists(self):
        self.assertTrue(
            any(
                exit_["location_key"] == "Claw / The Broken Shore Ring"
                for exit_ in defs.CODED_EXITS
            )
        )

    def test_broken_shore_ring_has_safe_entry_point(self):
        self.assertTrue(
            any(
                exit_["destination_key"] == "Claw / The Broken Shore Ring"
                for exit_ in defs.CODED_EXITS
            )
        )

    def test_broken_shore_ring_uses_production_safe_room_target(self):
        safe_targets = {
            exit_["destination_key"]
            for exit_ in defs.CODED_EXITS
            if exit_["location_key"] == "Claw / The Broken Shore Ring"
        }
        self.assertIn("Overgrown courtyard", safe_targets)
