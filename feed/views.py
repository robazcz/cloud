from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseForbidden, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError

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
def feed_list(request):
    if request.method == "POST":
        miss_i = models.Feed(owner_id=request.user.id)
        new_f = forms.NewFeed(request.POST, instance=miss_i)
        try:
            if new_f.errors or not new_f.is_valid:
                print(new_f)
                raise ValidationError("Not valid.")
            new_f.save()

        except (IntegrityError, ValueError, ValidationError) as err:
            feeds = models.Feed.objects.filter(owner__username=request.user.username).values("id", "name", "date_created", "owner__username")
            return render(request, "feed/feed_list.html", {"user": request.user, "form": {"form":forms.NewFeed(request.POST), "errors": new_f.errors, "error":err}, "feeds": feeds})

        feeds = models.Feed.objects.filter(owner__username=request.user.username).values("id", "name", "date_created", "owner__username")
        return render(request, "feed/feed_list.html", {"user":request.user, "form": {"form":forms.NewFeed}, "feeds": feeds})

    else:
        feeds = models.Feed.objects.filter(owner__username=request.user.username).values("id", "name", "date_created", "owner__username")
        # print(feeds)

    return render(request, "feed/feed_list.html", {"user":request.user, "form": {"form":forms.NewFeed} , "feeds": feeds})

@login_required
def feed_view(request, username, feed_name):
    try:
        feed = models.Feed.objects.get(name=feed_name, owner__username=username.lower())
    except models.Feed.DoesNotExist:
        raise Http404(f"Feed with name {feed_name} does not exist.")
    print(feed.owner)
    data = models.Data.objects.filter(feed__id = feed.id)

    return render(request, "feed/feed_view.html", {"user":request.user, "feed": feed, "data": data})

def new_data(request, username, feed_name):
    try:
        feed = models.Feed.objects.get(name=feed_name, owner__username=username.lower())
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

    redirect_to = request.POST.get("next", None) if request.method == "POST" else request.GET.get("next", None)

    if request.method == "POST":
        #print(request.POST["username"])
        username = request.POST["username"].lower()
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

    else:
        print(redirect_to)
        print(f"user auth? {request.user.is_authenticated}")

        if request.user.is_authenticated:
            return redirect("user_profile", request.user.username) if not redirect_to else redirect(redirect_to)
        else:
            return render(request, "feed/users/login.html", {"next": redirect_to, "form": {"errors": False, "form":forms.LoginForm}, "user": request.user})

    #return render(request, "feed/users/login.html", {"next":redirect_to, "form":{"errors": False}, "user": request.user})

def match_logged_user(logged, user):
    return logged.username == user.lower()

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
            return render(request, "feed/users/register.html", {"form": {"errors":None, "form":forms.RegisterForm}})
        
        elif request.method == "POST":
            user_i = models.User(username=request.POST["username_original"].lower())
            user = forms.RegisterForm(request.POST, instance=user_i)  #TODO: ke každý práci s username - lower username, přidat original username field
            #user_inst = models.User.objects.create_user(username=request.POST["username"], password=request.POST["password"])
            try:
                if user.errors or not user.is_valid:
                    #print(f"valid? {user.errors.as_json()}")
                    raise ValidationError("Error validating form")
                user_inst = user.save()
            # user.clean()
            except (IntegrityError, ValueError, ValidationError):
                ex = user.errors.as_data()
                print(ex)
                return render(request, "feed/users/register.html", {"form": {"errors":ex, "error":True, "form":forms.RegisterForm(request.POST)}})

            login(request, user_inst)
            return redirect("users_login")

    else:
        return redirect("user_profile_base")
    
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

@api_view(["GET", "POST"])
@permission_classes([permissions.IsAuthenticated])
def api_data(request, username, feed_name):
        if match_logged_user(request.user, username):
            try:
                feed = models.Feed.objects.get(name=feed_name, owner__username=username)
                #print(feed)
            except models.Feed.DoesNotExist:
                print("feed does not exist")
                return Response({'error':f'Feed with name \'{feed_name}\' does not exist.'}, status=status.HTTP_404_NOT_FOUND)

            if request.method == "POST":
                serial_data = serializers.DataSerializer(data=request.data, many=True)
                ################    serial_data.update({"feed":feed})
                print(serial_data.initial_data)
                if serial_data.is_valid():
                    serial_data.save(feed=feed)
                    return Response({'status':'Successfully created.'}, status=status.HTTP_201_CREATED)
                
                else:
                    return Response({'error':'Data is not valid.'}, status=status.HTTP_400_BAD_REQUEST)            

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
                user = models.User.objects.get(username=username)
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

import random
def graph(request):
    data = [{"poradi": number, "hodnota": random.randint(0, 50)} for number in range(10)]

    feed = models.Feed.objects.get(name="jamaica", owner__username="admin")
    datas = models.Data.objects.filter(feed__id=feed.id)
    print(datas)
    data = [{"value":i.value , "date":i.date_created} for i in datas]
    print(data)
    return render(request, "feed/graph.html", {"data": data})