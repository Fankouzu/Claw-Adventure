"""
Achievement check and unlock engine.

This module provides the core logic for checking and unlocking achievements.
"""

from .models import Achievement, UserAchievement


# Room / narrative unlock categories (not combat-only definitions)
_CONTEXT_UNLOCK_CATEGORIES = ("exploration", "puzzle", "story")


class AchievementEngine:
    """
    Achievement check and unlock engine.

    Static methods for exploration, contextual, and combat achievements.
    """

    @staticmethod
    def _requirement_satisfied_by_context(requirement, context):
        """
        True if every key in requirement matches the same key in context.

        Extra keys (action, puzzle, …) must appear in context with the same
        values, so a plain room visit does not unlock gated achievements.
        """
        if not requirement:
            return False
        for key, val in requirement.items():
            if context.get(key) != val:
                return False
        return True

    @staticmethod
    def _explorer_master_threshold():
        """Rooms required for explorer_master; falls back to 16."""
        try:
            ach = Achievement.objects.get(key="explorer_master")
            return int((ach.requirement or {}).get("count", 16))
        except (Achievement.DoesNotExist, ValueError, TypeError):
            return 16

    @staticmethod
    def check_exploration(agent, room_key, room_name):
        """
        Check exploration achievements when character moves to a new room.

        Unlocks achievements whose requirement is fully matched by
        {room_key, room_name} (so entries that also require action/puzzle/etc.
        are not granted on entry alone).

        Args:
            agent: The Agent object
            room_key: Room identifier (e.g. 'tut#02')
            room_name: Room display name

        Returns:
            list: List of newly unlocked Achievement objects
        """
        from .models import ExplorationProgress

        unlocked = []

        progress, created = ExplorationProgress.objects.get_or_create(
            agent=agent,
            room_key=room_key,
            defaults={"room_name": room_name},
        )

        if not created:
            return []

        context = {"room_key": room_key, "room_name": room_name}

        achievements = Achievement.objects.filter(
            category__in=_CONTEXT_UNLOCK_CATEGORIES,
        )

        for ach in achievements:
            req = ach.requirement or {}
            if "room_key" not in req:
                continue
            if not AchievementEngine._requirement_satisfied_by_context(
                req, context
            ):
                continue
            if UserAchievement.objects.filter(
                agent=agent, achievement=ach
            ).exists():
                continue
            UserAchievement.objects.create(agent=agent, achievement=ach)
            unlocked.append(ach)

        total_visited = ExplorationProgress.objects.filter(agent=agent).count()
        need = AchievementEngine._explorer_master_threshold()
        if total_visited >= need:
            master_ach = AchievementEngine._unlock_achievement(
                agent, "explorer_master"
            )
            if master_ach:
                unlocked.append(master_ach)

        return unlocked

    @staticmethod
    def apply_context_unlock(agent, **context):
        """
        Unlock achievements fully matched by the given keyword context.

        Call from game code for puzzle, climb, secret, speedrun, etc. Only
        exploration / puzzle / story categories are scanned.

        Example::

            AchievementEngine.apply_context_unlock(
                agent, room_key="tut#12", puzzle="broken_wall"
            )

        Returns:
            list: Newly unlocked Achievement model instances
        """
        unlocked = []
        achievements = Achievement.objects.filter(
            category__in=_CONTEXT_UNLOCK_CATEGORIES
        )

        for ach in achievements:
            req = ach.requirement or {}
            if not req:
                continue
            if not AchievementEngine._requirement_satisfied_by_context(
                req, context
            ):
                continue
            if UserAchievement.objects.filter(
                agent=agent, achievement=ach
            ).exists():
                continue
            UserAchievement.objects.create(agent=agent, achievement=ach)
            unlocked.append(ach)

        return unlocked

    @staticmethod
    def check_combat(
        agent,
        enemy_key,
        enemy_name,
        result,
        damage_dealt=0,
        damage_taken=0,
    ):
        """
        Check combat achievements when combat ends.

        Args:
            agent: The Agent object
            enemy_key: Enemy identifier
            enemy_name: Enemy display name
            result: Combat result ('victory', 'defeat', 'flee')
            damage_dealt: Damage dealt to enemy
            damage_taken: Damage taken from enemy

        Returns:
            list: List of newly unlocked Achievement objects
        """
        from .models import CombatLog

        unlocked = []

        CombatLog.objects.create(
            agent=agent,
            enemy_key=enemy_key,
            enemy_name=enemy_name,
            result=result,
            damage_dealt=damage_dealt,
            damage_taken=damage_taken,
        )

        if result != "victory":
            return []

        total_kills = CombatLog.objects.filter(
            agent=agent, result="victory"
        ).count()

        if total_kills == 1:
            ach = AchievementEngine._unlock_achievement(agent, "first_blood")
            if ach:
                unlocked.append(ach)

        enemy_kills = CombatLog.objects.filter(
            agent=agent,
            result="victory",
            enemy_key=enemy_key,
        ).count()

        if enemy_key == "ghost":
            if enemy_kills >= 1:
                ach = AchievementEngine._unlock_achievement(
                    agent, "ghost_slayer"
                )
                if ach:
                    unlocked.append(ach)

            if enemy_kills >= 3:
                ach = AchievementEngine._unlock_achievement(
                    agent, "ghostbane"
                )
                if ach:
                    unlocked.append(ach)

        if total_kills >= 10:
            ach = AchievementEngine._unlock_achievement(
                agent, "monster_hunter"
            )
            if ach:
                unlocked.append(ach)

        return unlocked

    @staticmethod
    def _unlock_achievement(agent, achievement_key):
        """
        Unlock a specific achievement by key.

        Args:
            agent: The Agent object
            achievement_key: The Achievement's unique key

        Returns:
            Achievement instance if newly unlocked, else None.
        """
        try:
            ach = Achievement.objects.get(key=achievement_key)
            _, created = UserAchievement.objects.get_or_create(
                agent=agent,
                achievement=ach,
            )
            return ach if created else None
        except Achievement.DoesNotExist:
            return None

    @staticmethod
    def get_agent_achievements(agent):
        """
        Get all achievements unlocked by an agent.

        Args:
            agent: The Agent object

        Returns:
            QuerySet: UserAchievement objects for this agent
        """
        return UserAchievement.objects.filter(agent=agent).select_related(
            "achievement"
        )

    @staticmethod
    def get_agent_progress(agent):
        """
        Get exploration progress for an agent.

        Args:
            agent: The Agent object

        Returns:
            dict: Statistics about agent's progress
        """
        from .models import ExplorationProgress

        visited_rooms = ExplorationProgress.objects.filter(agent=agent).count()
        unlocked_count = UserAchievement.objects.filter(agent=agent).count()
        ua_qs = UserAchievement.objects.filter(agent=agent).select_related(
            "achievement"
        )
        total_points = sum(ua.achievement.points for ua in ua_qs)

        return {
            "rooms_visited": visited_rooms,
            "achievements_unlocked": unlocked_count,
            "total_points": total_points,
        }
