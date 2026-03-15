"""
This is the starting point when a user enters a url in their web browser.

The urls is matched (by regex) and mapped to a 'view' - a Python function or
callable class that in turn (usually) makes use of a 'template' (a html file
with slots that can be replaced by dynamic content) in order to render a HTML
page to show the user.

This file includes the urls in website, webclient and admin. To override you
should modify urls.py in those sub directories.

Search the Django documentation for "URL dispatcher" for more help.

"""

from django.urls import include, path
from django.http import HttpResponse
import os

# agent auth claim views
from world.agent_auth import views as agent_auth_views

# default evennia patterns
from evennia.web.urls import urlpatterns as evennia_default_urlpatterns


def serve_skill_md(request):
    """Serve skill.md file for agents"""
    skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'skill.md')
    if os.path.exists(skill_path):
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/markdown; charset=utf-8')
    return HttpResponse('skill.md not found', status=404)


# add patterns
urlpatterns = [
    # website (includes our custom landing, agents, help pages)
    path("", include("web.website.urls")),
    # webclient
    path("webclient/", include("web.webclient.urls")),
    # web admin
    path("admin/", include("web.admin.urls")),
    # skill.md for agents
    path("skill.md", serve_skill_md, name="skill_md"),
    # agent auth API
    path("api/", include("world.agent_auth.urls")),
    # agent claim pages
    path("claim/<str:token>", agent_auth_views.claim_page, name="claim_page"),
    path("claim/<str:token>/verify", agent_auth_views.verify_tweet, name="verify_tweet"),
]

# 'urlpatterns' must be named such for Django to find it.
urlpatterns = urlpatterns + evennia_default_urlpatterns