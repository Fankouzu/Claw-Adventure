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
    # Example (uncomment to create on next deploy):
    # {
    #     "key": "Claw / Example Chamber",
    #     "aliases": ["example chamber", "claw example"],
    #     "desc": "A placeholder room created from Git. Replace with real content.",
    # },
]

# Objects placed inside a room identified by ``location_key`` (must match an existing
# or newly created room key in CODED_ROOMS order — rooms are synced first).
DEFAULT_OBJECT_TYPECLASS = "typeclasses.objects.Object"

CODED_THINGS: list[dict] = [
    # {
    #     "key": "Claw / Example Crate",
    #     "location_key": "Claw / Example Chamber",
    #     "desc": "A wooden crate.",
    # },
]

# Exits: ``location_key`` = room containing the exit; ``destination_key`` = target room key.
DEFAULT_EXIT_TYPECLASS = "typeclasses.exits.Exit"

CODED_EXITS: list[dict] = [
    # {
    #     "key": "out",
    #     "aliases": ["leave", "o"],
    #     "location_key": "Claw / Example Chamber",
    #     "destination_key": "Limbo",
    # },
]
