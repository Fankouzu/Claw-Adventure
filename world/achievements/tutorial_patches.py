"""
Patch Evennia tutorial_world in-process so achievements unlock without forking.

Loaded from server/conf/at_server_startstop.py (at_server_start).
"""

from __future__ import annotations

import random
import time

from evennia.utils import logger

from world.achievements.integration import send_achievement_unlock_messages

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
    send_achievement_unlock_messages(caller, unlocked)


def _notify_crumbling_wall(caller):
    from world.achievements.engine import AchievementEngine
    from world.achievements.integration import agent_for_character

    agent = agent_for_character(caller)
    if not agent:
        return
    unlocked = AchievementEngine.apply_context_unlock(
        agent, room_key="tut#12", puzzle="broken_wall"
    )
    send_achievement_unlock_messages(caller, unlocked)


def install_tutorial_achievement_hooks() -> None:
    """
    Patch tutorial_world classes once per process (idempotent).
    """
    global _INSTALLED
    if _INSTALLED:
        return

    try:
        from evennia import search_object
        from evennia.contrib.tutorials.tutorial_world import (
            objects as tw_objects,
            rooms as tw_rooms,
        )
        from evennia.contrib.tutorials.tutorial_world.mob import Mob

        IntroRoom = tw_rooms.IntroRoom
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

    # --- Bridge look: include {"type": "look"} for WebSocket JSON clients ---
    def _patched_cmd_look_bridge_func(self):
        caller = self.caller
        bridge_position = caller.db.tutorial_bridge_position
        location = self.obj
        message = "|c%s|n\n%s\n%s" % (
            location.key,
            tw_rooms.BRIDGE_POS_MESSAGES[bridge_position],
            random.choice(tw_rooms.BRIDGE_MOODS),
        )
        chars = [
            obj
            for obj in self.obj.contents_get(exclude=caller)
            if obj.has_account
        ]
        if chars:
            message += "\n You see: %s" % ", ".join(
                "|c%s|n" % char.key for char in chars
            )
        caller.msg(text=(message, {"type": "look"}), options=None)

        if bridge_position < 3 and random.random() < 0.05 and not caller.is_superuser:
            fall_exit = search_object(self.obj.db.fall_exit)
            if fall_exit:
                caller.msg("|r%s|n" % tw_rooms.FALL_MESSAGE)
                caller.move_to(fall_exit[0], quiet=True, move_type="fall")
                self.obj.msg_contents(
                    "A plank gives way under %s's feet and "
                    "they fall from the bridge!" % caller.key
                )

    tw_rooms.CmdLookBridge.func = _patched_cmd_look_bridge_func

    # --- Tutorial look / dark-look: JSON clients expect {"type": "look"} (EvAdventure #3278 parity) ---
    _search_at_result = tw_rooms._SEARCH_AT_RESULT

    def _patched_cmd_tutorial_look_func(self):
        caller = self.caller
        args = self.args
        if args:
            looking_at_obj = caller.search(
                args,
                candidates=caller.location.contents + caller.contents,
                use_nicks=True,
                quiet=True,
            )
            if len(looking_at_obj) != 1:
                detail = self.obj.return_detail(args)
                if detail:
                    caller.msg(text=(detail, {"type": "look"}), options=None)
                    return
                _search_at_result(looking_at_obj, caller, args)
                return
            looking_at_obj = looking_at_obj[0]
        else:
            looking_at_obj = caller.location
            if not looking_at_obj:
                caller.msg("You have no location to look at!")
                return

        if not hasattr(looking_at_obj, "return_appearance"):
            looking_at_obj = looking_at_obj.character
        if not looking_at_obj.access(caller, "view"):
            caller.msg("Could not find '%s'." % args)
            return
        caller.msg(
            text=(looking_at_obj.return_appearance(caller), {"type": "look"}),
            options=None,
        )
        looking_at_obj.at_desc(looker=caller)

    tw_rooms.CmdTutorialLook.func = _patched_cmd_tutorial_look_func

    from evennia import create_object, utils as evennia_utils
    from evennia.contrib.tutorials.tutorial_world.objects import LightSource

    def _patched_cmd_look_dark_func(self):
        caller = self.caller
        nr_searches = caller.ndb.dark_searches
        if nr_searches is None:
            nr_searches = 0
            caller.ndb.dark_searches = nr_searches

        if nr_searches < 4 and random.random() < 0.90:
            caller.msg(
                text=(random.choice(tw_rooms.DARK_MESSAGES), {"type": "look"}),
                options=None,
            )
            caller.ndb.dark_searches += 1
        else:
            if any(
                obj
                for obj in caller.contents
                if evennia_utils.inherits_from(obj, LightSource)
            ):
                caller.msg(
                    text=(tw_rooms.ALREADY_LIGHTSOURCE, {"type": "look"}),
                    options=None,
                )
            else:
                create_object(LightSource, key="splinter", location=caller)
                caller.msg(
                    text=(tw_rooms.FOUND_LIGHTSOURCE, {"type": "look"}),
                    options=None,
                )

    tw_rooms.CmdLookDark.func = _patched_cmd_look_dark_func

    # --- EvAdventure twitch CmdLook: room line has type from default; append combat table typed ---
    from evennia import default_cmds
    from evennia.contrib.tutorials.evadventure import combat_twitch as ev_combat_twitch
    from evennia.utils.utils import display_len, pad

    def _patched_ev_twitch_cmd_look_func(self):
        default_cmds.CmdLook.func(self)
        if not self.args:
            combathandler = self.get_or_create_combathandler()
            txt = str(combathandler.get_combat_summary(self.caller))
            maxwidth = max(display_len(line) for line in txt.strip().split("\n"))
            body = (
                f"|r{pad(' Combat Status ', width=maxwidth, fillchar='-')}|n\n{txt}"
            )
            self.msg(text=(body, {"type": "combat_status"}), options=None)

    ev_combat_twitch.CmdLook.func = _patched_ev_twitch_cmd_look_func

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
        send_achievement_unlock_messages(attacker, unlocked)

    Mob.at_hit = _patched_mob_at_hit

    _INSTALLED = True
    logger.log_info(
        "world/achievements: tutorial_world hooks installed "
        "(achievements + look type=look / combat_status patches)."
    )
