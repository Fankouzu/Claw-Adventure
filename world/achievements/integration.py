"""
Bridge between Evennia typeclasses and the achievement engine.

Combat credit uses an ndb flag on the defeated mob so loot and HP hooks
do not double-log.
"""

from evennia.utils.utils import inherits_from


def agent_for_character(character):
    """Resolve Django Agent for an Evennia puppet character."""
    if not character or not getattr(character, "account", None):
        return None
    from world.agent_auth.models import Agent

    try:
        return Agent.objects.get(evennia_account=character.account)
    except Agent.DoesNotExist:
        return None


def record_combat_victory_for_defeat(attacker, defeated_enemy):
    """
    Log a combat victory and run combat achievement checks.

    Args:
        attacker: Living entity that defeated the enemy (expected PC).
        defeated_enemy: Defeated EvAdventureMob (or subclass).

    Returns:
        list: Newly unlocked Achievement instances.
    """
    if getattr(defeated_enemy.ndb, "claw_combat_achievement_logged", False):
        return []
    if not getattr(attacker, "is_pc", False):
        return []

    from evennia.contrib.tutorials.evadventure.npcs import EvAdventureMob

    if not inherits_from(defeated_enemy, EvAdventureMob):
        return []
    if getattr(defeated_enemy, "hp", 1) > 0:
        return []

    agent = agent_for_character(attacker)
    if not agent:
        return []

    defeated_enemy.ndb.claw_combat_achievement_logged = True

    raw_key = (
        getattr(defeated_enemy, "db_key", None) or defeated_enemy.key or ""
    ).lower()
    # Long display keys still map to combat achievement id 'ghost'
    enemy_key = "ghost" if "ghost" in raw_key else (raw_key or "unknown")
    enemy_name = defeated_enemy.key

    from world.achievements.engine import AchievementEngine

    return AchievementEngine.check_combat(
        agent,
        enemy_key,
        enemy_name,
        "victory",
        damage_dealt=0,
        damage_taken=0,
    )


def record_tutorial_mob_kill(attacker, mob):
    """
    Log combat achievements when tutorial_world.mob.Mob dies (EvAdventure-style
    loot hooks do not run for this typeclass).
    """
    if not getattr(attacker, "is_pc", False):
        return []
    agent = agent_for_character(attacker)
    if not agent:
        return []

    raw = (getattr(mob, "db_key", None) or mob.key or "").lower()
    ghostish = "ghost" in raw
    enemy_key = "ghost" if ghostish else (raw or "unknown")
    enemy_name = mob.key

    from world.achievements.engine import AchievementEngine

    return AchievementEngine.check_combat(
        agent,
        enemy_key,
        enemy_name,
        "victory",
        damage_dealt=0,
        damage_taken=0,
    )


def send_achievement_unlock_messages(character, achievements):
    """
    Emit standard in-game lines for newly unlocked achievements.

    All player-visible copy is English (name/description come from DB).
    """
    if not character or not achievements:
        return
    for ach in achievements:
        character.msg(f"|gAchievement unlocked: {ach.name}|n")
        character.msg(f"|g{ach.description}|n")
