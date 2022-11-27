from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from . import models

def index(request):
    feeds = models.Feed.objects.all().values()
    print(feeds)
    return render(request, "feed/index.html", {"feeds": feeds})

def new_feed(request):
    feeds = models.Feed.objects.all().values()
    new_f = models.Feed(name=request.POST["feed_name"])
    new_f.save()
    return redirect("index")
    #return render(request, "feed/index.html", {"feeds": feeds})

def feed_view(request, feed_name):
    try:
        feed = models.Feed.objects.get(name=feed_name)
    except models.Feed.DoesNotExist:
        raise Http404(f"Feed with name {feed_name} does not exist.")

    data = models.Data.objects.filter(feed__name=feed_name)

    return render(request, "feed/feed_view.html", {"feed": feed, "data": data})

def new_data(request, feed_name):
    try:
        feed = models.Feed.objects.get(name=feed_name)
    except models.Feed.DoesNotExist:
        raise Http404(f"Feed with name {feed_name} does not exist.")

    new_d = models.Data(feed=feed, value=request.POST["data_value"])
    new_d.save()

    data = models.Data.objects.filter(feed__name=feed_name)

    return redirect("feed_view", feed_name)
    #return render(request, "feed/feed_view.html", {"feed": feed, "data": data})

def users_login(request):
    print(request.POST["username"])
    username = request.POST["username"]
    password = request.POST["password"]
    redirect_to = request.POST["next"]
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return redirect(redirect_to) if redirect_to else redirect("user_profile", username)

@login_required
def user_profile(request, username):
    return render(request, "cloud/index.html")
