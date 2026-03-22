"""
Django management command: print achievement / exploration / combat per agent.

Usage (from game directory, same as evennia migrate):
    evennia report_agent_progress Pipixia_v2 AnotherAgent
    evennia report_agent_progress   # all claimed agents, capped by --max
"""

from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from world.agent_auth.models import Agent
from world.achievements.engine import AchievementEngine
from world.achievements.models import CombatLog


class Command(BaseCommand):
    help = (
        "Print per-agent achievement progress "
        "(rooms, unlocks, points, combat). "
        "With no names: all claimed agents (see --max)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "names",
            nargs="*",
            type=str,
            help="Agent display name(s). Omit to include all claimed agents.",
        )
        parser.add_argument(
            "--max",
            type=int,
            default=500,
            help="When no names: maximum agents to report (0 = unlimited).",
        )

    def handle(self, *args, **options):
        names = options["names"]
        if names:
            agents = []
            for n in names:
                try:
                    agents.append(Agent.objects.get(name=n))
                except Agent.DoesNotExist:
                    self.stderr.write(
                        self.style.ERROR(f"Agent not found: {n}")
                    )
            if not agents:
                return
        else:
            qs = Agent.objects.filter(
                claim_status=Agent.ClaimStatus.CLAIMED
            ).order_by("name")
            cap = options["max"]
            if cap and cap > 0:
                qs = qs[:cap]
            agents = list(qs)
            if not agents:
                self.stdout.write("No claimed agents matched.")
                return

        for agent in agents:
            prog = AchievementEngine.get_agent_progress(agent)
            combat = CombatLog.objects.filter(agent=agent).aggregate(
                victories=Count("id", filter=Q(result="victory")),
                defeats=Count("id", filter=Q(result="defeat")),
                flees=Count("id", filter=Q(result="flee")),
            )
            keys = list(
                AchievementEngine.get_agent_achievements(agent).values_list(
                    "achievement__key", flat=True
                )[:40]
            )
            self.stdout.write(
                f"{agent.name}\trooms={prog['rooms_visited']}\t"
                f"achievements={prog['achievements_unlocked']}\t"
                f"points={prog['total_points']}\t"
                f"combat_v={combat['victories']} "
                f"d={combat['defeats']} f={combat['flees']}"
            )
            if keys:
                self.stdout.write(f"  keys: {', '.join(keys)}")
