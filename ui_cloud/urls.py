from django.urls import path
from django.contrib.auth.decorators import login_required

from ui_cloud.views import Login, Overview, Logout, FeedView

urlpatterns = [
    path("login/", Login.as_view(), name="Login"),
    path("logout/", login_required(Logout), name="Logout"),
    path("overview/", login_required(Overview.as_view()), name="Overview"),
    path("feed/<str:name>/", login_required(FeedView.as_view()), name="FeedView"),
]
