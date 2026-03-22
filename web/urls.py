"""
This is the starting point when a user enters a url in their web browser.

The urls is matched (by regex) and mapped to a 'view' - a Python function or
callable class that in turn (usually) makes use of a 'template' (a html file
with slots that can be replaced with dynamic content) in order to render a HTML
page to show the user.

This file includes the urls in website, webclient and admin. To override you
should modify urls.py in those sub directories.

Search the Django documentation for "URL dispatcher" for more help.

"""

from django.urls import include, path

# default evennia patterns
from evennia.web.urls import urlpatterns as evennia_default_urlpatterns

from web import views as web_views

# add patterns
urlpatterns = [
    # Agent auth: pages at /, API at /api/ and /api/v1/. Before default website
    # so / serves agent landing instead of Evennia index when both match.
    path("", include("world.agent_auth.urls")),
    # website
    path("", include("web.website.urls")),
    # webclient
    path("webclient/", include("web.webclient.urls")),
    # web admin
    path("admin/", include("web.admin.urls")),
    # Optional React SPA build output (see web/static/app/README.md)
    path("app/", web_views.serve_react_app),
    path("app/<path:_path>", web_views.serve_react_app),
]

# 'urlpatterns' must be named such for Django to find it.
urlpatterns = urlpatterns + evennia_default_urlpatterns
