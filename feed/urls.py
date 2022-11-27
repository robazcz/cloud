from django.urls import path, include 
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("feed/", views.index, name="index"),
    path("new_feed/", views.new_feed, name="new_feed"),
    path("feed/<str:feed_name>/", views.feed_view, name="feed_view"),
    path("feed/<str:feed_name>/new_data/", views.new_data, name="new_data"),
]
    
urlpatterns += [
    #path("users/", include("django.contrib.auth.urls")),
    path("users/login/", views.users_login, name="users_login"),
    #path("users/login/", auth_views.LoginView.as_view(template_name="feed/users/login.html"), name="users_login"),
    path("user/<str:username>/", views.user_profile, name="user_profile"),
]    