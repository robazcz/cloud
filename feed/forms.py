from django import forms
from django.contrib.auth.forms import UserCreationForm
from . import models

class LoginForm(forms.ModelForm):
    template_name = "form_snippet.html" #Custom template
    class Meta:
        model = models.User
        fields = ["username", "password"]

        widgets = {
            "password": forms.PasswordInput(),
            #"username": forms.TextInput()
        }

class NewFeed(forms.ModelForm):
    # template_name = "form_snippet.html"
    class Meta:
        model = models.Feed
        fields = ["name"]

class RegisterForm(UserCreationForm):
    template_name = "form_snippet.html"  # Custom template
    class Meta(UserCreationForm.Meta):
        model = models.User