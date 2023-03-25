import datetime

import pytz
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Max, Min, Avg
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseForbidden, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone, dateparse
from django.utils.timezone import make_aware
from django.conf import settings
from django.core.exceptions import PermissionDenied

from rest_framework import viewsets, permissions
from . import serializers
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from . import models, forms


def index(request):
    return redirect("feed_list")
@login_required
def feed_list_base(request):
    return redirect("feed_list_user", request.user.username)

@login_required
def feed_list(request, username):
    if not match_logged_user(request.user, username):
        raise Http404(f"You are not allowed to access!")

    feeds = models.Feed.objects.filter(owner__username=username).values("id", "name", "date_created", "owner__username")
    new_f_form = forms.NewFeed()

    if request.method == "POST":
        miss_i = models.Feed(owner_id=request.user.id)
        new_f_form = forms.NewFeed(request.POST, instance=miss_i)
        try:
            if new_f_form.errors or not new_f_form.is_valid():
                print(new_f_form)
                raise ValidationError("Not valid.")
            new_f_form.save()
            return redirect("feed_list")

        except (IntegrityError, ValueError, ValidationError) as err:
            if str(err) == "Feed name exists":
                new_f_form.add_error("name", "This name already exists")

    for feed in feeds:
        feed["last_value"] = models.Data.objects.filter(feed_id=feed["id"]).order_by("-date_created").last()
    print(feeds)

    return render(request, "feed/feed_list.html", {"user":request.user, "form": new_f_form , "feeds": feeds})

@login_required
def feed_view(request, username, feed_name):
    try:
        if match_logged_user(request.user, username):
            feed = models.Feed.objects.get(name=feed_name, owner__username=username.lower())
        else:
            raise models.Feed.DoesNotExist
    except models.Feed.DoesNotExist:
        raise Http404(f"Feed with name {feed_name} does not exist.")
    print(feed.owner)

    data = models.Data.objects.filter(feed__id=feed.id).order_by("-date_created")[:20]
    opt_f = forms.OptionsForm()
    dt_f = forms.DataForm()

    if request.method == "POST":
        if "value" in request.POST:
            dt_inst = models.Data(feed=feed)
            dt_f = forms.DataForm(request.POST, instance=dt_inst)
            if dt_f.is_valid():
                dt_f.save()
                return redirect("feed_view", username, feed_name)

        else:
            limit_date = request.POST["limit_date"].split(" to ")
            request_post_copy = request.POST.copy()
            request_post_copy["limit_date"] = None
            request_post_copy["limit_number"] = None

            opt_f = forms.OptionsForm(request_post_copy)

            if opt_f.is_valid():
                if opt_f.cleaned_data["limit_by"] == "number":
                    if request.POST["limit_number"] == "all":
                        data = models.Data.objects.filter(feed__id=feed.id).order_by("-date_created")
                    else:
                        data = models.Data.objects.filter(feed__id=feed.id).order_by("-date_created")[:int(request.POST["limit_number"])]

                elif opt_f.cleaned_data["limit_by"] == "date":
                    data = models.Data.objects.filter(feed__id=feed.id).filter(date_created__range=
                            (make_aware(dateparse.parse_datetime(limit_date[0]), pytz.timezone(settings.TIME_ZONE)),
                             make_aware(dateparse.parse_datetime(limit_date[1]), pytz.timezone(settings.TIME_ZONE)
                                        ).replace(second=59, microsecond=999999))).order_by("-date_created")

    stats = {"len": len(data)}
    if stats["len"] != 0:
        stats["avg"] = round(data.aggregate(Avg("value"))["value__avg"], 3)
        stats["max"] = list(filter(lambda a: a.value == data.aggregate(Max("value"))["value__max"], data))
        stats["min"] = list(filter(lambda a: a.value == data.aggregate(Min("value"))["value__min"], data))

    return render(request, "feed/feed_view.html", {"user":request.user, "feed": feed, "data": data, "dt": dt_f, "op": opt_f, "stats": stats})

@login_required
@csrf_exempt
def data_view(request, username, feed_name, pk):
    try:
        if match_logged_user(request.user, username):
            feed = models.Feed.objects.get(name=feed_name, owner__username=username.lower())
        else:
            raise models.Feed.DoesNotExist
    except models.Feed.DoesNotExist:
        raise Http404(f"Feed with name {feed_name} does not exist.")

    if request.method == "DELETE":
        try:
            data = models.Data.objects.get(id=pk, feed=feed)
        except models.Data.DoesNotExist:
            return HttpResponse("Data does not exist", status=status.HTTP_404_NOT_FOUND)

        data.delete()
        print("deleted")
        return HttpResponse("", status=status.HTTP_200_OK)

def users_login(request):
    redirect_to = request.POST.get("next", None) if request.method == "POST" else request.GET.get("next", None)

    if request.user.is_authenticated:
        return redirect("user_profile", request.user.username) if not redirect_to else redirect(redirect_to)

    login_form = forms.LoginForm(label_suffix="")
    errors = False

    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]

        redirect_to = "user_profile_base" if redirect_to == None or redirect_to == "None" else redirect_to

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(redirect_to)
        else:
            login_form = forms.LoginForm(request.POST, label_suffix="")
            errors = True


    return render(request, "feed/users/login.html", {"next": redirect_to, "form": {"errors": errors, "form":login_form}, "user": request.user})

def match_logged_user(logged, user):
    return logged.username == user.lower()

@login_required
def user_profile(request, username):
    if not match_logged_user(request.user, username):
        raise PermissionDenied
        # return HttpResponseForbidden(render(request, "feed/403.html"))
        #return HttpResponseForbidden("You are NOT ALLOWED to see this!")
    user_obj = models.User.objects.get(id=request.user.id)
    if user_obj.display_name == "":
        user_obj.display_name = user_obj.username
        user_obj.save()

    auth_token = Token.objects.get_or_create(user = user_obj)[0]
    print(auth_token)

    if "regenerate" in request.POST:
        Token.objects.get(user = user_obj).delete()
        auth_token = Token.objects.create(user = user_obj)

    return render(request, "feed/users/profile.html", {"user": request.user, "api_key": auth_token})

@login_required
def user_profile_base(request):
    return redirect("user_profile", request.user.username)

def users_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("users_login")
        #return HttpResponse(f"Logged out")

def users_register(request):
    if request.user.is_authenticated:
        return redirect("user_profile_base")

    register_form = forms.RegisterForm()

    if request.method == "POST":
        user_i = models.User(username=request.POST["display_name"].lower())
        register_form = forms.RegisterForm(request.POST, instance=user_i)
        try:
            if register_form.errors or not register_form.is_valid:
                raise ValidationError("Error validating form")
            user_inst = register_form.save()

        except (IntegrityError, ValueError, ValidationError) as err:
            if str(err) == "Username exists":
                register_form.add_error("display_name", "User with this username already exists.")
            return render(request, "feed/users/register.html", {"user": request.user, "form": register_form})

        login(request, user_inst)
        return redirect("users_login")

    return render(request, "feed/users/register.html", {"user": request.user, "form": register_form})

def http_403(request, exception):
    return render(request, "403.html", {"ex": exception}, status=403)

def http_404(request, exception):
    return render(request, "404.html", {"ex": exception}, status=404)

def http_500(request):
    return render(request, "500.html", status=500)

### API ###

@api_view(["GET", "POST", "DELETE"])
@permission_classes([permissions.IsAuthenticated])
def api_data(request, username, feed_name):
        if match_logged_user(request.user, username):
            try:
                feed = models.Feed.objects.get(name=feed_name, owner__username=username.lower())
            except models.Feed.DoesNotExist:
                return Response({'error':f'Feed with name \'{feed_name}\' does not exist.'}, status=status.HTTP_404_NOT_FOUND)

            if request.method == "POST":
                serial_data = serializers.DataSerializer(data=request.data, many=True)

                ################    serial_data.update({"feed":feed})
                print(serial_data)
                print(serial_data.initial_data)

                # for data in serial_data.initial_data:
                #     if isinstance(data["value"], str):
                #         try:
                #             data["value"] = float(data["value"])
                #         except ValueError:
                #             return Response({'error':'Data is not valid. (string, not int/float)'}, status=status.HTTP_400_BAD_REQUEST)
                if serial_data.is_valid():
                    print(serial_data.data)
                    serial_data.save(feed=feed)
                    return Response({'status':'Data successfully created.'}, status=status.HTTP_201_CREATED)

                else:
                    return Response({'error':'Data is not valid.'}, status=status.HTTP_400_BAD_REQUEST)

            elif request.method == "DELETE":
                pass #TODO

            else:
                feeds_data = models.Data.objects.filter(feed__id=feed.id)
                data_serialized = serializers.DataSerializer(feeds_data, many=True)
                return Response(data_serialized.data)

        else:
            return Response({'error':f'Feed with name \'{feed_name}\' does not exist.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET", "POST"])
@permission_classes([permissions.IsAuthenticated])
def api_feeds(request, username):
    if match_logged_user(request.user, username):
        try:
            feeds = models.Feed.objects.filter(owner__username=request.user.username).values("id", "name", "date_created", "owner__username")
        except models.User.DoesNotExist:
            print("feed does not exist")
            return Response({'error': f'User with name \'{username}\' does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == "POST":
            serialized_feed = serializers.FeedSerializer(data=request.data, many=True)
            print(serialized_feed.initial_data)
            try:
                if serialized_feed.is_valid():
                    user = models.User.objects.get(username=username.lower())
                    serialized_feed.save(owner=user)
                    return Response({'status':f'Feed{"s" if len(serialized_feed.data) > 1 else ""} successfully created.'}, status=status.HTTP_201_CREATED)
                else:
                    raise ValidationError("invalid")

            except (ValidationError, IntegrityError):
                return Response({'error': 'Feed is not valid.'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            feeds_serialized = serializers.FeedSerializer(feeds, many=True)
            return Response(feeds_serialized.data)

    else:
        print("feed does not exist")
        return Response({'error': f'User with name \'{username}\' does not exist.'}, status=status.HTTP_404_NOT_FOUND)

