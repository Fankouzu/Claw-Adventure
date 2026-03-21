import logging
import sys

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class AgentAuthConfig(AppConfig):
    """
    Agent authentication Django app.
    """

    name = "world.agent_auth"
    verbose_name = "Agent Authentication"

    def ready(self):
        """
        Ensure evennia._init() runs during django.setup().

        evennia_launcher skips _init() for many management commands (e.g.
        showmigrations). Django then runs URL checks that import
        typeclasses.characters -> evadventure while Command/AttributeProperty
        are still None. Portal and server processes also call django.setup()
        before their entrypoint runs _init(); priming here is idempotent
        (_LOADED guard inside evennia._init).
        """
        import evennia

        if getattr(evennia, "_LOADED", False):
            return

        def _portal_mode_from_argv() -> bool:
            # twistd passes e.g. --python=.../evennia/server/portal/portal.py
            for arg in sys.argv:
                norm = arg.replace("\\", "/").lower()
                if norm.endswith("portal.py") or "/portal/portal.py" in norm:
                    return True
            return False

        portal_mode = _portal_mode_from_argv()

        try:
            evennia._init(portal_mode=portal_mode)
        except Exception:
            logger.exception(
                "evennia._init(portal_mode=%s) failed in AppConfig.ready()",
                portal_mode,
            )