"""
Admin configuration for the achievements system.
"""

from django.contrib import admin
from .models import Achievement, UserAchievement, ExplorationProgress, CombatLog


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """Admin interface for Achievement model."""

    list_display = ['key', 'name', 'category', 'points', 'is_hidden', 'created_at']
    list_filter = ['category', 'is_hidden']
    search_fields = ['key', 'name', 'description']
    ordering = ['category', 'points']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('key', 'name', 'description', 'category', 'icon')
        }),
        ('Achievement Properties', {
            'fields': ('points', 'is_hidden')
        }),
        ('Unlock Requirement', {
            'fields': ('requirement',),
            'description': 'JSON configuration for unlock condition. Example: {"room_key": "tut#02"}'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    """Admin interface for UserAchievement model."""

    list_display = ['agent', 'achievement', 'unlocked_at']
    list_filter = ['achievement__category', 'unlocked_at']
    search_fields = ['agent__name', 'achievement__name', 'achievement__key']
    ordering = ['-unlocked_at']
    readonly_fields = ['unlocked_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('agent', 'achievement')


@admin.register(ExplorationProgress)
class ExplorationProgressAdmin(admin.ModelAdmin):
    """Admin interface for ExplorationProgress model."""

    list_display = ['agent', 'room_key', 'room_name', 'visited_at']
    list_filter = ['visited_at']
    search_fields = ['agent__name', 'room_key', 'room_name']
    ordering = ['agent', '-visited_at']
    readonly_fields = ['visited_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('agent')


@admin.register(CombatLog)
class CombatLogAdmin(admin.ModelAdmin):
    """Admin interface for CombatLog model."""

    list_display = ['agent', 'enemy_name', 'result', 'damage_dealt', 'damage_taken', 'combat_time']
    list_filter = ['result', 'combat_time']
    search_fields = ['agent__name', 'enemy_key', 'enemy_name']
    ordering = ['-combat_time']
    readonly_fields = ['combat_time']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('agent')