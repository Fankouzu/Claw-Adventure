"""
Achievement system data models.

This module defines:
- Achievement: Static achievement definitions
- UserAchievement: User's unlocked achievements
- ExplorationProgress: Room visit tracking
- CombatLog: Combat result logging (for future combat system)
"""

from django.db import models
import uuid


class Achievement(models.Model):
    """
    Achievement definition - static configuration, manageable via Admin.

    Stores the definition of each achievement including its unlock requirements.
    """

    CATEGORY_CHOICES = [
        ('exploration', 'Exploration'),  # Quest achievements - explore rooms
        ('puzzle', 'Puzzle'),            # Quest achievements - solve puzzles
        ('story', 'Story'),              # Quest achievements - story progress
        ('combat', 'Combat'),            # Combat achievements
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier"
    )

    key = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique key, e.g. 'first_steps'"
    )

    name = models.CharField(
        max_length=200,
        help_text="Display name"
    )

    description = models.TextField(
        help_text="Achievement description"
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="Achievement category"
    )

    points = models.IntegerField(
        default=10,
        help_text="Achievement points"
    )

    is_hidden = models.BooleanField(
        default=False,
        help_text="Hidden achievements are not shown until unlocked"
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Icon identifier for UI"
    )

    # Unlock condition (JSON configuration)
    # Example: {"type": "visit_room", "room_key": "tut#02"}
    # Example: {"type": "kill_mob", "mob_key": "ghost", "count": 1}
    requirement = models.JSONField(
        default=dict,
        help_text="JSON configuration for unlock condition"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'achievements'
        ordering = ['category', 'points']
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'

    def __str__(self):
        return f"{self.name} ({self.key})"


class UserAchievement(models.Model):
    """
    User's unlocked achievements.

    Records which achievements each agent has unlocked and when.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    agent = models.ForeignKey(
        'agent_auth.Agent',
        on_delete=models.CASCADE,
        related_name='unlocked_achievements',
        help_text="The agent who unlocked this achievement"
    )

    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='unlockers',
        help_text="The unlocked achievement"
    )

    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_achievements'
        unique_together = ['agent', 'achievement']
        verbose_name = 'User Achievement'
        verbose_name_plural = 'User Achievements'
        ordering = ['-unlocked_at']

    def __str__(self):
        return f"{self.agent.name} - {self.achievement.name}"


class ExplorationProgress(models.Model):
    """
    Exploration progress tracking - records room visits.

    Tracks which rooms each agent has visited for exploration achievements.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    agent = models.ForeignKey(
        'agent_auth.Agent',
        on_delete=models.CASCADE,
        related_name='exploration_progress',
        help_text="The exploring agent"
    )

    room_key = models.CharField(
        max_length=100,
        help_text="Room identifier, e.g. 'tut#05'"
    )

    room_name = models.CharField(
        max_length=200,
        help_text="Room name for display"
    )

    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'exploration_progress'
        unique_together = ['agent', 'room_key']
        verbose_name = 'Exploration Progress'
        verbose_name_plural = 'Exploration Progress'
        ordering = ['agent', 'visited_at']

    def __str__(self):
        return f"{self.agent.name} visited {self.room_key}"


class CombatLog(models.Model):
    """
    Combat log - for combat achievement statistics.

    Records combat results for tracking combat achievements.
    Will be integrated when combat system is implemented.
    """

    RESULT_CHOICES = [
        ('victory', 'Victory'),
        ('defeat', 'Defeat'),
        ('flee', 'Flee'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    agent = models.ForeignKey(
        'agent_auth.Agent',
        on_delete=models.CASCADE,
        related_name='combat_logs',
        help_text="The participating agent"
    )

    # Combat information
    enemy_key = models.CharField(
        max_length=100,
        help_text="Enemy identifier"
    )

    enemy_name = models.CharField(
        max_length=200,
        help_text="Enemy display name"
    )

    # Combat result
    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        help_text="Combat result"
    )

    # Combat data
    damage_dealt = models.IntegerField(
        default=0,
        help_text="Damage dealt to enemy"
    )

    damage_taken = models.IntegerField(
        default=0,
        help_text="Damage taken from enemy"
    )

    combat_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'combat_logs'
        verbose_name = 'Combat Log'
        verbose_name_plural = 'Combat Logs'
        ordering = ['-combat_time']

    def __str__(self):
        return f"{self.agent.name} vs {self.enemy_name} - {self.result}"