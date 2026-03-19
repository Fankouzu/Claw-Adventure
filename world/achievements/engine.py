"""
Achievement check and unlock engine.

This module provides the core logic for checking and unlocking achievements.
"""

from django.db import transaction


class AchievementEngine:
    """
    Achievement check and unlock engine.

    Provides static methods for checking exploration and combat achievements.
    """

    @staticmethod
    def check_exploration(agent, room_key, room_name):
        """
        Check exploration achievements when character moves to a new room.

        Args:
            agent: The Agent object
            room_key: Room identifier (e.g. 'tut#02')
            room_name: Room display name

        Returns:
            list: List of newly unlocked Achievement objects
        """
        from .models import ExplorationProgress, Achievement, UserAchievement

        unlocked = []

        # 1. Record exploration progress
        progress, created = ExplorationProgress.objects.get_or_create(
            agent=agent,
            room_key=room_key,
            defaults={'room_name': room_name}
        )

        if not created:
            return []  # Already visited, skip duplicate checks

        # 2. Check achievements that require visiting this room
        achievements = Achievement.objects.filter(
            category__in=['exploration', 'puzzle', 'story'],
            requirement__room_key=room_key
        )

        for ach in achievements:
            # Check if already unlocked
            if UserAchievement.objects.filter(agent=agent, achievement=ach).exists():
                continue

            # Unlock the achievement
            UserAchievement.objects.create(agent=agent, achievement=ach)
            unlocked.append(ach)

        # 3. Check cumulative achievements (e.g. visited all rooms)
        total_visited = ExplorationProgress.objects.filter(agent=agent).count()
        if total_visited >= 16:
            master_ach = AchievementEngine._unlock_achievement(agent, 'explorer_master')
            if master_ach:
                unlocked.append(master_ach)

        return unlocked

    @staticmethod
    def check_combat(agent, enemy_key, enemy_name, result, damage_dealt=0, damage_taken=0):
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
        from .models import CombatLog, Achievement, UserAchievement

        unlocked = []

        # 1. Log combat result
        CombatLog.objects.create(
            agent=agent,
            enemy_key=enemy_key,
            enemy_name=enemy_name,
            result=result,
            damage_dealt=damage_dealt,
            damage_taken=damage_taken
        )

        if result != 'victory':
            return []  # Only victories unlock achievements

        # 2. Check combat achievements
        total_kills = CombatLog.objects.filter(agent=agent, result='victory').count()

        # First blood - first kill
        if total_kills == 1:
            ach = AchievementEngine._unlock_achievement(agent, 'first_blood')
            if ach:
                unlocked.append(ach)

        # Ghost slayer - defeat ghost once
        enemy_kills = CombatLog.objects.filter(
            agent=agent,
            result='victory',
            enemy_key=enemy_key
        ).count()

        if enemy_key == 'ghost':
            if enemy_kills >= 1:
                ach = AchievementEngine._unlock_achievement(agent, 'ghost_slayer')
                if ach:
                    unlocked.append(ach)

            # Ghostbane - defeat ghost 3 times
            if enemy_kills >= 3:
                ach = AchievementEngine._unlock_achievement(agent, 'ghostbane')
                if ach:
                    unlocked.append(ach)

        # Monster hunter - defeat 10 enemies
        if total_kills >= 10:
            ach = AchievementEngine._unlock_achievement(agent, 'monster_hunter')
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
            Achievement or None: The unlocked achievement, or None if not found/already unlocked
        """
        from .models import Achievement, UserAchievement

        try:
            ach = Achievement.objects.get(key=achievement_key)
            _, created = UserAchievement.objects.get_or_create(
                agent=agent,
                achievement=ach
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
        from .models import UserAchievement
        return UserAchievement.objects.filter(agent=agent).select_related('achievement')

    @staticmethod
    def get_agent_progress(agent):
        """
        Get exploration progress for an agent.

        Args:
            agent: The Agent object

        Returns:
            dict: Statistics about agent's progress
        """
        from .models import ExplorationProgress, UserAchievement

        visited_rooms = ExplorationProgress.objects.filter(agent=agent).count()
        unlocked_count = UserAchievement.objects.filter(agent=agent).count()
        total_points = sum(
            ua.achievement.points for ua in UserAchievement.objects.filter(agent=agent).select_related('achievement')
        )

        return {
            'rooms_visited': visited_rooms,
            'achievements_unlocked': unlocked_count,
            'total_points': total_points,
        }