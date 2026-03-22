"""
Create a missing fission InvitationCode for an Agent (repair / backfill).

Same generation rule as register API: parent code generation + 1, or 1 if unknown.

Usage:
    evennia ensure_fission_code Pipixia_VI
    evennia ensure_fission_code Pipixia_VI --dry-run
"""

from django.core.management.base import BaseCommand

from world.agent_auth.models import Agent, InvitationCode, InvitationRelationship


def _resolve_generation(agent: Agent) -> int:
    """Match views.register_agent: generation = inv_code.generation + 1 or 1."""
    rel = InvitationRelationship.objects.filter(invitee=agent).select_related("code").first()
    if rel and rel.code_id:
        inv_code = rel.code
        return inv_code.generation + 1 if inv_code.generation else 1
    used = (
        agent.invitation_codes.filter(code_type="admin")
        .order_by("used_at")
        .first()
    )
    if not used:
        used = agent.invitation_codes.order_by("used_at").first()
    if used:
        return used.generation + 1 if used.generation else 1
    return 1


class Command(BaseCommand):
    help = (
        "Ensure the Agent has exactly one fission InvitationCode; create if missing. "
        "Idempotent if a fission code already exists."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "name",
            type=str,
            help="Agent.name (exact match)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be done without writing to the database.",
        )

    def handle(self, *args, **options):
        name = options["name"].strip()
        dry_run = options["dry_run"]

        try:
            agent = Agent.objects.get(name=name)
        except Agent.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Agent not found: {name!r}"))
            return

        existing = InvitationCode.objects.filter(
            created_by=agent, code_type="fission"
        ).first()
        if existing:
            self.stdout.write(
                self.style.NOTICE(
                    f"Agent already has fission code: {existing.code!r} (generation={existing.generation})"
                )
            )
            return

        generation = _resolve_generation(agent)
        self.stdout.write(
            f"No fission code; would create with generation={generation} (from registration parent code or default 1)."
        )
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run — no database changes."))
            return

        fission = InvitationCode.create_fission_code(agent, generation)
        self.stdout.write(self.style.SUCCESS(f"Created fission code: {fission.code!r}"))
        self.stdout.write(
            "The Cliff InvitationSign will show this code when the character reads the sign "
            "(same Evennia account as agent_connect)."
        )
