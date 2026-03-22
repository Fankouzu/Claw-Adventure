"""
Django management command: print Agent binding + fission code (Cliff sign diagnostics).

Usage (from game root, same as other evennia commands):
    evennia diagnose_agent Pipixia_VI
"""

from django.core.management.base import BaseCommand

from world.agent_auth.models import Agent, InvitationCode


class Command(BaseCommand):
    help = (
        "Show Agent row, evennia_account link, and fission InvitationCode(s). "
        "Use this when the Cliff sign shows story text but not the invitation block."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "name",
            type=str,
            help="Agent.name (exact match)",
        )

    def handle(self, *args, **options):
        name = options["name"].strip()
        try:
            agent = Agent.objects.get(name=name)
        except Agent.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Agent not found: {name!r}"))
            return

        self.stdout.write(self.style.NOTICE(f"=== Agent: {agent.name} ==="))
        self.stdout.write(f"id: {agent.id}")
        self.stdout.write(f"claim_status: {agent.claim_status}")
        self.stdout.write(f"in_world_character_key: {agent.in_world_character_key!r}")

        acc = agent.evennia_account
        if acc is None:
            self.stdout.write(
                self.style.WARNING(
                    "evennia_account: (none) — sign cannot resolve Agent from puppet; "
                    "need one successful agent_connect for this Agent."
                )
            )
        else:
            self.stdout.write(
                f"evennia_account: id={acc.id} username={acc.username!r}"
            )

        fissions = list(
            InvitationCode.objects.filter(created_by=agent, code_type="fission")
        )
        if not fissions:
            self.stdout.write(
                self.style.WARNING(
                    "fission InvitationCode: (none) — register API should create one; "
                    "or create via InvitationCode.create_fission_code(agent, generation)."
                )
            )
        else:
            self.stdout.write(f"fission InvitationCode count: {len(fissions)}")
            for c in fissions:
                self.stdout.write(f"  code={c.code!r} generation={c.generation}")

        self.stdout.write("")
        self.stdout.write(
            "Cliff sign shows the invitation block only when: "
            "evennia_account is set AND at least one fission code exists."
        )
