"""
Copy EvAdventure Character stats onto Agent columns for Prisma / web reads.

Game process is the only writer; values are pickled on ObjectDB but not on agent_auth_agents.
"""
from __future__ import annotations

import logging
from uuid import UUID

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


def _resolve_agent_for_character(character, agent=None):
    """
    Find Django Agent row for this Character.

    When the character is not the active puppet, ``character.account`` is often None, so
    ``_get_agent()`` fails. Fall back to ``character.db.claw_agent_id`` (set at connect).
    """
    from world.agent_auth.models import Agent

    if agent is not None:
        return agent

    getter = getattr(character, "_get_agent", None)
    if callable(getter):
        try:
            found = getter()
            if found is not None:
                return found
        except Exception:
            logger.exception("in_world sync: _get_agent failed for %s", character)

    aid = getattr(character.db, "claw_agent_id", None)
    if not aid:
        return None
    try:
        return Agent.objects.get(id=UUID(str(aid)))
    except (ValueError, TypeError, Agent.DoesNotExist):
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


def sync_in_world_snapshot_from_character(character, agent=None) -> bool:
    """
    Update the Django Agent row from a live Character typeclass instance.

    Pass ``agent`` when known (e.g. agent_connect, management command) so sync works even
    when the character is not currently puppeted (``character.account`` is None).

    Returns:
        True if the Agent row was saved; False if skipped or on error.
    """
    if character is None:
        return False

    resolved = _resolve_agent_for_character(character, agent=agent)
    if resolved is None:
        logger.warning(
            "in_world sync: no agent for character %r",
            getattr(character, "key", "?"),
        )
        return False

    try:
        xp_per_level = int(getattr(character, "xp_per_level", 1000))
        # Agent.in_world_character_key is CharField(max_length=255); stay within DB limit.
        ck = character.key or ""
        if len(ck) > 255:
            ck = ck[:255]
        resolved.in_world_character_key = ck
        resolved.in_world_hp = int(character.hp)
        resolved.in_world_hp_max = int(character.hp_max)
        resolved.in_world_level = int(character.level)
        resolved.in_world_xp = int(character.xp)
        resolved.in_world_xp_per_level = xp_per_level
        resolved.in_world_coins = int(character.coins)
        resolved.in_world_strength = int(character.strength)
        resolved.in_world_dexterity = int(character.dexterity)
        resolved.in_world_constitution = int(character.constitution)
        resolved.in_world_intelligence = int(character.intelligence)
        resolved.in_world_wisdom = int(character.wisdom)
        resolved.in_world_charisma = int(character.charisma)
        resolved.in_world_synced_at = timezone.now()
        resolved.save(update_fields=_IN_WORLD_UPDATE_FIELDS)
        return True
    except Exception:
        logger.exception(
            "in_world sync failed agent=%s character=%s",
            getattr(resolved, "name", "?"),
            getattr(character, "key", "?"),
        )
        return False
