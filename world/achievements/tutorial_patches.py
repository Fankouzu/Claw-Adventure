"""
Patch Evennia tutorial_world in-process so achievements unlock without forking.

Loaded from server/conf/at_server_startstop.py (at_server_start).
"""

from __future__ import annotations

import time

from evennia.utils import logger

_INSTALLED = False


def _notify_climb(caller):
    from world.achievements.engine import AchievementEngine
    from world.achievements.integration import agent_for_character

    agent = agent_for_character(caller)
    if not agent:
        return
    unlocked = []
    unlocked.extend(
        AchievementEngine.apply_context_unlock(
            agent, room_key="tut#02", action="climb_tree"
        )
    )
    unlocked.extend(
        AchievementEngine.apply_context_unlock(agent, type="find_secret")
    )
    for ach in unlocked:
        caller.msg(f"|g成就解锁: {ach.name}|n")
        caller.msg(f"|g{ach.description}|n")


def _notify_crumbling_wall(caller):
    from world.achievements.engine import AchievementEngine
    from world.achievements.integration import agent_for_character

    agent = agent_for_character(caller)
    if not agent:
        return
    unlocked = AchievementEngine.apply_context_unlock(
        agent, room_key="tut#12", puzzle="broken_wall"
    )
    for ach in unlocked:
        caller.msg(f"|g成就解锁: {ach.name}|n")
        caller.msg(f"|g{ach.description}|n")


def install_tutorial_achievement_hooks() -> None:
    """
    Patch tutorial_world classes once per process (idempotent).
    """
    global _INSTALLED
    if _INSTALLED:
        return

    try:
        from evennia.contrib.tutorials.tutorial_world import (
            objects as tw_objects,
        )
        from evennia.contrib.tutorials.tutorial_world.mob import Mob
        from evennia.contrib.tutorials.tutorial_world.rooms import (
            IntroRoom,
        )
    except ImportError as exc:
        logger.log_warn(
            f"world/achievements: tutorial_world not available ({exc}); "
            "skipping tutorial achievement hooks."
        )
        return

    # --- Intro: start timer for speedrun (monotonic seconds) ---
    _orig_intro_receive = IntroRoom.at_object_receive

    def _patched_intro_receive(
        self, character, source_location, move_type="move", **kwargs
    ):
        _orig_intro_receive(
            self, character, source_location, move_type=move_type, **kwargs
        )
        if character.has_account and not getattr(
            character.ndb, "batch_batchmode", None
        ):
            character.db.claw_tutorial_run_started_at = time.monotonic()

    IntroRoom.at_object_receive = _patched_intro_receive

    # --- Climb tree: cliff_explorer + secret_finder ---
    _orig_climb_func = tw_objects.CmdClimb.func

    def _patched_climb_func(self):
        caller = self.caller
        had = caller.tags.has(
            "tutorial_climbed_tree", category="tutorial_world"
        )
        _orig_climb_func(self)
        now = caller.tags.has(
            "tutorial_climbed_tree", category="tutorial_world"
        )
        if now and not had:
            _notify_climb(caller)

    tw_objects.CmdClimb.func = _patched_climb_func

    # --- Crumbling wall: puzzle_solver ---
    _orig_press_func = tw_objects.CmdPressButton.func

    def _patched_press_func(self):
        was_open = bool(getattr(self.obj.db, "exit_open", False))
        _orig_press_func(self)
        if self.obj.db.exit_open and not was_open:
            _notify_crumbling_wall(self.caller)

    tw_objects.CmdPressButton.func = _patched_press_func

    # --- Tutorial Mob (ghost): combat_log + combat achievements ---
    _orig_mob_set_alive = Mob.set_alive

    def _patched_mob_set_alive(self, *args, **kwargs):
        self.ndb.claw_tutorial_kill_logged = False
        return _orig_mob_set_alive(self, *args, **kwargs)

    Mob.set_alive = _patched_mob_set_alive

    _orig_mob_at_hit = Mob.at_hit

    def _patched_mob_at_hit(self, weapon, attacker, damage):
        _orig_mob_at_hit(self, weapon, attacker, damage)
        if not self.db.is_dead or not attacker or not attacker.has_account:
            return
        if getattr(self.ndb, "claw_tutorial_kill_logged", False):
            return
        self.ndb.claw_tutorial_kill_logged = True
        from world.achievements.integration import record_tutorial_mob_kill

        unlocked = record_tutorial_mob_kill(attacker, self)
        for ach in unlocked:
            attacker.msg(f"|g成就解锁: {ach.name}|n")
            attacker.msg(f"|g{ach.description}|n")

    Mob.at_hit = _patched_mob_at_hit

    _INSTALLED = True
    logger.log_info(
        "world/achievements: tutorial_world achievement hooks installed."
    )
