"""
Idempotent creation of rooms, objects, and exits from ``definitions.py``.
"""

from __future__ import annotations

import logging
from typing import Any

from evennia.objects.models import ObjectDB
from evennia.utils import create as create_utils

from world.codeworld import definitions as defs

logger = logging.getLogger(__name__)


def _get_by_key(key: str) -> ObjectDB | None:
    if not key:
        return None
    return ObjectDB.objects.filter(db_key=key).first()


def _ensure_room(spec: dict[str, Any]) -> tuple[bool, str]:
    key = spec.get("key")
    if not key:
        return False, "room spec missing key"
    if _get_by_key(key):
        return False, f"room exists: {key}"
    typeclass = spec.get("typeclass") or defs.DEFAULT_ROOM_TYPECLASS
    aliases = spec.get("aliases")
    room = create_utils.create_object(
        typeclass,
        key=key,
        aliases=aliases if aliases else None,
        home=spec.get("home"),
    )
    desc = spec.get("desc")
    if desc is not None:
        room.db.desc = desc
    room.tags.add("claw_codeworld", category="world")
    logger.info("codeworld: created room %s", key)
    return True, key


def _ensure_thing(spec: dict[str, Any]) -> tuple[bool, str]:
    key = spec.get("key")
    loc_key = spec.get("location_key")
    if not key or not loc_key:
        return False, "thing spec missing key or location_key"
    if _get_by_key(key):
        return False, f"thing exists: {key}"
    location = _get_by_key(loc_key)
    if not location:
        logger.warning(
            "codeworld: skip thing %r — location %r not found", key, loc_key
        )
        return False, f"skip missing location: {key}"
    typeclass = spec.get("typeclass") or defs.DEFAULT_OBJECT_TYPECLASS
    aliases = spec.get("aliases")
    obj = create_utils.create_object(
        typeclass,
        key=key,
        location=location,
        home=spec.get("home") or location,
        aliases=aliases if aliases else None,
    )
    desc = spec.get("desc")
    if desc is not None:
        obj.db.desc = desc
    obj.tags.add("claw_codeworld", category="world")
    logger.info("codeworld: created object %s in %s", key, loc_key)
    return True, key


def _ensure_exit(spec: dict[str, Any]) -> tuple[bool, str]:
    key = spec.get("key")
    loc_key = spec.get("location_key")
    dest_key = spec.get("destination_key")
    if not key or not loc_key or not dest_key:
        return False, "exit spec missing key, location_key, or destination_key"
    if _get_by_key(key):
        return False, f"exit exists: {key}"
    location = _get_by_key(loc_key)
    destination = _get_by_key(dest_key)
    if not location or not destination:
        logger.warning(
            "codeworld: skip exit %r — location=%r or dest=%r missing",
            key,
            loc_key,
            dest_key,
        )
        return False, f"skip exit (missing endpoint): {key}"
    typeclass = spec.get("typeclass") or defs.DEFAULT_EXIT_TYPECLASS
    aliases = spec.get("aliases")
    # Evennia exits: pass destination at creation.
    exi = create_utils.create_object(
        typeclass,
        key=key,
        location=location,
        destination=destination,
        aliases=aliases if aliases else None,
    )
    exi.tags.add("claw_codeworld", category="world")
    logger.info(
        "codeworld: created exit %s from %s -> %s", key, loc_key, dest_key
    )
    return True, key


def run_sync() -> tuple[int, int, list[str]]:
    """
    Apply CODED_ROOMS, CODED_THINGS, CODED_EXITS in order.

    Returns:
        (created_count, skipped_or_deferred_count, messages)
    """
    created = 0
    skipped = 0
    messages: list[str] = []

    for spec in defs.CODED_ROOMS:
        ok, msg = _ensure_room(spec)
        if ok:
            created += 1
            messages.append(f"+ room {msg}")
        else:
            skipped += 1
            messages.append(f"- room {msg}")

    for spec in defs.CODED_THINGS:
        ok, msg = _ensure_thing(spec)
        if ok:
            created += 1
            messages.append(f"+ thing {msg}")
        else:
            skipped += 1
            messages.append(f"- thing {msg}")

    for spec in defs.CODED_EXITS:
        ok, msg = _ensure_exit(spec)
        if ok:
            created += 1
            messages.append(f"+ exit {msg}")
        else:
            skipped += 1
            messages.append(f"- exit {msg}")

    return created, skipped, messages
