from django.urls import path, include 
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("feed/", views.feed_list, name="feed_list"),
    path("feed/<str:username>/<str:feed_name>/", views.feed_view, name="feed_view"),
    path("feed/<str:username>/<str:feed_name>/new_data/", views.new_data, name="new_data"),
]
    
urlpatterns += [
    #path("users/", include("django.contrib.auth.urls")),
    path("users/login/", views.users_login, name="users_login"),
    #path("users/login/", auth_views.LoginView.as_view(template_name="feed/users/login.html"), name="users_login"),
    path("users/logout/", views.users_logout, name="users_logout"),
    path("users/register/", views.users_register, name="users_register"),
    path("user/<str:username>/", views.user_profile, name="user_profile"),
    path("user/", views.user_profile_base, name="user_profile_base"),
]    