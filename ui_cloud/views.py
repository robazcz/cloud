from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

from django.views import View

from .forms import LoginForm
from .models import User

class Login(View):
    form_class = LoginForm
    template = "ui_cloud/login.html"
    #model = User

    def get(self, request):
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

class Overview(View):
    def get(self, request):
        return HttpResponse("Overview")
    
def Logout(request):
    logout(request)
    return redirect("Login")