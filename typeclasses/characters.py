"""
Characters

This is the customized Character class for the Claw Adventure universe.
"""

import logging
import time

from evennia.contrib.tutorials.evadventure.characters import (
    EvAdventureCharacter,
)
from evennia.contrib.tutorials.evadventure.combat_twitch import (
    TwitchCombatCmdSet,
)

from world.achievements.integration import send_achievement_unlock_messages

logger = logging.getLogger(__name__)


class Character(EvAdventureCharacter):
    """
    Claw Character: EvAdventure stats/combat, without forced drop-on-login.
    Players stay at Limbo, last location, or DEFAULT_HOME as configured.
    """

    def at_object_creation(self):
        super().at_object_creation()
        # Keep twitch combat cmdset for EvAdventure-style fights.
        self.cmdset.add(TwitchCombatCmdSet, persistent=True)

    # Forced air-drop on puppet was removed; login uses normal home/location.

    def at_pre_puppet(self, account=None, **kwargs):
        """
        Before puppet: if db location/home points to a deleted room (e.g. tutorial
        rebuild), move to DEFAULT_HOME so look/prompt does not error or confuse clients.
        """
        try:
            if self._rescue_stale_location_if_needed():
                self.ndb.claw_location_rescued = True
        except Exception:
            logger.exception("Stale location rescue failed for character %s", self.key)
        super().at_pre_puppet(account=account, **kwargs)

    def at_post_puppet(self, account=None, **kwargs):
        super().at_post_puppet(account=account, **kwargs)
        if getattr(self.ndb, "claw_location_rescued", False):
            self.msg(
                "|yYour previous room no longer exists; you were moved to a safe "
                "starting location.|n"
            )
            del self.ndb.claw_location_rescued

    def _fallback_start_room(self):
        """Resolve Limbo / DEFAULT_HOME / START_LOCATION for rescue moves."""
        from django.conf import settings
        from evennia import search_object
        from evennia.objects.models import ObjectDB

        for candidate in (
            getattr(settings, "DEFAULT_HOME", None),
            getattr(settings, "START_LOCATION", None),
        ):
            if candidate is None:
                continue
            if isinstance(candidate, int):
                try:
                    return ObjectDB.objects.get(id=candidate)
                except ObjectDB.DoesNotExist:
                    continue
            found = search_object(candidate)
            if found:
                return found[0]
        return None

    def _rescue_stale_location_if_needed(self):
        """
        Returns True if a rescue move was performed.
        """
        from evennia.objects.models import ObjectDB

        loc_id = self.db_location_id
        stale = False
        if loc_id is None:
            stale = True
        else:
            if not ObjectDB.objects.filter(id=loc_id).exists():
                stale = True

        home_id = self.db_home_id
        bad_home = (
            home_id is not None
            and not ObjectDB.objects.filter(id=home_id).exists()
        )

        if not stale and not bad_home:
            return False

        dest = self._fallback_start_room()
        if not dest:
            logger.error(
                "No fallback room (DEFAULT_HOME/START_LOCATION) for rescue; "
                "character=%s stale=%s bad_home=%s",
                self.key,
                stale,
                bad_home,
            )
            return False

        if bad_home:
            self.home = dest
        if stale:
            self.move_to(dest, quiet=True, use_destination=False)
        return True

    def at_post_move(self, source_location, **kwargs):
        """
        Hook called after character moves to a new location.
        Triggers exploration achievement checks.
        """
        super().at_post_move(source_location, **kwargs)

        if not self.location:
            return

        # Get associated Agent
        agent = self._get_agent()
        if not agent:
            return

        # Trigger exploration achievement check
        from world.achievements.engine import AchievementEngine

        # Use location's db_key if available, otherwise use key or id
        loc = self.location
        room_key = getattr(loc, "db_key", None) or loc.key or f"room_{loc.id}"
        room_name = self.location.key

        try:
            unlocked = AchievementEngine.check_exploration(
                agent, room_key, room_name
            )
        except Exception:
            logger.exception(
                "Achievement check_exploration failed (room_key=%r)", room_key
            )
            unlocked = []

        # Speedrun (must match achievements.requirement: type + minutes)
        started = getattr(self.db, "claw_tutorial_run_started_at", None)
        if room_key == "tut#16" and started is not None:
            try:
                if time.monotonic() - started <= 300:
                    unlocked.extend(
                        AchievementEngine.apply_context_unlock(
                            agent, type="speedrun", minutes=5
                        )
                    )
            except Exception:
                logger.exception("Achievement speedrun unlock failed")

        if unlocked:
            send_achievement_unlock_messages(self, unlocked)

    def at_do_loot(self, defeated_enemy):
        """
        EvAdventure: grant combat achievements when looting a defeated mob.
        """
        from world.achievements.integration import (
            record_combat_victory_for_defeat,
        )

        unlocked = record_combat_victory_for_defeat(self, defeated_enemy)
        super().at_do_loot(defeated_enemy)
        if unlocked:
            send_achievement_unlock_messages(self, unlocked)

    def _get_agent(self):
        """
        Get the Agent object associated with this character's account.

        Returns:
            Agent or None: The associated Agent object, or None if not found
        """
        if not self.account:
            return None

        from world.agent_auth.models import Agent
        try:
            return Agent.objects.get(evennia_account=self.account)
        except Agent.DoesNotExist:
            return None
