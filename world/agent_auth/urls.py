"""
Agent auth URL entrypoint.

Splits into:
- ``urls_api`` — JSON/API under ``/api/`` and ``/api/v1/`` (same handlers).
- ``urls_pages`` — HTML pages at site root (landing, claim, dashboard, …).

Mounted from ``web.urls`` via ``include("world.agent_auth.urls")``.
"""
from django.urls import include, path

urlpatterns = [
    path("api/", include("world.agent_auth.urls_api")),
    path("api/v1/", include("world.agent_auth.urls_api")),
    path("", include("world.agent_auth.urls_pages")),
]
