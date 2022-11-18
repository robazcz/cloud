from django.shortcuts import render
from django.http import HttpResponse
from . import models

def index(request):
    feeds = models.Feed.objects.all().values()
    print(feeds)
    return render(request, "feed/index.html", {"feeds": feeds})

def new_feed(request):
    feeds = models.Feed.objects.all().values()
    new_f = models.Feed(name=request.POST["feed_name"])
    new_f.save()
    return render(request, "feed/index.html", {"feeds": feeds})