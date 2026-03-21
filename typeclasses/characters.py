"""
Characters

This is the customized Character class for the Claw Adventure universe.
"""

import time

from evennia.contrib.tutorials.evadventure.characters import (
    EvAdventureCharacter,
)
from evennia.contrib.tutorials.evadventure.combat_twitch import (
    TwitchCombatCmdSet,
)


class Character(EvAdventureCharacter):
    """
    继承版躯壳：保留基础的属性和战斗模块，但移除强制空投逻辑。
    恢复玩家自由探索世界的权利。
    """

    def at_object_creation(self):
        super().at_object_creation()
        # 依然保留即时战斗指令集，以防未来用到
        self.cmdset.add(TwitchCombatCmdSet, persistent=True)

    # 【已清理】删除了 at_post_puppet 里的强制空投逻辑。
    # 现在角色登录后，将老老实实呆在系统默认的出生点（Limbo）或上次下线的位置。

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

        unlocked = AchievementEngine.check_exploration(
            agent, room_key, room_name
        )

        # Speedrun (must match achievements.requirement: type + minutes)
        started = getattr(self.db, "claw_tutorial_run_started_at", None)
        if room_key == "tut#16" and started is not None:
            if time.monotonic() - started <= 300:
                unlocked.extend(
                    AchievementEngine.apply_context_unlock(
                        agent, type="speedrun", minutes=5
                    )
                )

        # Notify player of unlocked achievements
        if unlocked:
            for ach in unlocked:
                self.msg(f"|g成就解锁: {ach.name}|n")
                self.msg(f"|g{ach.description}|n")

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
            for ach in unlocked:
                self.msg(f"|g成就解锁: {ach.name}|n")
                self.msg(f"|g{ach.description}|n")

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
