"""
Copy EvAdventure Character stats onto Agent columns for Prisma / public HTTP reads.

Game process is the only writer; values are pickled on ObjectDB but not on agent_auth_agents.
"""
from __future__ import annotations

import logging

from django.utils import timezone

logger = logging.getLogger(__name__)


def get_bound_character_for_agent(agent):
    """
    Resolve the EvAdventure Character for this Agent (no creation).

    Same binding rules as agent_connect: claw_agent_id, then slug key, then sole character.
    """
    if not getattr(agent, "is_claimed", False) or not agent.evennia_account_id:
        return None
    account = agent.evennia_account
    agent_id_str = str(agent.id)
    chars = list(account.characters.all())
    for char in chars:
        if getattr(char.db, "claw_agent_id", None) == agent_id_str:
            return char
    from world.agent_auth.in_world_snapshot import slug_character_key

    want_key = slug_character_key(agent.name, agent.id)
    for char in chars:
        if char.key == want_key:
            return char
    if len(chars) == 1:
        return chars[0]
    return None


_IN_WORLD_UPDATE_FIELDS = (
    "in_world_character_key",
    "in_world_hp",
    "in_world_hp_max",
    "in_world_level",
    "in_world_xp",
    "in_world_xp_per_level",
    "in_world_coins",
    "in_world_strength",
    "in_world_dexterity",
    "in_world_constitution",
    "in_world_intelligence",
    "in_world_wisdom",
    "in_world_charisma",
    "in_world_synced_at",
)


def sync_in_world_snapshot_from_character(character) -> None:
    """
    Update the Django Agent row from a live Character typeclass instance.

    No-op if the puppet has no bound Agent (e.g. human account).
    """
    if character is None:
        return
    getter = getattr(character, "_get_agent", None)
    if not callable(getter):
        return
    try:
        agent = getter()
    except Exception:
        logger.exception("in_world sync: _get_agent failed for %s", character)
        return
    if agent is None:
        return

    try:
        xp_per_level = int(getattr(character, "xp_per_level", 1000))
        agent.in_world_character_key = character.key or ""
        agent.in_world_hp = int(character.hp)
        agent.in_world_hp_max = int(character.hp_max)
        agent.in_world_level = int(character.level)
        agent.in_world_xp = int(character.xp)
        agent.in_world_xp_per_level = xp_per_level
        agent.in_world_coins = int(character.coins)
        agent.in_world_strength = int(character.strength)
        agent.in_world_dexterity = int(character.dexterity)
        agent.in_world_constitution = int(character.constitution)
        agent.in_world_intelligence = int(character.intelligence)
        agent.in_world_wisdom = int(character.wisdom)
        agent.in_world_charisma = int(character.charisma)
        agent.in_world_synced_at = timezone.now()
        agent.save(update_fields=_IN_WORLD_UPDATE_FIELDS)
    except Exception:
        logger.exception(
            "in_world sync failed agent=%s character=%s",
            getattr(agent, "name", "?"),
            getattr(character, "key", "?"),
        )
