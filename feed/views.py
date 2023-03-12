import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Max, Min, Avg
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseForbidden, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone, dateparse

from rest_framework import viewsets, permissions
from . import serializers
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from . import api_permissions

from . import models, forms

def root(request):
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

        except (IntegrityError, ValueError, ValidationError) as err:
            if str(err) == "Feed name exists":
                new_f_form.add_error("name", "This name already exists")

    for feed in feeds:
        feed["last_value"] = models.Data.objects.filter(feed_id=feed["id"]).last()
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
    op_f = forms.OptionsForm()
    dt_f = forms.DataForm()

    if request.method == "POST":
        if "value" in request.POST:
            dt_inst = models.Data(feed=feed)
            dt_f = forms.DataForm(request.POST, instance=dt_inst)
            if dt_f.is_valid():
                dt_f.save()

        else:
            limit_date = request.POST["limit_date"].split(" to ")
            request_post_copy = request.POST.copy()
            request_post_copy["limit_date"] = None
            request_post_copy["limit_number"] = None

            print(request_post_copy)
            opt_f = forms.OptionsForm(request_post_copy)
            print(opt_f.is_valid())
            print(opt_f.errors)

            if opt_f.cleaned_data["limit_by"] == "number":
                if request.POST["limit_number"] == "all":
                    data = models.Data.objects.filter(feed__id=feed.id).order_by("-date_created")
                else:
                    data = models.Data.objects.filter(feed__id=feed.id).order_by("-date_created")[:int(request.POST["limit_number"])]

            elif opt_f.cleaned_data["limit_by"] == "date":
                data = models.Data.objects.filter(feed__id=feed.id).filter(date_created__range=
                                                 (limit_date[0], f"{limit_date[1]}:59")).order_by("-date_created")

    stats = {"len": len(data)}
    if stats["len"] != 0:
        stats["avg"] = round(data.aggregate(Avg("value"))["value__avg"], 3)
        stats["max"] = list(filter(lambda a: a.value == data.aggregate(Max("value"))["value__max"], data))
        stats["min"] = list(filter(lambda a: a.value == data.aggregate(Min("value"))["value__min"], data))

    return render(request, "feed/feed_view.html", {"user":request.user, "feed": feed, "data": data, "dt": dt_f, "op": op_f, "stats": stats})

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

    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]

        redirect_to = ("user_profile", username) if redirect_to == None or redirect_to == "None" else redirect_to

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(*redirect_to)
        else:
            login_form = forms.LoginForm(request.POST, label_suffix="")


    return render(request, "feed/users/login.html", {"next": redirect_to, "form": {"errors": False, "form":login_form}, "user": request.user})

def match_logged_user(logged, user):
    return logged.username == user.lower()

@login_required
def user_profile(request, username):
    if not match_logged_user(request.user, username):
        return HttpResponseForbidden(render(request, "feed/not_allowed.html"))
        #return HttpResponseForbidden("You are NOT ALLOWED to see this!")
    user_obj = models.User.objects.get(id=request.user.id)
    if user_obj.username_original == "":
        user_obj.username_original = user_obj.username
        user_obj.save()

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
    if request.user.is_authenticated:
        return redirect("user_profile_base")

    register_form = forms.RegisterForm()

    if request.method == "POST":
        user_i = models.User(username=request.POST["username_original"].lower())
        register_form = forms.RegisterForm(request.POST, instance=user_i)
        try:
            if register_form.errors or not register_form.is_valid:
                raise ValidationError("Error validating form")
            user_inst = register_form.save()

        except (IntegrityError, ValueError, ValidationError) as err:
            if str(err) == "Username exists":
                register_form.add_error("username_original", "User with this username already exists.")
            return render(request, "feed/users/register.html", {"user": request.user, "form": register_form})

        login(request, user_inst)
        return redirect("users_login")

    return render(request, "feed/users/register.html", {"user": request.user, "form": register_form})

### API ###
"""
class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
"""

#@csrf_exempt
@api_view(["GET","POST"]) #https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/#object-level-permissions
@permission_classes([api_permissions.IsOwner]) #TODO: check_object_permissions, generating tokens for api https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
def api_users(request):
    if request.method == "GET":
        users = models.User.objects.all()
        serial_users = serializers.UserSerializer(users, many=True)
        return Response(serial_users.data)

    elif request.method == "POST":
        data = JSONParser().parse(request)
        #print(data)
        serializer = serializers.UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response("valid" if serializer.is_valid() else "invalid", status=status.HTTP_201_CREATED)

@api_view(["GET", "POST", "DELETE"])
@permission_classes([permissions.IsAuthenticated])
def api_data(request, username, feed_name):
        if match_logged_user(request.user, username):
            try:
                feed = models.Feed.objects.get(name=feed_name, owner__username=username.lower())
                #print(feed)
            except models.Feed.DoesNotExist:
                print("feed does not exist")
                return Response({'error':f'Feed with name \'{feed_name}\' does not exist.'}, status=status.HTTP_404_NOT_FOUND)

            if request.method == "POST":
                serial_data = serializers.DataSerializer(data=request.data, many=True)

                ################    serial_data.update({"feed":feed})
                print(serial_data.initial_data)

                for data in serial_data.initial_data:
                    if isinstance(data["value"], str):
                        try:
                            data["value"] = float(data["value"])
                        except ValueError:
                            return Response({'error':'Data is not valid. (string, not int/float)'}, status=status.HTTP_400_BAD_REQUEST)
                if serial_data.is_valid():
                    serial_data.save(feed=feed)
                    return Response({'status':'Successfully created.'}, status=status.HTTP_201_CREATED)

                else:
                    return Response({'error':'Data is not valid.'}, status=status.HTTP_400_BAD_REQUEST)

            elif request.method == "DELETE":
                pass #TODO

            else:
                feeds_data = models.Data.objects.filter(feed__id=feed.id)
                data_serialized = serializers.DataSerializer(feeds_data, many=True)
                return Response(data_serialized.data)

        else:
            print("user dont match")
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
            serialized_feed = serializers.FeedSerializer(data=request.data)
            print(serialized_feed.initial_data)
            if serialized_feed.is_valid():
                user = models.User.objects.get(username=username.lower())
                serialized_feed.save(owner=user)
                return Response({'status':f'Feed \'{serialized_feed.data.get("name")}\' successfully created.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Feed is not valid.'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            feeds_serialized = serializers.FeedSerializer(feeds, many=True)
            return Response(feeds_serialized.data)

    else:
        print("feed does not exist")
        return Response({'error': f'User with name \'{username}\' does not exist.'}, status=status.HTTP_404_NOT_FOUND)

