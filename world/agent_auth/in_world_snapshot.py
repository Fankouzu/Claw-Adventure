"""
Public JSON for GET .../in-world: read mirrored EvAdventure stats from Agent columns.

Live Character data is copied into agent_auth_agents by world.agent_auth.in_world_sync
(typeclasses.characters hooks). Node/Prisma reads the same columns without pickle or HTTP to self.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)


def slug_character_key(name: str, agent_id) -> str:
    """Same rules as commands.agent_commands (character object key slug)."""
    s = re.sub(r"[^a-zA-Z0-9_-]", "_", (name or "").strip())
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        compact = str(agent_id).replace("-", "")
        s = f"A_{compact[:12]}"
    return s[:60]


def _in_world_dict_from_agent(agent) -> Dict[str, Any]:
    xp_per_level = int(agent.in_world_xp_per_level or 1000)
    lvl = int(agent.in_world_level)
    xp = int(agent.in_world_xp)
    next_level_xp = lvl * xp_per_level
    return {
        "character_key": agent.in_world_character_key or "",
        "hp": int(agent.in_world_hp),
        "hp_max": int(agent.in_world_hp_max),
        "level": lvl,
        "xp": xp,
        "xp_per_level": xp_per_level,
        "xp_to_next_level": max(0, next_level_xp - xp),
        "coins": int(agent.in_world_coins),
        "strength": int(agent.in_world_strength),
        "dexterity": int(agent.in_world_dexterity),
        "constitution": int(agent.in_world_constitution),
        "intelligence": int(agent.in_world_intelligence),
        "wisdom": int(agent.in_world_wisdom),
        "charisma": int(agent.in_world_charisma),
    }


def build_in_world_payload(agent) -> Dict[str, Any]:
    """Full JSON payload for GET .../in-world (database mirror only)."""
    payload: Dict[str, Any] = {
        "agent_id": str(agent.id),
        "name": agent.name,
        "in_world_status": "ok",
        "in_world": None,
        "in_world_synced_at": (
            agent.in_world_synced_at.isoformat() if agent.in_world_synced_at else None
        ),
    }

    if not agent.is_claimed:
        payload["in_world_status"] = "not_claimed"
        return payload

    if not agent.evennia_account_id:
        payload["in_world_status"] = "no_evennia_account"
        return payload

    if not agent.in_world_synced_at:
        payload["in_world_status"] = "no_sync_yet"
        return payload

    try:
        payload["in_world"] = _in_world_dict_from_agent(agent)
    except Exception:
        logger.exception("in_world dict build failed for agent %s", agent.name)
        payload["in_world_status"] = "serialize_error"
    return payload
