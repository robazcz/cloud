from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError

from . import models, forms

@login_required
def feed_list(request):
    if request.method == "POST":
        miss_i = models.Feed(owner_id=request.user.id)
        new_f = forms.NewFeed(request.POST, instance=miss_i)
        try:
            new_f.save()
        except (IntegrityError, ValueError):
            feeds = models.Feed.objects.filter(owner__username=request.user.username).values("id", "name", "date_created", "owner__username")
            return render(request, "feed/feed_list.html", {"user": request.user, "form": forms.NewFeed(request.POST), "feeds": feeds, "errors": True})

        feeds = models.Feed.objects.filter(owner__username=request.user.username).values("id", "name", "date_created", "owner__username")
        return render(request, "feed/feed_list.html", {"user":request.user, "form": forms.NewFeed, "feeds": feeds})

    else:
        feeds = models.Feed.objects.filter(owner__username=request.user.username).values("id", "name", "date_created", "owner__username")
        # print(feeds)

    return render(request, "feed/feed_list.html", {"user":request.user, "form": forms.NewFeed , "feeds": feeds})

@login_required
def feed_view(request, username, feed_name):
    try:
        feed = models.Feed.objects.get(name=feed_name, owner__username=username)
    except models.Feed.DoesNotExist:
        raise Http404(f"Feed with name {feed_name} does not exist.")
    print(feed.owner)
    data = models.Data.objects.filter(feed__id = feed.id)

    return render(request, "feed/feed_view.html", {"feed": feed, "data": data})

def new_data(request, username, feed_name):
    try:
        feed = models.Feed.objects.get(name=feed_name, owner__username=username)
    except models.Feed.DoesNotExist:
        raise Http404(f"Feed with name {feed_name} does not exist.")

    new_d = models.Data(feed=feed, value=request.POST["data_value"])
    new_d.save()

    data = models.Data.objects.filter(feed__id = feed.id)

    return redirect("feed_view", username, feed_name)
    #return render(request, "feed/feed_view.html", {"feed": feed, "data": data})

def users_login(request):
    # print(request.GET)
    # print(request.GET.get("next", None))
    # try:
    #     redirect_to = request.POST["next"]
    # except MultiValueDictKeyError:
    redirect_to = None
    if request.method == "GET":
        redirect_to = request.GET.get("next", None)
        print(redirect_to)
        
        print(f"user? {request.user.is_authenticated}")
        if request.user.is_authenticated:
            return redirect("user_profile", request.user.username) if not redirect_to else redirect(redirect_to)

    elif request.method == "POST":
        redirect_to = request.POST.get("next", None)
        #print(request.POST["username"])
        username = request.POST["username"]
        password = request.POST["password"]

        print(f"redirect: {redirect_to}")

        redirect_to = "user_profile" if redirect_to == None or redirect_to == "None" else redirect_to
        args = username if redirect_to == "user_profile" else None
        print(f"redirect: {redirect_to}")

        user = authenticate(request, username=username, password=password)
        print(f"auth user {username}")

        if user is not None:
            login(request, user)
            return redirect(redirect_to, args)
        else:
            return render(request, "feed/users/login.html", {"next":redirect_to, "form":{"errors": True, "form": forms.LoginForm(request.POST)}, "user":request.user})

    return render(request, "feed/users/login.html", {"next": redirect_to, "form": {"errors": False, "form":forms.LoginForm}, "user": request.user})
    #return render(request, "feed/users/login.html", {"next":redirect_to, "form":{"errors": False}, "user": request.user})

def match_logged_user(logged, user):
    return logged.username == user

@login_required
def user_profile(request, username):
    if not match_logged_user(request.user, username):
        return HttpResponseForbidden(render(request, "feed/not_allowed.html"))
        #return HttpResponseForbidden("You are NOT ALLOWED to see this!")

    return render(request, "feed/users/profile.html", {"user": request.user})

@login_required
def user_profile_base(request):
    return redirect("user_profile", request.user.username)

def users_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("users_login")
        #return HttpResponse(f"Logged out")

def users_register(request):
    if not request.user.is_authenticated:
        if request.method == "GET":
            return render(request, "feed/users/register.html", {"form": {"errors":None, "form":forms.LoginForm}})
        
        elif request.method == "POST":
            user = forms.LoginForm(request.POST)
            try:
                if user.errors:
                    #print(f"valid? {user.errors.as_json()}")
                    raise ValidationError("Error validation form")
                user.save()
            # user.clean()
            except (IntegrityError, ValueError, ValidationError):
                return render(request, "feed/users/register.html", {"form": {"errors":user.errors.as_data(), "form":forms.LoginForm(request.POST)}})

            login(request, user)
            return redirect("users_login")

    else:
        return redirect("user_profile_base")
    
    
    
