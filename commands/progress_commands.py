from typing import Any, cast

from evennia.objects.models import ObjectDB

from commands.command import Command
from typeclasses.pvp_progression import build_pvp_progress_lines


def _is_progress_target(obj) -> bool:
    return bool(
        getattr(obj, "has_account", False)
        or getattr(obj, "typeclass_path", "") == "typeclasses.characters.Character"
    )


class CmdProgress(Command):
    key = "progress"
    aliases = ["rank", "pvp"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = cast(Any, getattr(self, "caller", None))
        if caller is None:
            return
        args = str(getattr(self, "args", "")).strip()
        if not args:
            caller.msg(build_pvp_progress_lines(caller, "PvP Progress"))
            return

        matches = [
            obj
            for obj in getattr(getattr(caller, "location", None), "contents", [])
            if _is_progress_target(obj)
            and getattr(obj, "key", "").lower() == args.lower()
        ]
        if not matches:
            matches = [
                obj
                for obj in ObjectDB.objects.filter(db_key__iexact=args)
                if _is_progress_target(obj)
            ]
        if not matches:
            caller.msg(f"Could not find '{args}'.")
            return
        if len(matches) > 1:
            caller.msg(f"More than one match for '{args}'.")
            return

        target = matches[0]
        caller.msg(build_pvp_progress_lines(target, f"PvP Progress for {target.key}"))
