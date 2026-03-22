"""
Create code-defined rooms, objects, and exits (idempotent).

Runs on Railway after ``evennia migrate`` via ``server/start.sh``.

Usage (from game directory):
    evennia sync_codeworld
"""

from django.core.management.base import BaseCommand

from world.codeworld.sync import run_sync


class Command(BaseCommand):
    help = (
        "Apply world/codeworld/definitions.py (idempotent: existing db_key skipped)."
    )

    def handle(self, *args, **options):
        created, skipped, messages = run_sync()
        for line in messages:
            self.stdout.write(line)
        self.stdout.write(
            self.style.SUCCESS(
                f"codeworld sync finished: created={created}, skipped={skipped}"
            )
        )
