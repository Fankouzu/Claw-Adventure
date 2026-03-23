"""
Declarative world content shipped with the repository.

Workflow (same mental model as web migrations + deploy):
  1. Edit this file (or split imports into sibling modules).
  2. Commit and push; Railway runs ``evennia migrate`` then ``evennia sync_codeworld``.
  3. New objects appear in PostgreSQL idempotently (existing keys are skipped).

Naming: use a unique prefix for ``key`` (e.g. ``Claw / Room Name``) so you never
collide with Evennia tutorial objects or player-created keys.

This module must remain import-safe without Django setup (for linters); sync logic
lives in ``world.codeworld.sync``.
"""

# Rooms: ``location`` is always None at creation (standard Evennia room).
# Optional: aliases (list[str]), desc (str), typeclass (str, default below).
DEFAULT_ROOM_TYPECLASS = "typeclasses.rooms.Room"

CODED_ROOMS: list[dict] = [
    {
        "key": "Claw / The Broken Shore Ring",
        "aliases": ["broken shore ring", "shore ring", "ring"],
        "typeclass": "typeclasses.pvp_rooms.BrokenShoreRingRoom",
        "desc": (
            "You stand inside a broken ring of sea-black stone at the edge of the "
            "ruins. Salt wind drives through gaps in the outer wall, and below the "
            "cracks you can see gray surf striking the rocks. There are no banners, "
            "no crowd, and no judge here—only chipped pillars, old weapon marks, and "
            "enough clear ground for two travelers to test each other in plain sight.\n\n"
            "Notable features:\n"
            "- A circular stone platform with several collapsed outer gaps\n"
            "- Crooked ruin pillars and carved grooves marking the fighting ring\n"
            "- A single safe return path back toward the overgrown courtyard"
        ),
    },
]

# Objects placed inside a room identified by ``location_key`` (must match an existing
# or newly created room key in CODED_ROOMS order — rooms are synced first).
DEFAULT_OBJECT_TYPECLASS = "typeclasses.objects.Object"

CODED_THINGS: list[dict] = [
    {
        "key": "The Salt-Worn Sparring Effigy",
        "aliases": ["effigy", "sparring effigy", "dummy"],
        "location_key": "Claw / The Broken Shore Ring",
        "typeclass": "typeclasses.training_dummy.SaltWornSparringEffigy",
        "desc": (
            "A salt-worn effigy of rope, driftwood, and cracked armor plates stands "
            "waiting for blows. It has no voice, no anger, and no purpose beyond "
            "enduring practice inside the ring."
        ),
    },
]

# Exits: ``location_key`` = room containing the exit; ``destination_key`` = target room key.
DEFAULT_EXIT_TYPECLASS = "typeclasses.exits.Exit"

CODED_EXITS: list[dict] = [
    {
        "key": "ring",
        "aliases": ["broken shore ring", "arena"],
        "location_key": "Overgrown courtyard",
        "destination_key": "Claw / The Broken Shore Ring",
    },
    {
        "key": "west",
        "aliases": ["leave", "return", "w"],
        "location_key": "Claw / The Broken Shore Ring",
        "destination_key": "Overgrown courtyard",
    },
]
