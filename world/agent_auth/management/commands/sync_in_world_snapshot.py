"""
Django management command: push Character stats into Agent in_world_* columns.

Usage (from game directory, same as evennia migrate):
    evennia sync_in_world_snapshot
    evennia sync_in_world_snapshot Pipixia_v2 AnotherAgent
"""

from django.core.management.base import BaseCommand

from world.agent_auth.in_world_sync import (
    get_bound_character_for_agent,
    sync_in_world_snapshot_from_character,
)
from world.agent_auth.models import Agent


class Command(BaseCommand):
    help = (
        "Refresh Agent in_world_* mirror from bound EvAdventure Character(s). "
        "With no names: all claimed agents that have an Evennia account."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "names",
            nargs="*",
            type=str,
            help="Agent name(s). Omit to process all eligible agents.",
        )

    def handle(self, *args, **options):
        names = options["names"]
        if names:
            agents = []
            for n in names:
                try:
                    agents.append(Agent.objects.get(name=n))
                except Agent.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"Agent not found: {n}"))
            if not agents:
                return
        else:
            agents = list(
                Agent.objects.filter(claim_status="claimed")
                .exclude(evennia_account__isnull=True)
                .iterator()
            )

        for agent in agents:
            char = get_bound_character_for_agent(agent)
            if not char:
                self.stdout.write(
                    self.style.WARNING(f"SKIP {agent.name}: no bound character")
                )
                continue
            sync_in_world_snapshot_from_character(char)
            self.stdout.write(
                self.style.SUCCESS(f"OK {agent.name} <- character {char.key!r}")
            )
