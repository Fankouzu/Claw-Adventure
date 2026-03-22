"""
Resolve an Agent's puppet EvAdventure character and serialize in-world stats.

Source of truth for combat progression is the Character object (EvAdventure),
not the Agent row's level/experience (HTTP-side profile).
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, Tuple

logger = logging.getLogger(__name__)


def slug_character_key(name: str, agent_id) -> str:
    """Same rules as commands.agent_commands.CmdAgentConnect._slug_character_key."""
    s = re.sub(r"[^a-zA-Z0-9_-]", "_", (name or "").strip())
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        compact = str(agent_id).replace("-", "")
        s = f"A_{compact[:12]}"
    return s[:60]


def _get_character_for_agent(agent) -> Tuple[Optional[Any], str]:
    """
    Return (character, status) where status explains a missing character.

    Mirrors binding logic in commands.agent_commands.CmdAgentConnect._get_or_create_agent_character.
    """
    if not agent.is_claimed:
        return None, "not_claimed"

    if not agent.evennia_account_id:
        return None, "no_evennia_account"

    account = agent.evennia_account
    agent_id_str = str(agent.id)
    chars = list(account.characters.all())

    for char in chars:
        if getattr(char.db, "claw_agent_id", None) == agent_id_str:
            return char, "ok"

    want_key = slug_character_key(agent.name, agent.id)
    for char in chars:
        if char.key == want_key:
            return char, "ok"

    if len(chars) == 1:
        return chars[0], "ok"

    return None, "no_character"


def serialize_evadventure_character(character) -> Dict[str, Any]:
    """Pull EvAdventure AttributeProperty fields from a live typeclass instance."""
    xp_per_level = getattr(character, "xp_per_level", 1000)
    next_level_xp = character.level * xp_per_level
    return {
        "character_key": character.key,
        "hp": character.hp,
        "hp_max": character.hp_max,
        "level": character.level,
        "xp": character.xp,
        "xp_per_level": xp_per_level,
        "xp_to_next_level": max(0, next_level_xp - character.xp),
        "coins": character.coins,
        "strength": character.strength,
        "dexterity": character.dexterity,
        "constitution": character.constitution,
        "intelligence": character.intelligence,
        "wisdom": character.wisdom,
        "charisma": character.charisma,
    }


def build_in_world_payload(agent) -> Dict[str, Any]:
    """Full JSON payload for GET .../in-world."""
    char, status = _get_character_for_agent(agent)
    payload: Dict[str, Any] = {
        "agent_id": str(agent.id),
        "name": agent.name,
        "in_world_status": status,
        "in_world": None,
    }
    if char is None:
        return payload
    try:
        payload["in_world"] = serialize_evadventure_character(char)
    except Exception:
        logger.exception("serialize_evadventure_character failed for agent %s", agent.name)
        payload["in_world_status"] = "serialize_error"
    return payload
