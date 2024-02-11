from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.urls import reverse

from django.views import View
from django.views.generic import ListView, FormView
from django.views.generic.edit import FormMixin

from .forms import LoginForm, FeedForm, ValueForm
from .models import User, Feed, Data

class Login(View):
    form_class = LoginForm
    template = "ui_cloud/login.html"
    #model = User

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("Overview")
        form = self.form_class()
        redir = request.GET.get("next", "Overview")
        return render(request, self.template, {"form": form, "next": redir})
    
    def post(self, request):
        redir = request.POST.get("next", "Overview")
        creds = [request.POST["username"], request.POST["password"]]
        user = authenticate(request, username=creds[0], password=creds[1])

        if user is not None:
            login(request, user)
            return redirect(redir)
        else:
            form = self.form_class(request.POST)
            return render(request, self.template, {"form": form, "next": redir})

class Overview(FormMixin, ListView):
    template_name = "ui_cloud/overview.html"
    context_object_name = "feed_list"
    form_class = FeedForm
    paginate_by = 5
    
    def post(self, request):
        #self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_queryset(self):
        self.feeds = Feed.objects.filter(owner__username=self.request.user.username)
        return self.feeds
    
    def get_success_url(self):
        return reverse("Overview")
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        print(form.cleaned_data)
        form.save()
        return super(Overview, self).form_valid(form)

    # def get(self, request):
    #     return HttpResponse("Overview")

class FeedView(FormMixin, ListView):
    template_name = "ui_cloud/feed.html"
    context_object_name = "value_list"
    form_class = ValueForm
    paginate_by = 5

    #feed_name = name=kwargs["name"]

    def post(self, request, name):
        form = self.get_form()
        print(name)

        if form.is_valid():
            return self.form_valid(form, name)
        else:
            return self.form_invalid(form)

    def get_queryset(self):
        feed = get_object_or_404(Feed, owner__username=self.request.user.username, name=self.kwargs["name"])
        self.values = Data.objects.filter(feed=feed)
        print(self.values)
        return self.values
    
    def get_success_url(self):
        return reverse("FeedView", args=[self.kwargs["name"]])
    
    def form_valid(self, form, name):
        form.instance.feed = get_object_or_404(Feed, owner__username=self.request.user.username, name=self.kwargs["name"])
        print(form.cleaned_data)
        form.save()
        return super(FeedView, self).form_valid(form)

    
def Logout(request):
    logout(request)
    return redirect("Login")