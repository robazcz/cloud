from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
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
