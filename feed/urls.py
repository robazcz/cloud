from django.urls import path

from . import views

urlpatterns = [
    path("feed/", views.index, name="index"),
    path("new_feed/", views.new_feed, name="new_feed"),
]