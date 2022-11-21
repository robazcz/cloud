from django.urls import path

from . import views

urlpatterns = [
    path("feed/", views.index, name="index"),
    path("new_feed/", views.new_feed, name="new_feed"),
    path("feed/<str:feed_name>", views.feed_view, name="feed_view"),
    path("feed/<str:feed_name>/new_data", views.new_data, name="new_data"),
]