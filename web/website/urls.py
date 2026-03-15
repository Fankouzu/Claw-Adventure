"""
This reroutes from an URL to a python view-function/class.

The main web/urls.py includes these routes for all urls (the root of the url)
so it can reroute to all website pages.

"""

from django.urls import path

from evennia.web.website.urls import urlpatterns as evennia_website_urlpatterns

# agent auth views
from world.agent_auth import views as agent_auth_views

# Custom pages - these will override Evennia defaults
urlpatterns = [
    # Landing page (overrides default index)
    path("", agent_auth_views.landing, name="landing"),
    # Agent profile page
    path("agents/<str:name>", agent_auth_views.agent_profile, name="agent_profile"),
    # Register success page
    path("register/success/<str:agent_id>", agent_auth_views.register_success, name="register_success"),
    # FAQ/Help page
    path("help", agent_auth_views.faq, name="faq"),
]

# read by Django - evennia patterns come after our custom patterns
urlpatterns = urlpatterns + evennia_website_urlpatterns