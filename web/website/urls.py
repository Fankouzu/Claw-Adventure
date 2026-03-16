"""
This reroutes from an URL to a python view-function/class.

The main web/urls.py includes these routes for all urls (the root of the url)
so it can reroute to all website pages.

"""

from django.urls import path

from evennia.web.website.urls import urlpatterns as evennia_website_urlpatterns

# Custom pages can be added here
# urlpatterns = [
#     path("custom/", custom_view, name="custom"),
# ]

urlpatterns = []

# read by Django - evennia patterns come after our custom patterns
urlpatterns = urlpatterns + evennia_website_urlpatterns
