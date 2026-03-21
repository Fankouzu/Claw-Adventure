"""Tests for achievement engine requirement matching."""

from django.test import TestCase

from world.agent_auth.models import Agent
from world.achievements.engine import AchievementEngine
from world.achievements.models import (
    Achievement,
    ExplorationProgress,
    UserAchievement,
)


class AchievementRequirementTest(TestCase):
    def setUp(self):
        self.agent, _ = Agent.create_agent(name="__ach_engine_test_agent")
        Achievement.objects.create(
            key="__test_room_only",
            name="Room only",
            description="",
            category="exploration",
            points=1,
            requirement={"room_key": "tut#01"},
        )
        Achievement.objects.create(
            key="__test_room_action",
            name="Room + action",
            description="",
            category="exploration",
            points=1,
            requirement={"room_key": "tut#01", "action": "climb_tree"},
        )

    def test_explore_skips_action_gated_achievement(self):
        AchievementEngine.check_exploration(self.agent, "tut#01", "tut#01")
        self.assertTrue(
            UserAchievement.objects.filter(
                agent=self.agent, achievement__key="__test_room_only"
            ).exists()
        )
        self.assertFalse(
            UserAchievement.objects.filter(
                agent=self.agent, achievement__key="__test_room_action"
            ).exists()
        )

    def test_apply_context_unlocks_action_gated_achievement(self):
        AchievementEngine.apply_context_unlock(
            self.agent, room_key="tut#01", action="climb_tree"
        )
        self.assertTrue(
            UserAchievement.objects.filter(
                agent=self.agent, achievement__key="__test_room_action"
            ).exists()
        )

    def test_revisit_does_not_recheck_exploration(self):
        AchievementEngine.check_exploration(self.agent, "tut#01", "tut#01")
        UserAchievement.objects.filter(
            agent=self.agent, achievement__key="__test_room_only"
        ).delete()
        out = AchievementEngine.check_exploration(
            self.agent, "tut#01", "tut#01"
        )
        self.assertEqual(out, [])
        self.assertFalse(
            UserAchievement.objects.filter(
                agent=self.agent, achievement__key="__test_room_only"
            ).exists()
        )

    def test_exploration_truncates_long_room_fields(self):
        long_key = "K" * 150
        long_name = "N" * 250
        AchievementEngine.check_exploration(self.agent, long_key, long_name)
        row = ExplorationProgress.objects.get(agent=self.agent, room_key="K" * 100)
        self.assertEqual(len(row.room_key), 100)
        self.assertEqual(len(row.room_name), 200)

    def test_explorer_master_uses_requirement_count(self):
        ach = Achievement.objects.get(key="explorer_master")
        old_req = dict(ach.requirement or {})
        try:
            ach.requirement = {"type": "visit_all_rooms", "count": 3}
            ach.save()
            self.assertEqual(AchievementEngine._explorer_master_threshold(), 3)
            for i in range(1, 3):
                ExplorationProgress.objects.create(
                    agent=self.agent, room_key=f"r{i}", room_name=str(i)
                )
            unlocked = AchievementEngine.check_exploration(
                self.agent, "r3", "r3"
            )
            self.assertIn("explorer_master", {a.key for a in unlocked})
        finally:
            ach.requirement = old_req
            ach.save(update_fields=["requirement"])
